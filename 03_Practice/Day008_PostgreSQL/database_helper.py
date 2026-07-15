import psycopg


class DatabaseHelper:
    def __init__(self, dbname="student_db", user="postgres", password="password@postgres", host="localhost", port="5432"):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None

    def connect(self):
        self.connection = psycopg.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        return self.connection

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def fetch_all_students(self):
        if self.connection is None:
            self.connect()

        with self.connection.cursor() as cur:
            cur.execute("SELECT id, name, age, city FROM students ORDER BY id")
            return cur.fetchall()

    def insert_student(self, student_id, name, age, city):
        if self.connection is None:
            self.connect()

        with self.connection.cursor() as cur:
            cur.execute(
                "INSERT INTO students (id, name, age, city) VALUES (%s, %s, %s, %s)",
                (student_id, name, age, city),
            )
        self.connection.commit()

    def update_student_city(self, student_id, new_city):
        if self.connection is None:
            self.connect()

        with self.connection.cursor() as cur:
            cur.execute(
                "UPDATE students SET city = %s WHERE id = %s",
                (new_city, student_id),
            )
        self.connection.commit()

    def delete_student(self, student_id):
        if self.connection is None:
            self.connect()

        with self.connection.cursor() as cur:
            cur.execute(
                "DELETE FROM students WHERE id = %s",
                (student_id,),
            )
        self.connection.commit()

    def run_query(self, query, params=None):
        if self.connection is None:
            self.connect()

        with self.connection.cursor() as cur:
            if params is None:
                cur.execute(query)
            else:
                cur.execute(query, params)
            return cur.fetchall()
