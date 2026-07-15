with open("e:/Career-Transformation/03_Practice/Python/Day003/merged.txt", "r") as file:
    words = []
    for line in file:
        words.extend(line.split())

print("Words in the file:", words)

if words:
    longest_word = max(words, key=len)
    print(f"Longest word: {longest_word}")
    print(f"Length: {len(longest_word)}")
else:
    print("No words found in the file.")
