# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 12:31:55 2020
Last updated Mon Jan 15 2024

@author: Dani Slavin

Financial records 2023
"""
global presetsFilepath
presetsFilepath = 'presets.csv'

import pandas
from datetime import date

#need this func before global variables
def loadPresets(filename=presetsFilepath):
    """
    opens the csv file in which the presets are stored, puts it in a dict assigning
    "variable" name to its definition
    
    Parameters
    ----------
    filename: string, optional
        the filename of the presets csv
        the default is presets
    
    Returns
    -------
    a dict mapping "variables" (first column) to "values" (second column)
    """
    #read file
    file = open(filename, encoding='utf-8-sig')
    f = file.read()
    file.close()
    
    #build up dictionary, changing types to correct ones that correspond to var name
    data = {}
    lines = f.split('\n')
    for line in lines[:-1]:#last line is blank, skip
        items = line.split(',')
        var, val = items[0], items[1]
            
        #determine type by first char
        if val[0] == "'":#single quotation = string
            val = str(val[1:-1])
            
        elif val[0] == "[":#list
            L = val[1:-1].split(";")
            val = []
            #all elements can be str or float            ### :)
            if L[0][0] == "'":#single quotation = string
                for el in L:
                    val.append(str(el[1:-1]).strip("'"))#strip is in case there was a leading space
            
            else:#float
                for el in L:
                    val.append(float(el))
        
        else:#number
            val = float(val)
        
        data[var] = val
    
    return data

#global variables
global today, presets
today = str(date.today())[5:]
presets = loadPresets(presetsFilepath)

#each row of a csv is returned as a list of string elements
class transaction:
    def __init__(self, row):#row is a list
        self.date = row[0]
        self.name = row[1]
        self.account = row[2]
        self.budget = row[3]
        self.amount = row[4]
    def getDate(self):
        date = self.date
        return date
    def getName(self):
        name = self.name
        return name
    def getAccount(self):
        acct = self.account
        return acct
    def getBudget(self):
        budget = self.budget
        return budget
    def getAmount(self):
        amt = self.amount
        return amt
    def __str__(self):
        nameCT = len(str(self.name))
        acctCT = len(str(self.account))
        budgetCT = len(str(self.budget))

        return str(self.date) + "\t" + str(self.name) + (7 - nameCT//4)*"\t" + \
            str(self.account) + (2 - acctCT//4)*"\t" + str(self.budget) + (5 - budgetCT//4)*"\t" + \
            str(self.amount)
        
class incomeClass:
    def __init__(self, row):
        self.date = row[0]
        self.amount = row[1]
        self.source = row[2]
    def getDate(self):
        return self.date
    def getAmount(self):
        return self.amount
    def getSource(self):
        return self.source
    def __str__(self):
        return str(self.date) + "\t" + str(self.amount) + "\t" + str(self.source)

def openFile(filename, index="date"):
    """
    opens csv file and returns it as pandas dataframe
    
    Parameters
    ----------
    filename : str
        filepath to CSV file to be opened
    index : str
        if indexed by something not default
    
    Returns
    -------
    the file as a pandas datafrome object
    """
    table = pandas.read_csv(filename, index_col=index)
    return table

def printLine():
    """
    prints a dashed line of uniform length

    Returns
    -------
    None.

    """
    print("--------------------")

def printList(transactionList):
    """
    prints a table from a list of transaction objects
    
    Parameters
    ----------
    transactionList : list
        list of transaction objects

    Returns
    -------
    None.
    """
    for item in transactionList:
        print(item)


def convertToClass(file, income=False):
    """
    takes in panda dataframe and converts it into a list of transaction objects
    (or income objects if income is True)
    
    Parameters
    ----------
    file : panda dataframe
        csv file as a panda dataframe with a list of transactions
    income : bool, optional
        True if they should instead be income objects over transaction

    Returns
    -------
    a list of transaction (or income) class objects

    """
    transactions = []
    
    for row in file.itertuples(index=False):
        if income:
            line = incomeClass(row)
        else:
            line = transaction(row)
        transactions.append(line)
    
    return transactions


def filepathToTransactionList(filename=presets['filepath'], income=False):
    """
    takes in a filepath and converts it into a list of transaction objects
    (or income objects if income is True)

    Parameters
    ----------
    filename : string, optional
        the filename to be converted into list
        the default is the global filepath from presets
    income : bool, optional
        should be True if the file is income rather than transactions

    Returns
    -------
    a list of transaction (or income) objects, the data in the file
    """
    return convertToClass(openFile(filename, None), income)

def total(condition, transactionList):
    """
    generalizes all the "total" functions: takes in a condition func that returns 
    a bool and transaction list, returns a list of all transactions from the given 
    list that satisfy the func.

    Parameters
    ----------
    condition : func
        condition to satisfy--must return a bool
    transactionList : list
        list of transaction objects, the csv file data

    Returns
    -------
    a list of transaction objects that satisfy the search

    """
    out = []
    for item in transactionList:
        if condition(item):
            out.append(item)
    return out

def totalName(query, transactionList):
    """
    creates a list of transactions with the given query in its name
    
    Parameters
    ----------
    query : str
        the string to search for in names
    transactionList : list
        list of transaction objects, the csv file data
        
    Returns
    -------
    a list of transaction objects that satisfy the search
    """
    def nameCond(transaction):
        return query in transaction.getName()
    
    return total(nameCond, transactionList)
    
def totalBudget(budget, transactionList):
    """
    adds the total left in a particular budget, from list of transactions
    
    Parameters
    ----------
    budget : string
        the name of a budget in the file
    transactionList : list
        list of transaction objects, the csv file data

    Returns
    -------
    a list of transaction objects that are in the given budget
    """
    def budgetCond(transaction):
        return transaction.getBudget() == budget

    return total(budgetCond, transactionList)

def totalAccount(account, transactionList):
    """
    adds the total left in a particular account, from list of transactions
    
    Parameters
    ----------
    account : string
        the name of an account in the file
    transactionList : list
        list of transaction objects, the csv file data

    Returns
    -------
    a list of transaction objects that are in the given account
    """
    def accountCond(transaction):
        return transaction.getAccount() == account
    
    return total(accountCond, transactionList)

def totalDate(start, end, transactionList):
    """
    from list of transactions, returns a list from start date to end date (inclusive)

    Parameters
    ----------
    start : string, format MM-DD
        string representation of a month in same format as transaction class object
    end : string, format MM-DD
        same as start
    transactionList : list
        list of transaction class objects, the csv file transaction data

    Returns
    -------
    a list from the transaction list that are from that date range
    """
    def dateCond(transaction):
        return transaction.getDate() >= start and transaction.getDate() < end
            
    return total(dateCond, transactionList)

def totalSource(source, incomeList):
    """
    from a list of income objects, returns a list of the ones that come from the 
    given source

    Parameters
    ----------
    query : str
        the name of the employer/source of income
    incomeList : list
        a list of income objects, the csv file income data

    Returns
    -------
    a list from the income list that are from that source

    """
    def sourceCond(transaction):
        return transaction.getSource() == source
    
    return total(sourceCond, incomeList)

def add(totalList):
    """
    adds the amount for a list of transaction objects
    
    Parameters
    ----------
    totalList : list
        list of transaction objects to be totaled

    Returns
    -------
    float, a total of the amounts of the objects in the list, rounded to cents
    """
    total = 0
    for item in totalList:
        total += item.getAmount()
    total = round(total, 2)
    return total
        

def checkInput(inp,typ,all_bool=False):
    """
    get correct input for various types of entry fields

    Parameters
    ----------
    inp : str
        user input
    typ : str
        must be in list: ["date","name","account","budget","amount","filter","income_filter","csv"]
    all_bool : bool
        True if "all" is a valid input (in which case, returns list of all budgets/accounts)

    Returns
    -------
    str in correct given format

    """    
    #if it's 'exit', return None
    if inp == 'exit' or inp == 'n' or inp == 'cancel' or inp == 'go away!':
        print("Okay, backing up...")
        return None
    
    if typ == "date":
        fail = True
        count = 0
        while fail:
            fail = False
            #find the index of the hyphen
            hyphen_i = inp.find('-')

            if hyphen_i < 0:#no hyphen
                #check for slash
                hyphen_i = inp.find('/')
            
            if hyphen_i < 0:#no slash and no hyphen
                fail = True
                print("Please include a hyphen separating month and day! (e.g. 11-10 for Nov. 10th)")

            else:
                try:
                    #check before hyphen for month format
                    month = int(inp[0:hyphen_i])
                    if month < 1 or month > 12:
                        print("Please enter a month between 1 and 12.")
                        fail = True
                    
                    #check after hyphen for day format
                    day = int(inp[hyphen_i+1:])
                    if day < 1 or day > 31:
                        print("Please enter a valid day of the month (between 1 and 31).")
                        fail = True
                
                except ValueError:
                    #if they entered letters
                    count += 1
                    fail = True
                    print("Please only enter digits and a hyphen.")
                    if count >= 3:
                        print("Like, dude, why you keep entering letters and stuff??")

            if fail:
                inp = input("Date (MM-DD): ")

        #now reformat if needed so it's actually MM-DD format
        #currently month and day are each a proper int
        inp = str(month).zfill(2) + '-' + str(day).zfill(2)
                               
    elif typ == "name":
        fail = True
        while fail:
            fail = False
            
            if "," in inp:
                fail = True
                print("Please do not use commas in the name.")
            
            if len(inp) > 27:
                fail = True
                print("That name is too long. Please keep it 27 characters or less.")
            
            if fail:
                inp = input("Name: ")
    
    elif typ == "account":
        accounts = presets['accounts']
        inp = inp.lower()
        
        while inp not in accounts and inp != "null":
            #check for all
            if inp == "all" and all_bool:
                inp = accounts #will return a list of all account names
                break
            acct_list_str = ""
            for acct in accounts:
                acct_list_str += acct
                acct_list_str += ", "
            print(f"{inp} is not a valid account. The valid accounts are {acct_list_str}and null.")
            inp = input("Account: ")
            inp = inp.lower()
            
    elif typ == "budget":
        budgets = presets['budgets']
        inp = inp.lower()
        while inp not in budgets and inp != "null":
            #check for all
            if inp == "all" and all_bool:
                inp = budgets #will return a list of all budget names
                break
            budget_list_str = ""
            for budget in budgets:
                budget_list_str += budget
                budget_list_str += ", "
            print(f"{inp} is not a valid budget. The valid budgets are {budget_list_str}and null.")
            inp = input("Budget: ")
            inp = inp.lower()
    
    elif typ == "amount":
        while type(inp) == str:
           try:
               inp = float(inp)
           except ValueError:
               print("That is an invalid entry. Please enter a number.")
               inp = input("Amount: ")
               
    elif "filter" in typ:#filter or income_filter
        inp = inp.lower()
        if typ == "income_filter":
            filter_list = ["date","source","none"]
        else:
            filter_list = ["budget","account","date","name","none"]
            
        string_list = ""
        for _ in filter_list[:-1]:
            string_list += _
            string_list += ", "
            
        while inp not in filter_list:
            print(f"{inp} is not a valid filter type. Please choose {string_list}or none.")
            inp = input("Filter: ")
            inp = inp.lower()
                
    elif typ == "csv":
        found = False
        while not found:
            try:
                f = open(inp)
                f.close()
                found = True
    
            except FileNotFoundError:
                if inp[-4:] != ".csv":
                    while inp[-4:] != ".csv":
                        print(f"{inp} does not end in '.csv'. Please enter the name of a .csv file.")
                        inp = input("Filename: ")
                else:#a csv name, but still not found
                    print(f"{inp} was not found in the local file. Please enter the name of a file",\
                          "or filepath in the local directory.")
                    inp = input("Filename: ")
    
    return inp

def askEach(category):
    """
    asks for an amount for each value in an iterable, returns a list of values in 
    the corresponding order to the input iterable
    
    Parameters
    ----------
    category : iter
        an iterable for which each element will be asked a value
        
    Returns
    -------
    list of values given by user
    """
    values = []
    for each in category:
        inp = input(f"How much is in {each}? ")
        inp = checkInput(inp, 'amount')
        values.append(inp)
    return values

def init():
    """
    creates initializing transactions in a blank csv file; makes sure account and budget 
    balances are what's given
    
    Returns
    -------
    None
    """
    #ask for values for accounts and for budgets
    printLine()
    print("Okay! First thing you need to do is let me know how much money is in each",\
          "account and budget.")
    
    acct_amts = askEach(presets['accounts'])
    budg_amts = askEach(presets['budgets'])
    
    #make sure total for accounts == total for budgets
    sum_acct = sum(acct_amts)
    sum_budg = sum(budg_amts)
    while sum_acct != sum_budg:
        print("The amounts in your accounts is not equal to the amounts in your budgets.",\
              f"Total in accounts is {sum_acct}, while total in budgets is {sum_budg}.",\
              "Please try again.")
        acct_amts = askEach(presets['accounts'])
        budg_amts = askEach(presets['budgets'])
        sum_acct = sum(acct_amts)
        sum_budg = sum(budg_amts)
    
    #create transactions to init accounts
    for i, amt in enumerate(acct_amts):
        #[date, name, account, budget, amount]
        data = [today, 'init', presets['accounts'][i], 'null', amt]
        writeTransaction(data)
    
    #create transactions to init budgets
    for i, amt in enumerate(budg_amts):
        #[date, name, account, budget, amount]
        data_from = [today, 'init', 'null', 'null', -1*amt]
        data_to = [today, 'init', 'null', presets['budgets'][i], amt]
        writeTransfer(data_from, data_to)
    
    #check with user that account totals are correct
    printLine()
    print("It's all in the file now! Let's just make sure that the account totals",\
          "match.")
    transactionList = filepathToTransactionList()
    checkBalances(transactionList)

def checkBalances(transactionList, checkFilepath=presets['checkFilename']):
    """
    checks that personal records and bank records match, from list of transactions
    and filepath for the file to be written to
    
    Parameters
    ----------
    transactionList : list
        list of transaction objects that represents the transactions csv file
    checkFilepath : string, optional
        filepath for the check balances csv file
        default is the checkFilename str found in presets dict

    Returns
    -------
    None.
    """
    #convert check file to panda df, other inits
    works = True
    checkFile = openFile(checkFilepath, "date")
    
    #loop until the user doesn't exit
    repeat = True
    while repeat:
        repeat = False
        #go through each account (except cash)
        accounts = presets['accounts']
        for i, acct in enumerate(accounts):
            #don't check cash every week (it has its own function)
            if acct == 'cash':
                continue
            
            #bank amt
            bal = input(f"Please enter the amount in the {accounts[i]} account (if you previously "\
                        "typed a number wrong, you can type 'exit' now to restart): ")
            bal = checkInput(bal,"amount")
            if bal is None:
                repeat = True
                break
            
            #add total
            totalList = totalAccount(accounts[i],transactionList)
            total = add(totalList)
            
            #check for match
            if bal != total:
                works = False
                print("Records do not match.\nTotal in records is", total)
            else:
                checkFile = pandas_append(checkFile, [accounts[i], bal, True], 
                                          today, "date")
                print("Records match")
    
    #write to file
    if works:
        checkFile.to_csv(checkFilepath)


def checkCash(checkFilepath=presets['checkFilename']):
    """
    checks the the counted cash total is the same as recorded

    Parameters
    ----------
    checkFilepath : str, optional
        filepath the the csv with check records. 
        The default is the str associated checkFilename in presets dict.

    Returns
    -------
    None.

    """
    #get transaction list
    transactionList = filepathToTransactionList()
    
    #convert check file to panda df, other inits
    works = True
    checkFile = openFile(checkFilepath, "date")
    
    cashBal = float(input("Please enter the amount you counted in cash: "))
    cashBal = checkInput(cashBal,"amount")
    
    cashTotalList = totalAccount("cash", transactionList)
    cashTotal = add(cashTotalList)
    
    if cashBal != cashTotal:
        works = False
        print("Records do not match.\nTotal in records is", cashTotal)
    else:
        checkFile = pandas_append(checkFile, ["cash", cashBal, True], 
                                  today, "date")
        print("Records match")
        
    #write to file
    if works:
        checkFile.to_csv(checkFilepath)


def sort(filename=presets['filepath']):
    """
    sorts the csv file by date (using built-in pandas mergesort), writes it to the file

    Parameters
    ----------
    filename : str, optional
        filepath to the transaction history to be sorted
        default is the str associated with filepath in the presets dict
    
    Returns
    -------
    none

    """
    #open as pandas
    file = openFile(filename)
    
    #sort by date
    file = file.sort_values("date",kind="mergesort")
    
    #rewrite file
    file.to_csv(filename)

def pandas_append(file, data, name, index):
    """
    takes a file and appends a line of data (as a list) to it

    Parameters
    ----------
    file : pandas DataFrame
        the csv file to be appended to
    data : list
        a list of data to be appended
    name : str
        what this data will be indexed by
    index : str
        name of the first column

    Returns
    -------
    muted file with data appended

    """    
    lineSeries = pandas.Series(data=data, name=name, index=file.columns)
    file = pandas.concat([file, lineSeries.to_frame().T])
    return file.rename_axis(index, axis=0) # set name of index to date
    
def writeTransaction(line, filename=presets['filepath']):
    """
    takes a transaction (as a list) and adds it to the end of a csv file, and sorts file by date
    
    Parameters
    ----------
    line : list
        the transaction to be added in form [date, name, account, budget, amount]
    filename : string, optional
        the name of the file being written to
        the default is filename (associated in presets dict)

    Returns
    -------
    None
    """
    #open file
    file = openFile(filename)
    
    #create series and concat to file (with helper) 
    file = pandas_append(file, line[1:], line[0], "date")
    file.to_csv(filename)

    #sort list by date
    file = file.sort_values("date")

    file.to_csv(filename)

def changePresets(filepath=presetsFilepath):
    """
    changes the presets csv file, and globals a new dict with the updated presets

    Parameters
    ----------
    filepath : str, optional
        the name of the file that the presets are stored in
        default is the global presetsFilepath (top of program)
        
    Returns
    -------
    None.

    """
    printLine()
    #show list of preset variables
    for var in presets:
        print(var)
    
    #ask which to change
    inp = input("Please enter the names of each of the presets, from the list above, "\
                "that you would like to change, separated by commas: ")
    to_change = (inp.replace(" ","")).split(",")#get rid of spaces and split by comma
    
    for variable in to_change:
        #check input
        try:
            og_value = presets[variable]
        except KeyError:
            while variable not in presets:
                variable = input(f"{variable} not found in presets. Please enter "\
                                 "a valid preset name, or type 'skip' to move on. ").lower()
                if variable == 'skip':
                    break
                
            if variable != 'skip':
                og_value = presets[variable]
        
        if variable == 'skip':
            continue
        
        printLine()
        print(f"Working on changing {variable}.")
        
        if not isinstance(og_value, list):#if value is a single item
            print(f'Current setting is {og_value}.')
            new = input(f'Please enter the desired {variable.replace("_", " ")}: ')
            #do a checkInput on this depending on type of variable
            if isinstance(og_value, str):
                if og_value[-4:] == ".csv":
                    presets[variable] = checkInput(new, 'csv')
                else:
                    presets[variable] = new
                    
        else:#value is a list
            #paycheck_split gets special case
            if variable == 'paycheck_split':
                budgets = presets['budgets']
                
                #show preexisting data
                print("The current split for your budgets are as follows:")
                for i, el in enumerate(og_value):
                    print(f"{budgets[i]}\t{el}")
                    
                #get input
                inp = input("Which budget(s) would you like to edit? Please separate "\
                             "by commas: ").split(",")
                budgs_inp = []
                for b in inp:
                    budgs_inp.append(b.strip())
                
                #loop in case it doesn't total right                    
                adds = False
                while not adds:
                    #correct/check input
                    budgs = []
                    for budg in budgs_inp:
                        budgs.append(checkInput(budg, 'budget'))
                    
                    #convert accounts to indices
                    budgs_i = []
                    for budg in budgs:
                        budgs_i.append(budgets.index(budg))
                        
                    #go through each account and ask for new values
                    new_values = og_value[:]
                    for j, budg_i in enumerate(budgs_i):
                        new = input('What fraction of the paycheck would you like '\
                                    f'to be put in {budgs[j]}? ')
                        new = checkInput(new, 'amount')
                        
                        new_values[budg_i] = new
                    
                    #check that it totals to 1
                    if abs(sum(new_values) - 1) > .0001:#account for float error
                        print("These values don't seem to sum to 1! Please re-enter.\n"\
                              "(If they do and this seems to be an error, please let Dani know.)")
                        adds = False
                    else:
                        adds = True
                
            #handle other lists
            else:
                #can either be accounts or budgets, both are lists of strings
                print(f"These are your current {variable}:")
                for val in og_value:
                    print(val)
                
                #options are add, remove, or modify
                #add
                add = input(f"Would you like to add any {variable}? Y/N ").lower()
                if add == 'y' or add == 'yes' or add == 'yee':
                    new_raw = input(f"Please enter the names of the new {variable} you "\
                                "would like to add, separated by commas: ").split(",")
                    new = []
                    for n in new_raw:
                        new.append(n.strip())
                    
                    for name in new:
                        #make sure it's a new name
                        while name in og_value:
                            name = input(f"{name} is already in {variable}! Please enter a "\
                                         "different name, or enter 'skip' to move on: ").lower()
                            if name == 'skip':
                                break

                        if name == 'skip':
                            printLine()
                            print(f"The following are your current {variable}:")
                            for item in og_value:
                                print(item)
                            continue
                        
                        #passes all checks
                        presets[variable].append(name)
                        og_value = presets[variable]#reset for remove/modify
                        
                    printLine()
                    print(f"The following are your current {variable}:")
                    for item in og_value:
                        print(item)
                
                #remove
                rem = input(f"Would you like to remove one of the above {variable}? Y/N ").lower()
                if rem == 'y' or rem == 'yes' or rem == 'yee':
                    rem_raw = input(f"Please enter the names of the new {variable} you "\
                                "would like to remove, separated by commas: ").split(",")
                    rem = []
                    for r in rem_raw:
                        rem.append(r.strip())
                    
                    for name in rem:
                        #make sure it's an existing name
                        while name not in og_value:
                            name = input(f"{name} is not in {variable}! Please enter an "\
                                         "existing name, or enter 'skip' to move on: ").lower()
                            if name == 'skip':
                                break

                        if name == 'skip':
                            continue
                        
                        #passes checks
                        presets[variable].remove(name)
                        og_value = presets[variable]#reset for later iterations
                        
                        printLine()
                        for item in og_value:
                            print(item)
                
                #modify
                mod = input(f"Would you like to modify one of the above {variable}? Y/N ").lower()
                if mod == 'y' or mod == 'yes' or mod == 'yee':
                    mod_raw = input(f"Please enter the names of the {variable} you "\
                                "would like to modify, separated by commas: ").split(",")
                    mod = []
                    for m in mod_raw:
                        mod.append(m.strip())
                    
                    for name in mod:
                        printLine()
                        print(f"Working on modifying the {name} {variable}.")
                        #make sure it's an existing name
                        while name not in og_value:
                            name = input(f"{name} is not in {variable}! Please enter an "\
                                         "existing name, or enter 'skip' to move on: ").lower()
                            if name == 'skip':
                                break

                        if name == 'skip':
                            continue
                        
                        new_name = input("Please enter the new name you would like to "\
                                         f"change {name} to: ").lower()
                        #make sure it's a new name
                        while new_name in og_value:
                            new_name = input(f"{new_name} is already in {variable}! Please "\
                                             "enter a different name, or enter 'skip' to move on: ").lower()
                            if new_name == 'skip':
                                break

                        if new_name == 'skip':
                            continue
                        
                        #change old name to new_name
                        index = presets[variable].index(name)
                        presets[variable][index] = new_name
                        og_value = presets[variable]#reset for later iterations
                        
                        
        #after modifying everything in presets dict, write new information to file
        #(restart from scratch and use pandas to create csv)
        
        #put in expected format
        data = []
        for var, val in presets.items():
            #if list, change , to ;
            if isinstance(val, list):
                val = str(val).replace(",", ";")
            
            #if str, add single quotations
            elif isinstance(val, str):
                val = "'" + val + "'"
                
            #otherwise it's a number/float and needs no editing
            data.append([var, val])
        
        #use pandas to overwrite file
        dataframe = pandas.DataFrame(data)
        dataframe.to_csv(filepath, index=False, header=False)

def writeTransfer(start, end):
    """
    actually writes the transaction as two separate writeTransaction lines

    Parameters
    ----------
    start : list
        the data of the first transaction, where it's being withdrawn, in the form 
        [date, name, account_from, budget_from, amount (neg)]
    end : list
        the data of the second transaction, where it's being deposited, in the form 
        [date, name, account_to, budget_to, amount]

    Returns
    -------
    None.

    """
    #write 2 transactions, one for withdrawal, one for deposit
    writeTransaction(start)
    writeTransaction(end)


def transfer(filename=presets['filepath']):
    """
    asks for transfer information and adds it to the record as 2 separate transactions,
    without changing total amount

    Parameters
    ----------
    filename : TYPE, optional
        the name of the file being written to
        the default is filepath from presets dict

    Returns
    -------
    None.

    """
    #gather info
    print("Please enter the following information about the transfer. Type 'exit' at any time to cancel.")
    date = input("Date (MM-DD): ")
    date = checkInput(date,"date")
    if date is None:
        return
        
    name = input("Name: ")
    name = checkInput(name,"name")
    if name is None:
        return
        
    account_from = input("Account being withdrawn from: ")
    account_from = checkInput(account_from,"account")
    if account_from is None:
        return
    
    account_to = input("Account being deposited to: ")
    account_to = checkInput(account_to,"account")
    if account_to is None:
        return
    
    budget_from = input("Budget being withdrawn from: ")
    budget_from = checkInput(budget_from,"budget")
    if budget_from is None:
        return

    budget_to = input("Budget being deposited to: ")
    budget_to = checkInput(budget_to,"budget")
    if budget_to is None:
        return
    
    amount = input("Amount (non-negative): ")
    amount = checkInput(amount,"amount")
    if amount is None:
        return

    writeTransfer([date,name,account_from,budget_from,-1*amount], \
                  [date,name,account_to,budget_to,amount])
    

def paycheck(amount, filename=presets['filepath'], paycheckFile=presets['paycheckFilename']):
    """
    adds paycheck balance, split up into different budgets, to csv transaction file

    Parameters
    ----------
    amount : float
        the amount of the paycheck
    filename : string, optional
        filepath to the file the transactions will be added to
        the default is filepath from presets dict
    paycheckFile : string, optional
        filepath to the file the paycheck records are in
        the default is paycheckFilename from presets dict

    Returns
    -------
    None.

    """
    #turn global dict variables into more convenient local ones
    budgets = presets['budgets']
    round_budget = presets['round_budget']
    
    print("Type 'exit' to cancel paycheck input.")
    
    #ask for input
    paydate = input("Date of paycheck (MM-DD): ")
    paydate = checkInput(paydate,"date")
    paycheck_account = input("Account the paycheck is in: ")
    paycheck_account = checkInput(paycheck_account, "account")
    if paydate is None:
        return
    
    #split amount
    total = []
    for i in range(len(budgets)):
        total.append(round(amount*presets['paycheck_split'][i],2))
        
    #check
    if int(round(sum(total), 2)*100) != int(amount*100):
        dif = round(amount - round(sum(total), 2), 2)
        total[budgets.index(round_budget)] += dif
        count = 0
        while round(sum(total), 2) != amount:
            count += 1
            total[budgets.index(round_budget)] += .01
            
        if round(sum(total), 2) != amount:
            statement = ""
            for i in range(len(budgets)):
                statement += "\n" + str(budgets[i]) + " = " + str(total[i])
                
            print("Does not add up, ask for help","\ntotal =", sum(total),statement)
            adds = False
        
        else:
            print("Off by "+"{:.2f}".format(round(dif + count/100, 2))+", corrected from %s budget." % round_budget)
            adds = True

    else:
        print("Adds up")
        adds = True
    
    if adds:
        #add to paycheck csv
        payfile = openFile(paycheckFile)
        payfile = pandas_append(payfile, [amount, presets['employer']], 
                                paydate, "date")
        payfile.to_csv(paycheckFile)
        
        #add to transactions csv
        file = openFile(filename)
        i = 0
        for split in total:
            if split != 0:
                file = pandas_append(file, ["paycheck",paycheck_account,budgets[i],split], 
                                     paydate, "date")
                file.to_csv(filename)
                
                i += 1


def getTransaction():
    """
    ask user for transaction information (no intro print statement)

    Returns
    -------
    a list of information in the format [date, name, account, budget, amount], 
    or None if the user cancelled
    """
    print("Enter 'exit' at any time to cancel this transaction.")
    
    date = input("Date of transaction (MM-DD): ")
    date = checkInput(date,"date")
    if date is None:
        return
        
    name = input("Name: ")
    name = checkInput(name,"name")
    if name is None:
        return
            
    amount = input("Amount: ")
    amount = checkInput(amount,"amount")
    if amount is None:
        return
    
    account = input("Account: ")
    account = checkInput(account,"account")
    if account is None:
        return
        
    budget = input("Budget: ")
    budget = checkInput(budget,"budget")
    if budget is None:
        return

    return [date, name, account, budget, amount]


def weekly(filename=presets['filepath']):
    """
    goes through the weekly routine (now called 'checkup')

    Parameters
    ----------
    filename : string, optional
        filename of the csv file with records in it
        the default is filepath from presets dict

    Returns
    -------
    None.

    """
    #add paycheck
    paycheckAsk = input("First we'll add the paycheck. Did you get a paycheck that you'd like to add? Y/N  ")
    if paycheckAsk.lower() == "y" or paycheckAsk.lower() == "yes" or paycheckAsk.lower() == "yee":
        print("Please enter the following information about the paycheck.")
        amount = input("Amount: ")
        amount = checkInput(amount,"amount")
        if amount is not None:
            paycheck(amount)
        
    print("Okay, moving on.\n--------------------\nNow are the bills.")
        
    #RENT
    restart = True
    while restart:
        restart = False
        rent_pay = input("Has the monthly rent check been cashed? Y/N  ")
        if rent_pay.lower() == "y" or rent_pay.lower() == "yes" or rent_pay.lower() == "yee":
            print("Enter 'exit' at any time to restart.")
            print("Check the checking account for low balance! And check against cc bill.")
            date_cashed = input("What date was the check cashed on? (MM-DD): ")
            date_cashed = checkInput(date_cashed,"date")
            if date_cashed is None:
                restart = True
            else:
                writeTransaction([date_cashed,"rent check","mit-ch","rent",-1*presets['monthly_rent']])
        
    #INTERNET
    restart = True
    while restart:
        restart = False
        int_pay = input("Has the internet bill been paid? Y/N  ")
        if int_pay.lower() == "y" or int_pay.lower() == "yes" or int_pay.lower() == "yee":
            print("Enter 'exit' at any time to restart.")
            print("Make sure autopay went through!")
            date = input("What date was it paid on? (MM-DD): ")
            date = checkInput(date,"date")
            if date is None:
                restart = True
            else:
                writeTransaction([date,"internet bill","mit-ch","rent",-1*presets['monthly_internet']])
        
    print("Perfect (I hope...).\n--------------------")

    #add new transactions
    print("Please enter the information for new transactions (except paychecks and recurring payments)",\
          "below.")
    ask = input("Done? Y/N  ")
    if ask.lower() == "y" or ask.lower() == "yes" or ask.lower() == "yee":
        done = True
    else:
        done = False
    while not done:
        printLine()
        data = getTransaction()
        if data is not None:
            writeTransaction(data)
        
        ask = input("Done? Y/N  ")
        if ask.lower() == "y" or ask.lower() == "yes" or ask.lower() == "yee":
            done = True
            
    print("Finished with new transactions.\n--------------------\nLast we'll check that the totals are the same.")
            
    #check balances
    #need transactions in list form
    transactionList = filepathToTransactionList()
    checkBalances(transactionList)
        
    print("All done!")


def helper():
    """
    Prints a string to the screen explaining all the functions and what they do

    Returns
    -------
    None.
    """
    print("""
