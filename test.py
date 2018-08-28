import pandas


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

buildPymolCall()
