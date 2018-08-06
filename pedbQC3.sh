#!/bin/bash

# A simple test: bash pedbQC.sh 1AAB PED1AAB 2 5 1 3

# A docker test, so far seems OK
# Paths must be set appropiately by using the script options (see help with -h).
  # docker run -it --rm -v ~/Projects/Chemes/IDPfun/PED-DB3/:/home/PED-DB3/ --volume="$HOME/.Xauthority:/root/.Xauthority:rw" --env="DISPLAY" --net=host  ubuntu:molprob /bin/bash
  # cd /home/PED-DB3/
  # bash pedbQC3.sh -p /home/PED-DB3/Scripts/ -m /home/PED-DB3/PDB-all-models/ 1AAB PED1AAB 2 5 1 3

# Initialize our own variables:
# These can be overwritten by using command-line options.
  # Eventually the server administrator should put whatever is appropiate herein.
input_file=""
entry_amount=1
all_scripts=~/Projects/Chemes/IDPfun/PED-DB2/Scripts/
pdbs_path=~/Projects/Chemes/IDPfun/PED-DB2/PDB-all-models/
logPath=`pwd`
leeme=".QC.log"
molprobity_binaries='/home/MolProbity/build/bin/'

# Parse options
# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Parse command-line options
while getopts "h?l:p:m:b:" opt; do
    case "$opt" in
    h|\?)
        echo "usage: pedbPipe [-l <entry list>] XXXX PEDXXXX ensemble_# ensemble1 ensemble2 ensemble3 ...
        -l input a list of entries from a list file (see csv format below, will ignore other arguments)
        -h show this help
        -p path for the perl scripts (with trailing '/', e.g. '-p ~/somewhere/scripts/')
        -m path where the PDB model files are (with trailing '/', e.g. '-p ~/somewhere/pdb-models/')
        -b path to the molprobity binaries:
            molprobity.cablam
            molprobity.cbetadev
            molprobity.clashscore
            molprobity.molprobity
            molprobity.omegalyze
            molprobity.probe
            molprobity.ramalyze
            molprobity.reduce
            molprobity.rotalyze
            molprobity.suitename

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
    l)  input_file=$OPTARG
        
        # Add a final newline if it is not there
        sed -i -e '$a\' $input_file
        
        # Count lines ignoring empy ones
        entry_amount=`cat $input_file | grep -c .`
        
        if [ $entry_amount == 0 ]; then
          echo "
          Your list file seems to be empty.
          Please check!
          "
          exit 1
        fi
        ;;
    p)  all_scripts=$OPTARG
    ;;
    b)  molprobity_binaries=$OPTARG
    ;;
    m)  pdbs_path=$OPTARG
    ;;
    esac
done

# I am not too sure what this does, but apparently it permits accessing the non-option arguments nicely.
shift $((OPTIND-1))
[ "${1:-}" = "--" ] && shift




