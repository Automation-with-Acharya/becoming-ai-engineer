# Day 037: DSA Problems for React and FastAPI API Integration

These exercises practice two common API-data transformation patterns:

```text
API response -> array -> group or transform -> UI model
```

Both solutions process the input in one pass.

## Problem 1: Frequency Counter

Given the following list:

```javascript
["python", "react", "python", "sql", "react", "python"];
```

Produce this frequency table:

```javascript
{
	python: 3,
	react: 2,
	sql: 1
}
```

### Approach

```text
value -> Map or dictionary -> increment count
```

### JavaScript solution

```javascript
function countFrequencies(values) {
  const frequencies = new Map();

  for (const value of values) {
    const currentCount = frequencies.get(value) ?? 0;
    frequencies.set(value, currentCount + 1);
  }

  return frequencies;
}

const technologies = ["python", "react", "python", "sql", "react", "python"];

const frequencyMap = countFrequencies(technologies);
console.log(Object.fromEntries(frequencyMap));
// { python: 3, react: 2, sql: 1 }
```

`Map` is used because it is designed for key-value storage and supports keys of any type. `Object.fromEntries` converts the result into a plain object for display or JSON-style use.

### Python solution

```python
def count_frequencies(values):
		frequencies = {}

		for value in values:
				frequencies[value] = frequencies.get(value, 0) + 1

		return frequencies


technologies = [
		"python",
		"react",
		"python",
		"sql",
		"react",
		"python",
]

print(count_frequencies(technologies))
# {'python': 3, 'react': 2, 'sql': 1}
```

### Complexity

- **Time:** `O(n)`, because each value is processed once.
- **Space:** `O(k)`, where `k` is the number of distinct values. In the worst case, this is `O(n)`.

## Problem 2: Group Students by City

This problem models a common transformation of student data returned by an API.

### Input

```javascript
[
  { name: "A", city: "Ahmedabad" },
  { name: "B", city: "Mumbai" },
  { name: "C", city: "Ahmedabad" },
  { name: "D", city: "Pune" },
];
```

### Expected output

```javascript
{
	Ahmedabad: ["A", "C"],
	Mumbai: ["B"],
	Pune: ["D"],
}
```

### Approach

```text
student -> city -> bucket -> append student name
```

### JavaScript solution

```javascript
function groupStudentsByCity(students) {
  const studentsByCity = new Map();

  for (const student of students) {
    if (!studentsByCity.has(student.city)) {
      studentsByCity.set(student.city, []);
    }

    studentsByCity.get(student.city).push(student.name);
  }

  return studentsByCity;
}

const students = [
  { name: "A", city: "Ahmedabad" },
  { name: "B", city: "Mumbai" },
  { name: "C", city: "Ahmedabad" },
  { name: "D", city: "Pune" },
];

const studentsByCity = groupStudentsByCity(students);
console.log(Object.fromEntries(studentsByCity));
// {
//   Ahmedabad: ["A", "C"],
//   Mumbai: ["B"],
//   Pune: ["D"],
// }
```

### Python solution

```python
def group_students_by_city(students):
		students_by_city = {}

		for student in students:
				city = student["city"]
				students_by_city.setdefault(city, []).append(student["name"])

		return students_by_city


students = [
		{"name": "A", "city": "Ahmedabad"},
		{"name": "B", "city": "Mumbai"},
		{"name": "C", "city": "Ahmedabad"},
		{"name": "D", "city": "Pune"},
]

print(group_students_by_city(students))
# {'Ahmedabad': ['A', 'C'], 'Mumbai': ['B'], 'Pune': ['D']}
```

### Complexity

- **Time:** `O(n)`, because each student is processed once.
- **Space:** `O(n)` in the worst case, because the output stores every student name.

## Key Takeaway

These are not random LeetCode exercises. Frequency counting and grouping are practical patterns for processing API responses before rendering or consuming the data in a React UI.
