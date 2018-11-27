import os
import subprocess
import re
import glob
import pandas as pd
from shutil import copyfile
import shutil
import json
from pprint import pprint

##"/home/julia/Escritorio/Bruselas/" should be replace with the drectory where the data is going to be

##Check if everything was runned
def check_run(structure):
    i = structure[0:-4]
    disicl_pdb= i + "_DISICL.pdb"
    log_file= "DISICL_" + i + ".log"
    out_file= "DISICL_psim_" + i + ".out"
    stat_file= "DISICL_psim_" + i + ".stat"
    dih_file = i + "_prot.dih"
    if (os.path.exists(out_file)==False):
        return False
    else:
        return True
    if (os.path.exists(log_file)==False):
        return False
    else:
        return True


def running_disicl(structure):
    run = "python DISICL_main.py "+ structure +" @protlib 2"
    os.system(run)

#Run_residues is a global variable 
#To obtain the list of residues is read by the program sometimes it may skip some residues
def extract_runned_residues(structure):
    os.chdir(disicl_directory)
    with open("DISICL_psim_%s.out" % (structure),"r") as out_disicl:
        out_disicl=out_disicl.read()
        START="#DISICL  time0  timestep  frames  segment0   reslist\n"
        END="#\n"
        m = re.compile(r'%s.*?%s' % (START,END), re.S)
        residues_list = re.findall(m,out_disicl)
        for i in range(len(residues_list)):
            residues_list[i] = residues_list[i].split("\n")
        try:
            residues_list = residues_list[0][1]
            residues_list= residues_list.split()[-1].strip("[]")
            first = residues_list.split("-")[0]
            last = residues_list.split("-")[-1]
            for i in range(int(first),int(last)):
                run_residues.append(i)
        except IndexError:
            pass

##Parsing disicl_file
##Parsing and secondary structure assigment lists 
#Clasification array description
#clasification[0]: 3-helical turns (3HT) residues --> other
#clasification[1]: Alpha-helical (HEL) residues --> alpha_helix
#clasification[2]: Beta-strand (BS) residues --> beta_strand
#clasification[3]: Irreg. Beta (IRB) residues --> other
#clasfication[4]: Beta-turn (BT) residues --> other
#clasification[5]: Other tight turns (OTT) residues --> other
#clasification[6]: Left-handed turn (LHT) residues --> other
#clasification[7]: unclassified (UC) residues --> other
def disicl_parser(structure):
    START = "#       time\tresidue"
    END = "&"
    m = re.compile(r'%s.*?%s' % (START,END), re.S)
    with open("DISICL_psim_%s.out" % (structure),"r") as out_disicl_psim :
        out_disicl_psim = out_disicl_psim.read()
        clasification = re.findall(m,out_disicl_psim)
        for i in range(len(clasification)):
            clasification[i]=clasification[i].split("\n")
        ##Alpha_helix,  and clasification[1]
        for z in range(1, (len(clasification[1])-1)):
            alpha_helix.append((int(clasification[1][z].split()[1])))
        ##Beta_strand, clasification[2], 
        for z in range(1, (len(clasification[2])-1)):
            beta_strand.append((int(clasification[2][z].split()[1])))
        ##Other,clasification[0],clasification[3],clasification[4], clasification[5], clasification[6], clasification[7]
        for z in range(1, (len(clasification[0])-1)):
            other.append((int(clasification[0][z].split()[1])))
        for j in range(3,8):
            for z in range(1, (len(clasification[j])-1)):
                other.append((int(clasification[j][z].split()[1])))


def disicl_table(structure):
    entry_id = structure[0:7]
    chain  = structure[-5]
    ensemble = structure[8]
    conformer = structure.split("_")[1].split("-")[1]
    for i in run_residues:
        if i in alpha_helix:
            disicl_df.loc[len(disicl_df)] = [i,1,0,0,entry_id,ensemble,conformer,chain,structure,1]
        elif i in beta_strand:
            disicl_df.loc[len(disicl_df)] = [i,0,1,0,entry_id,ensemble,conformer,chain,structure,1]
        elif i in other:
            disicl_df.loc[len(disicl_df)] = [i,0,0,1,entry_id,ensemble,conformer,chain,structure,1]
        else: 
            residues_without_info.append(i)
            disicl_df.loc[len(disicl_df)] = [i,-1,-1,-1,entry_id,ensemble,conformer,chain,structure,1]
            disicl_log_file.write("disicl was not able to make prediction to position %i of estructure %s\n" %(i, structure))


def check_renaming_residues(structure):
    with open("DISICL_%s.log" % (structure),"r") as log_disicl:
        log_disicl=log_disicl.read()
        re_pattern = r'residue:.*renamed to:.*'
        renamed_list = re.findall(re_pattern,log_disicl)
        return renamed_list

