
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="subscription_portfolio"
    )

if __name__ == "__main__":
    if not os.getenv("DB_USER") or os.getenv("DB_PASSWORD") is None:
        print("Missing DB_USER or DB_PASSWORD in .env")
    else:
        try:
            connection = get_connection()
            print("Connected to MySQL successfully!")
            connection.close()
        except mysql.connector.Error as error:
            print("Connection failed:", error)
