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


def pedbcall(args, wd, list=None):
    # Setup
    os.chdir(wd)
    if not settings['scripts'][0] == '/':
        # If the scripts path is not absolute, make it so.
        settings['scripts'] = '/'.join([wd, settings['scripts']])

    if list is "":
        print("Single entry:", args)
        pre(args, settings)
        pdb(args, settings['scripts'], settings['working_directory'])
        # saxs(args, settings['scripts'], settings['working_directory'])

    else:
        with open(list) as f:
            for line in f:
                # Convert the CSV/TSV/... to the correct input format
                # args = re.sub(r'[,\t\s-]+', ' ', line).strip().split(' ')
                args = re.split(r'[,;\t\s-]+', line.strip())
                pre(args, settings)
                pdb(args, settings['scripts'], settings['working_directory'])
                # saxs(args, settings['scripts'], settings['working_directory'])


def pre(args, settings):
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

        # Extract the PDB file to the working directory if not already
        if not os.path.exists("./%s/%s-all.pdb" % (pedxxxx, xxxx)):
            sprun('bzip2 -fckd %s%s-all.pdb.bz2 > ./%s/%s-all.pdb' % (
                settings['pdb'], xxxx, pedxxxx, xxxx))

        # Split the PDB file into models using awk
        os.chdir('%s/ensembles' % pedxxxx)
        sprun("awk -v PEDXXXX=%s -v START=%s 'match($0,/^MODEL/,x)\
            {outputName=PEDXXXX\"-\"START\".pdb\"; ++START;} \
            {print >outputName;}' ../%s-all.pdb" % (pedxxxx, indices[0], xxxx))

        # Cleanup
        os.remove('../%s-all.pdb' % xxxx)

        if ensembles == 1:
            print('One ensemble in the entry')
            # This range goes from 1 to the amount of conformers
            # in the single ensemble (all of them)
            for i in range(int(indices[0]), int(conformers), 1):
                os.rename('%s-%s.pdb' % (pedxxxx, i),
                    '%s_1-%s.pdb' % (pedxxxx, i))
        else:
            print('Multiple ensembles in the entry')
            # This range goes from 1 to the ensemble amount.
            with open('pdb.list', 'w') as pdblist:
                pdblist.write(",".join(['file', 'ensemble', 'conformer' + '\n']))
                r1 = range(1, int(ensembles) + 1, 1)
                for i in r1:
                    ensemble_start_confromer = int(indices[i - 1])
                    if not i == r1[-1]:
                        ensemble_last_confromer = int(indices[i])
                    else:
                        ensemble_last_confromer = int(conformers) + 1

                    print("Ensemble %s: %s %s" % (
                        i,
                        ensemble_start_confromer,
                        ensemble_last_confromer - 1))

                    # Range r2 goes from the 1st and last conformer's position
                    # in the PDB file, corresponding to the "current" ensemble.
                    r2 = range(
                        ensemble_start_confromer,
                        ensemble_last_confromer, 1)
                    for j in r2:
                        k = j - ensemble_start_confromer + 1
                        os.rename('%s-%s.pdb' % (pedxxxx, j),
                            '%s_%s-%s.pdb' % (pedxxxx, i, k))
                        pdblist.write(",".join(
                            ['%s_%s-%s.pdb' % (pedxxxx, i, k), str(i), str(k) + '\n']))

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


def pdb(args, script_path, wd, pdb_list_file='pdb.list'):
    try:
        # Setup
        pedxxxx = args[1]
        os.chdir(wd)

        # Crysol
        # Replaced Pipe1.pl with this
        os.chdir('%s/ensembles' % pedxxxx)
        pdb_files_df = pandas.read_csv(pdb_list_file)
        pipe1_crysol(pdb_files_df, pedxxxx)
        os.chdir(wd)

        # N-to-N distance calculations
        for index, row in pdb_files.iterrows():
            n2nd = n2n(pedxxxx, row.file)
            with open(".".join(row.file, '.n2n'), 'w') as d:
                [d.write(str(value) + "\n") for value in n2nd]

        # Plots
        os.chdir(pedxxxx)
        # Warning, the pymol script's name is hardcoded as "Pipe5.1.pml"
        sprun("Rscript %s/Pipe245.R %s" % (script_path, script_path))
        os.chdir(wd)

        # Cleanup
        tar_rm("%s/%s.-pdb.tar.gz" % (pedxxxx, pedxxxx), "%s/ensembles/*.pdb" % pedxxxx)
        os.chdir(wd)

    except subprocess.CalledProcessError as e:
        print('Subprocess error:')
        print(e.stderr.decode('UTF-8'))
        raise

    except InputError as e:
        # I use the bare except because i do not know
        print("Unexpected error in stage pre-prcessing stage:", e.message)
        raise


