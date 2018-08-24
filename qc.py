from optparse import OptionParser
import sys
import re
import os
import glob
import subprocess
import pandas
from Bio.PDB import PDBParser
import itertools
import json

# Test command:
# rm -rf PED1AAA/; cp ../pipe.py pipe.py; python3 pipe.py 1AAA PED1AAA 3 32 1 12 22
# rm -rf PED1AAA/; python3 pipe.py 1AAA PED1AAA 3 32 1 12 22


# Test command:
# python3 test.py -c config.json -w "/home/nicomic/Projects/Chemes/IDPfun/PED/testing" -l listaloca -n


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
            defaultOmitValues.extend(omitValues)

            if modifierDict[key] not in defaultOmitValues:
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
    "molprobity": 'Scripts/',
    "pdb": "./",
    "log": "qc.log"
}
settings = {
    "working_directory": os.getcwd(),
    "list_input": "",
    "molprobity": 'Scripts/',
    "pdb": "./",
    "log": "qc.log"
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

parser.add_option("-b", "--molprobin", action="store",
                  type="string", dest="molprobity", default='default',
                  help="path to where the molprobity are")

parser.add_option("-m", "--pdb", action="store",
                  type="string", dest="pdb", default='default',
                  help="path to the PDB files.")

parser.add_option("-g", "--log", action="store",
                  type="string", dest="log", default='default',
                  help="name of the log file")

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
    if options.config != "":
        prettyjson(configopts)
    prettyjson(settings)
    # https://stackoverflow.com/questions/19747371/python-exit-commands-why-so-many-and-when-should-each-be-used/19747562
    sys.exit()


# At this point, options have been parsed,
# and are available in the "settings" dictionary.


class InputError(Exception):
    # Custom exception class raised for errors in the input
    def __init__(self, message):
        self.message = message


def tar_rm(outfile, infiles):
        p = subprocess.run(
            "tar -cz --remove-files -f %s %s" % (outfile, infiles),
            shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return p


def sprun(command):
        subprocess.run(
            command, shell=True, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def qcall(args, wd, list=None):
    # Setup
    os.chdir(wd)
    if not settings['scripts'][0] == '/':
        # If the scripts directory path is not absolute, make it so.
        settings['scripts'] = '/'.join([wd, settings['scripts']])

    if not settings['log'][0] == '/':
        # If the log file path is not absolute, make it so.
        settings['log'] = '/'.join([wd, settings['log']])

    if list is "":
        print("Single entry:", args)
        pre(args, settings, wd)
        pdb(args, settings['scripts'], settings['working_directory'])

    else:
        with open(list) as f:
            for line in f:
                # Convert the CSV/TSV/... to the correct input format
                # args = re.sub(r'[,\t\s-]+', ' ', line).strip().split(' ')
                args = re.split(r'[,;\t\s-]+', line.strip())
                pre(args, settings, wd)
                pdb(args, settings['scripts'], settings['working_directory'])


def pre(args, settings, wd):
    try:
        # Setup
        os.chdir(wd)
        # Check if the input seems right
        pat = re.compile(r'^\w{4}\s\w{7}((\s[0-9]+)+)$')
        # Raise exception if input is bad
        arguments = ' '.join(args).strip()
        if not re.match(pat, arguments):
            raise InputError('\nInput arguments have an unexpected pattern\n')

        # Save parameters
        xxxx = args[0]
        pedxxxx = args[1]
        ensembles = args[2]
        conformers = args[3]
        indices = args[4:]

        print(xxxx)

        # Raise exception if input is bad
        if not indices.__len__() == int(ensembles):
            raise InputError('\nError in input arguments - \
                ensemble# is %s while %s indices were provided\n' % (ensembles,indices.__len__()))

        # Create directories
        subprocess.run(['mkdir', '-p', '%s/ensembles' % pedxxxx])
        subprocess.run(['mkdir', '-p', '%s/Crysol' % pedxxxx])
        subprocess.run(['mkdir', '-p', '%s/Pymol' % pedxxxx])
        subprocess.run(['mkdir', '-p', '%s/Rg' % pedxxxx])

        # Extract the PDB file to the entry directory if not already done
        if not os.path.exists("./%s/%s-all.pdb" % (pedxxxx, xxxx)):
            sprun('bzip2 -fckd %s/%s-all.pdb.bz2 > ./%s/%s-all.pdb' % (
                settings['pdb'], xxxx, pedxxxx, xxxx))

        # Check for UNK residures
        # The RES string begins at 18 and ends at 20
        #printf "\nScan for UNK residues\n" | tee -a $logName
        sprun("cat %s-all.pdb | awk '/^ATOM.+/ { print $0 \"LINE: \" NR }' | \
         awk '/^.{17}UNK.+/ { print \"Warning! UNK residue at ATOM \" $2 \", \
         line \" $NF \" of the PDB file.\"}' >> %s" % (xxxx, settings['log']))
        #tail $logName -n 5

        # Check for Q atoms (NMR dummies)
        # The element column may be useful for filtering
        # Make temporary PDB files w/o the dummy ones, to not mess up the originals
        # Perhaps checking the hydrogen naming version is being too picky
        #printf "\nScan for Q pseudoatoms\n" | tee -a $logName
        #cat ${xxxx}-all.pdb | awk '/^ATOM.+/ { print $0 "LINE: " NR }' | awk '/^.{17}Q[A-Z].+/ { print "Warning! Pseudoatom at line " $NF " of the PDB file."}' >> $logName
        #tail $logName -n 5
        # http://www.chem.uzh.ch/robinson/felixman/pseudoatom.html


        # Check for missing residues
        # Check for missing chain information
        # Select ATOM lines and append the line number from the PDB file
        # Select entries with whitespace where the chain should be found (position 22)
        #printf "\nScan for missing chain data\n" | tee -a $logName
        #cat ${xxxx}-all.pdb | awk '/^ATOM.+/ { print $0 "LINE: " NR }' | awk -v entryid="$xxxx" '/^.{21}(\ ).+/ { print "Warning! Missing chain information at ATOM " $2 ", line " $NF " of the "entryid" PDB file."}' >> $logName
        #tail $logName -n 5

        # Cleanup
        os.chdir(wd)

    except subprocess.CalledProcessError as e:
        print('Subprocess error:')
        print(e.stderr.decode('UTF-8'))
        raise

    except InputError as e:
        # I use the bare except because i do not know
        print("Unexpected error in stage pre-prcessing stage:", e.message)
        raise

qcall(args, wd=settings['working_directory'], list=settings['list_input'])
