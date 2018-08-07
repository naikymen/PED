#!usr/bin/perl -w

use strict;

open(LOG, "lista_AvgMinMax");

while(<LOG>){
	chomp;
    {
    /(\w+)-(\d+)-(\w+)-(\d+)-(\d+)-(\d+)/;
	#PED1AAA-13-min-242-233-225

	open(OUT, ">$1-$3.pml");
	## 3° max
	#print OUT "$1 $2 $3 $4 $5 $6 \n";

	print OUT "from pymol.cgo import *\n";
	print OUT "from pymol import cmd\n";
	print OUT 'cmd.load("','./ensembles/',$1,'-',$2,'.pdb")',"\n";

	print OUT "set ray_trace_mode, 0;\n";
	print OUT "bg_color white;\n";
	print OUT "as car;\n";
	print OUT "orient;\n";
	print OUT "set transparency, 0.5;\n";
	print OUT "show surface;\n";

	print OUT "set_color $3 = [$4, $5, $6];\n";
	print OUT "color $3, $1-$2;\n";

	print OUT "ray 520,390;\n";
	print OUT "png $1-$3.png;\n";

	print OUT "save $1-$3.pse,format=pse;\n";

	print OUT "quit;\n";
	close(OUT);

	system("pymol $1-$3.pml");

	close(OUT);
	}
}

close(LOG);
exit;

