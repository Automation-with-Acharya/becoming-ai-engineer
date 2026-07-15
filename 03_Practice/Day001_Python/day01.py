# Day 1 practice codes:
#     Reverse a string
#     Count vowels in a string
#     Check palindrome
#     Find largest element in a list
#     Find second largest element
#     Remove duplicates from a list
#     Generate first 20 Fibonacci numbers
#     Check prime number
#     Calculate factorial
#     Count word frequencies in a sentence

#     Reverse a string
input_x = 'Mayank'

def reverse_string(input_x):
    return input_x[::-1]

print(reverse_string(input_x))

#     Count vowels in a string
input_y = 'Hello, World!'

def count_vowels(input_y):
    vowels = 'aeiouAEIOU'
    count = 0
    for char in input_y:
        if char in vowels:
            count += 1
    return count

print(count_vowels(input_y))

#     Check palindrome
input_z = 'racecar'

def is_palindrome(input_z):
    
    return input_z == input_z[::-1]

print(is_palindrome(input_z))

#     Find largest element in a list
input_list = [3, 7, 2, 9, 1, 5]

def find_largest(input_list):
    return max(input_list)

print(find_largest(input_list))

#     Find second largest element
def find_second_largest(input_list):
    unique_elements = list(set(input_list))
    unique_elements.sort(reverse=True)
    return unique_elements[1] if len(unique_elements) > 1 else None

print(find_second_largest(input_list))

#     Remove duplicates from a list
def remove_duplicates(input_list):
    return list(set(input_list))

print(remove_duplicates(input_list))

#     Generate first 20 Fibonacci numbers
def generate_fibonacci(n):
    fib_sequence = [0, 1]
    while len(fib_sequence) < n:
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence

print(generate_fibonacci(20))

#     Check prime number
def is_prime(num):
    if num <= 1:
        return False
    for i in range(2, (num//2) + 1):
        if num % i == 0:
            return False
    return True

#     Calculate factorial
def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)

#     Count word frequencies in a sentence
def count_word_frequencies(sentence):
    words = sentence.split()
    frequency = {}
    for word in words:
        #word = word.lower().strip('.,!?;:"()[]{}')  # Normalize the word
        if word in frequency:
            frequency[word] += 1
        else:
            frequency[word] = 1
    return frequency