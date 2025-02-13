class RepDataProcessor {
  constructor() {
      this.reset();
  }
  
  reset() {
      // Store multiple reps in an array
      this.reps = [];
      this.currentRep = {
          rep_count: 0,
          max_pitch: -Infinity,
          max_gz_up: -Infinity,  // Max upward motion
          max_gz_down: Infinity, // Max downward motion
          max_az: -Infinity
      };
  }
  
  update(pitch, gz, az) {
      // Update max pitch
      if (pitch > this.currentRep.max_pitch) {
          this.currentRep.max_pitch = pitch;
      }
      
      // Update gz values
      if (gz > 0) {
          if (gz > this.currentRep.max_gz_up) {
              this.currentRep.max_gz_up = gz;
          }
      } else if (gz < 0) {
          if (gz < this.currentRep.max_gz_down) {
              this.currentRep.max_gz_down = gz;
          }
      }
      
      // Update max az
      if (az > this.currentRep.max_az) {
          this.currentRep.max_az = az;
      }
  }

  storeRep(repCount) {
      this.currentRep.rep_count = repCount;
      this.reps.push({ ...this.currentRep });  // Store the finished rep
      this.currentRep = {  // Reset for next rep
          rep_count: repCount,
          max_pitch: -Infinity,
          max_gz_up: -Infinity,
          max_gz_down: Infinity,
          max_az: -Infinity
      };
  }

  getAggregatedData() {
      return { reps: this.reps };
  }
}
