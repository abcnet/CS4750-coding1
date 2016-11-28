class PIDController(object):
    # Class initializer. Feel free to change the implementation,
    # but do not change the signature.
    def __init__(self, setpoint, kp=0, ki=0, kd=0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.error_history = []
        self.theta = setpoint

    # Return the voltage setting for the motor to make it reach
    # the setpoint, given its current angle
    def get_voltage(self, current_angle: float):
        print ("kp, ki, kd, setpoint, current_angle are ", self.kp, self.ki, self.kd, self.theta, current_angle)
        current_error = self.theta - current_angle
        p = self.kp * current_error
        # print ("p = ", p)
        # print (len(self.error_history) >= 1)
        # print ("kd = ", self.kd)
        # print("current_error = ", current_error)
        # print ("self.error_history = ", self.error_history)
        # print(" self.error_history[-1] = ",  self.error_history[-1])
        # print ("diff ", current_error - self.error_history[-1])
        # print (self.kd * (current_error - self.error_history[-1]))
        d = (self.kd * (current_error - self.error_history[-1])) if (len(self.error_history) >= 1) else 0
        print ("d = ", d)
        i = self.ki * sum(self.error_history)
        print ("p, i, d are", p, i, d)
        tmp = p + i + d
        print ("tmp = ", tmp)
        self.error_history.append(current_error)
        if len(self.error_history >= 1000):
            error_history.pop(0)
        return tmp
