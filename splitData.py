from collections import defaultdict
from datetime import time
from typing import Dict, Tuple, List

import pickle
from sklearn.model_selection import train_test_split


# <ID: 4004706, Name: Blue Line Hoboken Terminal / PATH>
# <ID: 4011456, Name: Red Line Residential>
# <ID: 4013792, Name: Green Line Light Rail / Elevator>
# <ID: 4013794, Name: Gray Line North Loop>

# {
#   'speed': 7,
#   'id': 4015251,
#   'position': [40.737064, -74.02863],
#   'route_id': 4004706,
#   'timestamp': 15:36:8,
#   'stop_id': 4208462,
#   'scheduled_time': 15:37
# }

def time_to_seconds(timestamp):
    return timestamp.hour * 1200 + timestamp.minute * 60 + timestamp.second


def split_x_and_y(entry) -> Tuple[Dict, time]:
    x = {
        "speed": entry["speed"],
        "id": entry["id"],
        "position": entry["position"],
        "route_id": entry["route_id"],
        "stop_id": entry["stop_id"],
        "timestamp": entry["timestamp"],
        "scheduled_time": entry["scheduled_time"]
    }

    # late is positive, early is negative
    y = time_to_seconds(entry["timestamp"]) - time_to_seconds(entry["scheduled_time"])

    return x, y


def x_and_y_for_lines(lines):
    ml_data = {}
    for line, data in lines.items():
        ml_data[line] = {"x": [], "y": []}
        for entry in data:
            x, y = split_x_and_y(entry)
            ml_data[line]["x"].append(x)
            ml_data[line]["y"].append(y)
    return ml_data


def get_train_test(ml_data):
    train_test_data = {}
    for line, xy in ml_data.items():
        train_test_data[line] = {
            "train": {"x": [], "y": []},
            "test": {"x": [], "y": []}
        }
        x_train, x_test, y_train, y_test = train_test_split(xy["x"], xy["y"], test_size=0.15, random_state=42)
        train_test_data[line]["train"]["x"] = x_train
        train_test_data[line]["train"]["y"] = y_train

        train_test_data[line]["test"]["x"] = x_test
        train_test_data[line]["test"]["y"] = y_test

    return train_test_data


def main():
    with open("stops_with_truth.dat", "rb") as confirmed_stops_file:
        data = pickle.load(confirmed_stops_file)

    lines = defaultdict(list)
    for entry in data:
        lines[entry["route_id"]].append(entry)

    ml_data = x_and_y_for_lines(lines)

    train_test_data = get_train_test(ml_data)

    with open("train_test_data.dat", "wb") as train_test_data_file:
        pickle.dump(train_test_data, train_test_data_file)


if __name__ == "__main__":
    main()
