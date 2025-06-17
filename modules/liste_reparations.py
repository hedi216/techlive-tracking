import streamlit as st
from db import get_connection
from modules.updates import log_action
from datetime import datetime
import base64
import locale
from fpdf import FPDF

# Utiliser le français pour la date
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

# ========== GESTION PDF FACTURE ==========

class FacturePDF(FPDF):
    def header(self):
        # Encadré d'en-tête à gauche
        self.set_fill_color(240, 240, 240)
        self.rect(10, 10, 80, 36, 'DF')
        self.set_xy(10, 12)
        self.set_font("Arial", "B", 12)
        self.cell(80, 6, "TLU Techlive Unity", ln=True, align="C")
        self.set_font("Arial", "", 10)
        self.cell(80, 6, "Repar. Materiels Info", ln=True, align="C")
        self.cell(80, 6, "Khezema Est 4051", ln=True, align="C")
        self.cell(80, 6, "Matricule Fiscal : 886815/N", ln=True, align="C")
        if hasattr(self, 'societe_tel') and self.societe_tel:
            self.cell(80, 6, f"{self.societe_tel}", ln=True, align="C")

        # Logo à droite
        self.image("modules/src/logo.jpg", 170, 10, 30)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, "Merci pour votre confiance !", 0, 0, "C")

def generer_facture_pdf(nom, identifiant, type_id, tel, adresse, societe_tel, lignes):
    pdf = FacturePDF()
    pdf.societe_tel = societe_tel.split(" - ")[-1]
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Informations client
    pdf.set_xy(15, 50)
    pdf.cell(0, 8, f"Client : {nom}", ln=True)
    pdf.set_x(15)
    pdf.cell(0, 8, f"{type_id} : {identifiant}", ln=True)
    pdf.set_x(15)
    pdf.cell(0, 8, f"Téléphone : {tel}", ln=True)
    if adresse:
        pdf.set_x(15)
        pdf.multi_cell(100, 8, f"Adresse : {adresse}")

    # Date à droite
    date_str = datetime.now().strftime("%d %B %Y")
    pdf.set_xy(140, 85)
    pdf.cell(0, 8, f"Date : {date_str}", ln=True)

    pdf.ln(5)

    # Tableau de facturation
    left_margin = 15
    col_widths = [30, 80, 25, 25, 30]
    pdf.set_font("Arial", "B", 10)
    pdf.set_x(left_margin)
    pdf.set_fill_color(240, 240, 240)
    headers = ["Réf", "Appareil", "Prix", "TVA 19%", "Total"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, 1, 0, 'C', True)
    pdf.ln()

    pdf.set_font("Arial", size=10)
    total = 0
    for ligne in lignes:
        prix = float(ligne["montant_total"])
        tva = round(prix * 0.19, 2)
        total_ligne = round(prix + tva, 2)
        total += total_ligne
        appareil = f"{ligne['type_appareil']} {ligne['modele']}"

        pdf.set_x(left_margin)
        pdf.cell(col_widths[0], 10, ligne["code_reparation"], 1)
        pdf.cell(col_widths[1], 10, appareil[:35], 1)
        pdf.cell(col_widths[2], 10, f"{prix:.2f}", 1)
        pdf.cell(col_widths[3], 10, f"{tva:.2f}", 1)
        pdf.cell(col_widths[4], 10, f"{total_ligne:.2f}", 1)
        pdf.ln()

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.set_x(left_margin)
    pdf.cell(0, 10, f"Total TTC : {total:.2f} TND", ln=True)

    return pdf.output(dest="S").encode("latin-1"), date_str
