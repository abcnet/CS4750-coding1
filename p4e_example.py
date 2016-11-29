import p4e

def f(x):
  return 9 * x[0] ** 2 + 4 * x[1] ** 2 + 6

constraints = [
    {
      'func': lambda x: x[0] + x[1],
      'c': 100
    },
    {
      'func': lambda x: x[0] ** 3,
      'c': 256
    }
  ]

optimum = p4e.lagrange(f, 2, constraints)
print(optimum)
