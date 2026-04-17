import psycopg2

import sys

def test_db():
    try:
        connection = psycopg2.connect(
            user="postgres",
            password='password123',
            host="localhost",
            port="5433",
            database="postgres"
        )
        print("Have connect to docker database")
        connection.close()
    except Exception as error:
        print(f"Connection failed:{error}")

if __name__ == "__main__":
    test_db()