def get_logo_base64(path="modules/src/logo.jpg"):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def generer_ticket_html(rep):
    date = datetime.now().strftime("%d/%m/%Y %H:%M")
    logo_base64 = get_logo_base64()
    return f"""
    <div id='ticket_{rep['id']}' style='border: 1px solid #ccc; padding: 10px; margin-top: 20px; width: 300px;'>
        <div style='text-align: center;'>
            <img src='data:image/png;base64,{logo_base64}' width='100' />
            <h3>TECHLIVE UNITY</h3>
        </div>
        <p>Date : {date}</p>
        <p>📱 Tel : {rep['numero_tel']}</p>
        <p>Appareil : {rep['type_appareil']} - {rep['modele']}</p>
        <p>Panne : {rep['panne']}</p>
        <p>Montant : {rep['montant_total']} TND</p>
        <p>Acompte : {rep['acompte']} TND</p>
        <p>Payé : {'Oui' if rep['paiement_effectue'] else 'Non'} ({rep['type_paiement']})</p>
        <p style='text-align: center; font-weight: bold; font-size: 16px;'>Réf : {rep['code_reparation']}</p>
        <div style='font-size: 10px; text-align: center; margin-top: 30px;'>Merci pour votre confiance !</div>
    </div>
    <div style='text-align: center; margin-top: 10px;'>
        <button onclick="printDiv('ticket_{rep['id']}')">🖨️ Imprimer</button>
    </div>
    <script>
        function printDiv(id) {{
            var content = document.getElementById(id).outerHTML;
            var myWindow = window.open('', '', 'width=400,height=600');
            myWindow.document.write('<!DOCTYPE html><html><head><title>Print</title></head><body>' + content + '</body></html>');
            myWindow.document.close();
            myWindow.focus();
            myWindow.print();
            myWindow.close();
        }}
    </script>
    """


# ========== APP PRINCIPALE ==========

