import streamlit as st
from db import get_connection
import psycopg2.extras  

def log_action(action_type, target_type, detail):
    """Log une action dans la base de données"""
    try:
        username = st.session_state.get("utilisateur", {}).get("username", "inconnu")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO logs (utilisateur, action_type, target_type, detail)
            VALUES (%s, %s, %s, %s)
        """, (username, action_type, target_type, detail))
        conn.commit()
    except Exception as e:
        print(f"Erreur log_action: {e}")
    finally:
        cursor.close()
        conn.close()

def app():
    st.title("📋 Historique des actions")

    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Filtres
        st.markdown("### 🔎 Filtres")
        col1, col2, col3 = st.columns(3)

        with col1:
            cursor.execute("SELECT DISTINCT utilisateur FROM logs ORDER BY utilisateur")
            utilisateurs = [row["utilisateur"] for row in cursor.fetchall()]
            utilisateur_sel = st.selectbox("👤 Utilisateur", ["Tous"] + utilisateurs, key="filtre_utilisateur")

        with col2:
            cursor.execute("SELECT DISTINCT action_type FROM logs ORDER BY action_type")
            actions = [row["action_type"] for row in cursor.fetchall()]
            action_sel = st.selectbox("⚙️ Action", ["Toutes"] + actions, key="filtre_action")

        with col3:
            cursor.execute("SELECT DISTINCT target_type FROM logs ORDER BY target_type")
            cibles = [row["target_type"] for row in cursor.fetchall()]
            cible_sel = st.selectbox("🎯 Cible", ["Toutes"] + cibles, key="filtre_cible")

        # Requête avec filtres
        requete = "SELECT * FROM logs WHERE 1=1"
        params = []

        if utilisateur_sel != "Tous":
            requete += " AND utilisateur = %s"
            params.append(utilisateur_sel)

        if action_sel != "Toutes":
            requete += " AND action_type = %s"
            params.append(action_sel)

        if cible_sel != "Toutes":
            requete += " AND target_type = %s"
            params.append(cible_sel)

        requete += " ORDER BY date_action DESC"
        cursor.execute(requete, tuple(params))
        logs = cursor.fetchall()

        # Pagination
        st.markdown("### 🧾 Résultats")
        items_per_page = 11
        total_pages = (len(logs) - 1) // items_per_page + 1

        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1, key="page_selector")
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        current_logs = logs[start_idx:end_idx]

        if current_logs:
            for log in current_logs:
                st.markdown(f"""
                <div style='padding: 10px; border: 1px solid #ccc; border-radius: 8px; margin-bottom: 8px; background-color: #f9f9f9'>
                    <b>👤 {log['utilisateur']}</b> a effectué une action <b>{log['action_type']}</b> sur <b>{log['target_type']}</b><br>
                    <small>🕒 {log['date_action'].strftime('%Y-%m-%d %H:%M:%S')}</small><br>
                    <code>{log['detail']}</code>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aucun log trouvé avec les filtres sélectionnés.")

        # Affichage du nombre total de pages
        st.markdown(f"<p style='text-align: center;'>Page {page} sur {total_pages}</p>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erreur chargement des logs : {e}")
    finally:
        cursor.close()
        conn.close()
