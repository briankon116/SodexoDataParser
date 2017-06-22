# Brian Kondracki
# This script takes Oracle financial exports and splits the data into files based on data type

import os, sys

# Stores the data and file type for the current line in the text file
date = ""
type = ""
multipleFiles = 0

# CHANGE THIS VARIABLE TO THE MAX NUMBER OF LINES PER EXPORT FILE YOU DESIRE
MAXLINES = 500000

# Buffer for the lines of each file type to later export into their respective destination files
fileLines = {"CDTL":[],"CHDR":[],"DSC":[],"GLID":[],"MID":[],"MNPR":[],"OT":[],"SUM":[],"SVC":[],"TAX":[],"TND":[]}

# Metadata for each data type. Holds information on the current number of files and lines per file respectively 
fileMetaData = {"CDTL":[0,0],"CHDR":[0,0],"DSC":[0,0],"GLID":[0,0],"MID":[0,0],"MNPR":[0,0],"OT":[0,0],"SUM":[0,0],"SVC":[0,0],
"TAX":[0,0],"TND":[0,0]}

def main(multipleFilesFlag, maxLinesPerFile):
    global multipleFiles, MAXLINES
    multipleFiles = multipleFilesFlag
    MAXLINES = int(maxLinesPerFile)
    
    # Keeps track of how many files have been completed so far
    count = 1

    # Main program loop that traverses the 'files' directory
    for file in os.listdir("files"):
        if(not file.startswith("GL")):
            continue

        # Extracts the date from the file name to later insert into the destination file
        global date
        date = file.split('_')[2]
        date = date.split('.')[0]

        file = "files/" + file

        with open(file, 'r') as f:
            parseFile(f)

        writeToFiles()

        test = str(count) + " files completed"
        count+=1
        print(test, end='\r')
    print("")

# Parses a given file, adds the date to each line and places them into the bucket in the hash table 'fileLines'
def parseFile(file):
    for line in file:
        line = str(line)

        line = line[:-1]

        line = fixLine(line)

        addLineToMatrix(type, line)

# Adds a new line to the hash table 'fileLines'
def addLineToMatrix(type, line):
    global fileLines
    if(type in fileLines):
        fileLines[type].append(line)
    else:
        lineToAdd = [line]
        fileLines[type] = lineToAdd

# Conditions each line to the proper format before adding it to the destination file
def fixLine(line):
    tokens = line.split('|')

    global type
    type = tokens[0]

    # Removes the data type from the current line
    tokens = tokens[1:]

    # If the data type is 'GLID' split the location code from the location name
    if(type == "GLID"):
        listA = [tokens[0]]
        listB = tokens[2:]

        listC = tokens[1].split("-")

        tokens = listA + listC + listB

    # Readd the '|' to the current line
    newLine = "|".join(str(x) for x in tokens)

    # Add the date to the line
    newLine = newLine + "|" + date

    return newLine

# Write the lines located in the hash table to their respective destination files
def writeToFiles():
    global fileLines
    global fileMetaData

    # Loop through each data type bucket in the hash table and export the lines to their files
    for key in fileLines:

        if(multipleFiles):
            fileName = "output/" + str(key) + "_" + str(fileMetaData[str(key)][0]) + ".txt"

            file = open(fileName, 'a')

            for line in fileLines[key]:
                file.write(line + "\n")

                fileMetaData[str(key)][1]+=1

                if(fileMetaData[str(key)][1]>=MAXLINES):
                    fileMetaData[str(key)][0]+=1
                    fileMetaData[str(key)][1]=0

                    file.close()
                    fileName = "output/" + str(key) + "_" + str(fileMetaData[str(key)][0]) + ".txt"
                    file = open(fileName, 'a')
                    
        else:
            fileName = "output/" + str(key) + ".txt"

            file = open(fileName, 'a')

            for line in fileLines[key]:
                file.write(line + "\n")

            
        fileLines[key] = []    
        file.close()


if(len(sys.argv) < 2):
       print("Usage: SodexoDataParser.py multipleFiles [maxFileSize]")
       print("\tmultipleFiles: y/n")
       print("\tmaxFileSize: Determines the maxiumum number of lines per file. Optional depending if multipleFiles was set to y")
elif(sys.argv[1] == 'y'):
    if(len(sys.argv) < 3):
        print("Usage: SodexoDataParser.py multipleFiles [maxFileSize]")
        print("\tmultipleFiles: y/n")
        print("\tmaxFileSize: Determines the maxiumum number of lines per file. Optional depending if multipleFiles was set to y")
        sys.exit(0)
    main(1, sys.argv[2])
elif(sys.argv[1] == 'n'):
    main(0,0)
else:
    print("Usage: SodexoDataParser.py multipleFiles [maxFileSize]")
    print("\tmultipleFiles: y/n")
    print("\tmaxFileSize: Determines the maxiumum number of lines per file. Optional depending if multipleFiles was set to y")