function pedbQC {

  logName=$1
  shift 1

  # Sacan so see if the input arguments look OK

  pat2="\w{4}\s\w{7}((\s[0-9]+)+)"
  ars="$@"

  if [[ $ars =~ $pat2 ]]; then
    echo "Input arguments are cool! $@" | tee -a $logName
  else
    echo "ERROR: Input arguments are not cool! $@ " | tee -a $logName
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

  echo "
  INPUT:
  XXXX: $xxxx
  PEDXXXX: $pedxxxx
  Specified ensemble amount: $ensemble
  Start positions provided: $ensemble_starts
  Amount of start positions provided: $start_positions_amount
  Specified conformer amount: $last
  " | tee -a $logName

  if [ $start_positions_amount !=  $ensemble ]
  then
    echo "ERROR: the specified ensemble amount int he input does not match the provided amount of start positions!" | tee -a $logName
    exit 1
  fi

  # Make folder for the entry
  mkdir -p ./${pedxxxx}
  cd ./${pedxxxx}
  
  # Decompress the PDB for the entry to the workind directory
  bzip2 -fckd ${pdbs_path}${xxxx}-all.pdb.bz2 > ${xxxx}-all.pdb

  # Check for UNK residures
  	# The RES string begins at 18 and ends at 20
  printf "\nScan for UNK residues\n" | tee -a $logName
  cat ${xxxx}-all.pdb | awk '/^ATOM.+/ { print $0 "LINE: " NR }' | awk '/^.{17}UNK.+/ { print "Warning! UNK residue at ATOM " $2 ", line " $NF " of the PDB file."}' >> $logName
  tail $logName -n 5
   
  # Check for Q atoms (NMR dummies)
      # The element column may be useful for filtering
    # Make temporary PDB files w/o the dummy ones, to not mess up the originals
    # Perhaps checking the hydrogen naming version is being too picky
  printf "\nScan for Q pseudoatoms\n" | tee -a $logName
  cat ${xxxx}-all.pdb | awk '/^ATOM.+/ { print $0 "LINE: " NR }' | awk '/^.{17}Q[A-Z].+/ { print "Warning! Pseudoatom at line " $NF " of the PDB file."}' >> $logName
  tail $logName -n 5
  	# http://www.chem.uzh.ch/robinson/felixman/pseudoatom.html

  
  # Check for missing residues
  #cat ${xxxx}-all.pdb | awk '/^ATOM.+/ { print $0 "LINE: " NR }' | awk '/^.{17}(\ ).+/ { print "Warning! Missing residue at ATOM " $2 ", line " $NF " of the PDB file."}' | tee -a $logName
  # Check for missing chain information
  	# Select ATOM lines and append the line number from the PDB file
  	# Select entries with whitespace where the chain should be found (position 22)
  printf "\nScan for missing chain data\n" | tee -a $logName
  cat ${xxxx}-all.pdb | awk '/^ATOM.+/ { print $0 "LINE: " NR }' | awk -v entryid="$xxxx" '/^.{21}(\ ).+/ { print "Warning! Missing chain information at ATOM " $2 ", line " $NF " of the "entryid" PDB file."}' >> $logName
  tail $logName -n 5


  # To-do
  	# Validation by MolProbity
      # documentation https://www.phenix-online.org/documentation/phenix_programs.html
      
      
      #molprobity.molprobity
      #molprobity.omegalyze
      #molprobity.probe
      #ramalyze  # Validate protein backbone Ramachandran dihedral angles
      #molprobity.reduce  # Adds hydrogens
      #molprobity.rotalyze  # Validate protein sidechain rotamers
      #molprobity.suitename

  # This little AWK inline script finds lines with regex:
    # returns the total clashscore, at the end of the file with /^MODEL/
    # returns the start lines for each model with /^Bad/
    # the clash counts for each one, by counting /^\ [A-Z][\ |0-9]+\ [A-Z]{3}/
  # The following also adds comments preceded by '#'' to each section (counts and summary)
  #printf "\nRun Molprobity clashscore\n" | tee -a $logName
  #${molprobity_binaries}molprobity.clashscore ${xxxx}-all.pdb > pedQC/${xxxx}-all.clashscore
  #cat pedQC/${xxxx}-all.clashscore | awk '/^MODEL/{if(count != 0) print count "\n\n#Clashscore summary"; count =0; print $0; next;}/^\ [A-Z][\ |0-9]+\ [A-Z]{3}/{count ++; next;}/^Bad\ Clashes/{print count; print $0; count = 0;next;}'  > pedQC/${xxxx}-all.summary.clashscore
  
  # Add a comment at the beggining of the clashscore file
  #sed -i '1s;^;# Bad clash count per model;' pedQC/${xxxx}-all.summary.clashscore
  
  printf "\nRun Molprobity ramalyze\n" | tee -a $logName
  #${molprobity_binaries}molprobity.ramalyze ${xxxx}-all.pdb > pedQC/${xxxx}-all.ramalyze
  #cat ${xxxx}-all.ramalyze | awk '/SUMMARY/{print $0}' > pedQC/${xxxx}-all.summary.ramalyze

  printf "\nRun Molprobity cablam\n" | tee -a $logName
  #${molprobity_binaries}molprobity.cablam ${xxxx}-all.pdb > pedQC/${xxxx}-all.cablam
  #cat ${xxxx}-all.cablam | awk '/SUMMARY/{print $0}' > pedQC/${xxxx}-all.summary.cablam

  printf "\nRun Molprobity cbetadev\n" | tee -a $logName
  #${molprobity_binaries}molprobity.cbetadev ${xxxx}-all.pdb > pedQC/${xxxx}-all.cbetadev
  #cat ${xxxx}-all.cbetadev | awk '/SUMMARY/{print $0}' > pedQC/${xxxx}-all.summary.cbetadev

  # Cleanup
  cd ..
  printf "\nAll items done.\n" | tee -a $logName
}









# Choose operating mode according to the input:
  # Either a single entry or multiple entries in a CSV file (TSV, hyphens, spaces are also supported).
if [ "$input_file" = '' ]; then

  # Check if the input seems right
  pat="\w{4}\s\w{7}((\s[0-9]+)+)"
  a="$@"

  if [[ $a =~ $pat ]]; then
    echo " Input arguments are cool! Your input: $@"
  else
    echo "ERROR: Input arguments are not cool! Your input: $@"
    exit 1
  fi

  # Setup logs
  logEntry=`echo $@ | sed -E 's/\w{4}\s(\w{7})((\s[0-9]+)+)/\1/'`
  mkdir -p $logEntry
  logName=$logPath/$logEntry/$logEntry$leeme

  echo "
  Your input was a single entry.
  Now processing entry: $@
  " | tee $logName
  
  pedbQC $logName $@

  echo "QC has finished, it should be OK if no warnings have appeared.
  " | tee -a $logName
  exit 0

else

  logNameList="${logPath}/${input_file}${leeme}"

  echo "
  Your input was a list with $entry_amount lines.
  List file: '$input_file'
  Unparsed arguments: $@
  Log files can be found within each entry folder.
  " | tee $logNameList

  pwd
  
  pat="\w{4}[,\t\s-]\w{7}(([,\t\s-][0-9]+)+)"
  #pat="\w{4},\w{7}((,[0-9]+)+)"  # Parse only CSV format
  while read line; do
    printf "\nNow parsing list...\n" | tee -a $logNameList

    pwd

    if [[ $line =~ $pat ]]; then
      # Read the line of the list file as arguments, separating them as needed.
      argumentos=`printf $line | sed -E "s/[,\t\s-]+/\ /g"`
      
      # Setup logs for the entry (XXXX)
      logEntry=`printf "$argumentos" | sed -E 's/\w{4}\s(\w{7})((\s[0-9]+)+)/\1/'`
      mkdir -p ${logEntry}/pedQC
      logName="${logPath}/${logEntry}/pedQC/${logEntry}${leeme}"
      
      printf "\nNow processing entry $argumentos of the list...\n" | tee $logName


      # Let the magic happen:
      pedbQC $logName $argumentos

    fi

    # Calculate the number or warnings in the logfile (there should be 26 non-warning lines, so subtract them)
    wcLog=`wc -l $logName | awk '{print $1}'`
    linesInLog=$( expr $wcLog - 26 )

    printf "\tWarnings written to logfile: $linesInLog \n" | tee -a $logNameList

  done < $input_file

  printf "\nQC has finished, check the logfile at ${logNameList}\n" | tee -a $logNameList
  exit 0
fi
