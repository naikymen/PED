import re
import subprocess
import os


def sprun(command):
    subprocess.run(
        command, shell=True, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def pipe1_crysol(pdb_files, pedxxxx):
    with open('rg.list', 'w') as rg_list:
        # Write the header
        rg_list.write('\t'.join(
            ['PDB', 'Dmax', 'Rg']))

        for f in pdb_files:
            sprun("crysol %s" % f)
            logfile = "".join([f.strip(".pdb"), '00.log'])

            with open(logfile) as log:
                # "Envelope  diameter :  68.43    "
                # https://regex101.com/r/uleo3Y/1
                dmax_p = re.compile(r'Envelope\s*diameter.*?:.*?((?:[\d.E\-\+])+)\s*')
                # "Rg ( Atoms - Excluded volume + Shell ) ................. : 21.35"
                rg_p = re.compile(r'Rg.*Atoms.*:.?([\d.E\-\+]+)')

                text = log.read()
                dmax_value = re.search(dmax_p, text).group(1)
                rg_value = re.search(rg_p, text).group(1)

                # Write saxs output
                rg_list.write('\n' + '\t'.join([f, dmax_value, rg_value]))
        rg_list.write('\n')

files = [f for f in os.listdir('.') if re.match(r'.*\.pdb$', f)]
pipe1_crysol(files, 'PED1AAA')
