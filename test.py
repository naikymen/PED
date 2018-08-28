import pandas
import sys


def buildPymolCall(chosenRgListFile='chosenRg.list'):
    pyMolColors = pandas.Series(['max 28 20 13',
                                 'average 203 232 107',
                                 'min 242 233 225'])
    calls = []
    chosenRgList = pandas.read_csv(chosenRgListFile, header=None)
    for ens in range(1, max(chosenRgList[1]) + 1):
        subset = chosenRgList.loc[chosenRgList[1] == ens]
        subset.reset_index(drop=True, inplace=True)
        subset.sort_values(3)
        merged = pandas.concat([subset, pyMolColors],
                               axis=1, ignore_index=True)
        result = pandas.concat([merged[5].astype(str),
                                merged[4].astype(str),
                                merged[1].astype(str),
                                merged[6].astype(str)], axis=1)

        for index, row in result.iterrows():
            calls.append(row.str.cat(sep=' '))

    return(calls)


def buildPymolCall2(chosenRgListDf):
    calls = []

    theChosenOnes = chosenRgListDf[chosenRgListDf['Value'].notnull()]

    print(theChosenOnes)

    result = pandas.concat([theChosenOnes['PDBname'].astype(str),
                            theChosenOnes['PEDXXXX'].astype(str),
                            theChosenOnes['Ensemble'].astype(str),
                            theChosenOnes['Value'].astype(str)],
                            axis=1)

    [calls.append(row.str.cat(sep=' ')) for index, row in result.iterrows()]

    print(calls)


def selectMinMeanMax(rgListFile='rg.list'):
    rgList = pandas.read_csv(rgListFile, sep='\t')
    rgList['PDBname'] = rgList['PDB'].map(lambda x: str(x)[:-4])
    rgList['Value'] = None
    rgGroups = rgList.groupby('Ensemble')

    for name, ens_subset in rgGroups:
        rgList.loc[ens_subset['Rg'].idxmax(), 'Value'] = 'max 28 20 13'
        rgList.loc[ens_subset['Rg'].idxmin(), 'Value'] = 'min 242 233 225'
        rgList.loc[(ens_subset['Rg'] - ens_subset['Rg'].mean()).abs().idxmin(),
                   'Value'] = 'average 203 232 107'

    return(rgList)


def buildPymolCalls(rgListFile='rg.list'):
    rgList = pandas.read_csv(rgListFile, sep='\t')
    rgList['PDBname'] = rgList['PDB'].map(lambda x: str(x)[:-4])
    rgList['Value'] = None
    rgGroups = rgList.groupby('Ensemble')

    for name, ens_subset in rgGroups:
        rgList.loc[ens_subset['Rg'].idxmax(), 'Value'] = 'max 28 20 13'
        rgList.loc[ens_subset['Rg'].idxmin(), 'Value'] = 'min 242 233 225'
        rgList.loc[(ens_subset['Rg'] - ens_subset['Rg'].mean()).abs().idxmin(),
                   'Value'] = 'average 203 232 107'

    theChosenOnes = rgList[rgList['Value'].notnull()]

    result = pandas.concat([theChosenOnes['PDBname'].astype(str),
                            theChosenOnes['PEDXXXX'].astype(str),
                            theChosenOnes['Ensemble'].astype(str),
                            theChosenOnes['Value'].astype(str)],
                           axis=1)

    calls = []
    [calls.append(row.str.cat(sep=' ')) for index, row in result.iterrows()]

    # print(theChosenOnes)
    # print(calls)
    return(calls)


pymolCalls = buildPymolCalls(rgListFile='Rg/rg.list')
print("python2 %s/Pipe5.2.py %s" %
      ('/somewhere/', " ".join("'{}'".format(k) for k in pymolCalls)))
