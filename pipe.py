from optparse import OptionParser
import re

usage = "usage: pedbPipe [-l <entry list>] XXXX PEDXXXX ensemble_# ensemble1 ensemble2 ensemble3 ..."
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

if args.input == "":
    # Check if the input seems right
    pat = re.compile(r'\w{4}\s\w{7}((\s[0-9]+)+)')
