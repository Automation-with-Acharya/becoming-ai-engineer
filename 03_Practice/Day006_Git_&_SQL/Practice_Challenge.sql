-- ==================================================
-- LIBRARY MANAGEMENT DATABASE
-- ==================================================

-- ==================================================
-- DATABASE SETUP
-- ==================================================
CREATE DATABASE library_db;
USE library_db;


-- ==================================================
-- BOOKS TABLE: Store book information
-- ==================================================
CREATE TABLE books (
    book_id INT PRIMARY KEY,           -- Unique identifier for each book
    title VARCHAR(200),                -- Book title (max 200 characters)
    author VARCHAR(100),               -- Author name (max 100 characters)
    price DECIMAL(8, 2)                -- Book price (format: XXXXX.XX)
);


-- ==================================================
-- MEMBERS TABLE: Store library member information
-- ==================================================
CREATE TABLE members (
    member_id INT PRIMARY KEY,         -- Unique identifier for each member
    name VARCHAR(100),                 -- Member's full name (max 100 characters)
    city VARCHAR(100)                  -- Member's residential city (max 100 characters)
);


-- ==================================================
-- BORROW_HISTORY TABLE: Track book borrowing records
-- ==================================================
CREATE TABLE borrow_history (
    borrow_id INT PRIMARY KEY,         -- Unique identifier for each borrowing transaction
    member_id INT,                     -- Foreign key referencing the members table
    book_id INT,                       -- Foreign key referencing the books table
    borrow_date DATE,                  -- Date when the book was borrowed
    return_date DATE,                  -- Date when the book was returned (NULL if not returned yet)
    FOREIGN KEY (member_id) REFERENCES members(member_id),  -- Link to members table
    FOREIGN KEY (book_id) REFERENCES books(book_id)         -- Link to books table
);


-- ==================================================
-- INSERT DATA: Sample Books
-- ==================================================
INSERT INTO books VALUES
(1, 'To Kill a Mockingbird', 'Harper Lee', 450.00),        -- Book 1: Classic literature
(2, 'The Great Gatsby', 'F. Scott Fitzgerald', 380.50),    -- Book 2: American classic
(3, 'Python Programming', 'Guido van Rossum', 850.00),     -- Book 3: Technical book
(4, '1984', 'George Orwell', 520.00),                       -- Book 4: Dystopian novel
(5, 'Data Science Basics', 'Andrew Ng', 1200.00);          -- Book 5: Educational book

-- Verify books insertion
SELECT * FROM books;


-- ==================================================
-- INSERT DATA: Sample Members
-- ==================================================
INSERT INTO members VALUES
(1, 'Mayank Acharya', 'Gandhinagar'),      -- Member 1
(2, 'Rahul Kumar', 'Ahmedabad'),           -- Member 2
(3, 'Priya Sharma', 'Surat'),              -- Member 3
(4, 'Amit Patel', 'Vadodara'),             -- Member 4
(5, 'Neha Singh', 'Gandhinagar');          -- Member 5

-- Verify members insertion
SELECT * FROM members;


-- ==================================================
-- INSERT DATA: Borrow History Records
-- ==================================================
INSERT INTO borrow_history VALUES
(1, 1, 1, '2024-01-10', '2024-01-25'),        -- Mayank borrowed 'To Kill a Mockingbird'
(2, 2, 3, '2024-02-05', '2024-02-20'),        -- Rahul borrowed 'Python Programming'
(3, 3, 2, '2024-02-15', NULL),                -- Priya borrowed 'The Great Gatsby' (not returned yet)
(4, 1, 4, '2024-03-01', '2024-03-15'),        -- Mayank borrowed '1984'
(5, 4, 5, '2024-03-10', NULL),                -- Amit borrowed 'Data Science Basics' (not returned yet)
(6, 2, 1, '2024-03-20', '2024-04-05');        -- Rahul borrowed 'To Kill a Mockingbird'

-- Verify borrow history insertion
SELECT * FROM borrow_history;


-- ==================================================
-- SELECT QUERIES: Various retrieval operations
-- ==================================================

-- Query 1: View all books with their information
SELECT * FROM books;

-- Query 2: View all members in the library
SELECT * FROM members;

-- Query 3: Find all books currently on loan (not returned) - Using Subqueries
SELECT 
    borrow_id,
    (SELECT name FROM members WHERE members.member_id = borrow_history.member_id) AS member_name,
    (SELECT title FROM books WHERE books.book_id = borrow_history.book_id) AS book_title,
    borrow_date
FROM borrow_history
WHERE return_date IS NULL
ORDER BY borrow_date DESC;

-- Query 4: Find all books borrowed by a specific member (e.g., Mayank) - Using Subqueries
SELECT 
    (SELECT title FROM books WHERE books.book_id = borrow_history.book_id) AS title,
    (SELECT author FROM books WHERE books.book_id = borrow_history.book_id) AS author,
    borrow_date,
    return_date
FROM borrow_history
WHERE member_id = 1
ORDER BY borrow_date DESC;

-- Query 5: Count how many books each member has borrowed - Using Subqueries
SELECT 
    name,
    (SELECT COUNT(*) FROM borrow_history WHERE borrow_history.member_id = members.member_id) AS total_books_borrowed
FROM members
ORDER BY (SELECT COUNT(*) FROM borrow_history WHERE borrow_history.member_id = members.member_id) DESC;

-- Query 6: Find most expensive books
SELECT 
    title,
    author,
    price
FROM books
ORDER BY price DESC
LIMIT 3;

-- Query 7: Members from Gandhinagar
SELECT * FROM members WHERE city = 'Gandhinagar';


-- ==================================================
-- UPDATE QUERY: Update borrow return date
-- ==================================================
-- Scenario: Priya returned 'The Great Gatsby' on April 1st
UPDATE borrow_history
SET return_date = '2024-04-01'
WHERE borrow_id = 3;

-- Verify the update
SELECT * FROM borrow_history WHERE borrow_id = 3;


-- ==================================================
-- DELETE QUERY: Remove a borrow record
-- ==================================================
-- Scenario: Remove a cancelled borrowing transaction
DELETE FROM borrow_history
WHERE borrow_id = 6;

-- Verify the deletion
SELECT * FROM borrow_history;


-- ==================================================
-- FINAL VERIFICATION QUERIES
-- ==================================================
-- Show all current borrowing status - Using Subqueries
SELECT 
    borrow_id,
    (SELECT name FROM members WHERE members.member_id = borrow_history.member_id) AS member_name,
    (SELECT title FROM books WHERE books.book_id = borrow_history.book_id) AS book_title,
    borrow_date,
    return_date,
    CASE 
        WHEN return_date IS NULL THEN 'BORROWED'
        ELSE 'RETURNED'
    END AS status
FROM borrow_history
ORDER BY borrow_date DESC;
