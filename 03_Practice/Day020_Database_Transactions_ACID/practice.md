# Day 020 Practice: Database Transactions and ACID

## Exercise 1: Create a Simple Transaction

Create a simple transaction using the following flow:

```sql
BEGIN;
INSERT ...;
COMMIT;
```

## Exercise 2: Force an Exception

Force an exception during a transaction.

Observe how the transaction is handled:

```sql
ROLLBACK;
```

## Exercise 3: Insert Two Related Records

Insert two related records inside a single transaction.

If the second insert fails, verify that the first insert is also rolled back.

## Exercise 4: Experiment With Autocommit

Experiment with:

```python
connection.autocommit
```

Understand the difference between autocommit mode and explicit transaction handling.

## Exercise 5: Update the Student Management Project

Update the Student Management project so that transactions are handled correctly whenever a write operation occurs:

- Create student
- Update student
- Delete student
