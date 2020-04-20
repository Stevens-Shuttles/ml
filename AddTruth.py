from collections import defaultdict
from datetime import datetime, time, timedelta
from decimal import Decimal
import json
import pickle
from typing import Dict, List

from Shuttles.ShuttleService import ShuttleService, Stop


def str_to_time(time_: str) -> time:
    time_ = time_.replace("p.m.", "PM")
    time_ = time_.replace("a.m.", "AM")

    dt = datetime.strptime(time_, "%I:%M %p")
    return dt.time()


def load_paper_schedules():
    """
    For each line get each schedule; for each schedule get each route; for each route get all times;
    convert times to time objects
    :return:
    """
    schedule_metadata = {
        4004706: [
            {
                "file": "Blue.json",
                "days": [0, 1, 2, 3, 4],  # Monday: 0, Sunday: 6
                "times": defaultdict(list)
            }
        ],
        4011456: [
            {
                "file": "RedEarly.json",
                "days": [0, 1, 2, 3, 4],
                "times": defaultdict(list)
            },
            {
                "file": "Red.json",
                "days": [0, 1, 2, 3, 4],
                "times": defaultdict(list)
            },
            {
                "file": "Saturday.json",
                "days": [5],
                "times": defaultdict(list)
            },
            {
                "file": "Sunday.json",
                "days": [6],
                "times": defaultdict(list)
            },
        ],
        4013792: [
            {
                "file": "Green.json",
                "days": [0, 1, 2, 3, 4],
                "times": defaultdict(list)
            }
        ],
        4013794: [
            {
                "file": "Gray.json",
                "days": [0, 1, 2, 3, 4],
                "times": defaultdict(list)
            },
            {
                "file": "GrayLate.json",
                "days": [0, 1, 2, 3, 4],
                "times": defaultdict(list)
            }
        ]
    }

    for route_id, schedules in schedule_metadata.items():
        for schedule in schedules:
            with open("schedules/" + schedule["file"]) as schedule_file:
                paper_schedule = json.load(schedule_file)
                for stop, times in paper_schedule.items():
                    for time_ in times:
                        try:
                            time_obj = str_to_time(time_)
                            schedule["times"][int(stop)].append(time_obj)
                        except ValueError:
                            pass
    return schedule_metadata


def time_difference(t1: time, t2: time) -> int:
    """Return t1 - t2 in seconds"""
    return (timedelta(hours=t1.hour, minutes=t1.minute, seconds=t1.second) - timedelta(hours=t2.hour, minutes=t2.minute,
                                                                                       seconds=t2.second)).seconds


def get_stops_by_route() -> Dict[int, List[Stop]]:
    ss = ShuttleService(307)

    stops = {s.id: s for s in ss.get_stops()}
    int_stops_by_route = ss.get_stop_ids_for_routes()
    return {route_id: [stops[s] for s in stops_] for route_id, stops_ in int_stops_by_route.items()}


def get_scheduled_time(schedules, recorded_timestamp: Decimal, route_id: int, stop_id: int) -> time:
    dt = datetime.fromtimestamp(recorded_timestamp)
    recorded_time = dt.time()
    weekday = dt.weekday()

    for num, schedule in enumerate(schedules[route_id]):
        if weekday in schedule["days"]:  # TODO account for past midnight
            first_time = schedule["times"][stop_id][0]
            last_time = schedule["times"][stop_id][-1]
            if recorded_time <= first_time:  # Early
                return first_time
            if recorded_time > last_time:  # After the schedule
                return last_time  # This works assuming that there is only 1 valid schedule for a weekday grouping
            for paper_time in schedule["times"][stop_id][1:]:  # Find the nearest time in the middle
                if recorded_time <= paper_time:
                    if time_difference(recorded_time, first_time) > time_difference(paper_time, recorded_time):
                        return paper_time
                    return first_time
                first_time = paper_time
    raise ValueError


def write_confirmed_stops():
    stops_by_route = get_stops_by_route()

    with open("entries.dat", "rb") as entries_file:
        entries = pickle.load(entries_file)
        print(len(entries))

    confirmed_stops = []
    last_stop = {}  # Avoid double-counting stops
    for entry in entries:
        try:
            for stop in stops_by_route[entry["route_id"]]:
                if last_stop.get(entry["route_id"]) != stop.id \
                        and stop.at_stop(entry["position"], 10):
                    last_stop[entry["route_id"]] = stop.id
                    entry["stop_id"] = stop.id
                    confirmed_stops.append(entry)
        except KeyError:
            print(f"Unknown route: {entry['route_id']}")
    with open("confirmed_stops.dat", "wb") as confirmed_stops_file:
        pickle.dump(confirmed_stops, confirmed_stops_file)

    print(len(entries))
    print(len(confirmed_stops))
    print(len(entries) - len(confirmed_stops))


def add_times_to_stops():
    schedules = load_paper_schedules()

    with open("confirmed_stops.dat", "rb") as confirmed_stops_file:
        confirmed_stops = pickle.load(confirmed_stops_file)

    stops_with_truth = []
    failed_entries = 0
    for entry in confirmed_stops:
        try:
            entry["scheduled_time"] = get_scheduled_time(
                schedules,
                entry["timestamp"],
                entry["route_id"],
                entry["stop_id"]
            )
            entry["timestamp"] = datetime.fromtimestamp(entry["timestamp"]).time()
            stops_with_truth.append(entry)
        except (ValueError, IndexError):
            failed_entries += 1

    print(f"Failed to get time for {failed_entries} stops")
    print(f"Have {len(stops_with_truth)} stops")

    with open("stops_with_truth.dat", "wb") as stops_truth_file:
        pickle.dump(stops_with_truth, stops_truth_file)


def main():
    for meta in load_paper_schedules().values():
        for sched in meta:
            count = 0
            for times in sched["times"].values():
                count += len(times)
            print(f"{sched['file']}: {count}")
    # ss = ShuttleService(307)
    # for s in ss.get_stops():
    #     print(f"{s.id} | {s.name}")
    # write_confirmed_stops()
    add_times_to_stops()


if __name__ == "__main__":
    main()
