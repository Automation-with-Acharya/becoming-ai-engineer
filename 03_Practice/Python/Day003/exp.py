lines_to_add = ["Line 1\n", "Line 2\n", "Line 3\n"]

with open("e:/Career-Transformation/03_Practice/Python/Day003/example.txt", "w") as file:
    file.writelines(lines_to_add)
    file.write("example2 file content is added.")