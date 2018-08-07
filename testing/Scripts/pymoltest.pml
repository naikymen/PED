from pymol.cgo import *
from pymol import cmd
from sys import argv

# Syntax highlighting for PyMol in Sublime Text :V
# https://packagecontrol.io/packages/Pymol%20Language

# Argument parsing
# https://pymolwiki.org/index.php/Scripting_FAQs

arguments = argv[1:]
pdbFile = arguments[0]

#"pymol -qrc ../Scripts/Pipe5.1.pml -- PED1AAB_1-2 PED1AAB 1 average 203 232 107"

cmd.load("./ensembles/%s.pdb" % pdbFile)