def app():
    st.title("📋 Liste des réparations")

    if "selected_reparations" not in st.session_state:
        st.session_state.selected_reparations = set()
    if "facture_mode" not in st.session_state:
        st.session_state.facture_mode = False
    if "afficher_formulaire_facture" not in st.session_state:
        st.session_state.afficher_formulaire_facture = False
    if "delete_confirm" not in st.session_state:
        st.session_state.delete_confirm = {}

    filtre_code = st.text_input("🔍 Filtrer par référence (ex: R-0000001)")

    if st.button("📄 Facturation"):
        st.session_state.facture_mode = not st.session_state.facture_mode
        st.session_state.afficher_formulaire_facture = False

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if filtre_code:
            like = f"%{filtre_code}%"
            cursor.execute("""
                SELECT * FROM reparations
                WHERE code_reparation LIKE %s OR numero_tel LIKE %s OR type_appareil LIKE %s 
                OR modele LIKE %s OR os LIKE %s OR panne LIKE %s OR type_paiement LIKE %s OR statut LIKE %s
                ORDER BY date_enregistrement DESC
            """, (like,) * 8)
        else:
            cursor.execute("SELECT * FROM reparations ORDER BY date_enregistrement DESC")

        reparations = cursor.fetchall()

        if reparations:
            if st.session_state.facture_mode and st.session_state.selected_reparations:
                if st.button("💼 Facturer les sélectionnées"):
                    ids_selectionnes = tuple(st.session_state.selected_reparations)
                    placeholders = ", ".join(["%s"] * len(ids_selectionnes))
                    cursor.execute(f"""
                        SELECT id, code_reparation FROM reparations 
                        WHERE id IN ({placeholders}) AND paiement_effectue = FALSE
                    """, ids_selectionnes)
                    non_payees = cursor.fetchall()
                    if non_payees:
                        erreurs = ", ".join([r["code_reparation"] for r in non_payees])
                        st.error(f"❌ Réparations non payées : {erreurs}")
                        st.stop()
                    else:
                        st.session_state.afficher_formulaire_facture = True


            if st.session_state.afficher_formulaire_facture:
                st.subheader("📄 Détails de la facture")
                with st.form("form_facture"):
                    nom = st.text_input("👤 Nom du client ou société")
                    type_id = st.selectbox("Type d'identifiant", ["CIN", "MF"])
                    identifiant_label = "CIN" if type_id == "CIN" else "MF"
                    identifiant = st.text_input(identifiant_label)
                    tel = st.text_input("📱 Téléphone du client", max_chars=8)
                    adresse = st.text_area("🏠 Adresse (facultatif)")

                    cursor.execute("""
                        SELECT username, telephone FROM users
                        JOIN roles ON users.role_id = roles.id
                        WHERE roles.nom IN ('owner', 'gerant') AND telephone IS NOT NULL
                    """)
                    societes = cursor.fetchall()
                    societe_tel = st.selectbox(
                        "☎️ Numéro de la société à afficher sur la facture",
                        [f"{s['username']} - {s['telephone']}" for s in societes]
                    )
                    valider = st.form_submit_button("✅ Générer la facture")

                if valider:
                    if not nom.strip() or not identifiant.strip() or not tel.strip():
                        st.warning("Remplir tous les champs obligatoires.")
                        st.stop()
                    if not tel.isdigit() or len(tel) != 8:
                        st.warning("Numéro client doit contenir 8 chiffres.")
                        st.stop()

                    lignes = [r for r in reparations if r["id"] in st.session_state.selected_reparations]
                    pdf_bytes, date_str = generer_facture_pdf(nom, identifiant, identifiant_label, tel, adresse, societe_tel, lignes)

                    date_filename = date_str.replace(" ", "-").lower()
                    filename = f"facture_{nom.lower()}_{date_filename}.pdf"

                    st.success("✅ Facture générée avec succès !")
                    st.download_button("📥 Télécharger la facture", data=pdf_bytes, file_name=filename, mime="application/pdf")

                    st.session_state.afficher_formulaire_facture = False
                    st.session_state.facture_mode = False
                    st.session_state.selected_reparations.clear()



            st.divider()
            items_per_page = 11
            total_pages = (len(reparations) - 1) // items_per_page + 1
            page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            current_reps = reparations[start_idx:end_idx]

            for rep in current_reps:
                if st.session_state.facture_mode:
                    col1, col2 = st.columns([0.05, 0.95])
                    with col1:
                        checked = st.checkbox("", key=f"chk_{rep['id']}", value=rep['id'] in st.session_state.selected_reparations)
                        if checked:
                            st.session_state.selected_reparations.add(rep['id'])
                        else:
                            st.session_state.selected_reparations.discard(rep['id'])
                    with col2:
                        st.markdown(f"**{rep['code_reparation']} - {rep['type_appareil']} - {rep['modele']}**")
                else:
                    with st.expander(f"{rep['code_reparation']} - {rep['type_appareil']} - {rep['modele']}"):
                        st.write(f"📱 Téléphone : {rep['numero_tel']}")
                        st.write(f"💰 Montant : {rep['montant_total']} TND | 💵 Acompte : {rep['acompte']} TND")
                        st.write(f"✅ Paiement : {'Oui' if rep['paiement_effectue'] else 'Non'} | 💳 Type : {rep['type_paiement']}")
                        st.write(f"📌 Statut : `{rep['statut']}`")

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("✏️ Éditer", key=f"edit_{rep['id']}"):
                                st.session_state[f"edit_mode_{rep['id']}"] = True
                        with col2:
                            if st.button("🗑️ Supprimer", key=f"del_{rep['id']}"):
                                st.session_state.delete_confirm[rep['id']] = True
                            if st.session_state.delete_confirm.get(rep['id']):
                                st.warning(f"Confirmer suppression de {rep['code_reparation']} ?")
                                c1, c2 = st.columns(2)
                                with c1:
                                    if st.button("✅ Oui", key=f"conf_{rep['id']}"):
                                        cursor.execute("DELETE FROM reparations WHERE id = %s", (rep["id"],))
                                        conn.commit()
                                        log_action("suppression", "reparation", rep['code_reparation'])
                                        st.success("Réparation supprimée.")
                                        st.rerun()
                                with c2:
                                    if st.button("❌ Non", key=f"cancel_{rep['id']}"):
                                        st.session_state.delete_confirm[rep['id']] = False
                        with col3:
                            if st.button("🧾 Ticket", key=f"ticket_{rep['id']}"):
                                st.markdown(generer_ticket_html(rep), unsafe_allow_html=True)

            st.markdown(f"<p style='text-align:center;'>Page {page} sur {total_pages}</p>", unsafe_allow_html=True)

        else:
            st.info("Aucune réparation trouvée.")

    except Exception as e:
        st.error(f"Erreur : {e}")
    finally:
        cursor.close()
        conn.close()