--------------------
2023 UPDATE NOTES:
    -Presets (such as filenames, monthly rent, etc.) have been put into a separate 
        csv file so the user can interact with the program to change them, rather 
        than having to go into the code
    -Initialization is now a function of the program and doesn't have to be done 
        "manually" by the user
    -Added functionality for going back if you typed something wrong
    -Can now filter history by searching for something in the name
    -Can also filter history by multiple filters
    -Can now filter income records
    -Can check all budgets or accounts at once
    -Updated use of pandas to remove append (deprecated)
    -Minor typos / rewording
    -Easter eggs!

help - shows this, a list of commands you can use and what they do

init - to use at the start of the year, initializes all budgets and accounts

checkup - regular check-up (checking financial health): add paycheck, 
    add transactions, and check to make sure the balances match
    
presets - change the presets such as file names, budgets, accounts, and paycheck split
    
budget - checks the balance of any particular budget

account - checks the balance of any particular account

history - shows a full transaction history (can also filter by certain parameters)

balance - checks to make sure the bank's balance matches personal records

cash - checks to make sure counted cash total matches digital records

transaction - add new transactions to the records

paycheck - add a paycheck

income - view previous paychecks

transfer - transfer an amount of money from one account and budget to another

sort - sorts the transaction history csv file by date (this should be done 
    automatically done after every step that needs it)

