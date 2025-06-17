import streamlit as st
from db import get_connection
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def app():
    # CSS global : fond clair
    st.markdown("""
        <style>
        body {
            background-color: #f5f6f8;
        }
        .login-title {
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    # Centrage vertical "simulé" avec espace
    st.write("\n\n\n\n")

    # Centrage horizontal via colonnes
    left, center, right = st.columns([1, 2, 1])
    with center:
        with st.container():
            # Conteneur visuel
            st.markdown("### ")
            #st.write("\n\n\n\n")
            st.image("src/logo.jpg", width=80)
            st.markdown("<h2 class='login-title'>🔐 Connexion à TechLive</h2>", unsafe_allow_html=True)
            st.markdown("Veuillez vous connecter pour accéder à l'application.")

            with st.form("login_form"):
                username = st.text_input("Nom d'utilisateur")
                password = st.text_input("Mot de passe", type="password")
                submit = st.form_submit_button("🔓 Connexion")

            if submit:
                try:
                    conn = get_connection()
                    cursor = conn.cursor(dictionary=True)
                    hashed_pw = hash_password(password)

                    cursor.execute("""
                        SELECT u.id, u.username, u.role_id, r.nom AS role
                        FROM users u
                        JOIN roles r ON u.role_id = r.id
                        WHERE u.username = %s AND u.password = %s AND u.actif = 1
                    """, (username, hashed_pw))

                    user = cursor.fetchone()

                    if user:
                        st.session_state["utilisateur"] = {
                            "id": user["id"],
                            "username": user["username"],
                            "role_id": user["role_id"],
                            "role": user["role"]
                        }
                        st.success("Connexion réussie !")
                        st.rerun()
                        st.stop()
                    else:
                        st.error("Identifiants incorrects ou utilisateur inactif.")
                except Exception as e:
                    st.error(f"Erreur de connexion : {e}")
                finally:
                    cursor.close()
                    conn.close()