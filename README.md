# PED
The pedbPipe3.sh has a help section, call it by using the help option:
 	$ bash pedbPipe3.sh -h

The "list-entry-new" file contains the entries in the new format.
	We should really check if the ensemble numbers/indices are ok.

## Dependencies
ATSAS (autorg, datgnom, cablam, etc. https://www.embl-hamburg.de/biosaxs/download.html)

MolProbity (no server needed, build/bin/molprobity.* tools only http://molprobity.biochem.duke.edu/)

R (with data.table and Cairo packages)

PyMol

## Notes
I have installed and run these tools in a Docker image of Ubuntu 18.04.
