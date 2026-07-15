import psycopg

# Connect to the PostgreSQL database named student_db
connection = psycopg.connect(
    dbname="student_db",      # Database name
    user="postgres",          # PostgreSQL username
    password="password@postgres",  # Password for the database user
    host="localhost",         # Database host
    port="5432"               # Default PostgreSQL port
)

print("✅ Connected Successfully!")

# Close the database connection properly
connection.close()