import json
import sys

with open("status.json", "r") as read_file:
    data = json.load(read_file)

print(json.dumps(data, sort_keys=True, indent=4))

#print(data["PDBfile"])

category = sys.argv[1]

field = sys.argv[2]

value = sys.argv[3]

data[category][field] = value

#print(data["PDBfile"])

#print(json.dumps(data, sort_keys=True, indent=4))
#print(category)
#print(field)
#print(value)

with open('status.json', 'w') as outfile:
    json.dump(data, outfile)
