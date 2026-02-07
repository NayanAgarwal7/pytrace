x = 0
y = 1

for i in range(3):
    x = x + i

if x > 2:
    z = x * 2
else:
    z = x - 1

def accumulate(n):
    total = 0
    for j in range(n):
        total = total + j
    return total

result = accumulate(4)

a = []
b = a
a.append(result)

sum2 = 0
for p in range(2):
    for q in range(2):
        sum2 = sum2 + p + q

def factorial(n):
    if n == 1:
        return 1
    return n * factorial(n - 1)

fact = factorial(4)