def renaming_df_set_up(renamed_list,structure):
    for i in renamed_list:
        original_position=i.split()[2]
        new_position=i.split()[-2]
        renamed_df.loc[len(renamed_df)] = [float(original_position), float(new_position),structure]


def processing_disicl_table(disicl_df):
    global disicl_df_grouped
    disicl_df_grouped = disicl_df.groupby(["Position","Chain","Ensemble","Entry"],as_index = False).sum()
    disicl_df_grouped["Alpha_helix_percentage"] = (disicl_df_grouped["Alpha_helix"] / disicl_df_grouped["Count"])*100
    disicl_df_grouped["Beta_strand_percentage"] = (disicl_df_grouped["Beta_strand"] / disicl_df_grouped["Count"])*100
    disicl_df_grouped["Other_percentage"] = (disicl_df_grouped["Other"] / disicl_df_grouped["Count"])*100
    disicl_df_grouped = disicl_df_grouped[["Entry","Chain","Ensemble","Position","Alpha_helix_percentage","Beta_strand_percentage","Other_percentage","Count"]]
    disicl_df_grouped.head()

def clean_disicl_directory(structure):
    i = structure[0:-4]
    disicl_pdb= i + "_DISICL.pdb"
    if os.path.exists(disicl_pdb):
        os.remove(disicl_pdb)
    log_file= "DISICL_" + i + ".log"
    if os.path.exists(log_file):
        os.remove(log_file)
    out_file= "DISICL_psim_" + i + ".out"
    if os.path.exists(out_file):
        os.remove(out_file)
    stat_file= "DISICL_psim_" + i + ".stat"
    if os.path.exists(stat_file):
        os.remove(stat_file)
    dih_file = i + "_prot.dih"
    if os.path.exists(dih_file):
        os.remove(dih_file)
    if os.path.exists(structure):
        os.remove(structure)

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
        disicl_directory = ("/home/julia/Escritorio/Bruselas/DISICL/")
        ensembles_directory = ("/home/julia/Escritorio/Bruselas/PED-data/PED-DB3/%s/ensembles/" % pedxxxx)
        entry_directory=("/home/julia/Escritorio/Bruselas/PED-data/PED-DB3/%s/" % pedxxxx)
        os.mkdir(entry_directory+"Secondary_structure")
        secondary_structure_directory = entry_directory+"Secondary_structure/"
        print entry_directory
        all_models_chain_directory = ensembles_directory+"ensembles/"
        os.chdir(all_models_chain_directory)
        all_pdb_structures = glob.glob("*.pdb")
        disicl_col_names =  ['Position',"Alpha_helix","Beta_strand","Other","Entry","Ensemble","Conformer","Chain","Protein","Count"]
        disicl_df = pd.DataFrame(columns = disicl_col_names)
        renamed_columns_names=["Original_position","Position","Protein"]
        renamed_df=pd.DataFrame(columns = renamed_columns_names)
        all_pdb_structures.sort()
        disicl_log_file=open(secondary_structure_directory+"disicl_log_file", "w")
        disicl_log_file.write("disicl is running\n")
        for i in all_pdb_structures:
            shutil.copy2(i, disicl_directory)
        os.chdir(disicl_directory)
        for i in all_pdb_structures:
            while check_run(i) == False:
                running_disicl(i)
                print ("DISICL is running for %s" % i)
        for i in all_pdb_structures:
            alpha_helix = []
            beta_strand = []
            other = []            
            run_residues=[]
            residues_without_info=[]
            renamed_list=[]
            extract_runned_residues(i[0:-4])
            disicl_parser(i[0:-4])
            disicl_table(i)
            renamed_list=check_renaming_residues(i[0:-4])
            renaming_df_set_up(renamed_list, i)
            clean_disicl_directory(i)
        if renamed_df.shape[0]>0:
            disicl_df=pd.merge(renamed_df,disicl_df, on = ["Protein","Position"])
            disicl_df=disicl_df.drop(["Position"],axis=1)
            disicl_df=disicl_df.rename(columns={"Original_position":"Position"})
            disicl_df.to_csv(secondary_structure_directory+"%s_secondary_all.csv" % pedxxxx)
        else:
            disicl_df.to_csv(secondary_structure_directory+"%s_secondary_all.csv" % pedxxxx)
            clean_disicl_directory(i)
        processing_disicl_table(disicl_df)
        disicl_df_grouped.to_csv(secondary_structure_directory+"secondary_structure_table.csv", index=False)
	##Check the directory where the r scirpts are
        shutil.copy2("/home/julia/Escritorio/Bruselas/Julia/data_disicl_plot.r", secondary_structure_directory+"data_disicl_plot.r")
        os.chdir(secondary_structure_directory)
        os.system("Rscript data_disicl_plot.r")
        disicl_log_file.close()
        os.chdir("/home/julia/Escritorio/Bruselas/PED-data/PED-DB3/")


