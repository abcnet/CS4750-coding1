import p4b

def f(x):
  return 9 * x[0] ** 2 + 4 * x[1] ** 2 + 6

optimum = p4b.grad_desc(f, 2)
print(optimum)


print(p4b.grad_desc(lambda x: (x[0]-2)**2 + (x[1]+1)**2, 2))