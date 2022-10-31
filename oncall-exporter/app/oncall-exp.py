import time
import requests
from prometheus_client import Counter, Gauge, start_http_server
import traceback


ONCALL_URL = "http://oncall:8080"

HOST = "0.0.0.0"
PORT = 9105
POLL = 10

ONCALL_HEALTH_STATUS = Gauge(
    "oncall_health_status", "oncall availability")

ONCALL_API_REQUESTS = Counter(
    "oncall_api_requests", "count of requests to oncall API")

ONCALL_API_REQUESTS_FAILED = Counter(
    "oncall_api_requests_failed", "count of failed requests to oncall API")

ONCALL_TEAMS_TOTAL = Gauge(
    "oncall_teams_total", "number of teams in oncall"
)

ONCALL_TEAMS_WITH_LESS_THAN_TWO_MEMBERS = Gauge(
    "oncall_teams_with_less_than_two_members",
    "total number of teams with less than two members"
)

ONCALL_SHIFTS_TOTAL = Gauge(
    "oncall_shifts_total", "total shifts planned to future from current time (inclusive)"
)

ONCALL_SHIFTS_PRIMARY = Gauge(
    "oncall_shifts_primary", "total shifts with primary role"
)

ONCALL_SHIFTS_SECONDARY = Gauge(
    "oncall_shifts_secondary", "total shifts with secondary role"
)

ONCALL_SHIFTS_WITHOUT_PARTNER = Gauge(
    "oncall_shifts_without_partner", "total shifts without secondary"
)


def oncall_proxy_get(url_component: str, api=True) -> requests.Response:
    ONCALL_API_REQUESTS.inc()
    print(f"GET {url_component}")
    url = ONCALL_URL + ("/api/v0" if api else "") + url_component
    try:
        r = requests.get(url, timeout=2, verify=False)
        if r.status_code != 200:
            print(f"GET {url_component} FAILED {r.status_code}")
            print(f"{r.__dict__}")
            ONCALL_API_REQUESTS_FAILED.inc()
        return r
    except Exception as e:
        traceback.print_exception(e)
        ONCALL_API_REQUESTS_FAILED.inc()
        return None

def health() -> bool:
    r = oncall_proxy_get("/", api=False)
    if r and r.status_code == 200:
        ONCALL_HEALTH_STATUS.set(1)
        return True
    else:
        ONCALL_HEALTH_STATUS.set(0)
        return False

def teams() -> int:
    r = oncall_proxy_get("/teams")
    if r.status_code != 200:
        return
    teams = r.json()
    print("GET /teams successful:")
    print(teams)
    ONCALL_TEAMS_TOTAL.set(len(teams))
    print(f"Set ONCALL_TEAMS_TOTAL to {len(teams)}")

    almost_empty_teams = 0
    for team in teams:
        data = oncall_proxy_get(f"/teams/{team}/")
        if data.status_code != 200:
            print(f"Skipping {team}")
            continue
        datajson = data.json()
        users = datajson["users"]
        if len(users) < 2:
            almost_empty_teams += 1
            print(f"INC almost_empty_teams = {almost_empty_teams}")
    
    ONCALL_TEAMS_WITH_LESS_THAN_TWO_MEMBERS.set(almost_empty_teams)
    return almost_empty_teams

def shifts() -> tuple[int, int, int, int]:
    unix_time = int(time.time())
    r = oncall_proxy_get(f"/events?start__ge={unix_time}&role__eq=primary")
    if r.status_code != 200:
        return
    shifts_primary: list[dict] = r.json()
    print(shifts_primary)
    shifts_primary_total = len(shifts_primary)
    ONCALL_SHIFTS_PRIMARY.set(shifts_primary_total)
    print(f"Set ONCALL_SHIFTS_PRIMARY to {shifts_primary_total}")

    r = oncall_proxy_get(f"/events?start__ge={unix_time}&role__eq=secondary")
    if r.status_code != 200:
        return
    shifts_secondary: list[dict] = r.json()
    print(shifts_secondary)
    shifts_secondary_total = len(shifts_secondary)
    ONCALL_SHIFTS_SECONDARY.set(shifts_secondary_total)
    print(f"Set ONCALL_SHIFTS_SECONDARY to {shifts_secondary_total}")

    shifts_total = 0
    shifts_without_partner = 0
    for p in shifts_primary:
        shift_time = p["start"]
        s = oncall_proxy_get(f"/events?start={shift_time}&role__eq=secondary")
        if s.status_code != 200:
            continue
        print(s.json())
        if len(s.json()) == 0:
            print("Shift without partner with time = ", shift_time)
            shifts_without_partner += 1
        shifts_total += 1
    print(f"total: {shifts_total}")
    print(f"without partner: {shifts_without_partner}")

    ONCALL_SHIFTS_TOTAL.set(shifts_total)
    ONCALL_SHIFTS_WITHOUT_PARTNER.set(shifts_without_partner)
    return shifts_primary_total, shifts_secondary_total, shifts_total, shifts_without_partner


if __name__ == "__main__":
    print("Start")
    start_http_server(port=PORT, addr=HOST)
    print(f"started http server on http://{HOST}:{PORT}")

    while True:
        try:
            if health():
                print(f"Teams (< 2): {teams()}")
                print("Shifts: pr={} sc={} total={} nopartner={}".format(*shifts()))
            else:
                print("healthcheck failed")
        except Exception as e:
            traceback.print_exception(e)
            continue
        time.sleep(POLL)
