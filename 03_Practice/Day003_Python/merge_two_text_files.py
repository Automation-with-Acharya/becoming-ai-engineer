with open("e:/Career-Transformation/03_Practice/Python/Day003/example.txt", "r") as f1:
    f1_content = f1.read()

with open("e:/Career-Transformation/03_Practice/Python/Day003/example2.txt", "r") as f2:
    f2_content = f2.read()

with open("e:/Career-Transformation/03_Practice/Python/Day003/merged.txt", "w") as merged_file:
    merged_file.write(f1_content + f2_content)
    