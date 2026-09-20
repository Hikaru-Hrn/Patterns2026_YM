import math

# Считываем значение, заменяя запятую на точку, без текста внутри input()
a = float(input())

perimeter = 5 * a
area = (5 * a**2) / (4 * math.tan(math.pi / 5))

# Если система требует вывод двух чисел (часто с округлением, например, до 2 знаков):
print(f"{perimeter:.2f}")
print(f"{area:.2f}")