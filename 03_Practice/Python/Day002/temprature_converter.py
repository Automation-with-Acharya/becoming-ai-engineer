def convert_temperature(value, unit):
    unit = unit.lower()

    if unit == 'c':
        celsius = value
        fahrenheit = (celsius * 9 / 5) + 32
        kelvin = celsius + 273.15
    elif unit == 'f':
        fahrenheit = value
        celsius = (fahrenheit - 32) * 5 / 9
        kelvin = celsius + 273.15
    elif unit == 'k':
        kelvin = value
        celsius = kelvin - 273.15
        fahrenheit = (celsius * 9 / 5) + 32
    else:
        raise ValueError("Invalid unit. Use C, F, or K.")

    return celsius, fahrenheit, kelvin


value = float(input("Enter temperature value: "))
unit = input("Enter unit (C/F/K): ").strip()

celsius, fahrenheit, kelvin = convert_temperature(value, unit)

print(f"\n{value}{unit.upper()} =")
print(f"{celsius:.2f}°C")
print(f"{fahrenheit:.2f}°F")
print(f"{kelvin:.2f}K")
