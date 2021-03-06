# PED
Scripts for the automatic extraction and processing of the Protein Ensemble Database (PED) entry data from protein ensembles.

A joint effort between Tadeo Saldaño, Nicolás Méndez, and Julia Marchetti. It is a complete re-write of the original PED pipeline.

## Dependencies
The scripts are written in Python3 and import the following modules: ```optparse.OptionParser sys re os glob subprocess pandas Bio.PDB.PDBParser itertools json```

ATSAS (autorg, datgnom, etc. https://www.embl-hamburg.de/biosaxs/download.html)

Note: the ATSAS binaries are assumed to be in $PATH.

MolProbity (no server needed, build/bin/molprobity.* tools only http://molprobity.biochem.duke.edu/)

Note: the MolProbity binaries' path must be specified as a command-line or configuration file option.


R (with data.table and Cairo packages)

PyMol

## Notes
I have installed and run these tools in a Docker image of debian:latest (you may use the Dockerfile inside the Docker directory)

## Updates
### 2018-08-28
Removed old BASH pipelines and cleaned up the repo.
### 2018-08-27
Migration of the pipeline and the quality check scripts to python3 is complete.

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
Two modes ar supported: list input OR single entry input. The format of the list mode is described in the "Input/Output Specifications" section below.
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
### Input
Generally, the script requires the following input:

          1)  Entry information (ID and the indexes of each ensemble [subset of models] within the PDB file).
              Provided as a list of entries in a plain text file, or as arguements for a single entry only (see format below, and an example in the 'list-entry-all' file).
	      
          2)  A PDB file with all of the models, sorted by the ensemble to which they belong.
	      The script will look for a file named: 'XXXX-all.pdb.bz2'
	  
          3)  An OPTIONAL SAXS .dat file.
	      The script will look for a file named: 'XXXX-saxs.dat.bz2'


The location of the input can be specified using a variety of options:

        usage: pipe.py [options] [-l <entry list>] XXXX PEDXXXX ensemble_# ensemble1 ensemble2 ensemble3 ...

        -w  Set the working directory.
	        # Default behavior is to move to the directory where the script is executed (os.getcwd())
	        # Unless other options are used, all required files are assumed to be in the working directory

        -c  Load options from a JSON configuration file:
	        {
	            "list_input": "default",
	            "molprobity": "/MolProbity/build/bin/",
	            "pdb": "Sample-models",
	            "saxs": "default",
	            "scripts": "default",
	            "working_directory": "default"
	        }

        -p  Path to the directory where the perl and R scripts are.
        
        -b  Path to the directory where the MolProbity binaries are.
        
        -m  Path where the PDB model files are (e.g. '-p ~/somewhere/pdb-models/')
        
        -s  Path to the SAXS data, where it will look for files named '1AAA-saxs.dat.bz2' and such.

        -l  Input a list of entries from a list file (see csv format below, will ignore other arguments)

	        The list input should NOT have a header, and the entries should look like:
	        	XXXX,PEDXXXX,ensemble_amount,model_amount,model1Start,model2Start,model3Start[, ...]
	        Where:
	         'XXXX' is the PED entry ID
	         'PEDXXXX' is the PED entry ID with PED at the beginning.
	         'ensemble_amount' is the total number of ensembles in the entry
	         'model_amount' is the total number of pdb models in the entry
	         'modelNStart' is the position where model N starts in the PDB file

	        They may be separated by a comma, tab, space or hyphen. They are parsed by the following regex:
	          \w{4}[,\t\s-]\w{7}(([,\t\s-][0-9]+)+)
	        These symbols are later replaced by a space in the awk command.
	        So please do not include any of these in the metadata (e.g. 'PED-ABCD' is NOT adequate input).

	        Please incude a final newline in the list file, this is necessary!
	        The script will attempt to include one if it is not there, by editing the list.

        Log files will appear inside the entry folder for single entries, unless a 
        An additional logfile will appear for list entries at the working directory.
### Output
Entry folders are created for each one as "PEDXXXX"
Inside there are files and directories containing the output of different analyses: rg/dmax histograms and files, pymol plots, crysol output, and n2n distance calculations.

- ensembles: a "pdb.list" that contains the PDB names of each conformer and usefully formatted metadata (ensemble and conformer numbers). Also, find herein a compressed .pdb.tar.gz file, which contains PDB files (one per conformer) and the n2n.tar.gx file. This last archive contains the n to n' distances of each conformer as a plain text list (separated by a newline character). We will probably not be using this part (the call to this function can be commented out in pipe.py in lines 312-319)

- Crysol: the compressed crysol output files. Useful warnings may be found in the "crysol_summary.txt" and in the ".log.tar.gz" archive.

- Pymol: PyMol renders of conformers with maximum, minimum and closest-to-average (per ensemble). Also here are the .pse files.

- Rg: this directory holds Rg histograms (per ensemble) and several files used to generate them (mainly rg.list).

## To-do
Improve this readme.

Replace n2n distance calculations with end-to-end distances.
