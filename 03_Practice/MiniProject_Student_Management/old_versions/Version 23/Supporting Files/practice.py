"""Rename duplicate student emails to unique plus-addressed email values.

The script loads existing non-null emails, finds duplicate student records,
generates an unused replacement for each duplicate, updates the database, and
commits the changes before closing the cursor and connection.
"""

import psycopg

conn = psycopg.connect("dbname=student_db user=postgres password=password@postgres")
cur = conn.cursor()

# 1. Cache all currently used emails in a set for O(1) collision checks
cur.execute("SELECT email FROM students WHERE email IS NOT NULL;")
existing_emails = {row[0] for row in cur.fetchall()}

# 2. Fetch duplicate rows where row_num > 1 (the ones that need renaming)
query = """
WITH ranked AS (
    SELECT id, email,
           ROW_NUMBER() OVER (PARTITION BY email ORDER BY id) AS rn,
           COUNT(*) OVER (PARTITION BY email) AS cnt
    FROM students
    WHERE email IS NOT NULL
)
SELECT id, email, rn FROM ranked WHERE cnt > 1 AND rn > 1;
"""
cur.execute(query)
duplicates_to_rename = cur.fetchall()

# 3. Generate unique replacements and update
for student_id, email, rn in duplicates_to_rename:
    username, domain = email.split("@", 1)
    suffix_counter = rn

    # Find a candidate that doesn't exist anywhere in the table
    while True:
        candidate_email = f"{username}+{suffix_counter}@{domain}"
        if candidate_email not in existing_emails:
            break
        suffix_counter += 1

    # Update database and register the new email in the set
    cur.execute(
        "UPDATE students SET email = %s WHERE id = %s;",
        (candidate_email, student_id),
    )
    existing_emails.add(candidate_email)

conn.commit()
cur.close()
conn.close()