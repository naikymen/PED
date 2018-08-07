#!/bin/bash
xxxx=1AAA
pedxxxx=PED1AAA
all_scripts=/home/PED-DB3/Scripts/
saxs_path=/home/PED-DB3/SAXS-dat/
ref_saxs_path=$saxs_path

Rscript ${all_scripts}Pipe6-SAXS.R ${pedxxxx}-autorg.out ${xxxx}-saxs.dat ${ref_saxs_path} ${xxxx}-saxs.dat.SJ.datgnom.csv ${xxxx}
