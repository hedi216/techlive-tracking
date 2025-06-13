import streamlit as st
import pandas as pd
from db import get_connection

def app():
    st.title("📋 Liste des réparations")

    filtre_code = st.text_input("🔍 Filtrer par référence (ex: R-0000001)")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Récupération des données
        if filtre_code:
            cursor.execute(
                "SELECT * FROM reparations WHERE code_reparation LIKE %s ORDER BY date_enregistrement DESC",
                (f"%{filtre_code}%",)
            )
        else:
            cursor.execute("SELECT * FROM reparations ORDER BY date_enregistrement DESC")

        reparations = cursor.fetchall()

        if reparations:
            st.write("🗂️ Réparations enregistrées :")

            for rep in reparations:
                with st.expander(f"{rep['code_reparation']} - {rep['type_appareil']} - {rep['modele']}"):
                    st.write(f"🛠️ OS : {rep['os']} | Panne : {rep['panne']}")
                    st.write(f"💰 Montant : {rep['montant_total']} TND")
                    st.write(f"💵 Acompte : {rep['acompte']} TND")
                    st.write(f"✅ Paiement effectué : {'Oui' if rep['paiement_effectue'] else 'Non'}")
                    st.write(f"💳 Type de paiement : {rep['type_paiement']}")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("✏️ Éditer", key=f"edit_{rep['id']}"):
                            st.info("Édition à venir.")
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
                        st.button("🧾 Facture", key=f"facture_{rep['id']}")
                    with col4:
                        st.button("🧾 Ticket", key=f"ticket_{rep['id']}")

        else:
            st.info("Aucune réparation trouvée.")

    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {e}")

    finally:
        cursor.close()
        conn.close()
