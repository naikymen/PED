#!/bin/bash

# A simple test: bash pedbPipe.sh 1AAB PED1AAB 2 5 1 3

# A docker test, so far seems OK
# Paths must be set appropiately by using the script options (see help with -h).
  # docker run -it --rm -v ~/Projects/Chemes/IDPfun/PED-DB3/:/home/PED-DB3/ --volume="$HOME/.Xauthority:/root/.Xauthority:rw" --env="DISPLAY" --net=host  ubuntu:molprob /bin/bash
  # cd /home/PED-DB3/
  # bash pedbPipe3.sh -p /home/PED-DB3/Scripts/ -m /home/PED-DB3/PDB-all-models/ -s /home/PED-DB3/SAXS-dat/ -l list-entry-one

# Initialize our own variables by sourcing from a default configuration file in the working directory
# It can be overwritten by using command line options.
# Individual values can also be overwritten by using the other command-line options.
  # Eventually the server administrator should put whatever is appropiate herein.
. pedbpipe3.cfg

# ?
entry_amount=1

# Extension for the log files
leeme=".log"

# Parse options with getopts
# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Parse command-line options
while getopts "h?c:w:l:p:m:s:" opt; do
    case "$opt" in
    h|\?)
        printf "usage: pedbPipe [-l <entry list>] XXXX PEDXXXX ensemble_# ensemble1 ensemble2 ensemble3 ...
        
        -h  Show this help and exit.

        -c  Load options from a configuration file.
        
        -p  Path to the directory where the perl and R scripts are.
        -m  Path where the PDB model files are (with trailing '/', e.g. '-p ~/somewhere/pdb-models/')
        -s  Path to the SAXS data, where it will look for files named '1AAA-saxs.dat.bz2' and such (with trailing '/', e.g. '')
            
            NOTE: all path should include the trailing '/', e.g. '-p ~/somewhere/scripts/ -p ~/somewhere/scripts/ -s /somewhere_else/SAXS-dat/' ...)

        The script requires the following input:
          1)  Entry information (ID and the indexes of each ensemble [subset of models] within the PDB file)
              Provided as a list of entries ina  file, or as arguements for a single entry only.
          2)  A PDB file with all of the models
          3)  An OPTIONAL sax.dat file

        -l  Input a list of entries from a list file (see csv format below, will ignore other arguments)

        The list input should have a header. The entries should look like:
        XXXX,PEDXXXX,ensemble_amount,model_amount,model1Start,model2Start,model3Start[, ...]
         'XXXX' is the PED entry ID
         'ensemble_amount' is the total number of ensembles in the entry
         'model_amount' is the total number of pdb models in the entry

        They may be separated by a comma, tab, space or hyphen. They are parsed by the following regex:
          \w{4}[,\t\s-]\w{7}(([,\t\s-][0-9]+)+)
        These symbols are later replaced by a space in the awk command.
        So please do not include any of these in the data (e.g. 'PED-ABCD' is NOT adequate input).

        Please incude a final newline in the list file, this is necessary!
        The script will attempt to include one if it is not there, by editing the list.

        Log files will appear inside the entry folder for single entries.
        An additional logfile will appear for list entries at the working directory.
        "
        exit 0
        ;;
    c)  config_file=$OPTARG
        . "$config_file"
    ;;
    w)  working_directory=$OPTARG
        cd "$working_directory"
    ;;
    l)  input_file=$OPTARG
        printf "List mode ON!"
        # Add a final newline if it is not there
        sed -i -e '$a\' $input_file
        
        # Count lines ignoring empy ones
        entry_amount=`cat $input_file | grep -c .`
        
        if [ $entry_amount == 0 ]; then
          printf "Your list file seems to be empty.\nPlease check!\n"
          exit 1
        fi
        ;;
    p)  all_scripts=$OPTARG
    ;;
    m)  pdbs_path=$OPTARG
    ;;
    s)  saxs_path=$OPTARG
        ref_saxs_path=$saxs_path
    ;;
    esac
done

# I am not too sure what this does, but apparently it permits accessing the non-option arguments nicely.
shift $((OPTIND-1))
[ "${1:-}" = "--" ] && shift


# Two functions are defined here: saxs() and pedb()
# pedb() is called at the end of the script, and performs all non-SAXS processing.
# saxs() is called at the end of pedb() and will process everything related to SAXS, if the data is available.

printf "
\nYour input arguments:
  $input_file
  $all_scripts
  $pdbs_path
  $saxs_path
  $ref_saxs_path\n"



