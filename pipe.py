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

wd = os.getcwd()
parser.add_option("-w", "--working_directory", action="store",
                  type="string", dest="working_directory", default=wd,
                  help="set the working directory.")

parser.add_option("-l", "--list", action="store",
                  type="string", dest="input", default=None,
                  help="file from where to read several input entries.")

parser.add_option("-p", "--scripts", action="store",
                  type="string", dest="scripts", default="Scripts/",
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
    if not options.scripts[0] == '/':
        # If the scripts path is not absolute, make it so.
        options.scripts = '/'.join([wd, options.scripts])

    if list is None:
        print("Single entry:", args)
        pre(args)
        pdb(args, options.scripts, options.working_directory)

    else:
        with open(list) as f:
            for line in f:
                # Convert the CSV/TSV/... to the correct input format
                # args = re.sub(r'[,\t\s-]+', ' ', line).strip().split(' ')
                args = re.split(r'[,;\t\s-]+', line.strip())
                pre(args)


def pre(args):
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
        subprocess.run(['mkdir', '-p', './%s/ensembles' % pedxxxx])
        subprocess.run(['mkdir', '-p', './%s/Crysol' % pedxxxx])
        subprocess.run(['mkdir', '-p', './%s/Pymol' % pedxxxx])
        subprocess.run(['mkdir', '-p', './%s/Rg' % pedxxxx])

        # Extract the PDB file to the working directory if not already
        if not os.path.exists("./%s/%s-all.pdb" % (pedxxxx, xxxx)):
            sprun('bzip2 -fckd %s%s-all.pdb.bz2 > ./%s/%s-all.pdb' % (
                options.pdb, xxxx, pedxxxx, xxxx))

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

                # This range goes from the first and last conformer's position
                # in the PDB file, corresponding to the "current" ensemble.
                r2 = range(
                    ensemble_start_confromer,
                    ensemble_last_confromer, 1)
                for j in r2:
                    k = j - ensemble_start_confromer + 1
                    os.rename('%s-%s.pdb' % (pedxxxx, j),
                        '%s_%s-%s.pdb' % (pedxxxx, i, k))

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


def pdb(args, script_path, wd):
    try:
        # Setup
        os.chdir(wd)
        pedxxxx = args[1]

        # Crysol
        os.chdir('%s/ensembles' % pedxxxx)
        # subprocess.run(
        # "perl %s/Pipe1-batchCrysol-2018.pl" % script_path,
        # shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # re.match() is the same as putting a "^" at the start of the regex
        files = [f for f in os.listdir('.') if re.match(r'.*\.pdb$', f)]
        for f in files:
            subprocess.run(
                "crysol %s" % f,
                shell=True, check=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            log = "".join([f.strip(".pdb"), '00.log'])
            lofg = open(log)

            # "Envelope  diameter :  68.43    "
            e_dmax = re.compile(r'Envelope\s\sdiameter.*:.*((?:[0-9]|\.)+)\s*$')
            e_rg = re.compile(r'Rg.*Atoms.*:.?([\d.E\-\+]+)')


        # Cleanup Crysol output
        os.rename('rg.list', '../Rg/rg.list')
        os.rename('log.list', '../Crysol/log.list')
        tar_rm("../Crysol/%s.alm.tar.gz" % pedxxxx, "./*.alm")
        tar_rm("../Crysol/%s.int.tar.gz" % pedxxxx, "./*.int")
        tar_rm("../Crysol/%s.log.tar.gz" % pedxxxx, "./*.log")

        # Plots
        os.chdir('..')
        subprocess.run(
            "Rscript %s/Pipe245.R" % script_path,
            shell=True, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Cleanup
        tar_rm("%s/%s.-pdb.tar.gz" % pedxxxx, "%s/ensembles/*.pdb" % pedxxxx)
        os.chdir(wd)

    except subprocess.CalledProcessError as e:
        print('Subprocess error:')
        print(e.stderr.decode('UTF-8'))
        raise

    except InputError as e:
        # I use the bare except because i do not know
        print("Unexpected error in stage pre-prcessing stage:", e.message)
        raise


pedbcall(args, wd=options.working_directory, list=options.input)
