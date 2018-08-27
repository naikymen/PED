from pymol.cgo import *
from pymol import cmd
from sys import argv

# Syntax highlighting for PyMol in Sublime Text :V
# https://packagecontrol.io/packages/Pymol%20Language

# Argument parsing
# https://pymolwiki.org/index.php/Scripting_FAQs

arguments = argv[1:];
# "pymol -qrc ../Scripts/Pipe5.1.pml -- PED1AAB_1-2 PED1AAB 1 average 203 232 107"
pdbFile = arguments[0];
entryName = arguments[1];
ensembleNumber = arguments[2];
colorName = arguments[3];
color1 = int(arguments[4]);
color2 = int(arguments[5]);
color3 = int(arguments[6]);

cmd.load("./ensembles/%s.pdb" % pdbFile)
set ray_trace_mode, 0;
bg_color white;
as car;
orient;
set transparency, 0.5;
show surface;
#set_color colorName, [color1, color2, color3];
cmd.set_color(colorName, [color1, color2, color3]);

#color colorName, pdbFile;
cmd.color( colorName, pdbFile )

ray 520,390;

outputName = "Pymol/%s-%s-%s" % (entryName, ensembleNumber, colorName);
cmd.png(outputName);
cmd.save(outputName + ".pse", format='pse');

quit;