function saxs {

  xxxx=$1
  pedxxxx=$2

  if [ -f ${saxs_path}${xxxx}-saxs.dat.bz2 ]; then

    printf "SAXS data found for entry ${xxxx}, processing...\n" | tee -a $logName

    mkdir -p SAXS-${pedxxxx}
    cd SAXS-${pedxxxx}

    # Calculate Rg from the SAXS data
    ## There seem to be different formatting for SAXS data (why oh why!?)
      ## The following regex matches lines with a tolerant number-like format
      ## i.e. only lines with three numbers in some numerical notation ([0-9]|\.|-|\+|e|E) and with some separator ([\ \t]).
      ## I have considered space or tab as separators, not commas. Modify the regex to your needs
      ## If the line contains any other thing except the three numbers, it is not considered.
      ## i.e. the pattern is all there is between the start (^) and end ($) of the line.
    bzip2 -fckd ${saxs_path}${xxxx}-saxs.dat.bz2 | awk '/^[\ \t]*(([0-9]|\.|-|\+|e|E)+)[\ \t]+(([0-9]|\.|-|\+|e|E)+)[\ \t]+(([0-9]|\.|-|\+|e|E)+)[\ \t\r]$/{print}' > ${xxxx}-saxs.dat
    printf "\nRunning autorg"
    autorg ${xxxx}-saxs.dat -f csv -o ${pedxxxx}-autorg.out
    

    # GNOM plots with R
      # Match /-saxs.dat/ to exclude the header from the autorg.out
      # the "-F ','" option is for reading CSV files
    rg=`cat ${pedxxxx}-autorg.out | awk -F ',' '/.dat/{print $2}'`
    
    printf "\nRunning datgnom"
    datgnom -r $rg -o ${xxxx}-saxs.dat.datgnom ${xxxx}-saxs.dat > /dev/null

    # Extract data from the datgnom output file
      ## Read lines after the header, including it, with: /R.+P\(R\).+ERROR/
      ## Empty lines and lines ensuing /####/ are filtered out (including the line which contains the pattern).
    cat ${xxxx}-saxs.dat.datgnom | awk '/####/{show=0} /^\ *$/{next} /R.+P\(R\).+ERROR/{show=1} show;' > ${xxxx}-saxs.dat.rPr.datgnom    
      ## Read lines after the header, including it, with: /S[\ \t]+J[\ \t]+EXP[\ \t]+ERROR[\ \t]+J[\ \t]+REG.+I.+REG/
      ## Empty lines and lines ensuing /####/ (including that line) are filtered out.
    cat ${xxxx}-saxs.dat.datgnom | awk '/####/{show=0} /^\ *$/{next} /S[\ \t]+J[\ \t]+EXP[\ \t]+ERROR[\ \t]+J[\ \t]+REG.+I.+REG/{show=1; next;} show;' > ${xxxx}-saxs.dat.SJ.datgnom  # Without header
    #cat ${xxxx}-saxs.dat.datgnom | awk '/####/{show=0} /^\ *$/{next} /S[\ \t]+J[\ \t]+EXP[\ \t]+ERROR[\ \t]+J[\ \t]+REG.+I.+REG/{show=1;} show;' > ${xxxx}-saxs.dat.SJ.datgnom  # With header
    
    # The scattering data requires further processing to be read by R's fread().
      # AWK does not handle missing values, which are present in at least the 1AAA SAXS datgnom file
      # In a fixed with file, such as the output from datgnom, the width information can be used to tolerate missing values
        ## To find the widths using the 50th line as reference, or any complete one for this matter.
        #sed -n '50,50p;50q' < 1AAA-saxs.dat.SJ.datgnom | grep -Po '.*? (?=\S|$)' | awk '{print length}'  ## Outputs 3,15,15,15,15  
      # Reference: https://www.embl-hamburg.de/biosaxs/manuals/gnom.html#runtime
    cat ${xxxx}-saxs.dat.SJ.datgnom | awk -v OFS=',' 'BEGIN {FIELDWIDTHS = "3 15 15 15 15 15"} {print $2,$3,$4,$5,$6}' | tr -d ' ' > ${xxxx}-saxs.dat.SJ.datgnom.csv

    # Make and save all plots as PNG images
      # Guinier and Normalized Kratky Plots, rPr and Scattering
    printf "\nRunning Pipe6.R - making plots"
    Rscript ${all_scripts}Pipe6-SAXS.R ${pedxxxx}-autorg.out ${xxxx}-saxs.dat ${ref_saxs_path} ${xxxx}-saxs.dat.SJ.datgnom.csv ${xxxx} > /dev/null
      # It reads the following arguments:
        # PEDXXXX-autorg.out XXXX-saxs.dat /path/to/reference/saxs/ XXXX-saxs.dat.SJ.datgnom.csv XXXX
    cd ..
    printf "Done! Find the output files in the SAXS folder for the entry (SAXS-${pedxxxx}).\n" | tee -a $logName

  else
    printf "No SAXS data found for entry ${xxxx}.\n" | tee -a $logName
  fi
}








