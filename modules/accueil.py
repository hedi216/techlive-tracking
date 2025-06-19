import streamlit as st
from db import get_connection
import psycopg2.extras  

def app():
    st.title("📱 Application de Réparation - TechLive")
    st.write("Bienvenue dans l'application de gestion des réparations.")
    st.write("Cette application vous permet de suivre et de gérer les réparations de vos appareils électroniques.")
    st.write("Utilisez le menu latéral pour naviguer entre les différentes sections de l'application.")

    st.markdown("---")
    st.subheader("🔎 Rechercher une référence")

    col1, col2, col3 = st.columns([1, 3, 2])
    with col1:
        prefix = st.selectbox("", ["R", "C"], label_visibility="collapsed")
    with col2:
        numero = st.text_input("", placeholder="Entrez le numéro", label_visibility="collapsed")
    with col3:
        numero_tel = st.text_input("", placeholder="Téléphone", label_visibility="collapsed")

    if numero or numero_tel:
        if not numero_tel:
            st.warning("📌 Veuillez entrer votre numéro de téléphone.")
        elif not numero_tel.isdigit() or len(numero_tel) != 8:
            st.error("❌ Le numéro de téléphone doit contenir exactement 8 chiffres.")
        else:
            try:
                conn = get_connection()
                cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

                if prefix == "R":
                    if numero:
                        code = f"{prefix}-{int(numero):07d}" if numero.isdigit() else f"{prefix}-{numero}"
                        cursor.execute(
                            "SELECT * FROM reparations WHERE code_reparation = %s AND numero_tel = %s",
                            (code, numero_tel)
                        )
                        result = cursor.fetchone()

                        if result:
                            st.success(f"✅ Réparation trouvée : {result['code_reparation']}")
                            afficher_reparation(result)
                        else:
                            st.error("❌ Aucune réparation trouvée avec ce code et numéro.")
                    else:
                        cursor.execute(
                            "SELECT * FROM reparations WHERE numero_tel = %s ORDER BY date_enregistrement DESC",
                            (numero_tel,)
                        )
                        results = cursor.fetchall()
                        if results:
                            st.success(f"✅ {len(results)} réparation(s) trouvée(s) pour ce numéro.")
                            for rep in results:
                                with st.expander(f"{rep['code_reparation']} - {rep['type_appareil']} - {rep['modele']}   |   ✅ {rep['statut']}"):

                                    afficher_reparation(rep)
                        else:
                            st.warning("Aucune réparation enregistrée pour ce numéro.")
                elif prefix == "C":
                    st.info("📦 Suivi des commandes à venir.")

            except Exception as e:
                st.error(f"Erreur : {e}")
            finally:
                cursor.close()
                conn.close()

def afficher_reparation(rep):
    st.write(f"📱 **Appareil :** {rep['type_appareil']} - {rep['modele']}")
    st.write(f"🧬 **OS :** {rep['os']}")
    st.write(f"🛠️ **Panne :** {rep['panne']}")
    st.write(f"💰 **Montant :** {rep['montant_total']} TND")
    st.write(f"💵 **Acompte :** {rep['acompte']} TND")
    st.write(f"✅ **Paiement :** {'Oui' if rep['paiement_effectue'] else 'Non'}")
    st.write(f"📌 **Statut :** `{rep['statut']}`")
