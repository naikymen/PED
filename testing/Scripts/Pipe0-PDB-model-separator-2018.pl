#!usr/bin/perl -w

use strict;

open(LIST1, "NUM-model");
chomp(my $modelNumber = <LIST1>);

open(LIST2, "ID-model");
chomp(my $pedbID = <LIST2>);

open(FILE, shift(@ARGV));

while(<FILE>){
  chomp;
  if($_ =~ /^MODEL/){
#    $modelNumber++;
    open(OUT, ">$pedbID-".$modelNumber.".pdb");
      print OUT "$_\n";
    } elsif($_ =~ /^ENDMDL/){
      $modelNumber++;
      print OUT "$_\n";
      close(OUT);
    } elsif($_ !~ /^$/) {
      print OUT "$_\n";
    }
}

# Separa 1 archivo de PDB con varios modelos
# en un archivo con cada modelo

#1) Se fija si dice MODEL
#	Abre el archivo a escribir con el ID+el numero de modelo
#2) Si en la linea esta el ENDMDL
#	Imprime la linea y genera un salto de linea
#	Cierra el archivo
#3) Si no es igual a ninguna opcion, es decir tiene los datos del pdb
#	Imprime la linea

