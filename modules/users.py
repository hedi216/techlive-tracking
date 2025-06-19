import streamlit as st
from db import get_connection
import hashlib
import re
import psycopg2.extras  

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_roles(cursor):
    cursor.execute("SELECT * FROM roles")
    return cursor.fetchall()

def app():
    st.title("👥 Gestion des utilisateurs")

    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        current_user_role = st.session_state["utilisateur"]["role"]

        # 🔼 Formulaire d'ajout
        st.subheader("➕ Ajouter un nouvel utilisateur")

        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        telephone = st.text_input("Téléphone (8 chiffres)")
        roles = get_roles(cursor)
        role_names = [r["nom"] for r in roles]
        role_selection = st.selectbox("Rôle", role_names)

        if st.button("✅ Créer l'utilisateur"):
            if not username or not password or not telephone:
                st.warning("Veuillez remplir tous les champs.")
            elif not re.fullmatch(r"\d{8}", telephone):
                st.error("Le numéro de téléphone doit contenir exactement 8 chiffres.")
            else:
                role_id = next(r["id"] for r in roles if r["nom"] == role_selection)
                hashed_pw = hash_password(password)
                try:
                    cursor.execute("INSERT INTO users (username, password, telephone, role_id) VALUES (%s, %s, %s, %s)",
                                   (username, hashed_pw, telephone, role_id))
                    conn.commit()
                    st.success("Utilisateur créé.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")

        st.markdown("---")

        # 🛠️ Gestion des utilisateurs existants
        st.subheader("📋 Liste des utilisateurs")

        cursor.execute("""
            SELECT users.id, username, actif, telephone, roles.nom as role 
            FROM users 
            JOIN roles ON users.role_id = roles.id
            ORDER BY username
        """)
        users = cursor.fetchall()

        # Pagination
        items_per_page = 8
        total_pages = (len(users) - 1) // items_per_page + 1
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1, key="page_utilisateurs")
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        current_users = users[start_idx:end_idx]

        for user in current_users:
            target_role = user["role"]
            est_protege = (
                target_role == "owner" and current_user_role != "owner"
            )

            with st.expander(f"{user['username']} ({target_role})", expanded=False):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"📞 **Téléphone :** {user.get('telephone', '-')}")
                    st.markdown(f"🟢 **Statut :** {'Actif' if user['actif'] else 'Inactif'}")

                with col2:
                    # 🗑️ Supprimer
                    if not est_protege:
                        if st.button("🗑️ Supprimer", key=f"del_{user['id']}"):
                            st.session_state[f"confirm_supp_user_{user['id']}"] = True

                        if st.session_state.get(f"confirm_supp_user_{user['id']}", False):
                            st.warning("❗ Voulez-vous vraiment supprimer cet utilisateur ?", icon="⚠️")
                            confirm_col1, confirm_col2 = st.columns(2)
                            with confirm_col1:
                                if st.button("✅ Confirmer", key=f"conf_suppr_user_{user['id']}"):
                                    try:
                                        cursor.execute("DELETE FROM users WHERE id = %s", (user["id"],))
                                        conn.commit()
                                        st.success("🗑️ Utilisateur supprimé.")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erreur suppression : {e}")
                            with confirm_col2:
                                if st.button("❌ Annuler", key=f"cancel_suppr_user_{user['id']}"):
                                    st.session_state[f"confirm_supp_user_{user['id']}"] = False
                    else:
                        st.info("🔒 Action non autorisée")

                    # 🔄 Activer/Inactiver
                    if not est_protege:
                        new_status = not user['actif']
                        if st.button("🔄 Activer/Inactiver", key=f"toggle_{user['id']}"):
                            cursor.execute("UPDATE users SET actif = %s WHERE id = %s", (new_status, user['id']))
                            conn.commit()
                            st.success("Statut mis à jour")
                            st.rerun()

    except Exception as e:
        st.error(f"Erreur : {e}")
    finally:
        cursor.close()
        conn.close()
