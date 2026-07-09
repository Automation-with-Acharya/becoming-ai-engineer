# Git Commands

## 1. Check Repository Status

```bash
git status
```

Shows:

- Modified files
- New files
- Deleted files
- Staged files

---

## 2. Stage All Changes

```bash
git add .
```

Stages every modified file.

---

## 3. Stage a Single File

```bash
git add filename.py
```

Example:

```bash
git add day05.sql
```

---

## 4. Commit Changes

```bash
git commit -m "Day 005: Learn Git and SQL fundamentals"
```

Creates a snapshot of your staged changes.

---

## 5. View Commit History

```bash
git log
```

Useful options:

```bash
git log --oneline
```

```bash
git log --graph
```

---

## 6. View Differences

```bash
git diff
```

Shows changes before staging.

To compare staged changes:

```bash
git diff --staged
```

---

## 7. Restore a File

Discard local changes.

```bash
git restore filename.py
```

Example:

```bash
git restore day05.sql
```

---

## 8. Check Branches

```bash
git branch
```

Shows all local branches.

---

## 9. Push Changes

```bash
git push
```

Uploads commits to GitHub.

---

## 10. Pull Latest Changes

```bash
git pull
```

Downloads and merges the latest changes from GitHub.

---

# Git Workflow

```text
Modify File
      │
git status
      │
git add .
      │
git commit
      │
git push
```

---

# Git Cheat Sheet

| Command            | Purpose                 |
| ------------------ | ----------------------- |
| `git status`       | Repository status       |
| `git add .`        | Stage all files         |
| `git add file.py`  | Stage one file          |
| `git commit -m ""` | Save snapshot           |
| `git log`          | View history            |
| `git diff`         | Compare changes         |
| `git restore`      | Undo local changes      |
| `git branch`       | Show branches           |
| `git push`         | Upload commits          |
| `git pull`         | Download latest changes |
