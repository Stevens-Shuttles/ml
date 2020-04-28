import pickle
import time

import boto3
from boto3.dynamodb.conditions import Attr


# Can also use environment variable: `set AWS_PROFILE=shuttles`
sess = boto3.session.Session(profile_name="shuttles")

dynamodb = sess.resource("dynamodb")


def entries_since(timestamp: int):
    table = dynamodb.Table("shuttles")

    params = {
        "Select": "SPECIFIC_ATTRIBUTES",
        "ProjectionExpression": "id, #t, #p, route_id, speed",
        "ExpressionAttributeNames": {"#t": "timestamp", "#p": "position"},
        "Limit": 5000,
        "FilterExpression": Attr("timestamp").gt(timestamp)
    }

    entries = []

    res = table.scan(**params)
    entries.extend(res["Items"])
    count = 1
    while res.get("LastEvaluatedKey"):
        print(f"{count}: {res['ScannedCount']}")
        params["ExclusiveStartKey"] = res["LastEvaluatedKey"]
        res = table.scan(**params)
        entries.extend(res["Items"])
        time.sleep(1)
        count += 1

    return entries


def main():
    entries = entries_since(timestamp=1571529600)
    with open("entries.dat", "wb") as entries_file:
        pickle.dump(entries, entries_file)


if __name__ == "__main__":
    main()