quit - end the program    

Ask Dani if you have any questions or need help! :)
          
          """)
        
def __main__():
    print("Welcome to Dani's Financial Manager 2023!")
    
    q = False
    
    while not q:
        printLine()
                
        entry = input("Please enter a command. Type 'help' for options: ")
        entry = entry.lower()
        
        if entry == "help":
            helper()
        
        elif entry == "init":
            init()
        
        elif entry == "checkup":
            weekly()
            
        elif entry == "presets":
            changePresets()
            
        elif entry == "budget":
            budget = input("Please enter which budget you would like to check (type 'all' too see all budgets): ")
            budget = checkInput(budget,"budget",True)
            if budget is not None:
                #turn into a list if it isn't
                if not isinstance(budget, list):
                    budget = [budget]
                transactionList = filepathToTransactionList()
                # print(f'{transactionList=}')
                for budg in budget:
                    budgetList = totalBudget(budg, transactionList)
                    # print(f'{budg=}, {budgetList=}, {add(budgetList)=}')
                    print(budg, "\t", add(budgetList))
            
        elif entry == "account":
            account = input("Please enter which account you would like to check (type 'all' to see all accounts): ")
            account = checkInput(account,"account",True)
            if account is not None:
                #turn into a list if it isn't
                if not isinstance(account, list):
                    account = [account]
                transactionList = filepathToTransactionList()
                for acc in account:
                    accountList = totalAccount(acc, transactionList)
                    print(acc, "\t", add(accountList))
            
        elif entry == "history":
            filterList = filepathToTransactionList()
            
            filterType = input("How would you like to filter the list?  ")
            filterType = filterType.lower()
            filterType = checkInput(filterType,"filter")
            
            while filterType != "none":
                    
                if filterType == "budget":
                    budget = input("Please enter which budget you would like to filter by: ")
                    budget = checkInput(budget,"budget")
                        
                    filterList = totalBudget(budget, filterList)
                    
                elif filterType == "account":
                    account = input("Please enter which account you would like to filter by: ")
                    account = checkInput(account,"account")
                    
                    filterList = totalAccount(account, filterList)
                    
                elif filterType == "date":
                    start_date = input("Please enter the start date of the range (MM-DD): ")
                    start_date = checkInput(start_date,"date")
                    
                    end_date = input("Please enter the end date of the range (MM-DD): ")
                    end_date = checkInput(end_date,"date")
                    
                    filterList = totalDate(start_date, end_date, filterList)
                
                elif filterType == "name":
                    query = input("Please enter what text you would like to search for: ").lower()
                    filterList = totalName(query, filterList)
                    
                filterType = input("How would you like to further filter the list?  ")
                filterType = filterType.lower()
                filterType = checkInput(filterType,"filter")
                    
            printList(filterList)

        elif entry == "balance":
            transactionList = filepathToTransactionList()
            checkBalances(transactionList)
            
        elif entry == "cash":
            checkCash()
        
        elif entry == "transaction":
            print("Please enter the information for new transactions (except paychecks)",\
                  "below (or enter 'done' if done with adding new transactions).")
            ask = input("Done? Y/N  ")
            if ask.lower() == "y" or ask.lower() == "yes" or ask.lower() == "yee":
                done = True
            else:
                done = False
            while not done:
                printLine()
                data = getTransaction()
                if data is not None:
                    writeTransaction(data)
                
                ask = input("Done? Y/N  ")
                if ask.lower() == "y" or ask.lower() == "yes" or ask.lower() == "yee":
                    done = True
            
        elif entry == "paycheck":
            print("Please enter the following information about the paycheck.")
            amount = input("Amount: ")
            amount = checkInput(amount,"amount")
            if amount is not None:
                paycheck(amount)
                sort()
        
        elif entry == "income":
            incomeList = filepathToTransactionList(presets['paycheckFilename'], True)
            
            filterType = input("How would you like to filter the list?  ")
            filterType = filterType.lower()
            filterType = checkInput(filterType,"income_filter")
            
            while filterType != "none":

                if filterType == "date":
                    start_date = input("Please enter the start date of the range (MM-DD): ")
                    start_date = checkInput(start_date,"date")
                    
                    end_date = input("Please enter the end date of the range (MM-DD): ")
                    end_date = checkInput(end_date,"date")
                    
                    incomeList = totalDate(start_date, end_date, incomeList)
                
                elif filterType == "source":
                    source = input("What source are you filtering by? ").lower()
                    
                    incomeList = totalSource(source, incomeList)
                    
                filterType = input("How would you like to further filter the list?  ")
                filterType = filterType.lower()
                filterType = checkInput(filterType,"income_filter")
                    
            printList(incomeList)
            
            ans = input("Would you like to sum these paychecks? Y/N  ")
            ans = ans.lower()
            if ans == "y" or ans == "yes" or ans == "yee":
                total = add(incomeList)
                print(total)
                
        elif entry == "transfer":
            transfer()
            sort()
            
        elif entry == "sort":
            sort()
            print("The file is now sorted by date!")
            
        elif entry == "quit":
            q = True
            print("Thank you for being financially responsible! Goodbye.")

        else:
            print("That is not a valid entry. Please type 'help' for a list of valid commands.")
            
__main__()
