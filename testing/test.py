from optparse import OptionParser
import os
import sys
import json

# Test command:
# rm -rf PED1AAA/; cp ../pipe.py pipe.py; python3 pipe.py 1AAA PED1AAA 3 32 1 12 22


# Start the option.parser and look for a configuration file
usage = "usage: pedbPipe [-l <entry list>] XXXX PEDXXXX ensemble# conformer# ensemble1 ensemble2 ensemble3 ..."
parser = OptionParser(usage)

parser.add_option("-c", "--config", action="store",
                  type="string", dest="config", default="",
                  help="load options from a configuration file.")

(options, args) = parser.parse_args()
print('Hay un config file?')
print(options)


# Load default variables
wd = os.getcwd()
list_input = None
scripts = 'Scripts/'
pdb = "./"
saxs = "./"
dry = False

print('Opciones dafault')
print(wd, list_input, scripts, pdb, saxs, dry)


# Let default options be overriden if a config file is provided


def assign(jsondata, fieldname, default):
    try:
        if jsondata.get(fieldname) != 'default':
            return(jsondata.get(fieldname))
        else:
            return(default)
    except Exception as e:
        print(e)
        pass


if options.config != '':
    with open(options.config, "r") as read_file:
        data = json.load(read_file)
        # Parse
        wd = assign(data, 'working_directory', wd)
        list_input = assign(data, 'input', list_input)
        scripts = assign(data, 'scripts', scripts)
        pdb = assign(data, 'pdb', pdb)
        saxs = assign(data, 'saxs', saxs)
        dry = assign(data, 'dry', dry)


print('Opciones del config')
print(wd, list_input, scripts, pdb, saxs, dry)



# Let everything be overwritten by command-line options
parser.add_option("-w", "--working_directory", action="store",
                  type="string", dest="working_directory", default=wd,
                  help="set the working directory.")

parser.add_option("-l", "--list", action="store",
                  type="string", dest="input", default=list_input,
                  help="file from where to read several input entries.")

parser.add_option("-p", "--scripts", action="store",
                  type="string", dest="scripts", default=scripts,
                  help="path to where the perl and R scripts are")

parser.add_option("-m", "--pdb", action="store",
                  type="string", dest="pdb", default=pdb,
                  help="path to the PDB files.")

parser.add_option("-s", "--saxs", action="store",
                  type="string", dest="saxs", default=saxs,
                  help="path to the SAXS files.")

parser.add_option("-n", "--dry", action="store_true",
                  dest="dry", default=dry,
                  help="print input and exit.")

(options, args) = parser.parse_args()

if dry is True:
    print(options)
    sys.exit()
