import csv

def auth(filename):
    auth = {}
    with open(filename, 'rb') as config:
        reader = csv.reader(config)
        for row in reader:
            auth[row[0]] = row[1]

    return auth

