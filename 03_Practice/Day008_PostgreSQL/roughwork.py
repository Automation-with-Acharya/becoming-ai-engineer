import psycopg

conn = psycopg.connect(
    dbname="student_db",
    user="postgres",
    password="password@postgres",
    host="localhost",
    port="5432",
)

with conn.cursor() as cur:
    cur.execute("SELECT id, name, age, city FROM students ORDER BY id")
    rows = cur.fetchall()

for row in rows:
    print(row)

conn.close()