import os
import copy
from xlrd import open_workbook
import xlsxwriter
book = open_workbook("prefs_table.xlsx")
sheet = book.sheet_by_index(0)
# taking the data from EXCEL file
list_from_excel = []
for i in range(1, sheet.nrows):
    row = []
    for j in range(sheet.ncols - 1):
        row.append(sheet.cell_value(i, j))
    list_from_excel.append(row)
# in case of odd number of people we add an 'unknown' person
if len(list_from_excel) % 2 == 1:
    list_from_excel.append(['Unknown', 5.0, 5.0, 5.0, 5.0, 5.0])
# creating a list with preferences
# # the preferences are sorted
## sorting the given data in alphabetical order (why not?)
list_from_excel = sorted(list_from_excel, key=lambda x: x[0])
preferenceList = []
for i in range(len(list_from_excel)):
    subPreference = [list_from_excel[i][0]]
    subOfContent = []
    for j in range(len(list_from_excel)):
        if i != j:
            subOfPerson = [list_from_excel[j][0]]
            difference = 0
            for u in range(1, len(list_from_excel[i])):
                difference += abs(list_from_excel[i][u] - list_from_excel[j][u])
            subOfPerson.append(difference)
            subOfContent.append(subOfPerson)
    subOfContent = sorted(subOfContent, key=lambda subOfContent: subOfContent[1])
    subPreference.append(subOfContent)
    preferenceList.append(subPreference)
# Creating dictionary that contains all the preferences of every person, no numbers
sortedPreference = {}
for i in range(len(preferenceList)):
    preferences = []
    for j in range(len(preferenceList[i][1])):
        preferences.append(preferenceList[i][1][j][0])
    sortedPreference[preferenceList[i][0]] = preferences
# Getting the information about the country of each person
countryList = {}
for i in range(1, sheet.nrows):
    countryList[sheet.cell_value(i, 0)] = sheet.cell_value(i, sheet.ncols - 1)
# Sorting people according to their country. 2 people of the same country cannot be roommates
# In that case, if countries are the same, then that person goes to the end of the preference list
for key in sortedPreference:
    i = 0
    k = 0
    while i + k < len(sortedPreference[key]):
        if countryList[key] != countryList[sortedPreference[key][i]]:
            i += 1
        else:
            sortedPreference[key].append(sortedPreference[key][i])
            del sortedPreference[key][i]
            k += 1
beforeMainAlgorithm = {"preferences": sortedPreference}
# The code below is from internet :))))
def getKeyByVal(inptDict, inputVal):
    for key, val in inptDict.items():
        if val == inputVal:
            return key
def removeCycle(preferences, table):
    tmpPreferences = preferences
    # remove the cycle matches symmetrically
    for i in range(len(table[0]) - 1):
        tmpPreferences[table[1][i]].remove(table[0][i + 1])
        tmpPreferences[table[0][i + 1]].remove(table[1][i])
    return tmpPreferences
def cycleExists(table):
    tableLeft = table[0]
    tableRight = table[1]
    # check if all elements in column are unique
    if len(tableLeft) > len(set(tableLeft)):
        return True
    else:
        return False
def stableNotPossible(preferences):
    for i in preferences:
        if len(preferences[i]) == 0:
            return True
    return False
def isStable(preferences):
    for i in preferences:
        if len(preferences[i]) != 1:
            return False
    return True
def step1(inputList):
    proposals = {}
    numProposals = {}
    queue = []
    for i in inputList["preferences"]:
        queue.append(i)
        proposals[i] = None
        numProposals[i] = 0
    tmpPreferences = copy.deepcopy(inputList["preferences"])
    while not len(queue) == 0:
        i = queue[0]
        numProposals[i] += 1
        for j in inputList["preferences"][i]:
            if proposals[j] == None:
                del queue[0]
                proposals[j] = i
                break
            elif proposals[j] != i:
                current_index = inputList["preferences"][j].index(i)
                other_index = inputList["preferences"][j].index(proposals[j])

                if current_index < other_index:
                    del queue[0]
                    queue.insert(0, proposals[j])
                    # Remove old proposal symmetrically
                    tmpPreferences[proposals[j]].remove(j)
                    tmpPreferences[j].remove(proposals[j])
                    proposals[j] = i
                    break
                else:
                    # Remove invalid proposal symmetrically
                    tmpPreferences[i].remove(j)
                    tmpPreferences[j].remove(i)
        inputList["preferences"] = copy.deepcopy(tmpPreferences)
    return (proposals, inputList)
def step2(proposals, inputList):
    tmpPreferences = copy.deepcopy(inputList["preferences"])
    for i in inputList["preferences"]:
        #  Remove the right hand side of the preferred element
        proposalIndex = tmpPreferences[i].index(proposals[i])
        tmpPreferences[i] = tmpPreferences[i][:proposalIndex + 1]
        # Remove all other instances of the given element
        for j in inputList["preferences"]:
            # Try to remove element from all preference lists
            key = getKeyByVal(proposals, i)
            if j != i and j != proposals[i] and j != key:
                try:
                    tmpPreferences[j].remove(i)
                except ValueError:
                    pass
    # for i in inputList["preferences"]:
    #    pass
    return tmpPreferences
def step3(preferences):
    first = True
    # search for cycles until a stable or unstable matches are found
    while True:
        # create a table with two columns
        table = ([], [])
        # check if stable matching is possible
        if stableNotPossible(preferences):
            raise AlgorithmError("Stable matching not possible.")
        for i in preferences:
            # add the first instance that has atleast 2 preferences
            if len(preferences[i]) >= 2 and first == True:
                # add element
                firstPreference = i
                table[0].append(firstPreference)
                # add second preference of element
                secondPreference = preferences[i][1]
                table[1].append(secondPreference)
                first = False
            elif first == False:
                # check if a cycle exists in the table
                if cycleExists(table):
                    # remove cycle
                    preferences = removeCycle(preferences, table)
                    first = True
                    # start again
                    break
                # add the last preference of the previous second preference
                # from the table
                firstPreference = preferences[secondPreference][-1]
                table[0].append(firstPreference)
                # add the second preference of the first preference
                secondPreference = preferences[firstPreference][1]
                table[1].append(secondPreference)
        # If the preferences are stable, return them
        if isStable(preferences):
            return preferences
def apply(input1):
    step_1 = step1(input1)
    return step3(step2(step_1[0], step_1[1]))
###################end of the internet algorithm
afterMainAlgorithm = apply(beforeMainAlgorithm)
result = {}
for key, item in afterMainAlgorithm.items():
    if key != result.get(item[0]):
        result[key] = item[0]
if os.path.exists('result.xlsx'):
    os.remove('result.xlsx')
workbook = xlsxwriter.Workbook('result.xlsx')
worksheet = workbook.add_worksheet()
i = 1
for key, item in result.items():
    worksheet.write('A' + str(i), key)
    worksheet.write('B' + str(i), item)
    i += 1
workbook.close()