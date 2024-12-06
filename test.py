import operator

t = [1, 2, 3, 4, 5]
print(list(map(operator.mul(t, 2), t)))