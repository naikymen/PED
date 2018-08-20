# PED
The pedbPipe3.sh has a help section, call it by using the help option:
 	$ bash pedbPipe3.sh -h

The "list-entry-new" file contains the entries in the new format.
	We should really check if the ensemble numbers/indices are ok.

## Dependencies
ATSAS (autorg, datgnom, etc. https://www.embl-hamburg.de/biosaxs/download.html)

MolProbity (no server needed, build/bin/molprobity.* tools only http://molprobity.biochem.duke.edu/)

R (with data.table and Cairo packages)

PyMol

## Notes
I have installed and run these tools in a Docker image of Ubuntu 18.04.

## Updates
### 2018-08-20
Migration of the pipeline to python3 is almost complete.

ATSAS will probably not be required anymore.

There is now a Dockerfile that describes all required dependencies, and can be used to build a Debian image that satisfies all requirements.

# Examples

### Help
```
$ bash pedbPipe3.sh -h
```
### Input
Two modes ar supported: list input OR single entry input. The format of the list mode is described in the help section.
```
$ bash pedbPipe3.sh -l list-entry-one

$ bash pedbPipe3.sh 1AAA PED1AAA 3 32 1 12 22
```
### Working directory
The -w flag can be passed to specify the working directory, where we expect to have read/write permissions.
Otherwise, the default behaviour is to use the output of ```pwd```.
```
$ bash pedbPipe3.sh -w /path/to/entry_folder 1AAA PED1AAA 3 32 1 12 22
```
This option is not described in the configuration file, but it may be set as any other variable, as the whole configuration file is sourced (i.e. adding ```working_directory=/something/``` to the config file).
### Config file
The -c flag may be used to specify a configuration file. Default behaviour is described in the help section.
```
$ bash pedbPipe3.sh -w /path/to/entry_folder -c /path/to/pedb.cfg -l list-entry-one
```
### Other options
They are described in the help section. Using options flags will override the values in the configuration file (i.e. paths to executables or input files).

