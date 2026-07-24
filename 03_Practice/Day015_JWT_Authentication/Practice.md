# Day 015: JWT Authentication Practice

## Exercise 1: Password Hashing

Use `passlib` to:

- Hash a password.
- Verify a password.

## Exercise 2: JWT Generation

Generate a JWT containing:

- `username`
- `role`
- `expiration`

## Exercise 3: JWT Decoding

Decode the JWT and inspect:

- Header
- Payload
- Signature

## Exercise 4: Protected Endpoint

Create a protected endpoint:

```http
GET /profile
```

Return data only if a valid JWT is provided.

## Exercise 5: Swagger Testing

Test in Swagger with:

- No token
- Invalid token
- Expired token
- Valid token

Observe the different responses.
