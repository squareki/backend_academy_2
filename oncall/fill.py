import requests
import datetime

BASE_URL = "http://localhost:8080/api/v0"
USERS_URL = BASE_URL + "/users"
TEAMS_URL = BASE_URL + "/teams"
EVENTS_URL = BASE_URL + "/events"
LOGIN_URL = "http://localhost:8080/login"
TEAM_NAME = "theoneswhowatch"

def create_user(name: str, shortname: str, phone: str) -> None:
    data = {"name": shortname}
    r = requests.post(
        USERS_URL,
        json=data
    )
    if r.status_code != 201:
        print("User POST create failed")
        print(r.__dict__)
        print(r.status_code)
        print(r.json())
        raise Exception

    data = {
        "active": 1,
        "contacts": {
            "call": phone,
            "email": f"{shortname}@tinkoff.ru",
            "sms": phone
        },
        "full_name": name,
        "time_zone": "Europe/Moscow"
    }
    r = requests.put(
        USERS_URL + "/" + shortname,
        json=data
    )
    if r.status_code != 204:
        print("User PUT info failed")
        print(r.status_code)
        print(r.__dict__)
        raise Exception

def login_admin(admin: str) -> tuple[str, requests.Session]:
    # https://github.com/linkedin/oncall/blob/master/src/oncall/auth/login.py
    data = {
        "username": admin,
        "password": "dummy"
    }
    s: requests.Session = requests.Session()
    r = s.post(
        LOGIN_URL,
        data=data,
    )
    if r.status_code != 200:
        print("Login failed")
        print(r.status_code)
        print(r.__dict__)
        raise Exception

    csrf_token: str = r.json().get("csrf_token")
    return csrf_token, s

def create_team(name: str, admin: str) -> None:
    try:
        token, s = login_admin(admin)
        print("Received token {}".format(token))
    except:
        print("Failed to receive CSRF token")
        return
    data = {
        "name": name,
        "scheduling_timezone": "Europe/Moscow",
    }
    headers = {
        "X-CSRF-TOKEN": token,
    }
    r = s.post(
        TEAMS_URL,
        json=data,
        headers=headers,
    )
    if r.status_code != 201:
        print("Team create failed")
        print(r.status_code)
        print(r.json())
        raise Exception
    

def fill_team(team, names, roster):
    data = {
        "name": roster,
    }
    r = requests.post(
        TEAMS_URL + "/" + team + "/rosters",
        json=data,
    )
    if r.status_code != 201:
        print("Roster create failed")
        print(r.status_code)
        print(r.__dict__)
        raise Exception

    for name in names:
        data = {
            "name": name,
        }
        r = requests.post(
            TEAMS_URL + "/" + team + "/rosters/" + roster + "/users",
            json=data,
        )
        if r.status_code != 201:
            print("Roster fill failed")
            print(r.status_code)
            print(r.__dict__)
            print(r.request.url)
            raise Exception

def create_event(start: datetime.datetime, end: datetime.datetime, primary: str, secondary: str):
    data = {
        "start": int(start.timestamp()),
        "end": int(end.timestamp()),
        "team": TEAM_NAME,
        "user": primary,
        "role": "primary",
    }
    r = requests.post(
        EVENTS_URL,
        json=data
    )
    if r.status_code != 201:
        print(f"Primary create failed for {start}-{end}")
        print(r.status_code)
        print(r.json())
        print(r.__dict__)
        raise Exception
    
    data["user"] = secondary
    data["role"] = "secondary"
    r = requests.post(
        EVENTS_URL,
        json=data
    )
    if r.status_code != 201:
        print(f"Secondary create failed for {start}-{end}")
        print(r.status_code)
        print(r.json())
        print(r.__dict__)
        raise Exception


def flush():
    names = ["aboba", "boba", "coba", "doba", "foba", "hoba"]
    for name in names:
        r = requests.delete(USERS_URL + "/" + name)
        #print(r.status_code)
        if r.status_code // 200 != 1:
            print("Flush failed on " + name)
            print(r.__dict__)
            raise Exception
    print("Flush done")

def flush_events():
    r = requests.get(EVENTS_URL + "/?team=" + TEAM_NAME)
    if r.status_code != 200:
        print("Events get failed")
        print(r.status_code)
        print(r.json())
        raise Exception
    
    print(r.json())
    for e in r.json():
        r = requests.delete(
            EVENTS_URL + "/" + str(e.get("id")),
        )
        if not (r.status_code >= 200 and r.status_code < 300):
            print("Event delete failed")
            print(r.status_code)
            print(r.json())
            raise Exception
        else:
            print(r.status_code)

    print("Events flush -- all good") 

def fill_users():
    try:
        create_user("Aboba Bobovich", "aboba", "+7 111-111-1111")
        create_user("Boba Cobovich", "boba", "+7 211-111-1111")
        create_user("Coba Dobovich", "coba", "+7 311-111-1111")
        create_user("Doba Fobovich", "doba", "+7 411-111-1111")
        create_user("Foba Hobovich", "foba", "+7 511-111-1111")
        create_user("Hoba Kobovich", "hoba", "+7 611-111-1111")
    except:
        print("Users fill failed")
    
    print("Users fill done")

def fill_teams():
    first_team = TEAM_NAME
    second_team = "dfh"
    try:
        create_team(first_team, "aboba")
        create_team("dfh", "doba")
    except:
        print("Team create failed")
        raise Exception
    
    try:
        fill_team(first_team, ["aboba", "boba", "coba"], "rosterowski")
        fill_team(second_team, ["doba", "foba", "hoba"], "rosterinski")
    except Exception as e:
        print("Roster create/fill failed")
        print(e)
        raise Exception

    print("Team fill done")

def fill_events():
    events = [
        # [datetime.datetime(2022, 9, 30, 12), datetime.datetime(2022, 10, 4, 12), "aboba", "boba"],
        [datetime.datetime(2022, 10, 4, 12), datetime.datetime(2022, 10, 9, 12), "boba", "coba"],
        [datetime.datetime(2022, 10, 9, 12), datetime.datetime(2022, 10, 14, 12), "coba", "aboba"],
        [datetime.datetime(2022, 10, 14, 12), datetime.datetime(2022, 10, 19, 12), "aboba", "boba"],
        [datetime.datetime(2022, 10, 19, 12), datetime.datetime(2022, 10, 24, 12), "boba", "coba"],
        [datetime.datetime(2022, 10, 24, 12), datetime.datetime(2022, 10, 29, 12), "coba", "aboba"],
        [datetime.datetime(2022, 10, 29, 12), datetime.datetime(2022, 11, 3, 12), "aboba", "boba"],
        [datetime.datetime(2022, 11, 3, 12), datetime.datetime(2022, 11, 8, 12), "boba", "coba"],
        [datetime.datetime(2022, 11, 8, 12), datetime.datetime(2022, 11, 13, 12), "coba", "aboba"],
        [datetime.datetime(2022, 11, 13, 12), datetime.datetime(2022, 11, 18, 12), "aboba", "boba"],
        [datetime.datetime(2022, 11, 18, 12), datetime.datetime(2022, 11, 23, 12), "boba", "coba"],
        [datetime.datetime(2022, 11, 23, 12), datetime.datetime(2022, 11, 28, 12), "coba", "aboba"],
        [datetime.datetime(2022, 11, 28, 12), datetime.datetime(2022, 12, 3, 12), "aboba", "boba"],
    ]
    try:
        for e in events:
            create_event(*e)
    except Exception as e:
        print("Events fill failed")
        print(e)
        return
    
    print("Events fill done")


#flush()
fill_users()
fill_teams()
#flush_events()
fill_events()