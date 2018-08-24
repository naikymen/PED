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


def updateDict(originalDict, modifierDict, defaultDict, omitKeys=[], omitValues=[], defaultOmitValues=['default']):
    # The original will be updated by the modified:
    # Only if the modified is different from the default.
    # Specific keys and values can be omitted from modification,
    # by using the omitKeys and omitValues parameters.
    for key in modifierDict.keys():
        if key in omitKeys:
            continue
        try:
            # Check if the keys in the modifier are present in the original
            # An exception will be raised if the option is "unrecognized"
            originalDict[key]

            # Update the original with the modified
            # except if if the values are in the omitions list.
            defaultOmitValues.append(omitValues)
            if modifierDict[key] not in omitValues:
                originalDict[key] = modifierDict[key]
        except KeyError as ke:
            # https://docs.python.org/3/library/exceptions.html
            print("\nERROR\nOption '%s' is not available." % key)
            print("\nAvailable options in original are:")
            print(originalDict.keys())
            print("\nAvailable options in default are:")
            print(defaultDict.keys())
            print("\nOptions in modifier are:")
            print(modifierDict.keys(), '\n')
            raise ke


# Default Options
defaults = {
    "working_directory": os.getcwd(),
    "list_input": "",
    "scripts": 'Scripts/',
    "pdb": "./",
    "saxs": "./",
}
settings = {
    "working_directory": os.getcwd(),
    "list_input": "",
    "scripts": 'Scripts/',
    "pdb": "./",
    "saxs": "./",
}



# Start the option.parser and look for a configuration file
usage = "usage: pedbPipe [options] [-l <entry list>] \
XXXX PEDXXXX ensemble# conformer# ensemble1 ensemble2 ensemble3 ..."
parser = OptionParser(usage)

parser.add_option("-c", "--config", action="store",
                  type="string", dest="config", default="",
                  help="load options from a configuration file.")

parser.add_option("-w", "--working_directory", action="store",
                  type="string", dest="working_directory", default='default',
                  help="set the working directory.")

parser.add_option("-l", "--list", action="store",
                  type="string", dest="list_input", default='default',
                  help="file from where to read several input entries.")

parser.add_option("-p", "--scripts", action="store",
                  type="string", dest="scripts", default='default',
                  help="path to where the perl and R scripts are")

parser.add_option("-m", "--pdb", action="store",
                  type="string", dest="pdb", default='default',
                  help="path to the PDB files.")

parser.add_option("-s", "--saxs", action="store",
                  type="string", dest="saxs", default='default',
                  help="path to the SAXS files.")

parser.add_option("-n", "--dry", action="store_true",
                  dest="dry", default=False,
                  help="print input and exit.")
(options, args) = parser.parse_args()

# Config file options
if options.config != "":
    with open(options.config, "r") as read_file:
        configopts = json.load(read_file)  # It is dict type
        # Update the configuration
        updateDict(settings, configopts, defaults)
else:
    print("No configuration file was CLI-specified")
    print("With no default, only default and CLI options are used.")

# Let everything be overwritten by non-default CLI options
# https://stackoverflow.com/questions/1753460/python-optparse-values-instance

cliopts = vars(options)
updateDict(settings, cliopts, defaults, omitKeys=['config', 'dry'])

if options.dry is True:
    print("Dry run, printing options and exiting:")
    prettyjson(defaults)
    prettyjson(cliopts)
    prettyjson(configopts)
    prettyjson(settings)
    # https://stackoverflow.com/questions/19747371/python-exit-commands-why-so-many-and-when-should-each-be-used/19747562
    sys.exit()
