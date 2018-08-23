from optparse import OptionParser
import os
import sys
import json

# Test command:
# rm -rf PED1AAA/; cp ../pipe.py pipe.py; python3 pipe.py 1AAA PED1AAA 3 32 1 12 22


def prettyjson(diccionario):
    # Pretty print a dictionary as would a json output
    # https://docs.python.org/3/library/json.html
    jsonstring = json.dumps(diccionario)
    data = json.loads(jsonstring)
    print(json.dumps(data, sort_keys=True, indent=4))


# Start the option.parser and look for a configuration file
usage = "usage: pedbPipe [options] [-l <entry list>] \
XXXX PEDXXXX ensemble# conformer# ensemble1 ensemble2 ensemble3 ..."
parser = OptionParser(usage)
parser.add_option("-c", "--config", action="store",
                  type="string", dest="config", default="",
                  help="load options from a configuration file.")
(options, args) = parser.parse_args()


# Default Options
defaults = {
    "working_directory": os.getcwd(),
    "list_input": None,
    "scripts": 'Scripts/',
    "pdb": "./",
    "saxs": "./",
}
print('Defaults')
prettyjson(defaults)

# Config file options: PARSE AS DEFINED IN THE "Default Options" section above
if options.config != '':
    with open(options.config, "r") as read_file:
        data = json.load(read_file)
        for key in data.keys():
            try:
                defaults[key]
            except KeyError as ke:
                # https://docs.python.org/3/library/exceptions.html
                print("\nOption name '%s' in config file is not valid." % key)
                print("Available options are:")
                prettyjson(defaults)
                raise ke
            if data[key] != 'default':
                    defaults[key] = data[key]
print('Config')
prettyjson(defaults)


# Let everything be overwritten by command-line options
parser.add_option("-w", "--working_directory", action="store",
                  type="string", dest="working_directory", default=defaults["working_directory"],
                  help="set the working directory.")

parser.add_option("-l", "--list", action="store",
                  type="string", dest="input", default=defaults["list_input"],
                  help="file from where to read several input entries.")

parser.add_option("-p", "--scripts", action="store",
                  type="string", dest="scripts", default=defaults["scripts"],
                  help="path to where the perl and R scripts are")

parser.add_option("-m", "--pdb", action="store",
                  type="string", dest="pdb", default=defaults["pdb"],
                  help="path to the PDB files.")

parser.add_option("-s", "--saxs", action="store",
                  type="string", dest="saxs", default=defaults["saxs"],
                  help="path to the SAXS files.")

parser.add_option("-n", "--dry", action="store_true",
                  dest="dry", default=False,
                  help="print input and exit.")

(options, args) = parser.parse_args()

if options.dry is True:
    print(options)
    # https://stackoverflow.com/questions/19747371/python-exit-commands-why-so-many-and-when-should-each-be-used/19747562
    sys.exit()

print('Options')
# https://stackoverflow.com/questions/1753460/python-optparse-values-instance
prettyjson(vars(options))
