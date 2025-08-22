import time

class TrafficController:
    def __init__(self, phases, base_green=15, max_green=45):
        """
        phases: list of approach names, e.g. ['N', 'E', 'S', 'W']
        base_green: default green time per phase in seconds
        max_green: maximum allowed green time
        """
        self.phases = phases
        self.base_green = base_green
        self.max_green = max_green
        self.current_phase = 0
        self.phase_start = time.time()
        self.phase_duration = base_green

    def compute_green_time(self, vehicle_count):
        # simple linear mapping: base + k * vehicles
        k = 3  # seconds added per vehicle (tune)
        t = self.base_green + int(k * vehicle_count)
        return min(t, self.max_green)

    def next_phase(self, counts):
        # counts: dict approach -> vehicle_count
        # choose next phase in round-robin but compute duration using counts for that phase
        self.current_phase = (self.current_phase + 1) % len(self.phases)
        ph = self.phases[self.current_phase]
        dur = self.compute_green_time(counts.get(ph, 0))
        self.phase_start = time.time()
        self.phase_duration = dur
        return ph, dur

    def get_current_phase(self):
        return self.phases[self.current_phase], self.phase_duration, int(max(0, self.phase_duration - (time.time() - self.phase_start)))