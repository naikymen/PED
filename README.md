# PED
The pedbPipe3.sh has a help section, call it by using the help option:
 	$ bash pedbPipe3.sh -h

The "list-entry-new" file contains the entries in the new format.
	We should really check if the ensemble numbers/indices are ok.

## Dependencies
The scripts are written in Python3 and import the following modules: ```optparse.OptionParser sys re os glob subprocess pandas Bio.PDB.PDBParser itertools json```

ATSAS (autorg, datgnom, etc. https://www.embl-hamburg.de/biosaxs/download.html)

MolProbity (no server needed, build/bin/molprobity.* tools only http://molprobity.biochem.duke.edu/)

R (with data.table and Cairo packages)

PyMol

## Notes
I have installed and run these tools in a Docker image of debian:latest (you may use the Dockerfile inside the Docker directory)

## Updates
### 2018-08-20
Migration of the pipeline to python3 is almost complete.

ATSAS will probably not be required anymore.

There is now a Dockerfile that describes all required dependencies, and can be used to build a Debian image that satisfies all requirements.

# Examples

### Help
```
$ python3 qc.py -h
```
```
$ python3 pipe.py -h
```
### Input
Two modes ar supported: list input OR single entry input. The format of the list mode is described in the help section.
```
$ python3 pipe.py -l list-entry

$ python3 pipe.py 1AAA PED1AAA 3 32 1 12 22
```
The location of the PDB file containing all models can be passed with the ```-m``` flag. The PDB is expected to be *in tar.bz format*.


### Config file
*CLI options will always override the default and config file options*.

The -c flag may be used to specify a configuration file in JSON format.
```
$ python3 pipe.py -c /path/to/pedb.cfg -l list-entry
```
Here "default" is a keyword interpreted as "skip this option". Any other value is interpreted as a value for the option.

A valid JSON config file that can be used for both qc.py and pipe.py is:
```
{
    "list_input": "default",
    "molprobity": "/MolProbity/build/bin/",
    "pdb": "Sample-models",
    "saxs": "default",
    "scripts": "default",
    "working_directory": "default"
}
```
Unexpected option names will not be parsed and an exception will be raised if they are present.
Use the ```-n``` flag to print parsed options in JSON format.

### Working directory
The -w flag can be passed to specify the working directory, where we expect to have read/write permissions.
Otherwise, the default behaviour is to use the output of ```pwd```.
```
$ python3 pipe.py -w /path/to/wd/ 1AAA PED1AAA 3 32 1 12 22
```
### Other options
They are described in the help section. Using options flags will override the values in the configuration file (i.e. paths to executables or input files).

## Input/Output Specifications
usage: pipe.py [options] [-l <entry list>] XXXX PEDXXXX ensemble_# ensemble1 ensemble2 ensemble3 ...
        
        -h  Show this help and exit.

        -n 	Dry run, print only the input options and exit.

        -w  Set the working directory.
	        # Default behavior is to move to the directory where the script is executed (os.getcwd())
	        # Unless other options are used, all required files are assumed to be in the working directory

        -c  Load options from a configuration file.

			# Directory where the auxiliary scripts are.
			# This string must end with a slash '/'
			all_scripts='~/IDPfun/PED/Scripts/'

			# Directory where the PDB files are
			# This string must end with a slash '/'
			pdbs_path=./

			# Directory where the optional SAXS files are
			# This string must end with a slash '/'
			saxs_path=./

			# Directory where the reference SAXS files are (in CSV format)
			# This string must end with a slash '/'
			ref_saxs_path=$saxs_path

			# Path for the log files
			# This string must end with a slash '/'
			logPath=./

			# Directory where the molprobity binaries are found (for the QC script only).
			# This string must end with a slash '/'
			molprobity_binaries='/home/MolProbity/build/bin/' 

			# Note: relative paths such as './something/' will be interpreted according to the working directory
			# The default is to use the output from pwd, but this can be overriden by using the -w flag.
        
        -p  Path to the directory where the perl and R scripts are.
        
        -b 	Path to the directory where the MolProbity binaries are.
        
        -m  Path where the PDB model files are (e.g. '-p ~/somewhere/pdb-models/')
        
        -s  Path to the SAXS data, where it will look for files named '1AAA-saxs.dat.bz2' and such.

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

        Log files will appear inside the entry folder for single entries, unless a 
        An additional logfile will appear for list entries at the working directory.
