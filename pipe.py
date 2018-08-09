from optparse import OptionParser
import re
import os
import subprocess

# Test command:
# rm -rf PED1AAA/; cp ../pipe.py pipe.py; python3 pipe.py 1AAA PED1AAA 3 20 1 5 15

usage = "usage: pedbPipe [-l <entry list>] XXXX PEDXXXX ensemble# conformer# ensemble1 ensemble2 ensemble3 ..."
parser = OptionParser(usage)

parser.add_option("-c", "--config", action="store",
                  type="string", dest="", default="pedbpipe.cfg",
                  help="load options from a configuration file.")

parser.add_option("-w", "--working_directory", action="store",
                  type="string", dest="", default="./",
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

try:
    # Check if the input seems right
    pat = re.compile(r'\w{4}\s\w{7}((\s[0-9]+)+)')
    arguments = ' '.join(args)

    if re.match(pat, arguments):
        print('Happy1')
    else:
        print('Unhappy')

    print(arguments)

    xxxx = args[0]
    pedxxxx = args[1]
    ensembles = args[2]
    conformers = args[3]
    indices = args[4:]

    if indices.__len__() == int(ensembles):
        print("Happy2")
    else:
        print('Unhappy')

    subprocess.run(['mkdir', '-p', './%s/ensembles' % pedxxxx])
    subprocess.run(['mkdir', '-p', './%s/Crysol' % pedxxxx])
    subprocess.run(['mkdir', '-p', './%s/Pymol' % pedxxxx])
    subprocess.run(['mkdir', '-p', './%s/Rg' % pedxxxx])

    if not os.path.exists("./%s/%s-all.pdb" % (pedxxxx, xxxx)):
        p = subprocess.run(
            'bzip2 -fckd %s%s-all.pdb.bz2 > ./%s/%s-all.pdb'
            % (options.pdb, xxxx, pedxxxx, xxxx),
            shell=True, check=True, capture_output=True)

except subprocess.CalledProcessError as e:
    print('Unhappy3')
    print(e.stderr.decode('UTF-8'))

except:
    # I use the bare except because i do not know
    print("Unexpected error in stage pre-prcessing stage")
    raise
