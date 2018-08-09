from optparse import OptionParser
import re
import os
import subprocess

# Test command:
# rm -rf PED1AAA/; cp ../pipe.py pipe.py; python3 pipe.py 1AAA PED1AAA 3 32 1 12 22

usage = "usage: pedbPipe [-l <entry list>] XXXX PEDXXXX ensemble# conformer# ensemble1 ensemble2 ensemble3 ..."
parser = OptionParser(usage)

parser.add_option("-c", "--config", action="store",
                  type="string", dest="config", default="pedbpipe.cfg",
                  help="load options from a configuration file.")

parser.add_option("-w", "--working_directory", action="store",
                  type="string", dest="working_directory", default="./",
                  help="set the working directory.")

parser.add_option("-l", "--list", action="store",
                  type="string", dest="input", default="",
                  help="file from where to read several input entries.")

parser.add_option("-p", "--scripts", action="store",
                  type="string", dest="scripts", default="./",
                  help="path to where the perl and R scripts are")

parser.add_option("-m", "--pdb", action="store",
                  type="string", dest="pdb", default="./",
                  help="path to the PDB files.")

parser.add_option("-s", "--saxs", action="store",
                  type="string", dest="saxs", default="./",
                  help="path to the SAXS files.")

parser.add_option("-n", "--dry", action="store_true",
                  dest="dry", default=False,
                  help="print input and exit.")

(options, args) = parser.parse_args()

# Save the 'root' working directory
if options.working_directory:
    working_directory = options.working_directory
else:
    working_directory = os.getcwd()

# Custom exception class raised for errors in the input
class InputError(Exception):
    def __init__(self, message):
        self.message = message

try:
    # Check if the input seems right
    pat = re.compile(r'^\w{4}\s\w{7}((\s[0-9]+)+)$')
    arguments = ' '.join(args)

    # Raise exception if input is bad
    if not re.match(pat, arguments):
        raise InputError('\nInput arguments do not match the expected pattern\n')

    xxxx = args[0]
    pedxxxx = args[1]
    ensembles = args[2]
    conformers = args[3]
    indices = args[4:]

    # Raise exception if input is bad
    if not indices.__len__() == int(ensembles):
        raise InputError('\nError in input arguments - \
            ensemble# is %s while %s indices were provided\n' % (ensembles,indices.__len__()))

    # Create directories
    subprocess.run(['mkdir', '-p', './%s/ensembles' % pedxxxx])
    subprocess.run(['mkdir', '-p', './%s/Crysol' % pedxxxx])
    subprocess.run(['mkdir', '-p', './%s/Pymol' % pedxxxx])
    subprocess.run(['mkdir', '-p', './%s/Rg' % pedxxxx])

    # Extract the PDB file to the working directory if it has not been done yet
    if not os.path.exists("./%s/%s-all.pdb" % (pedxxxx, xxxx)):
        p = subprocess.run(
            'bzip2 -fckd %s%s-all.pdb.bz2 > ./%s/%s-all.pdb'
            % (options.pdb, xxxx, pedxxxx, xxxx),
            shell=True, check=True, capture_output=True)

    # Split the PDB file into models using awk
    os.chdir('%s/ensembles' % pedxxxx)
    p = subprocess.run(
        "awk -v PEDXXXX=%s -v START=%s \
        'match($0,/^MODEL/,x){outputName=PEDXXXX\"-\"START\".pdb\"; ++START;} \
        {print >outputName;}' ../%s-all.pdb" % (pedxxxx, indices[0], xxxx),
        shell=True, check=True, capture_output=True)
    # Cleanup
    os.remove('../%s-all.pdb' % xxxx)

    if ensembles == 1:
        print('One ensemble in the entry')
        # This range goes from 1 to the amount of conformers
        # in the single ensemble (all of them)
        for i in range(int(indices[0]), int(conformers), 1):
            os.rename('%s-%s.pdb' % (pedxxxx, i), '%s_1-%s.pdb' % (pedxxxx, i))
    else:
        print('Multiple ensembles in the entry')
        # This range goes from 1 to the ensemble amount.
        r1 = range(1, int(ensembles) + 1, 1)
        for i in r1:
            ensemble_start_confromer = int(indices[i - 1])
            if not i == r1[-1]:
                ensemble_last_confromer = int(indices[i])
            else:
                ensemble_last_confromer = int(conformers) + 1

            print("Ensemble %s: %s %s" % (
                i, ensemble_start_confromer, ensemble_last_confromer - 1))

            # This range goes from the first and last conformer's position
            # in the PDB file, corresponding to the "current" ensemble.
            r2 = range(ensemble_start_confromer, ensemble_last_confromer, 1)
            for j in r2:
                k = j - ensemble_start_confromer + 1
                os.rename('%s-%s.pdb' % (pedxxxx, j),
                    '%s_%s-%s.pdb' % (pedxxxx, i, k))

except subprocess.CalledProcessError as e:
    print('Subprocess error:')
    print(e.stderr.decode('UTF-8'))
    raise

except InputError as e:
    # I use the bare except because i do not know
    print("Unexpected error in stage pre-prcessing stage:", e.message)
    raise
