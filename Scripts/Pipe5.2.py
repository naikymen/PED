# A python 2 script for controlling PyMol

import __main__
__main__.pymol_argv = ['pymol', '-qc'] # Pymol: quiet and no GUI
from time import sleep
import pymol
from pymol.cgo import *
from pymol import cmd
from sys import argv

# https://pymolwiki.org/index.php/Python_Integration
pymol.finish_launching()

myargs = open('Pymol/pymolArguments')
for a in myargs:
    arguments = a.split()
    pymol.cmd.reinitialize()
    print arguments


    # "pymol -qrc ../Scripts/Pipe5.1.pml -- PED1AAB_1-2 PED1AAB 1 average 203 232 107"
    pdbFile = arguments[0];
    entryName = arguments[1];
    ensembleNumber = arguments[2];
    colorName = arguments[3];
    color1 = int(arguments[4]);
    color2 = int(arguments[5]);
    color3 = int(arguments[6]);

    cmd.load("./ensembles/%s.pdb" % pdbFile)
    cmd.set('ray_trace_mode', 0)
    cmd.bg_color('white');
    cmd.show_as('car');
    cmd.orient();
    cmd.set('transparency', 0.5);
    cmd.show('surface');
    #set_color colorName, [color1, color2, color3];
    cmd.set_color(colorName, [color1, color2, color3]);

    #color colorName, pdbFile;
    cmd.color( colorName, pdbFile )

    cmd.ray(520, 390);

    outputName = "Pymol/%s-%s-%s" % (entryName, ensembleNumber, colorName);
    cmd.png(outputName);
    cmd.save(outputName + ".pse", format='pse');

    quit;

    sleep(0.5) # (in seconds)
