import streamlit as st
from PIL import Image
import os
from db import get_connection

# Configuration de la page
st.set_page_config(page_title="TechLive - Réparations", layout="wide")

# Charger le logo depuis le dossier "src"
logo_path = os.path.join("src", "logo.jpg")
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    st.sidebar.image(logo, width=200)

# Barre latérale de navigation
st.sidebar.title("📂 Menu")
page = st.sidebar.radio("Aller vers :", ["Accueil", "Nouvelle réparation", "Liste des réparations"])

# Affichage selon la page choisie
if page == "Accueil":
    st.title("📱 Application de Réparation - TechLive")
    st.write("Bienvenue dans l'application de gestion des réparations.")
elif page == "Nouvelle réparation":
    st.title("➕ Ajouter une nouvelle réparation")

    with st.form("form_reparation"):
        type_appareil = st.selectbox("Type d'appareil", ["Téléphone", "Tablette", "PC", "PlayStation", "Autre"])
        os = st.selectbox("Système d'exploitation", ["Android", "iOS", "Windows", "Linux", "Autre"])
        modele = st.text_input("Modèle de l'appareil")
        panne = st.text_area("Description de la panne")

        montant_total = st.number_input("Montant total (TND)", min_value=0.0, step=1.0)
        acompte = st.number_input("Acompte versé (TND)", min_value=0.0, step=1.0)
        paiement_effectue = st.radio("Paiement effectué ?", ["Oui", "Non"])
        type_paiement = st.selectbox("Type de paiement", ["Espèces", "Carte", "Virement", "Autre"])

        submit = st.form_submit_button("💾 Enregistrer")

    if submit:
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # 1. Insérer sans code_reparation
            insert_query = """
            INSERT INTO reparations (
                type_appareil, os, panne, modele,
                montant_total, acompte, paiement_effectue, type_paiement
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                type_appareil, os, panne, modele,
                montant_total, acompte,
                True if paiement_effectue == "Oui" else False,
                type_paiement
            )
            cursor.execute(insert_query, values)
            conn.commit()

            # 2. Récupérer ID et générer code
            dernier_id = cursor.lastrowid
            code_reparation = f"R-{dernier_id:07d}"

            # 3. Mettre à jour la ligne
            update_query = "UPDATE reparations SET code_reparation = %s WHERE id = %s"
            cursor.execute(update_query, (code_reparation, dernier_id))
            conn.commit()

            st.success(f"✅ Réparation enregistrée avec le code **{code_reparation}**")
        
        except Exception as e:
            st.error(f"❌ Erreur lors de l'enregistrement : {e}")
        
        finally:
            cursor.close()
            conn.close()

elif page == "Liste des réparations":
    st.title("📋 Liste des réparations")

    filtre_code = st.text_input("Filtrer par référence (ex: R-0000001)")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if filtre_code:
            cursor.execute(
                "SELECT * FROM reparations WHERE code_reparation LIKE %s ORDER BY date_enregistrement DESC",
                (f"%{filtre_code}%",)
            )
        else:
            cursor.execute("SELECT * FROM reparations ORDER BY date_enregistrement DESC")

        reparations = cursor.fetchall()

        if reparations:
            for rep in reparations:
                st.markdown(f"### {rep['code_reparation']} - {rep['type_appareil']} - {rep['modele']}")
                st.write(f"OS: {rep['os']} | Panne: {rep['panne']}")
                st.write(f"Montant: {rep['montant_total']} TND, Acompte: {rep['acompte']} TND, Paiement: {'Oui' if rep['paiement_effectue'] else 'Non'}")
                
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    if st.button("✏️ Éditer", key=f"edit_{rep['id']}"):
                        st.info(f"Fonction Éditer en cours de développement pour ID {rep['id']}")

                with col2:
                    if st.button("🗑️ Supprimer", key=f"del_{rep['id']}"):
                        try:
                            cursor.execute("DELETE FROM reparations WHERE id = %s", (rep['id'],))
                            conn.commit()
                            st.success(f"Réparation {rep['code_reparation']} supprimée.")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Erreur suppression : {e}")

                with col3:
                    if st.button("🧾 Facture", key=f"facture_{rep['id']}"):
                        st.info(f"Imprimer facture pour {rep['code_reparation']} (fonction à implémenter)")

                with col4:
                    if st.button("🧾 Ticket", key=f"ticket_{rep['id']}"):
                        st.info(f"Imprimer ticket pour {rep['code_reparation']} (fonction à implémenter)")

                st.markdown("---")

        else:
            st.info("Aucune réparation enregistrée.")

    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {e}")

    finally:
        cursor.close()
        conn.close()
