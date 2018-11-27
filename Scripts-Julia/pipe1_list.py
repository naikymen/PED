import os
import subprocess
import glob
import json
from pprint import pprint
import re 
from Bio.PDB import PDBParser, PDBIO , Selection
import tarfile
from Bio.SeqUtils import seq1
import shutil
import numpy
import math
import pandas as pd
import urllib2

##"/home/julia/Escritorio/Bruselas/" should be replace with the drectory where the data is going to be

#There are some structures that lack of a chain name so in this function is set to default value of "A"
def chain_correction(structure):
    with open(structure, "r") as f:
        new_pdb_file_name=structure[0:-4] + "_A.pdb"
        with open(new_pdb_file_name,"w") as chain_corrected_pdb:
            f = f.readlines()
            for i  in range(len(f)):
                f[i] = list(f[i])
                if len(f[i]) > 20:
                    f[i][21] = "A"
                    new_string = ''.join(f[i])
                else: 
                    new_string = ''.join(f[i])      
                chain_corrected_pdb.write(new_string)
        print new_pdb_file_name


##This function splits each structure in different chains, each chain in a diffent file.
#This is done because the DISCL program runs by chain and if the file doesn't have a chain by default 
#name "A" is assigned
def chain_splitter(structure,chains):
    io = PDBIO()
    pdb = PDBParser().get_structure(structure,structure)
    for chain in pdb.get_chains():
        if (chain.get_id() != " "):
            io.set_structure(chain)
            io.save(structure[:-4] + "_" + chain.get_id() + ".pdb")
            chains.append(chain.get_id())
        else:
            chain_correction(structure)
            chains.append("A")
    os.remove(structure)
    return(chains)

#This is done because otherwise the DISCL won't run for those positions
def modified_residues(structure):
    io = PDBIO()
    pdb_parser = PDBParser()
    new_structure = pdb_parser.get_structure(" ", structure)
    for i, residue in enumerate(new_structure.get_residues()):
        res_id = list(residue.id)
        if residue.get_resname() == "TPO":
            residue.resname = "THR"
        elif residue.get_resname() == "SEP":
            residue.resname = "SER"
        elif residue.get_resname() == "TYP":
            residue.resname = "TYR"
        elif residue.get_resname() == "HYP":
            residue.resname = "PRO"
        elif residue.get_resname() == "HID":
            residue.resname = "ALA"
    io.set_structure(new_structure)
    io.save(structure)

##This function extracts the sequence from the pdb file
def extract_seq_from_pdb (pedxxxx,ensemble,confomer,chain):
    pdb = ("%s_%s-%s_%s.pdb"%(pedxxxx, ensemble,conformer,chain))
    structure = PDBParser().get_structure("pdb",pdb)
    seq_pdb=[]
    seq_pdb_complete=[]
    for residue in structure.get_residues():
        if residue.id[0] == " ":
            seq_pdb.append(residue.get_resname())
    seq_pdb = ''.join(seq_pdb)
    
    seq_pdb= seq1(seq_pdb)
    longitud=len(seq_pdb)
    return (seq_pdb)

###This function extracts the coordinates from the first and last residue and compute the euclidean function with
##numpy function
#First I save al residues number in an array and then select the coordinates for the first [0] and last one [-1]
def end_to_end_distance(structure):
    entry_id = structure[0:7]
    chain_id  = structure[-5]
    ensemble = structure[8]
    conformer = structure.split("_")[1].split("-")[1]
    io = PDBIO()
    pdb = PDBParser().get_structure(structure,structure)
    residues_number_list=[]
    for chain in pdb.get_chains():
        for residue in chain.get_residues():
            if residue.id[0] == " ":
                residues_number_list.append(residue.get_id()[1])
            else:
                pass
    coordinates_first=[]
    coordinates_last=[]
    for chain in pdb.get_chains():
        for residue in chain.get_residues():
            if residue.get_id()[1] == residues_number_list[0]:
                coordinates_first.append((residue['CA'].get_coord()))
            elif residue.get_id()[1] == residues_number_list[-1]:
                coordinates_last.append((residue['CA'].get_coord()))
    dist = numpy.linalg.norm(coordinates_first[0]-coordinates_last[0])
    end_to_end_df.loc[len(end_to_end_df)] = [entry_id,ensemble,conformer,chain_id,structure,dist]


