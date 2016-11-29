class PIDController(object):
    # Class initializer. Feel free to change the implementation,
    # but do not change the signature.
    def __init__(self, setpoint, kp=0, ki=0, kd=0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.error_sum = 0
        self.prev_error = 0
        self.theta = setpoint

    # Return the voltage setting for the motor to make it reach
    # the setpoint, given its current angle
    def get_voltage(self, current_angle: float):
        print ("kp, ki, kd, setpoint, current_angle are ", self.kp, self.ki, self.kd, self.theta, current_angle)
        current_error = self.theta - current_angle
        p = self.kp * current_error
        d = self.kd * (current_error - self.prev_error) 
        print ("d = ", d)
        i = self.ki * self.error_sum
        print ("p, i, d are", p, i, d)
        tmp = p + i + d
        print ("tmp = ", tmp)
        self.prev_error = current_error
        self.error_sum += current_error
        return tmp
