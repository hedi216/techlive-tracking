import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # À adapter selon ton config MySQL
        password="",  # Ton mot de passe MySQL ("" par défaut parfois)
        database="projet"
    )
