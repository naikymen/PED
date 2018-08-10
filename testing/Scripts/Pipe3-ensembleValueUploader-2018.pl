#!usr/bin/perl -w

use strict;

open(LIST, 'rg.uploader');
open(PHP, ">uploadStuff");

while(<LIST>){
  chomp;
  unless(/^PDB\s+/){
    /\w+-(\d+).pdb\s+(\d+.*\d*)\s+(\d+.*\d*)\s+(\d+)/;
    print PHP "INSERT INTO EnsembleStructure (EnsembleStructureEnsembleID, EnsembleStructureNumber, EnsembleStructureRg, EnsembleStructureDmax)";
#    if($1 < 200){print PHP "VALUES ('$4', '$1', '$3', '$2');\n";}
    {print PHP "VALUES ('$4', '$1', '$3', '$2');\n";}
  }
}


## escribe en un archivo PHP, data para identificar y Rg y Dmax
