import json
json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}])

print(json.dumps("\"foo\bar"))

print(json.dumps('\u1234'))

print(json.dumps('\\'))

print(json.dumps({"c": 0, "b": 0, "a": 0}, sort_keys=True))

from io import StringIO
io = StringIO()
json.dump(['streaming API'], io)
io.getvalue()


# Pretty printing
print(json.dumps({'4': 5, '6': 7}, sort_keys=True, indent=4))


# Examplpe 1: load from hardcode
json_string = """
{
    "researcher": {
        "name": "Ford Prefect",
        "species": "Betelgeusian",
        "relatives": [
            {
                "name": "Zaphod Beeblebrox",
                "species": "Betelgeusian"
            }
        ]
    }
}
"""
data = json.loads(json_string)

print(json.dumps(data, sort_keys=True, indent=4))


# Examplpe 2: load from file
json_string = """
{
  "firstName": "John",
  "lastName": "Smith",
  "isAlive": true,
  "age": 27,
  "address": {
    "streetAddress": "21 2nd Street",
    "city": "New York",
    "state": "NY",
    "postalCode": "10021-3100"
  },
  "phoneNumbers": [
    {
      "type": "home",
      "number": "212 555-1234"
    },
    {
      "type": "office",
      "number": "646 555-4567"
    },
    {
      "type": "mobile",
      "number": "123 456-7890"
    }
  ],
  "children": [],
  "spouse": null
}

"""

with open("sample.json", "r") as read_file:
    data = json.load(read_file)

print(json.dumps(data, sort_keys=True, indent=4)) 