def end_to_end_processing(end_to_end_df):
    global df_report
    global end_to_end_df_grouped 
    end_to_end_df_grouped = end_to_end_df.groupby(["Ensemble","Entry","Chain"],as_index = False)
    max_df= end_to_end_df_grouped["Ensemble","Entry","End_to_End","Chain"].max()
    max_df=max_df.rename(columns={"End_to_End":"Max_Dist"})
    mean_df= end_to_end_df_grouped["Ensemble","Entry","End_to_End","Chain"].mean()
    mean_df=mean_df.rename(columns={"End_to_End":"Mean_Dist"})
    min_df=end_to_end_df_grouped["Ensemble","Entry","End_to_End","Chain"].min()
    min_df=min_df.rename(columns={"End_to_End":"Min_Dist"})
    end_to_end_df_grouped_std = end_to_end_df.groupby(["Ensemble","Entry","Chain"])
    end_to_end_df_grouped_std=end_to_end_df_grouped_std.std().reset_index()
    end_to_end_df_grouped_std=end_to_end_df_grouped_std.rename(columns={"End_to_End":"Std"})
    df_report = pd.merge(max_df,mean_df, on = (["Ensemble","Entry","Chain"]))
    df_report = pd.merge(df_report,min_df, on = (["Ensemble","Entry","Chain"]))
    df_report = pd.merge(df_report,end_to_end_df_grouped_std, on = (["Ensemble","Entry","Chain"]))


##Reading parameters from list
os.chdir("/home/julia/Escritorio/Bruselas/PED-data/PED-DB3/")
##If reading from a list
with open("lista_prueba","r") as list_entry:
    for i in list_entry.readlines():
        args = re.split(r'[,;\t\s-]+', i.strip())
        xxxx = args[0] 
        pedxxxx = args[1]
        ensembles = args[2]
        conformers = args[3]
        indices = args[4:]
        chains = []
        print args
        ensembles_directory = ("/home/julia/Escritorio/Bruselas/PED-data/PED-DB3/%s/ensembles/" % pedxxxx)
        entry_directory=("/home/julia/Escritorio/Bruselas/PED-data/PED-DB3/%s/" % pedxxxx)
        os.mkdir(entry_directory+"End_to_End/")
        end_to_end_directory = entry_directory+"End_to_End/"
        os.chdir(ensembles_directory)
        tar = tarfile.open("%s-pdb.tar.gz" % pedxxxx)
        tar.extractall()
        tar.close()
        os.chdir(ensembles_directory+"ensembles/")
        all_pdb_models = glob.glob("*.pdb")
        for i in all_pdb_models:
            chain_splitter(i,chains)
            chains = list(set(chains))
        print chains
        r1 = range(1, int(ensembles) + 1, 1)
        all_pdb_structures = glob.glob("*.pdb")
        all_pdb_structures.sort()
        col_names =  ["Entry","Ensemble","Conformer","Chain","Protein",'End_to_End']
        end_to_end_df = pd.DataFrame(columns = col_names)
        with open(("%s%s_all_sequence.txt" % (entry_directory, pedxxxx)), "w+") as all_sequence_file: ##Chequear el directorio al que queremos que vaya
            for i in r1 :
                for chain in chains:
                    conformer = 1
                    ensemble = i
                    pdb = ("%s_%s-%s_%s.pdb"%(pedxxxx, ensemble,conformer,chain))
                    print pdb
                    seq_pdb = extract_seq_from_pdb(pedxxxx,ensemble,conformer,chain)
                    all_sequence_file.write(">%s_%s_%s\n%s\n"%(pedxxxx,ensemble,chain,seq_pdb))
        for i in all_pdb_structures:
            modified_residues(i)
            end_to_end_distance(i)
        end_to_end_processing(end_to_end_df)
        end_to_end_processing(end_to_end_df)
        end_to_end_df.to_csv(end_to_end_directory+"end_to_end_table.csv", index = False)
        df_report.to_csv(end_to_end_directory+"%s_end_to_end_report_table.csv" % (pedxxxx), index = False)
	##Check the directory where the r scirpts are
        shutil.copy2("/home/julia/Escritorio/Bruselas/Julia/end_to_end_plot.r", end_to_end_directory+"end_to_end_plot.r")
        os.chdir(end_to_end_directory)
        os.system("Rscript end_to_end_plot.r")
        os.chdir("/home/julia/Escritorio/Bruselas/PED-data/PED-DB3/")


