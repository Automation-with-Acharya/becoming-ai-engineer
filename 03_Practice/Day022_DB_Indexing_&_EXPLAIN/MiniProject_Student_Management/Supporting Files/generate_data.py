import random
import sys

# ── Sample data pools ───────────────────────────────────────────────────────
first_names = [
    "Mayank", "Rahul", "Priya", "Aarav", "Ananya", "Vikram", "Sneha", "Rohan",
    "Kavya", "Arjun", "Nisha", "Karan", "Pooja", "Amit", "Riya", "Siddharth",
    "Deepika", "Nikhil", "Shreya", "Varun", "Meera", "Aditya", "Tanvi", "Harsh",
    "Divya", "Rajesh", "Sunita", "Mohit", "Ankita", "Vivek", "Swati", "Gaurav",
    "Neha", "Pranav", "Sakshi", "Akash", "Pallavi", "Sumit", "Ritika", "Kunal",
    "Manisha", "Ashish", "Preeti", "Dhruv", "Simran", "Yash", "Shweta", "Tarun",
    "Isha", "Abhinav", "Rekha", "Nitin", "Jyoti", "Saurabh", "Archana", "Rajan",
    "Vandana", "Praveen", "Anjali", "Kapil", "Bhavna", "Geeta", "Ramesh",
    "Sonal", "Hemant", "Alka", "Manoj", "Usha", "Vinay", "Lalita", "Dinesh",
    "Saroj", "Pankaj", "Mona", "Sandeep", "Radha", "Ajay", "Savita", "Vijay",
    "Lata", "Dilip", "Kamla", "Naresh", "Sudha", "Girish", "Chanda", "Sunil",
    "Veena", "Arun", "Shanti", "Rakesh", "Pushpa", "Mohan", "Asha", "Rajendra",
    "Madhuri", "Nandini", "Prakash", "Sarita", "Umesh", "Padma", "Devendra",
    "Harish", "Bharti", "Suresh", "Leela", "Gopal", "Seema", "Brijesh", "Kamini",
]

last_names = [
    "Sharma", "Patel", "Singh", "Kumar", "Gupta", "Mehta", "Shah", "Joshi",
    "Verma", "Mishra", "Agarwal", "Tiwari", "Rao", "Nair", "Iyer", "Reddy",
    "Bose", "Das", "Ghosh", "Mukherjee", "Chatterjee", "Banerjee", "Sen", "Roy",
    "Malhotra", "Khanna", "Chopra", "Kapoor", "Bhatia", "Arora", "Sethi", "Grover",
    "Narang", "Sehgal", "Walia", "Chawla", "Anand", "Bajaj", "Garg", "Mittal",
    "Tandon", "Saxena", "Srivastava", "Pandey", "Shukla", "Tripathi", "Dubey", "Yadav",
    "Chaudhary", "Maurya", "Chauhan", "Thakur", "Rathore", "Rajput", "Shekhawat", "Bhatt",
    "Desai", "Trivedi", "Parmar", "Makwana", "Solanki", "Vasava", "Prajapati",
    "Jain", "Soni", "Pillai", "Menon", "Varma", "Krishnan", "Subramaniam", "Venkatesh",
    "Hegde", "Kulkarni", "Deshpande", "Patil", "Kadam", "More", "Jadhav", "Shinde",
]

cities = [
    "Gandhinagar", "Ahmedabad", "Surat", "Vadodara", "Rajkot", "Mumbai", "Pune",
    "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Kolkata", "Jaipur", "Lucknow",
    "Kanpur", "Nagpur", "Indore", "Bhopal", "Patna", "Ludhiana", "Agra", "Nashik",
    "Meerut", "Varanasi", "Amritsar", "Ranchi", "Coimbatore", "Vijayawada", "Madurai",
    "Ghaziabad", "Faridabad", "Noida", "Gurgaon", "Thane", "Visakhapatnam", "Kochi",
    "Mysuru", "Hubli", "Mangaluru", "Thiruvananthapuram", "Bhubaneswar", "Cuttack",
    "Guwahati", "Shillong", "Jammu", "Dehradun", "Shimla", "Chandigarh", "Jodhpur",
    "Udaipur", "Kota", "Ajmer", "Bikaner", "Alwar", "Bhilai", "Raipur", "Jabalpur",
    "Gwalior", "Ujjain", "Sagar", "Satna", "Bilaspur", "Durgapur", "Asansol",
    "Siliguri", "Howrah", "Dhanbad", "Jamshedpur", "Bokaro", "Muzaffarpur", "Gaya",
]

domains = [
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
    "rediffmail.com", "live.com", "icloud.com", "protonmail.com",
]

# ── Config ───────────────────────────────────────────────────────────────────
TOTAL_RECORDS = 2_500_000
BATCH_SIZE    = 10_000          # rows per INSERT statement
OUTPUT_PATH   = r"E:\Career-Transformation\03_Practice\MiniProject_Student_Management\data_entry_query.md"

random.seed(42)

# ── Helpers ──────────────────────────────────────────────────────────────────
def make_row(i):
    first  = random.choice(first_names)
    last   = random.choice(last_names)
    name   = f"{first} {last}".replace("'", "''")
    age    = random.randint(18, 35)
    city   = random.choice(cities).replace("'", "''")
    suffix = random.randint(1, 999999)
    domain = random.choice(domains)
    email  = f"{first.lower()}.{last.lower()}{suffix}@{domain}"
    return f"    ({i}, '{name}', {age}, '{city}', '{email}')"

# ── Write ────────────────────────────────────────────────────────────────────
print(f"Generating {TOTAL_RECORDS:,} records in batches of {BATCH_SIZE:,} …")

with open(OUTPUT_PATH, "w", encoding="utf-8", buffering=1 << 20) as f:
    # Markdown header
    f.write("# Student Management System — Bulk Data Insert\n\n")
    f.write(f"Generated **{TOTAL_RECORDS:,}** student records for the `students` table.\n\n")
    f.write("## SQL Insert Query\n\n")
    f.write("```sql\n")
    f.write("-- ================================================================\n")
    f.write(f"-- Student Management System - Bulk Data Insert ({TOTAL_RECORDS:,} records)\n")
    f.write("-- Table  : students\n")
    f.write(f"-- Batches: {TOTAL_RECORDS // BATCH_SIZE} × {BATCH_SIZE:,} rows each\n")
    f.write("-- ================================================================\n\n")

    batch_num = 0
    i = 1
    while i <= TOTAL_RECORDS:
        batch_end = min(i + BATCH_SIZE - 1, TOTAL_RECORDS)
        batch_num += 1

        f.write(f"-- Batch {batch_num} (rows {i:,} – {batch_end:,})\n")
        f.write("INSERT INTO students (id, name, age, city, email) VALUES\n")

        rows = [make_row(j) for j in range(i, batch_end + 1)]
        f.write(",\n".join(rows))
        f.write(";\n\n")

        i = batch_end + 1

        # Progress every 10 batches
        if batch_num % 10 == 0:
            pct = batch_end / TOTAL_RECORDS * 100
            print(f"  [{pct:5.1f}%]  batch {batch_num:>4}  rows up to {batch_end:>10,}", flush=True)

    f.write("```\n")

print(f"\nDone! Written to:\n  {OUTPUT_PATH}")
