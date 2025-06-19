#import mysql.connector
import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="neondb",
        user="neondb_owner",
        password="npg_dNVqt4s3SAzC",
        host="ep-delicate-meadow-a94wdnrt-pooler.gwc.azure.neon.tech",
        port="5432",
        sslmode="require"
    )


#def get_connection():
#    return mysql.connector.connect(
#       host="localhost",
#       user="root",
#       password="",
#       database="projet"
#    )
