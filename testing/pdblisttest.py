import itertools
from Bio.PDB import PDBParser


def n2n(pedxxxx, file):
    # Code adapted as found in satckexchange
    # https://bioinformatics.stackexchange.com/questions/783/how-can-we-find-the-distance-between-all-residues-in-a-pdb-file

    # Create parser
    parser = PDBParser()

    # Read structure from file
    # The first argument is a user-given name for the structure
    structure = parser.get_structure(pedxxxx, file)

    model = structure[0]
    # Get the first chain (i guess there is a more direct way than this one)
    chain_id = [c.id[0] for c in model.get_chains()][0]
    chain = model[chain_id]

    # this example uses only the first residue of a single chain.
    # it is easy to extend this to multiple chains and residues.

    distances=[]

    [distances.append(i[0]['CA'] - i[1]['CA']) for i in itertools.combinations(chain, 2)]

    return(distances)


n2nd = n2n('PED1AAA', 'PED1AAA_3-11.pdb')

with open(".".join(['PED1AAA_3-11.pdb', 'n2n']), 'w') as d:
    for i in n2nd:
    	d.write(str(i) + "\n")
