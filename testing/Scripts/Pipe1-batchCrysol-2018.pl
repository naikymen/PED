#!usr/bin/perl -w

use strict;

system("ls *.pdb |sort -nk 2 -t'-' > pdb.list");					#Necesita tener los pdbs en un directorio, los lista
											#y genera la lista que va a usar
open(LIST, "pdb.list");									#Abre la lista

while(<LIST>){										#Mientras la lista no sea linea vacia
  chomp;										#define la linea como variable default : $_
  system("crysol $_");									#CRYSOL es un programa a descargar, genera los .log
}

system("ls *.log |sort -nk 2 -t'-' > log.list");					#Arma la lista de los .log

open(LOG, "log.list");
open(OUT, ">rg.list");

print OUT "PDB\tDmax\tRg\n";								#Escribe primera linea en rg.list

while(<LOG>){
  chomp;										#Define el nombre como $_
  open(FILE, "$_");
  while(<FILE>){									#Empieza a escribir, pero no se bien que...jajaja
    if($_ =~ m/(PDB file name)/){
      $_ =~ m/(\w+-\w+.pdb)/;
      print OUT ($1);
    } elsif($_ =~ m/Envelope\s+diameter\s+:\s+(\d+.\d+)/){
      print OUT "\t$1";
    } elsif($_ =~ m/Rg\s+\(\s+Atoms\s+-\s+Excluded\s+volume\s+\+\s+Shell\s+\)/){
      $_ =~ m/(\d+.\d+)/;
      print OUT "\t${1}\n";
    }
  }
  close(FILE);
}

close(LOG);										
exit;											#Genera el rg.list para luego ordenarlo en Pipe3-sortRg.pl
