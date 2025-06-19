import streamlit as st
from db import get_connection
import psycopg2.extras  

def app():
    st.title("🛡️ Gestion des rôles")

    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        current_user_role = st.session_state["utilisateur"]["role"]

        # ➕ Ajouter un rôle
        st.subheader("➕ Ajouter un nouveau rôle")
        nouveau_role = st.text_input("Nom du rôle")
        if st.button("✅ Ajouter le rôle"):
            if not nouveau_role.strip():
                st.warning("Veuillez entrer un nom de rôle.")
            else:
                try:
                    cursor.execute("INSERT INTO roles (nom) VALUES (%s)", (nouveau_role.strip(),))
                    conn.commit()
                    st.success("✅ Rôle ajouté.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")

        st.markdown("---")
        st.subheader("📋 Liste des rôles existants")

        cursor.execute("SELECT * FROM roles ORDER BY id")
        roles = cursor.fetchall()

        for role in roles:
            nom = role["nom"]
            with st.expander(f"{nom.capitalize()}"):
                peut_supprimer = False

                if nom == "owner":
                    if current_user_role == "owner":
                        st.warning("🔒 Ce rôle est protégé et ne peut pas être supprimé.")
                elif nom == "gerant":
                    if current_user_role == "owner":
                        peut_supprimer = True
                    else:
                        st.warning("🔒 Seul un owner peut supprimer ce rôle.")
                else:
                    peut_supprimer = True

                if peut_supprimer:
                    if st.button("🗑️ Supprimer", key=f"del_role_{role['id']}"):
                        st.session_state[f"confirm_supp_role_{role['id']}"] = True

                    if st.session_state.get(f"confirm_supp_role_{role['id']}", False):
                        st.warning("❗ Confirmer la suppression de ce rôle ?", icon="⚠️")
                        conf1, conf2 = st.columns(2)
                        with conf1:
                            if st.button("✅ Confirmer", key=f"conf_suppr_role_{role['id']}"):
                                try:
                                    cursor.execute("DELETE FROM roles WHERE id = %s", (role["id"],))
                                    conn.commit()
                                    st.success("Rôle supprimé.")
                                    st.rerun()
                                except Exception as e:
                                    if "foreign key constraint" in str(e).lower():
                                        # Rechercher les utilisateurs avec ce rôle
                                        cursor.execute("SELECT username FROM users WHERE role_id = %s", (role["id"],))
                                        utilisateurs = cursor.fetchall()
                                        if utilisateurs:
                                            noms = ", ".join([u["username"] for u in utilisateurs])
                                            st.error(f"❌ Impossible de supprimer ce rôle car il est encore utilisé par : {noms}")
                                        else:
                                            st.error("❌ Impossible de supprimer ce rôle à cause d'une contrainte d'intégrité.")
                                    else:
                                        st.error(f"Erreur suppression : {e}")

                        with conf2:
                            if st.button("❌ Annuler", key=f"cancel_suppr_role_{role['id']}"):
                                st.session_state[f"confirm_supp_role_{role['id']}"] = False

    except Exception as e:
        st.error(f"Erreur de gestion des rôles : {e}")
    finally:
        cursor.close()
        conn.close()
