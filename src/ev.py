class ElectricVehicle:
    def __init__(self, capacity_kwh, soc_percent, wh_per_km, min_safe_percent=10):
        self.capacity = capacity_kwh
        self.soc = soc_percent / 100
        self.wh_per_km = wh_per_km
        self.min_safe = min_safe_percent / 100

    @property
    def energy_remaining(self):
        return self.capacity * self.soc

    @property
    def range_remaining(self):
        return self.energy_remaining * 1000 / self.wh_per_km

    def consume(self, km):
        used = km * self.wh_per_km / 1000
        self.soc -= used / self.capacity
        self.soc = max(self.soc, 0)

    def can_travel(self, km):
        return self.range_remaining >= km and self.soc > self.min_safe

    def charge_to(self, target_percent):
        """
        Sạc đến X% pin. Trả về thời gian sạc (giả lập).
        """
        initial = self.soc
        target_soc = target_percent / 100
        delta = max(0, target_soc - initial)
        time_hours = delta * self.capacity / 50  # giả sử 50 kW
        self.soc = target_soc
        return time_hours * 60  # phút
