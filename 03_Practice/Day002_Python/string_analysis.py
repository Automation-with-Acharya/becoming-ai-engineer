def count_characters(text):
    uppercase = 0
    lowercase = 0
    digits = 0
    special = 0

    for char in text:
        if char.isupper():
            uppercase += 1
        elif char.islower():
            lowercase += 1
        elif char.isdigit():
            digits += 1
        else:
            special += 1

    return uppercase, lowercase, digits, special


user_input = input("Enter a string: ")
upper, lower, digit, special = count_characters(user_input)

print(f"Uppercase letters: {upper}")
print(f"Lowercase letters: {lower}")
print(f"Digits: {digit}")
print(f"Special characters: {special}")
