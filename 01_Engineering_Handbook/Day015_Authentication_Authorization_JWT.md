# Day 015 — Authentication, Authorization & JWT

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 24 July 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand Authentication and Authorization.
- Understand Stateless Authentication.
- Understand JWT (JSON Web Token).
- Learn how JWTs are created and verified.
- Understand password hashing with bcrypt.
- Understand why JWT and password hashing are different.
- Understand how protected endpoints work.
- Compare FastAPI authentication with ASP.NET Core.

---

# Big Picture

Yesterday we learned:

```text
Client

↓

Validation

↓

Router

↓

Service

↓

Repository
```

Today we add one more important layer:

```text
Client

↓

Authentication

↓

Authorization

↓

Validation

↓

Router

↓

Service

↓

Repository
```

Only authenticated users should reach the application.

---

# 1. Authentication vs Authorization

These two terms are often confused.

## Authentication

Authentication answers:

> **Who are you?**

Examples:

- Username + Password
- Google Login
- Microsoft Login
- Face ID
- Fingerprint

Authentication verifies identity.

---

## Authorization

Authorization answers:

> **What are you allowed to do?**

Examples:

User:

```text
Mayank
```

Role:

```text
Admin
```

Allowed:

- Add Student
- Delete Student
- Update Student

---

User:

```text
Rahul
```

Role:

```text
Viewer
```

Allowed:

- View Students

Not allowed:

- Delete Student

---

# Authentication & Authorization Flow

```text
User

↓

Login

↓

Authentication

↓

JWT Generated

↓

Protected API

↓

Authorization

↓

Business Logic
```

Authentication always happens before Authorization.

---

# 2. What is JWT?

JWT stands for:

**JSON Web Token**

It is a compact, digitally signed token used to prove that a user has already authenticated.

Instead of sending a username and password with every request, the client sends a JWT.

---

# JWT Structure

A JWT has three parts:

```text
Header

.

Payload

.

Signature
```

Example:

```text
xxxxx.yyyyy.zzzzz
```

---

# JWT Diagram

```text
Header

↓

Algorithm

↓

Payload

↓

Claims

↓

Signature

↓

Integrity
```

---

# 3. Header

The header describes the token.

Example:

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

Common fields:

- Algorithm
- Token Type

---

# 4. Payload

The payload contains **claims**.

Claims describe the user.

Example:

```json
{
  "sub": "mayank",
  "role": "admin",
  "exp": 1753500000
}
```

Common claims:

- sub (Subject)
- role
- exp (Expiration)
- iss (Issuer)
- aud (Audience)

---

# 5. Signature

The signature protects the JWT from modification.

It is generated using:

```text
Base64(Header)

+

Base64(Payload)

+

SECRET_KEY
```

↓

```text
HMAC SHA-256
```

↓

Signature

---

# JWT Creation

```text
Header

↓

Base64 Encode

↓

Payload

↓

Base64 Encode

↓

Header.Payload

↓

SECRET_KEY

↓

Signature

↓

JWT
```

---

# 6. Login Flow

```text
Username

+

Password

↓

Authentication Server

↓

Password Verification

↓

JWT Generated

↓

Client Stores JWT
```

The password is used **only during login**.

---

# 7. Password Hashing (bcrypt)

Password hashing and JWT are two completely different concepts.

bcrypt is used only to verify passwords.

Example:

Registration:

```text
Password

↓

bcrypt.hash()

↓

Database
```

Login:

```text
Password

↓

bcrypt.verify()

↓

True / False
```

After successful verification:

bcrypt's job is finished.

---

# bcrypt Uses Random Salt

Each time a password is hashed:

```text
Password

↓

Random Salt

↓

bcrypt

↓

Hash
```

Even if the password is identical, the hash changes because a new random salt is generated.

Example:

```text
Password123

↓

Hash A
```

Later:

```text
Password123

↓

Hash B
```

Different hashes.

Same password.

---

# How Verification Works

bcrypt stores:

- Algorithm
- Cost
- Salt
- Hash

inside the final hash string.

During verification:

```text
Stored Hash

↓

Extract Salt

↓

bcrypt(password, extracted salt)

↓

Compare Hashes
```

The salt is **not ignored**.

It is extracted and reused.

---

# 8. JWT vs Password Hashing

| Password Hashing       | JWT                             |
| ---------------------- | ------------------------------- |
| Verifies password      | Identifies authenticated user   |
| Uses bcrypt            | Uses HMAC or RSA/ECDSA          |
| Random salt            | Secret key or private key       |
| Used only during login | Used on every protected request |
| Stored in database     | Sent by the client              |

These technologies solve different problems.

---

# 9. JWT Verification

When a client sends:

```text
Authorization:

Bearer <JWT>
```

The API server:

- Extracts Header
- Extracts Payload
- Extracts Signature

Then computes:

```text
Header.Payload

+

SECRET_KEY

↓

New Signature
```

Compare:

```text
JWT Signature

==

Generated Signature
```

If equal:

Request is trusted.

---

# JWT Verification Flow

```text
Client

↓

JWT

↓

API Server

↓

Extract Header

↓

Extract Payload

↓

Generate Signature

↓

Compare

↓

Valid?

↓

YES

↓

Protected Endpoint
```

---

# 10. Where Does the SECRET_KEY Come From?

The API server already knows the secret.

Example:

Authentication Server:

```text
SECRET_KEY

↓

SuperSecretKey123
```

API Server:

```text
SECRET_KEY

↓

SuperSecretKey123
```

Usually stored in:

