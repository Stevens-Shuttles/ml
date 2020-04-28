import pickle


def ml(train_x, train_y, test_x, test_y):
    # TODO ML code goes here
    pass


def main():
    # <ID: 4004706, Name: Blue Line Hoboken Terminal / PATH>
    # <ID: 4011456, Name: Red Line Residential>
    # <ID: 4013792, Name: Green Line Light Rail / Elevator>
    # <ID: 4013794, Name: Gray Line North Loop>

    with open("train_test_data.dat", "rb") as train_test_data_file:
        data = pickle.load(train_test_data_file)
    red_train_x = data[4011456]["train"]["x"]
    red_train_y = data[4011456]["train"]["y"]

    red_test_x = data[4011456]["test"]["x"]
    red_test_y = data[4011456]["test"]["y"]

    ml(red_train_x, red_train_y, red_test_x, red_test_y)


if __name__ == "__main__":
    main()