def pipe1_crysol(pdb_files, pedxxxx):
    with open('../Rg/rg.list', 'w') as rg_list:
        # Write the header
        rg_list.write('\t'.join(
            ['PDB', 'Ensemble', 'Dmax', 'Rg']))

        for index, row in pdb_files.iterrows():
            sprun("crysol %s" % row.file)

            logfile = "".join([f.strip(".pdb"), '00.log'])

            with open(logfile) as log:
                # "Envelope  diameter :  68.43    "
                # https://regex101.com/r/uleo3Y/1
                dmax_p = re.compile(r'Envelope\s*diameter.*?:.*?((?:[\d.E\-\+])+)\s*')
                # "Rg ( Atoms - Excluded volume + Shell ) ................. : 21.35"
                rg_p = re.compile(r'Rg.*Atoms.*:.?([\d.E\-\+]+)')

                text = log.read()
                dmax_value = re.search(dmax_p, text).group(1)
                rg_value = re.search(rg_p, text).group(1)

                # Write saxs output
                rg_list.write('\n' + '\t'.join([row.file, row.ensemble, dmax_value, rg_value]))
        rg_list.write('\n')

    # Cleanup Crysol output
    # Tar and move the Crysol output, removing the original files
    tar_rm("../Crysol/%s.alm.tar.gz" % pedxxxx, "./*.alm")
    tar_rm("../Crysol/%s.int.tar.gz" % pedxxxx, "./*.int")
    tar_rm("../Crysol/%s.log.tar.gz" % pedxxxx, "./*.log")


def n2n(pedxxxx, pdb_file):
    # Code adapted as found in satckexchange
    # https://bioinformatics.stackexchange.com/questions/783/how-can-we-find-the-distance-between-all-residues-in-a-pdb-file

    # Create parser
    parser = PDBParser()

    # Read structure from file
    # The first argument is a user-given name for the structure
    structure = parser.get_structure(pedxxxx, pdb_file)

    model = structure[0]
    # Get the first chain (i guess there is a more direct way than this one)
    chain_id = [c.id[0] for c in model.get_chains()][0]
    chain = model[chain_id]

    # this example uses only the first residue of a single chain.
    # it is easy to extend this to multiple chains and residues.

    distances = []

    [distances.append(i[0]['CA'] - i[1]['CA']) for i in itertools.combinations(chain, 2)]

    return(distances)


def saxs(args, script_path, wd):
    # If there is a file such as "1AAA*saxs.dat*"
    if glob.glob("*" + args[0] + "*saxs.dat*"):
        try:
            # Setup
            os.chdir(wd)
            # Save parameters
            xxxx = args[0]
            pedxxxx = args[1]

            # Create directories
            subprocess.run(['mkdir', '-p', '%s/SAXS' % pedxxxx])

            # Extract the PDB file to the working directory if not already
            # If there is a file such as "1AAA*saxs.dat" try to decompress it
            if not glob.glob(args[0] + "-saxs.dat"):
                sprun('bzip2 -fckd %s-saxs.dat.bz2 > %s-saxs.dat' % xxxx)

            # Run autorg
            sprun('autorg %s-saxs.dat -f csv -o SAXS/%s-autorg.out' % xxxx)

            # Extract Rg from the autorg output
            autorg_out = pandas.read_csv('SAXS/%s-autorg.out' % xxxx)
            rg = autorg_out.Rg[0]

            # Run datgnom
            sprun('datgnom -r %s -o SAXS/%s-saxs.dat.datgnom SAXS/%s-saxs.dat' % (
                rg, xxxx, xxxx))

            # ...

        except subprocess.CalledProcessError as e:
            print('Subprocess error:')
            print(e.stderr.decode('UTF-8'))
            raise

        except InputError as e:
            # I use the bare except because i do not know
            print("Unexpected error in stage pre-prcessing stage:", e.message)
            raise


pedbcall(args, wd=settings['working_directory'], list=settings['list_input'])
