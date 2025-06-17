import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
import os
from modules import login

# 👉 fonction utilitaire pour récupérer le rôle
def get_user_role():
    return st.session_state.get("utilisateur", {}).get("role", "")

st.set_page_config(page_title="TechLive", layout="wide", page_icon="🛠️")

if "utilisateur" not in st.session_state:
    login.app()
    st.stop()

# Sidebar - logo + menu
with st.sidebar:
    st.title("📱 TechLive")

    logo_path = os.path.join("src", "logo.jpg")
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)

    st.markdown("### 📁 Menu")

    menu_items = [
        "Accueil",
        "Nouvelle réparation",
        "Liste des réparations",
        "Achats"
    ]
    menu_icons = [
        "house",
        "plus-circle",
        "list-task",
        "cash-coin"
    ]

    # ➕ Montre "Utilisateurs" et "Updates" si role = owner
    if get_user_role() in ["owner", "gerant"]:
        menu_items.extend(["Utilisateurs", "Updates","Rôles"])
        menu_icons.extend(["people", "arrow-up-circle","shield-lock"])

    selected = option_menu(
        menu_title="",
        options=menu_items,
        icons=menu_icons,
        menu_icon="cast",
        default_index=0
    )

    # Espacement pour pousser les éléments vers le bas selon le rôle
    if get_user_role() in ["owner", "gerant"]:
        st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='height:180px;'></div>", unsafe_allow_html=True)


    # Bouton Se déconnecter
    if st.button("🔒 Se déconnecter"):
        st.session_state.clear()
        st.rerun()

    # Affichage du nom et rôle d'utilisateur connecté
    if "utilisateur" in st.session_state:
        username = st.session_state["utilisateur"].get("username", "Utilisateur inconnu")
        st.markdown(
            f"<p style='text-align: center; font-size: 14px; margin-top: 10px;'>👤 Connecté : <b>{username}</b></p>",
            unsafe_allow_html=True
        )
        role = st.session_state["utilisateur"].get("role", "Rôle inconnu")
        st.markdown(
            f"<p style='text-align: center; font-size: 13px; color: gray;'>🔐 Rôle : <b>{role.capitalize()}</b></p>",
            unsafe_allow_html=True
        )
# Navigation
if selected == "Accueil":
    import modules.accueil as pg
elif selected == "Nouvelle réparation":
    import modules.nouvelle_reparation as pg
elif selected == "Liste des réparations":
    import modules.liste_reparations as pg
elif selected == "Achats":
    import modules.achats as pg
elif selected == "Utilisateurs":
    if get_user_role() in ["owner", "gerant"]:
        import modules.users as pg
    else:
        st.error("⛔️ Accès refusé.")
        st.stop()
elif selected == "Updates":
    if get_user_role() in ["owner", "gerant"]:
        import modules.updates as pg
    else:
        st.error("⛔️ Accès refusé.")
        st.stop()
elif selected == "Rôles":
    if get_user_role() in ["owner", "gerant"]:
        import modules.roles as pg
    else:
        st.error("⛔️ Accès refusé.")
        st.stop()


pg.app()
