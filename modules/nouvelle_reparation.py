import streamlit as st
from db import get_connection
from modules import updates  # pour log_action
import psycopg2.extras  


def app():
    st.title("➕ Ajouter une nouvelle réparation")

    with st.form("form_reparation"):
        type_appareil = st.selectbox("Type d'appareil", ["Téléphone", "Tablette", "PC", "PlayStation", "Autre"])
        os = st.selectbox("Système d'exploitation", ["Android", "iOS", "Windows", "Linux", "Autre"])
        modele = st.text_input("Modèle de l'appareil")
        panne = st.text_area("Description de la panne")
        numero_tel = st.text_input("📱 Numéro de téléphone du client")

        montant_total = st.number_input("Montant total (TND)", min_value=0.0, step=1.0)
        acompte = st.number_input("Acompte versé (TND)", min_value=0.0, step=1.0)
        paiement_effectue = st.radio("Paiement effectué ?", ["Oui", "Non"])
        type_paiement = st.selectbox("Type de paiement", ["Espèces", "Carte", "Virement", "Autre"])
        statut = st.selectbox("Statut", [
            "En attente", "En cours de réparation", "Diagnostiqué", "En attente de pièces",
            "Réparé", "En attente de paiement", "Livré", "Annulé"
        ])

        submit = st.form_submit_button("💾 Enregistrer")

    if submit:
        if not numero_tel.isdigit():
            st.error("❌ Le numéro de téléphone ne doit contenir que des chiffres.")
            st.stop()
        if len(numero_tel) != 8:
            st.error("❌ Le numéro de téléphone doit contenir exactement 8 chiffres.")
            st.stop()

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            insert_query = """
                INSERT INTO reparations (
                    type_appareil, os, panne, modele, numero_tel,
                    montant_total, acompte, paiement_effectue,
                    type_paiement, statut
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            values = (
                type_appareil, os, panne, modele, numero_tel,
                montant_total, acompte,
                True if paiement_effectue == "Oui" else False,
                type_paiement, statut
            )
            cursor.execute(insert_query, values)
            dernier_id = cursor.fetchone()[0]

            code_reparation = f"R-{dernier_id:07d}"
            cursor.execute("UPDATE reparations SET code_reparation = %s WHERE id = %s", (code_reparation, dernier_id))
            conn.commit()

            st.success(f"✅ Réparation enregistrée avec le code **{code_reparation}**")

            updates.log_action(
                action_type="ajout",
                target_type="reparation",
                detail=f"Ajout de la réparation {code_reparation} ({type_appareil} - {modele})"
            )

        except Exception as e:
            st.error(f"❌ Erreur lors de l'enregistrement : {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
