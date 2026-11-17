import re
import threading
import requests

MIN_INTERVAL_SECONDS = 10
REQUEST_TIMEOUT_SECONDS = 10
UPTIME_FEHLER = "Uptime Fehler"

# Uptime-Kuma-Status: 0 = DOWN, 1 = UP, 2 = PENDING, 3 = MAINTENANCE
OK_STATES = (1, 3)

METRIC_RX = re.compile(r"^monitor_status\{(.*)\}\s+(\S+)\s*$", re.M)
NAME_RX = re.compile(r'monitor_name="((?:[^"\\]|\\.)*)"')


def _unescape(value):
    return value.replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")


def parse_metrics(text):
    """Liefert eine Liste von (name, status) aller monitor_status-Zeilen."""
    states = []
    for labels, value in METRIC_RX.findall(text):
        match = NAME_RX.search(labels)
        name = _unescape(match.group(1)) if match else "?"
        states.append((name, int(float(value))))
    return states


class LogicModule:
    def __init__(self, hsl3):
        self.fw = hsl3
        self.debug = self.fw.create_debug_section()
        self.url = ""
        self.api_key = ""
        self.intervall = 60
        self.busy = False
        self.last = None

    def on_init(self, inputs, store):
        self._read_inputs(inputs)
        self.poll()

    def on_calc(self, inputs):
        changed = any(inputs.changed(k) for k in ("url", "api_key", "intervall"))
        self._read_inputs(inputs)
        if changed or (inputs.changed("trigger") and inputs.value("trigger")):
            self.poll()

    def on_timer(self, timer):
        if timer.changed("timer_poll"):
            self.poll()

    def _read_inputs(self, inputs):
        self.url = inputs.value("url").decode("iso-8859-15").strip().rstrip("/")
        self.api_key = inputs.value("api_key").decode("iso-8859-15").strip()
        self.intervall = max(int(inputs.value("intervall")), MIN_INTERVAL_SECONDS)

    def poll(self):
        self.fw.set_timer("timer_poll", self.intervall)
        if not self.url:
            self.debug.log("Keine URL konfiguriert")
            return
        if self.busy:
            return
        self.busy = True
        threading.Thread(target=self._fetch, args=(self.url, self.api_key)).start()

    def _fetch(self, url, api_key):
        query_error = False
        bad = []
        try:
            response = requests.get(
                url + "/metrics", auth=("", api_key), timeout=REQUEST_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            states = parse_metrics(response.text)
            if not states:
                raise ValueError("Keine monitor_status-Zeilen in /metrics")
            bad = sorted(name for name, status in states if status not in OK_STATES)
        except Exception:
            self.debug.exception("Abfrage von Uptime Kuma fehlgeschlagen")
            query_error = True
        self.fw.run_in_context(self._apply, (query_error, bad))

    def _apply(self, query_error, bad):
        self.busy = False
        names = ([UPTIME_FEHLER] if query_error else []) + bad
        result = (int(query_error or bool(bad)), len(bad), ", ".join(names))
        self.debug.set("Letzte Abfrage", "Fehler" if query_error else "OK")
        self.debug.timestamp("Zeitpunkt")
        if result == self.last:
            return
        self.last = result
        self.fw.set_output("fehler", result[0])
        self.fw.set_output("anzahl", result[1])
        self.fw.set_output("namen", result[2].encode("iso-8859-15", "replace"))
