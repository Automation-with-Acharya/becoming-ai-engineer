Today's DSA problem is intentionally small and directly reinforces stack-based reasoning.

## Problem — Valid Parentheses

Given a string containing:

```text
()
{}
[]
```

determine whether the brackets are correctly balanced and properly nested.

Examples:

```text
"()"       → true
"()[]{}"   → true
"(]"       → false
"([{}])"   → true
"([)]"     → false
```

## Why a Stack?

When you see an opening bracket:

```text
(
[
{
```

you do not yet know which closing bracket will arrive.

The most recent unmatched opening bracket must be matched first.

That is exactly Last-In, First-Out behavior.

```text
Opening brackets
      ↓
    STACK
      ↑
Latest opening bracket
```

## JavaScript

```javascript
function isValidParentheses(s) {
  const stack = [];

  const pairs = {
    ")": "(",
    "]": "[",
    "}": "{",
  };

  for (const char of s) {
    if (char === "(" || char === "[" || char === "{") {
      stack.push(char);
      continue;
    }

    if (stack.pop() !== pairs[char]) {
      return false;
    }
  }

  return stack.length === 0;
}
```

## Complexity

```text
Time  → O(n)
Space → O(n)
```

The stack stores unmatched opening brackets.

## Interview Pattern

Recognize this family of problems:

```text
Nested structure
      ↓
Most recent unmatched item
      ↓
Stack
```

This same reasoning appears in:

- parentheses validation,
- undo systems,
- expression parsing,
- syntax checking,
- tree traversal patterns,
- backtracking workflows.

The goal is not to memorize one LeetCode solution.

The goal is to recognize:

> **LIFO requirement → stack.**

---
