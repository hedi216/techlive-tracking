from flask import Flask, request, jsonify, render_template
#import mysql.connector
import os
import psycopg2
import psycopg2.extras  
app = Flask(__name__, template_folder='templates')



def get_connection():
    return psycopg2.connect(
        dbname="neondb",
        user="neondb_owner",
        password="npg_dNVqt4s3SAzC",
        host="ep-delicate-meadow-a94wdnrt-pooler.gwc.azure.neon.tech",
        port="5432",
        sslmode="require"
    )


@app.route('/')
def index():
    return render_template('tracking.html')

@app.route("/track")
def track():
    code = request.args.get("code", "").strip()
    tel = request.args.get("tel", "").strip()

    if not tel or not tel.isdigit() or len(tel) != 8:
        return jsonify({"error": "Numéro de téléphone invalide."})

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if code:
        cursor.execute("SELECT * FROM reparations WHERE code_reparation = %s AND numero_tel = %s", (code, tel))
        row = cursor.fetchone()
        if row:
            return jsonify({"data": [row]})
        else:
            return jsonify({"error": "Aucune réparation trouvée avec ce code et ce numéro."})
    else:
        cursor.execute("SELECT * FROM reparations WHERE numero_tel = %s ORDER BY date_enregistrement DESC", (tel,))
        rows = cursor.fetchall()
        if rows:
            return jsonify({"data": rows})
        else:
            return jsonify({"error": "Aucune réparation trouvée pour ce numéro."})

    cursor.close()
    conn.close()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
