import threading
import requests

REFRESH_INTERVAL_SECONDS = 3600
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
MAX_FORECAST_DAYS = 16


class LogicModule:
    def __init__(self, hsl3):
        self.fw = hsl3
        self.debug = self.fw.create_debug_section()
        self.lat = 0.0
        self.lng = 0.0
        self.tage_rasen = 2
        self.schwellwert_rasen_mm = 15.0
        self.tage_beete = 3
        self.schwellwert_beete_mm = 20.0

    def on_init(self, inputs, store):
        self.debug.log(f"Called on_init with keys: {inputs.keys()}")
        self.lat = inputs.value("lat")
        self.lng = inputs.value("lng")
        self.tage_rasen = int(inputs.value("tage_rasen"))
        self.schwellwert_rasen_mm = inputs.value("schwellwert_rasen_mm")
        self.tage_beete = int(inputs.value("tage_beete"))
        self.schwellwert_beete_mm = inputs.value("schwellwert_beete_mm")
        self.fw.set_timer("timer_refresh", REFRESH_INTERVAL_SECONDS)
        self.request_update()

    def on_calc(self, inputs):
        self.debug.log(f"Called on_calc with keys: {inputs.keys()}")
        coordinates_changed = False
        if inputs.changed("lat"):
            self.lat = inputs.value("lat")
            coordinates_changed = True
        if inputs.changed("lng"):
            self.lng = inputs.value("lng")
            coordinates_changed = True
        if inputs.changed("tage_rasen"):
            self.tage_rasen = int(inputs.value("tage_rasen"))
            coordinates_changed = True
        if inputs.changed("schwellwert_rasen_mm"):
            self.schwellwert_rasen_mm = inputs.value("schwellwert_rasen_mm")
            coordinates_changed = True
        if inputs.changed("tage_beete"):
            self.tage_beete = int(inputs.value("tage_beete"))
            coordinates_changed = True
        if inputs.changed("schwellwert_beete_mm"):
            self.schwellwert_beete_mm = inputs.value("schwellwert_beete_mm")
            coordinates_changed = True
        if coordinates_changed:
            self.request_update()

    def on_timer(self, timer):
        if timer.changed("timer_refresh"):
            self.request_update()
            self.fw.set_timer("timer_refresh", REFRESH_INTERVAL_SECONDS)

    def request_update(self):
        if self.lat == 0 and self.lng == 0:
            self.debug.log("Skipping update: lat/lng not yet configured")
            return
        thread = threading.Thread(target=self.fetch_forecast)
        thread.start()

    def fetch_forecast(self):
        forecast_days = min(max(self.tage_rasen, self.tage_beete), MAX_FORECAST_DAYS)
        params = {
            "latitude": self.lat,
            "longitude": self.lng,
            "daily": "precipitation_sum",
            "timezone": "auto",
            "forecast_days": forecast_days,
        }
        try:
            self.debug.log(f"Requesting forecast for lat={self.lat}, lng={self.lng}")
            response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
            response.raise_for_status()
            daily_precipitation = response.json()["daily"]["precipitation_sum"]

            regen_summe_rasen = sum(daily_precipitation[: self.tage_rasen])
            sperre_rasen = float(regen_summe_rasen >= self.schwellwert_rasen_mm)

            regen_summe_beete = sum(daily_precipitation[: self.tage_beete])
            sperre_beete = float(regen_summe_beete >= self.schwellwert_beete_mm)

            self.fw.run_in_context(
                self.set_outputs,
                (
                    regen_summe_rasen,
                    sperre_rasen,
                    regen_summe_beete,
                    sperre_beete,
                ),
            )
        except Exception:
            self.debug.exception("Fehler beim Abruf der OpenMeteo Regenvorhersage")

    def set_outputs(
        self,
        regen_summe_rasen,
        sperre_rasen,
        regen_summe_beete,
        sperre_beete,
    ):
        self.fw.set_output("regen_summe_rasen_mm", float(regen_summe_rasen))
        self.fw.set_output("sperre_rasen", sperre_rasen)
        self.fw.set_output("regen_summe_beete_mm", float(regen_summe_beete))
        self.fw.set_output("sperre_beete", sperre_beete)