function pedb {

  # Get the log file
  logName=$1
  # Shift the arguments to remove the one we just read
  shift 1

  printf "\nExecution started, checking arguments...\n" | tee -a $logName

  # Scan so see if the input arguments look OK

  apat="\w{4}\s\w{7}((\s[0-9]+)+)"
  asd="$@"

  if [[ $asd =~ $apat ]]; then
    printf "Input arguments are cool!\n" | tee -a $logName
  else
    printf "ERROR: Input arguments are not cool!\n$@\n" | tee -a $logName
    exit 1
  fi

  xxxx=$1
  pedxxxx=$2
  ensemble=$3
  #first=$4
  first=1
  last=$4
  ensemble_starts=${@:5}  # All arguments after the fourth should be start positions for ensembles
  start_positions_amount=$(( $# - 4 ))

  printf "Your input was: \nXXXX: $xxxx \nPEDXXXX: $pedxxxx \nSpecified ensemble amount: $ensemble \nStart positions provided: $ensemble_starts \nAmount of start positions provided: $start_positions_amount \nSpecified conformer amount: $last \n" | tee -a $logName

  if [ $start_positions_amount !=  $ensemble ]
  then
    printf "ERROR: the specified ensemble amount int he input does not match the provided amount of start positions!\n" | tee -a $logName
    exit 1
  fi
  
  # Make folders for the entry
  mkdir -p ./${pedxxxx}/ensembles
  mkdir -p ./${pedxxxx}/Crysol
  mkdir -p ./${pedxxxx}/PymolScript
  mkdir -p ./${pedxxxx}/Rg
  #mkdir -p ./${pedxxxx}/UploadStuff  # Acá irian los SQL de Rg/Dmax Mean/SD para cada ensemble
  #mkdir -p ./${pedxxxx}/PipeScriptR
  
  # Setup and run Pipe0 to split the PDB file
  cd ./${pedxxxx}/ensembles  # move to the ensembles directory (two levels down)
  # The following files will be read by the first Perl script.
  printf ${pedxxxx} > ID-model
  printf ${first} > NUM-model
  
  if [ ! -f ../${xxxx}-all.pdb ]; then
    bzip2 -fckd ${pdbs_path}${xxxx}-all.pdb.bz2 > ../${xxxx}-all.pdb
  fi
  
  perl ${all_scripts}Pipe0-PDB-model-separator-2018.pl ../${xxxx}-all.pdb
  bzip2 -c ../${xxxx}-all.pdb > ../${xxxx}-all.pdb.bz2
  rm ../${xxxx}-all.pdb
  
  # Rename the individual PDB files to explicitly show the ensemble number to which they belong
  if [ "$ensemble" == "1" ]
    
    then
      printf "\nOnly one ensemble for this entry was specified.\nRenaming PDB files\n" | tee -a $logName

      for n in `seq ${first} 1 ${last}`
        do
          mv ${pedxxxx}-${n}.pdb ${pedxxxx}_1-${n}.pdb
        done

    else
      printf "\nMore than one ensemble for this entry was specified.\nRenaming PDB files\n" | tee -a $logName

      i=1
      while [ $i -lt $ensemble ]  # while it is not the last ensemble
        do
          current=$((i + 4))  # get the current ensemble's pdb start position argument position
          next=$((i + 5))  # get the next ensemble's pdb start position argument position
          currentPos=${!current}
          lastPos=$(( ${!next} - 1))
          printf "\nEnsemble $i: $currentPos $lastPos\n" | tee -a $logName
          

          for x in `seq ${currentPos} 1 ${lastPos}`
            do
              j=$((x-currentPos+1))
              mv ${pedxxxx}-${x}.pdb ${pedxxxx}_${i}-${j}.pdb
            done

          i=$((i+1))
      done
      current=$((i + 4))  # get the current ensemble's pdb start position argument position
      currentPos=${!current}
      lastPos=$last
      printf "\nEnsemble $i: $currentPos $lastPos\n" | tee -a $logName
      for x in `seq ${currentPos} 1 ${lastPos}`
        do
          j=$((x-currentPos+1))
          mv ${pedxxxx}-${x}.pdb ${pedxxxx}_${i}-${j}.pdb
        done
  fi

  # Run Pipe1
  printf "\nRunning Pipe 1 - Crysol...\n"
  perl ${all_scripts}Pipe1-batchCrysol-2018.pl > /dev/null
  printf "Pipe 1 done.\n"

  mv pdb.list ../
  mv rg.list ../

  # Cleanup Crysol output
  mv log.list ../Crysol/
  tar -cz --remove-files -f ../Crysol/${pedxxxx}.alm.tar.gz ./*.alm
  tar -cz --remove-files -f ../Crysol/${pedxxxx}.int.tar.gz ./*.int
  tar -cz --remove-files -f ../Crysol/${pedxxxx}.log.tar.gz ./*.log

  # Run Pipe2, Pipe4, Pipe5 (condensed version)
  cd ..  # move tho the entry folder, e.g. "PED1AAB" (i.e. one level above)
  printf "\nRunning Pipe245 - Plots and PyMol figures...\n"
  Rscript ${all_scripts}Pipe2.1.r > /dev/null
  printf "Pipe245 done.\n"

  # Pipe3
    # Este lo unico que hace es generar SQL, y ponerlo en un "uploadStuff"
    # No lo necesitamos más

  # Process SAXS data
  printf "\nRunning Pipe6 - SAXS data plots...\n"
  saxs $xxxx $pedxxxx
  printf "Pipe6 done.\n"

  #To-do:
    # Limpieza para que no queden archivos zombie

  # Tar all of the .pdb files, and remove the original files
  tar -cz --remove-files -f./ensembles/${pedxxxx}-pdb.tar.gz ./ensembles/*.pdb

  cd .. # move back to the main working directory
}









# Choose operating mode according to the input:
  # Either a single entry or multiple entries in a CSV file (TSV, hyphens, spaces are also supported).
if [ "$input_file" = '' ]; then


  # Check if the input seems right
  pat="\w{4}\s\w{7}((\s[0-9]+)+)"
  a="$@"

  if [[ $a =~ $pat ]]; then
    printf "\nInput arguments are cool!\nYour input: $@\n"
  else
    printf "\nERROR: Input arguments are not cool!\nYour input: $@\n"
    exit 1
  fi

  # Setup logs
  logEntry=`printf $@ | sed -E 's/\w{4}\s(\w{7})((\s[0-9]+)+)/\1/'`
  mkdir -p $logEntry
  logName=$logPath/$logEntry/$logEntry$leeme

  printf "Your input was a single entry.\nNow processing entry: $@ \n" | tee $logName
  
  pedb $logName $@

  printf "Run succesfully!\n" | tee -a $logName
  exit 0

else

  logNameList="${logPath}/${input_file}${leeme}"

  printf "\nYour input was a list with $entry_amount lines.\nList file: '$input_file'\nUnparsed arguments: $@\nLog files can be found within each entry folder.\n" | tee $logNameList
  
  pat="\w{4}[,\t\s-]\w{7}(([,\t\s-][0-9]+)+)"
  #pat="\w{4},\w{7}((,[0-9]+)+)"  # Parse only CSV format
  
  while read line; do
    printf "\nNow parsing list entry $line...\n" | tee -a $logNameList

    if [[ $line =~ $pat ]]; then
      # Read the line of the list file as arguments, separating them as needed.
      argumentos=`printf $line | sed -E "s/[,\t\s-]+/\ /g"`
      
      # Setup logs
      logEntry=`printf "$argumentos" | sed -E 's/\w{4}\s(\w{7})((\s[0-9]+)+)/\1/'`
      mkdir -p $logEntry
      logName="${logPath}/${logEntry}/${logEntry}${leeme}"
      
      printf "\nNow processing entry $argumentos of the list...\n" | tee $logName

      # Let the magic happen:
      pedb $logName $argumentos

      printf "\nAll items done for entry $logEntry.\n" | tee -a $logName
    else
      printf "\n ERROR the line does not match the input pattern.\n"
      printf "Pattern: $pat \n"
      printf "Pattern: $line \n"
      printf "Exiting... \n"
      exit 1
    fi
  done < $input_file

  printf "Execution succesfull!\n" | tee -a $logNameList
  exit 0
fi
