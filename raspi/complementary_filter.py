import math

class OrientationFilter:
    def __init__(self, alpha=0.98, dt=0.02):
        """
        Initialize the complementary filter.
        
        :param alpha: Weighting factor between gyro and accelerometer.
                      Closer to 1 gives more weight to gyro (fast response), 
                      while closer to 0 favors the accelerometer (more stable).
        :param dt: Time interval between updates in seconds.
        """
        self.alpha = alpha
        
        self.angle = 0.0

    def update(self, gyro_rate, accel_x, accel_y, accel_z, dt):
        """
        Update the angle estimate using sensor readings.
        
        :param gyro_rate: Angular rate from the gyroscope (degrees per second).
        :param accel_x: Accelerometer reading along the x-axis.
        :param accel_y: Accelerometer reading along the y-axis.
        :param accel_z: Accelerometer reading along the z-axis.
        :return: Updated angle estimate in degrees.
        """

        accel_angle = math.atan2(accel_x, math.sqrt(accel_y**2 + accel_z**2)) * (180.0 / math.pi)
        
        gyro_angle = self.angle + gyro_rate * dt
        
        self.angle = self.alpha * gyro_angle + (1 - self.alpha) * accel_angle
        
        return self.angle

