def grad_desc(f, input_length):
    x = [0] * input_length
    grad_sum = 0
    first = True
    d = 1e-3
    eps = 1e-8
    eta = 1e-3
    while first or grad_sum > eps:
    	first = False
    	curr = f(x)
    	grad_sum = 0
    	for i in range(input_length):
    		x[i] += d
    		grad = (f(x) - curr) / d
    		grad_sum += grad ** 2
    		x[i] -= d + eta * grad
    return x