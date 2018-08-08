import json
import sys

with open("status.json", "r") as read_file:
    data = json.load(read_file)

print(json.dumps(data, sort_keys=True, indent=4))

# print(data["PDBfile"])

field = sys.argv[1]

value = sys.argv[2]

data[field] = value

# print(data["PDBfile"])

print(json.dumps(data, sort_keys=True, indent=4))

print(field)
print(value)
