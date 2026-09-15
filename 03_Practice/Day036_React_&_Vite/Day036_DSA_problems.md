# Day 36: DSA Problems

Solve these two small problems in JavaScript and Python today. JavaScript reinforces the frontend language used in this week's React exercises, while Python matches your usual DSA practice language.

## Problem 1: Two Sum

Given an array of numbers and a target value, return the indices of the two numbers whose sum equals the target.

### Example

**Input:**

```javascript
const numbers = [2, 7, 11, 15];
const target = 9;
```

**Output:**

```javascript
[0, 1];
```

### Approach

For each number:

1. Calculate the complement: `target - number`.
2. Check whether the complement has already been seen.
3. If it has, return the two indices.
4. Otherwise, store the current number and its index.

### Solution

```javascript
function twoSum(numbers, target) {
  const seenNumbers = new Map();

  for (let index = 0; index < numbers.length; index += 1) {
    const number = numbers[index];
    const complement = target - number;

    if (seenNumbers.has(complement)) {
      return [seenNumbers.get(complement), index];
    }

    seenNumbers.set(number, index);
  }

  return [];
}

console.log(twoSum([2, 7, 11, 15], 9));
// [0, 1]
```

### Complexity

- **Time:** `O(n)`
- **Space:** `O(n)`

### Python Solution

```python
def two_sum(numbers, target):
  seen_numbers = {}

  for index, number in enumerate(numbers):
    complement = target - number

    if complement in seen_numbers:
      return [seen_numbers[complement], index]

    seen_numbers[number] = index

  return []


print(two_sum([2, 7, 11, 15], 9))
# [0, 1]
```

## Problem 2: First Duplicate

Given an array of numbers, return the first value encountered more than once while scanning from left to right.

### Example

**Input:**

```javascript
const numbers = [4, 1, 3, 2, 3, 5];
```

**Output:**

```javascript
3;
```

### Approach

Use a `Set` to store values already encountered. When a value is already in the set, return it immediately.

### Solution

```javascript
function firstDuplicate(numbers) {
  const seenNumbers = new Set();

  for (const number of numbers) {
    if (seenNumbers.has(number)) {
      return number;
    }

    seenNumbers.add(number);
  }

  return null;
}

console.log(firstDuplicate([4, 1, 3, 2, 3, 5]));
// 3
```

### Complexity

- **Time:** `O(n)`
- **Space:** `O(n)`

### Python Solution

```python
def first_duplicate(numbers):
  seen_numbers = set()

  for number in numbers:
    if number in seen_numbers:
      return number

    seen_numbers.add(number)

  return None


print(first_duplicate([4, 1, 3, 2, 3, 5]))
# 3
```
