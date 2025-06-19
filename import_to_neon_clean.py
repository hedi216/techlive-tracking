
import psycopg2

# Connexion à Neon
conn = psycopg2.connect(
    dbname="neondb",
    user="neondb_owner",
    password="npg_dNVqt4s3SAzC",
    host="ep-delicate-meadow-a94wdnrt-pooler.gwc.azure.neon.tech",
    port="5432",
    sslmode="require"
)

cursor = conn.cursor()

# Lire le fichier SQL PostgreSQL propre
with open(r"C:\Users\guessMeWho\Desktop\techliveApp\neon_full_schema_clean.sql", "r", encoding="utf-8") as f:
    sql_commands = f.read()

# Exécuter commande par commande
commands = sql_commands.split(";")
for command in commands:
    command = command.strip()
    if command:
        try:
            cursor.execute(command)
        except Exception as e:
            print(f"❌ Erreur :\n{command}\n→ {e}\n")

conn.commit()
cursor.close()
conn.close()
print("✅ Import terminé avec succès.")
