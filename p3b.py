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
        return -6
