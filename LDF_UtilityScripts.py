import csv
import os
import sqlite3
ADDRESS_DIR = "data/Addresses.csv"
DATA_DIR = "data"

def unknownBlankLabel(label):
    if label == '' or label == "-- None Selected --" or label == ' ':
        return True
    return False 

def fixApos(string):
    new_string = ""
    for i in range(0, len(string)):
        if string[i] == "'":
            new_string = new_string + "''"
        else:
            new_string = new_string + string[i]
    return new_string
       
def ageStrToInt(age):
    temp = age.replace(',', '')
    return int(temp)

def ageFilter(ages):
    temp = [ageStrToInt(age) for age in ages if age != '' and ageStrToInt(age) >= 18]
    return temp    

def createAgeBins(ages, age_bin):
    temp_bin = []
    for age in ages:
        if age <= age_bin[0] and age >= age_bin[1]:
            temp_bin.append(age)
    return temp_bin


def isNum(char):
    return(char >= '0' and char <= '9')

def hasNum(string):
    try:
        for i in range(0, len(string)):
            if isNum(string[i]):
                return i

    except Exception as e:
        print(str(e))
    return -1

def getNum(string, index):
    number = ""
    for i in range(index, len(string)):
        if isNum(string[i]) or string[i] == '.':
            number = number+string[i]
    return number

# Checks if character is within the alphabet.  
def isAlpha(char):
    return(char <= 'Z' and char >= 'A') or (char <= 'z' and char >= 'a')

# Removes number, non-alphabetic symbol, and space - characters to ease interpretation in the sorting algorithm. 
def alphaFormat(string):
    alpha_string = ""
    for char in string:
        if isAlpha(char):
            alpha_string += char.lower()
    return alpha_string

def getAddresses(address_list):
    alpha_addresses = []
    try:
        addresses = {}
        for address, ap_phase_id in address_list:
            addresses[alphaFormat(address)] = (address, ap_phase_id)
        alpha_addresses = [addresses[key] for key in sorted(addresses.keys())]
 
    except Exception as e:
        print("getAddress() Failed: "+str(e))

    return alpha_addresses

def tabNameFormat(tab_name):
    temp = tab_name.lower()
    temp = temp.split('_')
    for i in range(0, len(temp)):
        fir_let = temp[i][0].upper()
        temp[i] = fir_let + temp[i][1:len(temp[i])]
    formatted_tab_name = ' '.join(temp)
    return formatted_tab_name 

def excelColumnFromNumber(column):
    column_string = ""
    column_number = column;
    while (column_number > 0):    
        current_letter_number = (column_number - 1) % 26
        current_letter = chr(current_letter_number + 65)
        column_string = current_letter + column_string;
        column_number = (column_number - (current_letter_number + 1)) // 26
            
    return column_string;
        