class RepDataProcessor:
    def __init__(self):
        self.reset()

    def reset(self):
        # Initialize or reset the aggregated metrics for a new rep
        self.min_pitch = float('inf')
        self.max_pitch = -float('inf')
        self.max_gz_up = -float('inf')   # For upward motion (assuming gz positive means upward)
        self.max_gz_down = float('inf')   # For downward motion (assuming gz negative means downward)
        self.max_az = -float('inf')

    def update(self, pitch, gz, az):
        if pitch < self.min_pitch:
            self.min_pitch = pitch
        if pitch > self.max_pitch:
            self.max_pitch = pitch

        if gz > 0:
            if gz > self.max_gz_up:
                self.max_gz_up = gz
        elif gz < 0:
            if gz < self.max_gz_down:
                self.max_gz_down = gz

        # Update max az
        if az > self.max_az:
            self.max_az = az

    def get_aggregated_data(self):
        return {
            "min_pitch": self.min_pitch,
            "max_pitch": self.max_pitch,
            "max_gz_up": self.max_gz_up,
            "max_gz_down": self.max_gz_down,
            "max_az": self.max_az
        }