- Environment Variables
- Azure Key Vault
- AWS Secrets Manager
- Kubernetes Secrets

It is **never sent inside the JWT**.

---

# 11. HS256 vs RS256

## HS256

One shared secret.

```text
Authentication Server

↓

SECRET_KEY

↓

Sign JWT

──────────────

API Server

↓

Same SECRET_KEY

↓

Verify JWT
```

Simple.

Fast.

Common for internal applications.

---

## RS256

Uses asymmetric cryptography.

Authentication Server:

```text
Private Key
```

↓

Signs JWT

API Server:

```text
Public Key
```

↓

Verifies JWT

API servers never know the private key.

This is common in large enterprise systems.

---

# 12. Protected Endpoints

FastAPI:

```python
oauth2_scheme = OAuth2PasswordBearer(...)
```

Route:

```python
@app.get("/profile")
def profile(token: str = Depends(oauth2_scheme)):
    ...
```

Only authenticated users can access it.

---

# 13. Complete Authentication Architecture

```text
Client

↓

Username + Password

↓

Authentication Server

↓

bcrypt.verify()

↓

Password Correct?

↓

YES

↓

Generate JWT

↓

Return JWT

↓

Client Stores JWT

↓

Protected API Request

↓

JWT Verification

↓

Authorization

↓

Business Logic

↓

Database
```

---

# 14. Enterprise Comparison

## ASP.NET Core

Authentication:

```csharp
builder.Services.AddAuthentication();
```

Authorization:

```csharp
[Authorize]
```

---

## FastAPI

Authentication:

```python
OAuth2PasswordBearer()
```

Authorization:

```python
Depends(oauth2_scheme)
```

The concepts are identical.

---

# Common Beginner Mistakes

❌ Storing passwords in plain text.

❌ Including passwords inside JWTs.

❌ Using the same JWT forever (no expiration).

❌ Confusing Authentication with Authorization.

❌ Hardcoding SECRET_KEY into source code.

---

# Production Best Practices

✅ Hash passwords using bcrypt.

✅ Store only password hashes.

✅ Store SECRET_KEY securely.

✅ Use JWT expiration.

✅ Keep JWT payload small.

✅ Never place sensitive data inside JWT payloads.

---

# Interview Questions

### Q1. Difference between Authentication and Authorization?

Authentication verifies identity.

Authorization determines permissions.

---

### Q2. What is JWT?

A digitally signed token used to identify authenticated users without sending credentials on every request.

---

### Q3. Why use bcrypt?

To securely hash passwords before storing them.

---

### Q4. Does JWT use bcrypt?

No.

bcrypt verifies passwords.

JWT uses HMAC (HS256) or public/private key cryptography (RS256) to create and verify signatures.

---

### Q5. Why do bcrypt hashes change every time?

bcrypt generates a new random salt for every hash.

Different salts produce different hashes.

---

### Q6. How can bcrypt verify passwords if the salt is random?

The generated hash stores:

- algorithm
- cost
- salt
- hash

During verification, bcrypt extracts the stored salt and recomputes the hash using the entered password.

---

### Q7. How does the API server verify a JWT?

The API server already has the same SECRET_KEY (HS256) or the public key (RS256). It recomputes the signature and compares it with the signature inside the JWT.

---

# Cheat Sheet

```text
Authentication

↓

Who are you?
```

---

```text
Authorization

↓

What are you allowed to do?
```

---

```text
Password

↓

bcrypt

↓

Database
```

---

```text
Password

↓

bcrypt.verify()

↓

JWT Generated
```

---

```text
JWT

↓

Header

Payload

Signature
```

---

```text
JWT

↓

API Server

↓

Verify Signature

↓

Protected API
```

---

# 🏗 Why does this exist?

## What problem does it solve?

Users should not send their username and password with every API request.

Authentication proves identity once.

JWT allows the client to securely prove that identity on future requests.

Password hashing ensures passwords are never stored in plain text.

---

## Who depends on it?

```text
Client

↓

Authentication

↓

JWT

↓

Protected Router

↓

Service
```

Every protected endpoint depends on successful authentication before business logic is executed.

---

## Who should NOT depend on it?

The Repository Layer.

Repositories should never know whether the request came from an authenticated user.

Authentication belongs to the API and security layers.

---

## ASP.NET Core Equivalent

```csharp
builder.Services.AddAuthentication();

[Authorize]
```

---

## FastAPI Equivalent

```python
oauth2_scheme = OAuth2PasswordBearer(...)

token: str = Depends(oauth2_scheme)
```

---

# Key Takeaways

- Authentication verifies identity; Authorization determines permissions.
- bcrypt and JWT solve different security problems.
- bcrypt hashes passwords using a random salt and stores the salt within the hash.
- JWT contains Header, Payload, and Signature.
- JWT signatures are verified using a shared secret (HS256) or a public key (RS256).
- Passwords should never be stored in plain text or embedded inside JWTs.
- Authentication occurs once during login, while JWT verification happens on every protected request.

---

# Revision Checklist

- [ ] Can explain Authentication vs Authorization.
- [ ] Understand JWT structure.
- [ ] Know the purpose of Header, Payload, and Signature.
- [ ] Understand how bcrypt works.
- [ ] Know why bcrypt and JWT are separate concepts.
- [ ] Can explain HS256 vs RS256.
- [ ] Can describe the complete authentication lifecycle.

---

# Tomorrow's Preview

- FastAPI Middleware
- Request/Response lifecycle
- Custom Middleware
- CORS (Cross-Origin Resource Sharing)
- Request logging and timing
- Understanding how every HTTP request flows through middleware before reaching your routers
