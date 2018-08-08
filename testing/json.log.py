import json

with open("status.json", "r") as read_file:
    data = json.load(read_file)

print(json.dumps(data, sort_keys=True, indent=4)) 

print(data["PDBfile"])

data["PDBfile"]="asd"

print(data["PDBfile"])

print(json.dumps(data, sort_keys=True, indent=4)) 
