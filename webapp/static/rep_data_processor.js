class RepDataProcessor {
  constructor() {
      this.reset();
  }
  
  reset() {
      
      this.reps = [];
      this.currentRep = {
          rep_count: 0,
          max_pitch: -Infinity,
          max_gz_up: -Infinity,  
          max_gz_down: Infinity, 
          max_az: -Infinity
      };
  }
  
  update(pitch, gz, az) {
      
      if (pitch > this.currentRep.max_pitch) {
          this.currentRep.max_pitch = pitch;
      }
      
      
      if (gz > 0) {
          if (gz > this.currentRep.max_gz_up) {
              this.currentRep.max_gz_up = gz;
          }
      } else if (gz < 0) {
          if (gz < this.currentRep.max_gz_down) {
              this.currentRep.max_gz_down = gz;
          }
      }
      
      
      if (az > this.currentRep.max_az) {
          this.currentRep.max_az = az;
      }
  }

  storeRep(repCount) {
      this.currentRep.rep_count = repCount;
      this.reps.push({ ...this.currentRep });  
      this.currentRep = {  
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
