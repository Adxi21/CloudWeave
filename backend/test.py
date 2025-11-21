from fastapi import FastAPI
import psycopg2

app = FastAPI()

DB_HOST = "13.201.93.107"   # EC2 Public IP
DB_PORT = 5432
DB_NAME = "eventdb"
DB_USER = "adiuser"
DB_PASS = "rajarama"


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

@app.get("/")
def root():
    return {"message": "FastAPI + Postgres connected!"}

@app.post("/setup")
def setup_db():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                location VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        sample_events = [
            ("Spiritual Gathering", "Rajaram Gurukul"),
            ("Annual Utsav", "Main Hall"),
            ("Monthly Satsang", "Prayer Room")
        ]

        cur.executemany(
            "INSERT INTO events (name, location) VALUES (%s, %s)",
            sample_events
        )

        conn.commit()
        cur.close()
        conn.close()

        return {"status": "success", "msg": "DB setup complete on EC2!"}

    except Exception as e:
        return {"status": "error", "details": str(e)}

@app.get("/events")
def get_all_events():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, location, created_at FROM events")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return {
            "status": "success",
            "events": [
                {
                    "id": r[0],
                    "name": r[1],
                    "location": r[2],
                    "created_at": str(r[3])
                }
                for r in rows
            ]
        }

    except Exception as e:
        return {"status": "error", "details": str(e)}


@app.get("/db-test")
def db_test():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        conn.close()
        return {"connected": True, "version": version}
    except Exception as e:
        return {"connected": False, "error": str(e)}
