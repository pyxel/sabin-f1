import requests, json, csv


def appendfile(file: str, content: str):
    print(f"Writing {file}")
    f = open(file, "a")
    f.write(content)
    f.close()

l = []

round = 5
response = requests.get(f'https://ergast.com/api/f1/current/{round}/sprint.json')


for round in range(17, 18):
    print(f"Getting round {round}")
    response = requests.get(f'https://ergast.com/api/f1/current/{round}/sprint.json')

    if len(json.loads(response.text)["MRData"]["RaceTable"]["Races"]) == 0: continue
    results = json.loads(response.text)["MRData"]["RaceTable"]["Races"][0]["SprintResults"]

    for r in results:
        l.append((round if round < 6 else round+1, 'sprint', r["position"], r["Driver"]["code"], r["points"], ))

f = open("sprints.csv", "w", newline="")
fcsv = csv.writer(f)

for row in l:
    fcsv.writerow(row)

f.close()
