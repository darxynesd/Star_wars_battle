"""
Узгодження часу кадру: дельта-час, таймери перезарядки/ефектів, планувальник відкладених подій (наприклад, інвертований контроль на льоду).
"""

class Time:
    def __init__(self):
        self.dt = 0.0
        self._accum = 0.0

    def update(self, clock):
        self.dt = clock.get_time() / 1000.0
        self._accum += self.dt

    def every(self, seconds: float) -> bool:
        if self._accum >= seconds:
            self._accum = 0.0
            return True
        return False
