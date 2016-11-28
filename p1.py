import math
def joint_force(lengths, thetas, masses):
    print(lengths, thetas, masses)
    m1 = masses[0]
    m2 = masses[1]
    g = 9.8
    l1 = lengths[0]
    l2 = lengths[1]
    t1 = thetas[0]
    t2 = thetas[1]
    tmp = m2 * l2 / 2.0 * math.cos(t1 + t2)
    tau1 = ((m1 / 2.0 + m2) * l1 * math.cos(t1) + tmp) * g
    tau2 = tmp * g
    # print (tau1, tau2)
    return (-tau1, -tau2)
