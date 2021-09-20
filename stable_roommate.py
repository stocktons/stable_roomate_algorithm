# Credit to https://algorithmia.com/algorithms/matching/StableRoommateAlgorithm/source
# for the base code

# Updated to Python 3 syntax and modified to handle odd-numbered groups of people by 
# Loni Kuang and Sarah Stockton

# Reference(s) for the algorithm:
# 1. https://www.youtube.com/watch?v=9Lo7TFAkohE
# 2. http://www.dcs.gla.ac.uk/~pat/jchoco/roommates/papers/Comp_sdarticle.pdf
# 3. https://en.wikipedia.org/wiki/Stable_roommates_problem

import copy
import random


def apply(input):
    student_choices = input["preferences"]
    
    # if there are an odd number of students in the cohort, 
    # add "solo" as an option
    if len(student_choices) % 2 == 1:
        student_choices.update(
            {
                "solo": random.sample(student_choices.keys(), len(student_choices))
            }
        )

    # run the algorithm on input with updated student_choices
    verified_input = checkInput({"preferences": student_choices})

    params = step1(verified_input)

    param = step2(params)

    stable_preferences = step3(param)

    return parseOutput(stable_preferences)


class AlgorithmError(Exception):
    """Throws an error when Algorithm cannot be successfully completed."""


def checkInput(input):
    preferences = input["preferences"]

    allElements = []
    numElements = len(preferences)
    for i in preferences:
        allElements.append(i)
        if len(preferences[i]) > len(set(preferences[i])):
            raise AlgorithmError(
                "Invalid preference list. Duplicate element in a preference list.")

        # check if any of the preference lists are missing an element
        if len(preferences[i]) != numElements-1:
            raise AlgorithmError(
                "Invalid preference list. Missing element in a preference list.")

    if len(allElements) > len(set(allElements)):
        raise AlgorithmError(
            "Invalid preference list. Duplicate elements exist.")

    for i in allElements:
        for j in preferences:
            if i != j and i not in preferences[j]:
                raise AlgorithmError(
                    "Invalid preference list. Elements don't match in a preference list.")

    return input


def getKeyByVal(inptDict, inputVal):
    #breakpoint()
    for key, val in inptDict.items():
        if val == inputVal:
            return key


def removeCycle(preferences, table):
    tmpPreferences = preferences
    # remove the cycle matches symmetrically
    for i in range(len(table[0])-1):
        tmpPreferences[table[1][i]].remove(table[0][i+1])
        tmpPreferences[table[0][i+1]].remove(table[1][i])

    return tmpPreferences


def cycleExists(table):
    tableLeft = table[0]
    # tableRight = table[1]

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
        if numProposals[i] > len(proposals):
            raise AlgorithmError("A stable matching does not exist.")
        for j in inputList["preferences"][i]:
            if proposals[j] is None:
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


def step2(params): #removed outer parens proposals, inputList
    (proposals, inputList) = params
    tmpPreferences = copy.deepcopy(inputList["preferences"])
    for i in inputList["preferences"]:
        # Remove the right hand side of the preferred element
        proposalIndex = tmpPreferences[i].index(proposals[i])
        tmpPreferences[i] = tmpPreferences[i][:proposalIndex+1]
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
            if len(preferences[i]) >= 2 and first is True:
                # add element
                firstPreference = i
                table[0].append(firstPreference)
                # add second preference of element
                secondPreference = preferences[i][1]
                table[1].append(secondPreference)

                first = False

            elif first is False:
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


def parseOutput(preferences):
    rVal = {}
    for i in preferences:
        rVal[i] = preferences[i][0]

    return rVal


# Examples:
rithm_input = {
    "preferences": {
        "Loni": ["Mike", "Zach", "Nathan", "Sarah", "Alex"],
        "Sarah": ["Loni", "Alex", "Nathan", "Zach", "Mike"],
        "Mike": ["Loni", "Nathan", "Alex", "Zach", "Sarah"],
        "Alex": ["Loni", "Sarah", "Mike", "Nathan", "Zach"],
        "Zach": ["Nathan", "Sarah", "Mike", "Loni", "Alex"],
        "Nathan": ["Alex", "Zach", "Mike", "Sarah", "Loni"]
    }
}
odd_rithm_input = {
    "preferences": {
        "Loni": ["Mike", "solo", "Zach", "Nathan", "Sarah", "Alex", "Ray"],
        "Sarah": ["Loni", "Alex", "Nathan", "Ray", "solo", "Zach", "Mike"],
        "Mike": ["solo", "Ray", "Loni", "Nathan", "Alex", "Zach", "Sarah"],
        "Alex": ["Loni", "Sarah", "Ray", "Mike", "Nathan", "Zach", "solo"],
        "Zach": ["Nathan", "Sarah", "Mike", "Ray", "Loni", "solo", "Alex"],
        "Nathan": ["Alex", "Ray", "solo", "Zach", "Mike", "Sarah", "Loni"],
        "Ray" : ["Nathan", "Sarah", "Mike", "Loni", "Alex", "Zach", "solo"],
    }
}

stable_input = {
    "preferences": {
        "Charlie": ["Peter", "Paul", "Sam", "Kelly", "Elise"],
        "Peter": ["Kelly", "Elise", "Sam", "Paul", "Charlie"],
        "Elise": ["Peter", "Sam", "Kelly", "Charlie", "Paul"],
        "Paul": ["Elise", "Charlie", "Sam", "Peter", "Kelly"],
        "Kelly": ["Peter", "Charlie", "Sam", "Elise", "Paul"],
        "Sam": ["Charlie", "Paul", "Kelly", "Elise", "Peter"]
    }
}

stable_input2 = {
    "preferences": {
        "A": ["B", "D", "F", "C", "E"],
        "B": ["D", "E", "F", "A", "C"],
        "C": ["D", "E", "F", "A", "B"],
        "D": ["F", "C", "A", "E", "B"],
        "E": ["F", "C", "D", "B", "A"],
        "F": ["A", "B", "D", "C", "E"]
    }
}

unstable_input = {
    "preferences": {
        "Charlie": ["Peter", "Paul", "Elise"],
        "Peter": ["Paul", "Charlie", "Elise"],
        "Elise": ["Peter", "Charlie", "Paul"],
        "Paul": ["Charlie", "Peter", "Elise"]
    }
}

unstable_input2 = {
    "preferences": {
        "A": ["B", "C", "M"],
        "B": ["C", "A", "M"],
        "C": ["A", "B", "M"],
        "M": ["A", "B", "C"]
    }
}

invalid_input = {
    "preferences": {
        "A": ["B", "D", "F", "C", "E"],
        "B": ["D", "E", "F", "A", "C"],
        "C": ["D", "E", "F", "A", "B"],
        "D": ["F", "C", "A", "E", "B"],
        "E": ["F", "C", "D", "B", "A"],
        "A": ["A", "B", "D", "C", "E"]
    }
}

invalid_input2 = {
    "preferences": {
        "A": ["B", "D", "F", "C", "E"],
        "B": ["D", "E", "F", "A", "C"],
        "C": ["D", "E", "F", "A", "B"],
        "D": ["F", "C", "A", "E"],
        "E": ["F", "C", "D", "B", "A"],
        "F": ["A", "B", "D", "C", "E"]
    }
}

invalid_input3 = {
    "preferences": {
        "A": ["B", "D", "F", "C"],
        "B": ["D", "E", "F", "A"],
        "C": ["D", "E", "F", "A"],
        "D": ["F", "C", "A", "E"],
        "E": ["F", "C", "D", "B"],
        "F": ["A", "B", "D", "C"]
    }
}
