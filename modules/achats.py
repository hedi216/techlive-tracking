import streamlit as st
from datetime import datetime
from db import get_connection
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from modules.updates import log_action

def app():
    st.title("🛒 Suivi des achats & bénéfices")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        current_year = datetime.now().year
        current_month = datetime.now().month

        st.markdown("### 🗓️ Sélectionnez une période")
        col1, col2 = st.columns(2)
        with col1:
            annee = st.selectbox("Année", list(range(current_year, current_year - 5, -1)), index=0)
        with col2:
            mois = st.selectbox("Mois", list(range(1, 13)), index=current_month - 1)

        date_selection = f"{annee}-{mois:02d}"

        cursor.execute("SELECT * FROM reparations WHERE DATE_FORMAT(date_enregistrement, '%Y-%m') = %s", (date_selection,))
        reparations_mois = cursor.fetchall()

        if reparations_mois:
            ids_reparations = [rep["id"] for rep in reparations_mois]
            total_clients = sum(float(rep["montant_total"]) for rep in reparations_mois)

            format_ids = ",".join(["%s"] * len(ids_reparations))
            cursor.execute(f"SELECT * FROM achats WHERE reparation_id IN ({format_ids})", tuple(ids_reparations))
            achats_mois = cursor.fetchall()
            total_achats = sum(float(a["montant"]) for a in achats_mois)

            benefice = total_clients - total_achats
            nom_mois = datetime.strptime(date_selection, "%Y-%m").strftime("%B %Y")

            st.markdown(f"### 📊 Bénéfice de **{nom_mois.capitalize()}** : `{benefice:.2f} TND`")

            df_reparations = pd.DataFrame(reparations_mois)
            df_achats = pd.DataFrame(achats_mois)
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df_reparations.to_excel(writer, sheet_name="Reparations", index=False)
                df_achats.to_excel(writer, sheet_name="Achats", index=False)
            buffer.seek(0)

            pdf = FPDF()
            pdf.add_page()
            pdf.image("src/logo.jpg", x=8, y=6, w=25)
            pdf.set_xy(40, 15)
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, f"Rapport mensuel - {nom_mois}", ln=True, align="L")
            pdf.ln(27)
            pdf.set_font("Arial", size=12)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(80, 10, "Téléphone / Réparation", border=1, fill=True)
            pdf.cell(40, 10, "Montant client", border=1, fill=True)
            pdf.cell(40, 10, "Total achats", border=1, fill=True)
            pdf.cell(30, 10, "Bénéfice", border=1, ln=True, fill=True)

            for rep in reparations_mois:
                achats_rep = [a for a in achats_mois if a["reparation_id"] == rep["id"]]
                m_achats = sum(float(a["montant"]) for a in achats_rep)
                benefice_rep = float(rep["montant_total"]) - m_achats
                libelle = f"{rep['code_reparation']} - {rep['type_appareil']} {rep['modele']}"
                pdf.cell(80, 10, libelle, border=1)
                pdf.cell(40, 10, f"{rep['montant_total']:.2f} TND", border=1)
                pdf.cell(40, 10, f"{m_achats:.2f} TND", border=1)
                pdf.cell(30, 10, f"{benefice_rep:.2f}", border=1, ln=True)

            pdf.set_font("Arial", "B", 12)
            pdf.cell(160, 10, "Total bénéfice brut :", border=0)
            pdf.cell(30, 10, f"{benefice:.2f} TND", border=0, ln=True)
            pdf_bytes = pdf.output(dest='S').encode('latin1')

            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📄 Export Excel", data=buffer.getvalue(), file_name=f"rapport_{date_selection}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            with col2:
                st.download_button("📄 Rapport PDF", data=pdf_bytes, file_name=f"rapport_{date_selection}.pdf", mime="application/pdf")

        else:
            st.info("Aucune réparation enregistrée pour cette période.")

    except Exception as e:
        st.error(f"Erreur : {e}")

    st.divider()

    try:
        cursor.execute("SELECT id, code_reparation, type_appareil, modele FROM reparations ORDER BY date_enregistrement DESC")
        reparations = cursor.fetchall()
        if not reparations:
            st.info("Aucune réparation enregistrée.")
            return

        options = {f"{r['code_reparation']} - {r['type_appareil']} {r['modele']}": r["id"] for r in reparations}
        selection = st.selectbox("🛠️ Sélectionner une réparation", list(options.keys()))
        selected_id = options[selection]

        st.markdown("### ➕ Ajouter un achat")
        with st.form("ajout_achat"):
            libelle = st.text_input("Libellé de l'achat")
            montant = st.number_input("Montant (TND)", min_value=0.0, step=1.0)
            submitted = st.form_submit_button("🗓 Ajouter")
            if submitted:
                try:
                    cursor.execute("SELECT type_appareil, modele FROM reparations WHERE id = %s", (selected_id,))
                    rep_info = cursor.fetchone()
                    appareil_desc = f"{rep_info['type_appareil']} {rep_info['modele']}" if rep_info else "Appareil inconnu"
                    cursor.execute("INSERT INTO achats (reparation_id, libelle, montant) VALUES (%s, %s, %s)", (selected_id, libelle, montant))
                    conn.commit()
                    log_action("ajout", "achat", f"{libelle} ({montant:.2f} TND) : {appareil_desc}")
                    st.success("Achat ajouté.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur ajout : {e}")

        st.subheader("📋 Liste des achats ")
        cursor.execute("SELECT * FROM achats WHERE reparation_id = %s", (selected_id,))
        achats = cursor.fetchall()
        total = 0.0

        for achat in achats:
            with st.expander(f"🧾 {achat['libelle']} - {achat['montant']} TND"):
                new_label = st.text_input("Libellé", value=achat["libelle"], key=f"l_{achat['id']}")
                new_price = st.number_input("Montant", value=float(achat["montant"]), key=f"m_{achat['id']}", step=1.0)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗓 Modifier", key=f"modif_{achat['id']}"):
                        try:
                            cursor.execute("SELECT type_appareil, modele FROM reparations WHERE id = %s", (selected_id,))
                            rep_info = cursor.fetchone()
                            appareil_desc = f"{rep_info['type_appareil']} {rep_info['modele']}" if rep_info else "Appareil inconnu"
                            cursor.execute("UPDATE achats SET libelle = %s, montant = %s WHERE id = %s", (new_label, new_price, achat["id"]))
                            conn.commit()
                            log_action("modification", "achat", f"{new_label} ({new_price:.2f} TND) : {appareil_desc}")
                            st.success("Achat modifié")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur modif : {e}")
                with col2:
                    if st.button("🔚 Supprimer", key=f"del_{achat['id']}"):
                        st.session_state[f"confirm_supp_achat_{achat['id']}"] = True

                if st.session_state.get(f"confirm_supp_achat_{achat['id']}", False):
                    st.warning("❗ Confirmer la suppression de cet achat ?", icon="⚠️")
                    conf1, conf2 = st.columns(2)
                    with conf1:
                        if st.button("✅ Confirmer", key=f"conf_suppr_achat_{achat['id']}"):
                            try:
                                cursor.execute("SELECT type_appareil, modele FROM reparations WHERE id = %s", (selected_id,))
                                rep_info = cursor.fetchone()
                                appareil_desc = f"{rep_info['type_appareil']} {rep_info['modele']}" if rep_info else "Appareil inconnu"
                                cursor.execute("DELETE FROM achats WHERE id = %s", (achat["id"],))
                                conn.commit()
                                log_action("suppression", "achat", f"{achat['libelle']} supprimé : {appareil_desc}")
                                st.success("Supprimé")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erreur supp : {e}")
                    with conf2:
                        if st.button("❌ Annuler", key=f"cancel_suppr_achat_{achat['id']}"):
                            st.session_state[f"confirm_supp_achat_{achat['id']}"] = False

                total += new_price

        cursor.execute("SELECT montant_total FROM reparations WHERE id = %s", (selected_id,))
        montant_total = float(cursor.fetchone()["montant_total"])
        st.success(f"💰 Bénéfice estimé : `{montant_total - total:.2f} TND`")

    except Exception as e:
        st.error(f"Erreur achat : {e}")
    finally:
        cursor.close()
        conn.close()
