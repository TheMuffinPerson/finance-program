# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 12:31:55 2020
Last updated Mon Jan 15 2024

@author: Dani Slavin

Financial records 2023
"""
global presetsFilepath
presetsFilepath = 'presets.csv'

import glob
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
            val = []            ### :)
            #all elements can be str or float
            if L[0][0] == "'":#single quotation = string
                for el in L:
                    val.append(str(el[1:-1]).strip("'"))#strip is in case there was a leading space
            
            else:#float
                for el in L:
                    val.append(float(el))
        
        else:#number
            val = float(val)
        
        data[var] = val

    #for budget_caps, if active, -1 values should be changed to 'null'
    if isinstance(data['budget_caps'], list):
        for i, el in enumerate(data['budget_caps']):
            if el == -1:
                data['budget_caps'][i] = 'null'
    
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


def filepathToTransactionList(filename=presets['transactions_file'], income=False):
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

def findBudgetCap(budget):
    """
    finds the set cap of the given budget

    Parameters
    ----------
    budget : str
        a valid budget from the list of budgets in presets

    Returns
    -------
    float or str, the value of the cap as a float if it has one, 'null' if it does not
    """
    if isinstance(presets['budget_caps'], str):
        return 'null'#if budget caps are not turned on
    cap = presets['budget_caps'][presets['budgets'].index(budget)]

    return cap

def overcapAmt(budget, amount_to_add, cap=False):
    """
    gives the amount a budget will be overcapped by if the given amount is added.

    Parameters
    ----------
    budget : str
        a valid budget from the list of budgets in presets
    amount_to_add : float
        the amount to be added to the budget
    cap : bool, float
        the cap of the budget being added to. Default is False, if a cap is 
        not given, the function will find it based on the global presets
    
    Returns
    -------
    float or None, None if the budget has no cap, otherwise float represending the overcap amount
        Note that if the budget will not overcap, this function will return a negative number
    """
    if not(cap) and isinstance(cap, bool):
        cap = findBudgetCap(budget)
    if cap == 'null':
        return
    
    return (add(totalBudget(budget,filepathToTransactionList())) + amount_to_add) - cap

def overcapCheck(budget, amount_to_add, cap=False):
    """
    checks if a budget will become overcapped if the given amount is added.

    Parameters
    ----------
    budget : str
        a valid budget from the list of budgets in presets
    amount_to_add : float
        the amount to be added to the budget
    cap : bool, float
        the cap of the budget being added to. Default is False, if a cap is 
        not given, the function will find it based on the global presets
    
    Returns
    -------
    bool, True if it will overcap, False if not.
        Note that if the amount reaches the cap exactly, this function will return False

    """
    total = overcapAmt(budget, amount_to_add, cap)

    if total == None:#no cap
        return False
    elif total > 0:#over cap
        return True
    else:
        return False#0 or negative -- under cap

def overcapProcedure(budget, amount_to_add, cap=False):
    """
    handles the event where user wants to add an amount that would cause the 
    corresponding budget to go over its set cap

    Parameters
    ----------
    budget : str
        a valid budget from the list of budgets in presets
    amount_to_add : float
        the amount to be added to the budget
    cap : bool, float
        the cap of the budget being added to. Default is False, if a cap is 
        not given, the function will find it based on the global presets
    
    Returns
    -------
    None, list
        None if user cancels the transaction
        list - nested list of transactions in the format [budget, amount] to be added to file
    """
    #first check if the budget is already capped before the amount is added
    if overcapAmt(budget, 0, cap) >= 0:
    # if overcapCheck(budget, 0, cap):
        already_capped = True
        what_do = input(f"The {budget} budget is already capped! You can enter 1 to override "\
                        "the cap and add this amount anyway, 2 to add the amount to "\
                        "a different budget, or 3 to cancel this transaction. 1/2/3 ").strip().lower()
    else:
        already_capped = False
        what_do = input(f"Adding this amount to the {budget} budget will result in it going over "\
                        "its set cap. You can enter 1 to override the cap and add this amount "\
                        "anyway, 2 to add money up to this budget's set cap, or 3 to cancel "\
                        "this transaction. 1/2/3 ").strip().lower()

    while what_do not in {"1","2","3","exit","override"}:
        what_do = input("This is not a valid option. Please choose 1, 2, or 3 from the "\
                        "options listed above. 1/2/3 ").strip().lower()
        
    if what_do in {"3", "exit"}:
        print("You have selected to cancel this transaction. Now exiting.")
        return
    
    elif what_do in {"1","override"}:
        print("You have selected to override the cap.")
        return [[budget, amount_to_add]]

    elif what_do in {"2"}:
        printLine()
        cap = findBudgetCap(budget)

        #need different handling for if all of the new amount is being moved,
        # vs just a portion
        transactions = list()

        if already_capped:
            print("You have selected to change the destination budget.")
            overcap = amount_to_add
            next_budget = input("Which budget would you like to change to? ").strip().lower()

        else:
            print("You have selected to add an amount up to the budget cap.")
            overcap = round(overcapAmt(budget, amount_to_add, cap),2)
            undercap = amount_to_add - overcap
            print(f"${undercap} of the amount will be added to {budget}.")
            transactions.append([budget, undercap])
            print(f"The {budget} budget will overcap your set cap of {cap} by ${overcap}.")

            options = input("Would you like to (1) remove this amount from the transaction, (2) add it "\
                            "to the set overflow budget, or (3) add it to another budget? 1/2/3 ").strip().lower()
            
            while options not in {"1","2","3","remove","overflow","other","another","exit"}:
                options = input("This is not a valid option. Please choose 1, 2, or 3 from the "\
                                "options listed above. 1/2/3 ").strip().lower()

            if options == "exit":
                return
            elif options in {"1","remove"}:
                return transactions
            elif options in {"2","overflow"}:
                transactions.append([presets['overflow_budget'], overcap])
                return transactions
            elif options in {"3","other","another"}:
                next_budget = input("Which budget would you like this extra money to go to? ").strip().lower()
        
        next_budget = checkInput(next_budget,"budget")
        if next_budget is None:
            return
        
        if overcapCheck(next_budget,overcap):
            printLine()
            #ask again if they'd like to add to overflow budget
            print(f"Adding this amount to the {next_budget} budget will put that budget over the set cap.")
            overflow = input("Would you like to add the amount to the set overflow budget instead? Y/N ").strip().lower()
            if overflow == 'exit':
                return
            elif overflow in {'y','yes','yee'}:
                transactions.append([presets["overflow_budget"], overcap])
            else:
                #recursive problem with capped budget
                printLine()
                handling = overcapProcedure(next_budget,overcap)
                if handling is None:
                    return
                else:
                    transactions += handling
        else:
            transactions.append([next_budget,overcap])

        if overcapAmt(next_budget,overcap) == 0:
            print(f"The {next_budget} budget is now capped at {findBudgetCap(next_budget)}.")

        return transactions


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
    if inp in {'exit', 'n', 'cancel', 'go away!'}:
        print("Okay, backing up...")
        return None
    
    if typ == "date":
        fail = True
        count = 0
        while fail:
            fail = False
            try:
                #if too short, assume lower month
                if len(inp) == 4:
                    inp = "0"+inp
                
                #wrong length
                if len(inp) != 5:
                    fail = True
                    print("Please enter a date in the format MM-DD (it should be 5 characters long!).")
                
                #no hyphen
                if inp[2] != "-" and not fail:
                    fail = True
                    print("Please enter a date in the format MM-DD (there should be a hyphen in the middle!).")
                    
                #month out of range
                if (int(inp[:2]) < 1 or int(inp[:2]) > 12) and not fail:
                    fail = True
                    print("Please enter a valid month.")
                
                #day out of range
                if (int(inp[3:]) < 1 or int(inp[3:]) > 31) and not fail:
                    fail = True
                    print("Please enter a valid day.")
            
            except ValueError:
                #if they entered letters
                count += 1
                fail = True
                print("Please only enter digits and a hyphen.")
                if count >= 3:
                    print("Like, dude, why you keep entering letters and stuff??")
            
            except IndexError:
                fail = True
            
            if fail:
                inp = input("Date (MM-DD): ")
    
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
            
            if inp == "exit":
                break

            acct_list_str = ""
            for acct in accounts:
                acct_list_str += acct
                acct_list_str += ", "
            print(f"{inp} is not a valid account. The valid accounts are {acct_list_str}and null.")
            inp = input("Account: ").strip().lower()
            
    elif typ == "budget":
        budgets = presets['budgets']
        inp = inp.lower()
        while inp not in budgets and inp != "null":
            #check for all
            if inp == "all" and all_bool:
                inp = budgets #will return a list of all budget names
                break

            if inp == 'exit':
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
            if inp == 'exit':
                break
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
            if inp.lower() == 'exit':
                found == True
                print("Exiting...")
                break

            #add .csv extension if not there
            if inp[-4:] != ".csv":
                inp = inp + ".csv"

            try:
                f = open(inp)
                f.close()
                found = True
    
            except FileNotFoundError:
                print(f"{inp} was not found in the local file. Please enter the name of a csv file",\
                    "or filepath in the local directory.")
                inp = input("Filename: ").strip()
    
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
    #DEBUG - exit doesn't work properly in this function

    #ask for values for accounts and for budgets
    printLine()
    print("Okay! First thing you need to do is let me know how much money is in each",\
          "account and budget.")
    
    print("First are your accounts.")
    acct_amts = askEach(presets['accounts'])
    printLine()
    print("Now are the budgets.")
    budg_amts = askEach(presets['budgets'])
    
    #make sure total for accounts == total for budgets
    sum_acct = round(sum(acct_amts), 2)
    sum_budg = round(sum(budg_amts), 2)
    while sum_acct != sum_budg:
        print("The amounts in your accounts is not equal to the amounts in your budgets.",\
              f"Total in accounts is {sum_acct}, while total in budgets is {sum_budg}.",\
              "Please try again.")
        #ask again
        print("First are your accounts.")
        acct_amts = askEach(presets['accounts'])
        printLine()
        print("Now are the budgets.")

        budg_amts = askEach(presets['budgets'])
        sum_acct = round(sum(acct_amts), 2)
        sum_budg = round(sum(budg_amts), 2)
    
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
    
    print("It's all added to the file now!")

def checkBalances(transactionList, checkFilepath=presets['balance_checks_file']):
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


def checkCash(checkFilepath=presets['balance_checks_file']):
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


def sort(filename=presets['transactions_file']):
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
    
def writeTransaction(line, filename=presets['transactions_file']):
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
    instructions = {
        "transactions_file": "The transactions file is the file that all transactions are "\
            "recorded in.",
        "balance_checks_file": "The balance checks file is the file that records the balance "\
            "of your accounts every time you check that they match your records, and the "\
            "date it was checked.",
        "income_record_file": "The income record file is the file that records your income.",
        "accounts": "Accounts is a list of your accounts.",
        "budgets": "Budgets is a list of your budgets.",
        "employer": "The employer is the name you give to the source of your income.",
        "paycheck_account": "The paycheck account is which account, from your list, you "\
            "have your paycheck deposited into.",
        "paycheck_split": "The paycheck split is how you want your paycheck to be divided "\
            "among the budgets you have set, represented as a decimal amount for each budget.",
        "round_budget": "The round budget comes into play after your paycheck is divided "\
            "among your budgets. In the case that the total doesn't equal your actual "\
            "paycheck due to rounding, the amount needed in order for it to add correctly "\
            "will be taken from or added to the budget you set here.",
        "monthly_rent": "The monthly rent is the amount you pay per month for rent.",
        "monthly_internet": "The monthly internet is the amount you pay per month for internet.",
        "budget_caps": "The budget caps is a list of the max amount of money you want to have "\
            "in each budget. If an item in the list is 'null', it means the corresponding budget "\
            "does not have a cap.",
        "overflow_budget": "The overflow budget is the budget that income from things like paychecks "\
            "will go into if all the budgets it's set to go into are capped."
            }

    printLine()
    print("Type 'exit' in any field to cancel.")

    #show list of preset variables
    for var in presets:
        print("\t",var)
    
    #ask which to change
    inp = input("Please enter the names of each of the presets, from the list above, "\
                "that you would like to change, separated by commas, or type 'all' to change "\
                "every preset: ").lower().strip()
    if inp == 'all':
        to_change = list(presets)

    elif inp == 'exit':
        print("Exiting presets modification...")
        return #end function
    
    else:
        to_change_input = (inp.replace(" ","")).split(",")#get rid of spaces and split by comma
        
        to_change = []
        for variable in to_change_input:
            #check input
            while variable not in presets:
                variable = input(f"{variable} not found in presets. Please enter "\
                        "a valid preset name, or type 'skip' to move on: ").lower().strip()
                if variable == 'skip':
                    break
                elif variable == 'exit':
                    print("Exiting presets modification...")
                    return #end function

            #only add if it's not already in it
            if variable not in to_change:
                to_change.append(variable)

    for i, variable in enumerate(to_change):
        if variable == 'skip':
            continue

        og_value = presets[variable]#get original value
        
        printLine()
        print(f"Working on changing {variable}.")
        print(instructions[variable])#give a brief explanation of the variable

        #budget_caps needs special case because it can be a str or list
        if variable == 'budget_caps':
            budgets = presets['budgets']

            if isinstance(og_value, str):
                on = input("You currently have budget caps turned off. Would you like to turn this "\
                      "setting on? Y/N ").strip().lower()
                if on == 'exit':
                    print("Exiting budget caps editing...")
                    continue
                elif on in {'yes','y','yee'}:
                    #create a list to put the budgets through, and then run the second part of budget_caps handling
                    og_value = ['null' for _ in range(len(budgets))]
                    edit_list = True
                else:#no change
                    continue

            else:
                off = input("You currently have budget caps turned on. Would you like to turn this "\
                      "setting off? Y/N ").strip().lower()
                if off == 'exit':
                    print("Exiting budget caps editing...")
                    continue
                elif off in {'yes','y','yee'}:
                    presets['budget_caps'] = 'null'
                    edit_list = False
                else:
                    edit_list = True

            #runs only if there is a list & they want to edit it
            if edit_list:
                #make sure list is same length as budgets list
                if len(budgets) != len(og_value):
                    #add nulls to budget_caps if budgets is longer
                    if len(budgets) > len(og_value):
                        for _ in range(len(budgets) - len(og_value)):
                            og_value.append('null')
                    #arbitrarily remove values off the end of budget_caps if it's longer
                    else:
                        for _ in range(len(og_value) - len(budgets)):
                            og_value.pop()

                #show existing data
                print("The current budget caps are as follows:")
                for i, el in enumerate(og_value):
                    print(f"{budgets[i]}\t{el}")

                check = input("Would you like to change any of these caps? Y/N ").strip().lower()
                if check not in {'y','yes','yee'}:
                    continue#move on to next to_change variable
                
                inp = input("Which budgets would you like to change the cap for? this includes "\
                            "adding, removing, and changing a cap. Please separate by commas, or "\
                            "type 'all' to change all budget caps: ").strip().lower()
                if inp == 'exit':
                    print("Exiting paycheck split editing...")
                    continue#move to next variable in to_change
                elif inp == 'all':
                    budgs = budgets[:]
                else:
                    #correct/check input
                    budgs = []
                    for budg in inp.split(","):
                        budg = checkInput(budg.strip(), 'budget')
                        if budg == 'exit':
                            print("Removing this budget from editing...")
                        if budg not in {'null', 'exit'}:
                            budgs.append(budg)
                
                #build list of budget indices to change
                budg_indices = []
                for budg in budgs:
                    budg_indices.append(budgets.index(budg))

                #go through each and ask for new caps
                new_caps = og_value[:]
                for i, budg_index in enumerate(budg_indices):
                    new = input(f"What cap would you like to set for {budgs[i]}? Type 'null' for no cap. ").strip().lower()
                    if new == 'exit':
                        new_caps = og_value[:]#reset to beginning
                        print("Exiting budget caps editing...")
                        break#still want to reset to str 'null' if all els are 'null'
                    
                    if new != 'null':
                        new = checkInput(new, 'amount')
                        #check if the cap is lower than the current amount
                        current_amt = add(totalBudget(budgs[i],filepathToTransactionList()))
                        if new < current_amt:
                            uncap = input(f"The cap you set is lower than the current total in {budgs[i]}! Type "\
                                  "'yes' to transfer the excess balance to another budget, or 'no' to "\
                                  "manually keep it higher than the budget. Note that moving this "\
                                  "balance may overcap the destination budget. Y/N ").strip().lower()
                            if uncap == 'exit':
                                new_caps = og_value[:]
                                print("Exiting budget caps editing...")
                                break
                            elif uncap in {'y','yes','yee'}:
                                to_budget = input("Which budget would you like to move it to? ").strip().lower()
                                to_budget = checkInput(to_budget, 'budget')
                                if to_budget == 'exit':
                                    new_caps = og_value[:]
                                    print("Exiting budget caps editing...")
                                    break

                                overcap_amt = current_amt - new

                                writeTransfer([today,"budget cap transfer",'null',budgs[i],-1*overcap_amt],
                                              [today,"budget cap transfer",'null',to_budget,overcap_amt])


                    new_caps[budg_index] = new

                #add check at the end - if every value in the list is 'null', reset whole variable to 'null'
                if new_caps == ['null' for _ in range(len(new_caps))]:
                    presets['budget_caps'] = 'null'

                else:
                    presets['budget_caps'] = new_caps

                    #check if there is an overflow budget set
                    if presets['overflow_budget'] == '':
                        print("You do not have an overflow budget set. To avoid potential errors, you will need to set one now.")
                        to_change.insert(i+1, 'overflow_budget')

        elif not isinstance(og_value, list):
            #if value is a single item
            #includes everything except accounts, budgets, and paycheck_split

            csv_settings = {"transactions_file", "balance_checks_file", "income_record_file"}

            #if it's a csv filename, print possible files in the local directory
            if variable in csv_settings:
                files = glob.glob("*.csv")
                print("The available csv files in the current folder are:")
                for file in files:
                    if file != "presets.csv":#don't want to list itself as an option
                        print("\t",file)

            print(f'Current setting is {og_value}.')
            new = input(f'Please enter the new {variable.replace("_", " ")}: ').strip()

            if new.lower() == 'exit':
                print(f"Exiting {variable.replace('_',' ')} editing...")
                continue#cancel just the current variable

            #change checkInput type depending on the variable
            #str
            if isinstance(og_value, str):
                if variable in csv_settings:
                    inputType = 'csv'
                elif variable == 'paycheck_account':
                    inputType = 'account'
                elif variable == 'round_budget' or variable == 'overflow_budget':
                    inputType = 'budget'
                else:
                    inputType = 'name'
            #int
            else:
                inputType = 'amount'

            #make input lowercase unless it's a name (the employer preset)
            if inputType != 'name':
                new = new.lower()

            new_value = checkInput(new, inputType)

            #making sure it's not already set for another csv variable
            if variable in csv_settings:
                #create list of other filenames already set
                set_filenames = []
                for preset in csv_settings:
                    #not this variable, and not going to be changed this run
                    if preset not in to_change[i:]:
                        set_filenames.append(presets[preset])
                
                #if already a set file, they need to put in a different file
                while new_value in set_filenames:
                    new_value = input("This file is already being used for another preset! "\
                        "Please input a valid file not being used, or type 'exit' to move on. ").lower().strip()
                    if new_value == 'exit':
                        print(f"Exiting {variable.replace('_',' ')} editing...")
                        break
                    new_value = checkInput(new_value, 'csv')

            if new_value != 'exit':
                presets[variable] = new_value

        else:#value is a list
            #paycheck_split gets special case
            if variable == 'paycheck_split':

                budgets = presets['budgets']

                #make sure the length of the paycheck_split matches the length of the budgets
                if len(budgets) != len(og_value):
                    #add 0s to paycheck_split if budgets is longer
                    if len(budgets) > len(og_value):
                        for _ in range(len(budgets) - len(og_value)):
                            og_value.append(0)
                    #arbitrarily remove values off the end of paycheck_split if it's longer
                    else:
                        for _ in range(len(og_value) - len(budgets)):
                            og_value.pop()
                
                #show preexisting data
                print("The current split for your budgets are as follows:")
                for i, el in enumerate(og_value):
                    print(f"{budgets[i]}\t{el}")
                    
                #get input
                inp = input("Which budget(s) would you like to edit? Please separate "\
                             "by commas, or type 'all' to change all budgets: ").lower().strip()
                
                if inp == 'all':
                    budgs = budgets[:]
                
                elif inp == 'exit':
                    print("Exiting paycheck split editing...")
                    continue#skip current variable in to_change
                
                else:
                    #correct/check input
                    budgs = []
                    for budg in inp.split(","):
                        budg = checkInput(budg.strip(), 'budget')
                        if budg == 'exit':
                            print("Removing this budget from editing...")

                        if budg not in {'null', 'exit'}:
                            budgs.append(budg)

                #convert budgets to indices
                budgs_i = []
                for budg in budgs:
                    budgs_i.append(budgets.index(budg))

                #loop in case it doesn't total right                    
                adds = False
                while not adds:
                    #go through each account and ask for new values
                    new_values = og_value[:]
                    for j, budg_i in enumerate(budgs_i):
                        new = input('What fraction of the paycheck would you like '\
                                    f'to be put in {budgs[j]}? ').strip().lower()

                        if new == 'exit':
                            new_values = og_value[:]#reset to beginning
                            print("Exiting paycheck split editing...")
                            break

                        new = checkInput(new, 'amount')
                        
                        new_values[budg_i] = new
                    
                    #check that it totals to 1
                    if abs(sum(new_values) - 1) > .0001:#account for float error
                        #if they exited but it doesn't sum to 1, put 1 for i=0 and 0 for rest
                        if new == 'exit':
                            new_values = [0] * len(budgets)
                            if len(new_values) > 0:#prevent index error
                                new_values[0] = 1

                            print("Your paycheck split is now the following:")
                            for i, el in enumerate(new_values):
                                print(f"{budgets[i]}\t{el}")
                            print("If you would like this to be different, please rerun presets.")
                            adds = True
                        
                        else:
                            print("These values don't seem to sum to 1! Please re-enter.")
                            adds = False
                    else:
                        adds = True

                presets['paycheck_split'] = new_values
                
            #handle other lists
            else:
                #can either be accounts or budgets, both are lists of strings

                #make a copy of budgets list to manage paycheck_split properly
                if variable == 'budgets':
                    original_budgets = og_value[:]

                print(f"These are your current {variable}:")
                for val in og_value:
                    print("\t",val)
                
                #options are add, remove, or modify
                print(f"\nYou can add, remove, or modify {variable}.")
                #add
                add_var = input(f"Would you like to add any {variable}? Y/N ").lower().strip()

                if add_var == 'exit':
                    print(f"Exiting {variable} editing...")
                    continue#go to next entry in to_change

                if add_var in {'y','yes','yee'}:
                    new_raw = input(f"Please enter the names of the new {variable} you "\
                                "would like to add, separated by commas: ").strip().lower()

                    if new_raw == 'exit':
                        #just exit adding new budgets
                        new = list()
                        print(f"Exiting {variable} addition...")

                    else:
                        new = []
                        for n in new_raw.split(","):
                            new.append(n.strip())
                    
                    to_add = list()
                    exit = False
                    for name in new:
                        #make sure it's a new name
                        while name in og_value:
                            name = input(f"{name} is already in {variable}! Please enter a "\
                                         "different name, or enter 'skip' to move on: ").lower().strip()
                            if name == 'skip':
                                break
                            if name == 'exit':
                                break

                        if name == 'skip':
                            continue
                        elif name == 'exit':
                            exit = True
                            print(f"Exiting {variable} addition...")
                            break#move on
                        else:
                            #passes checks
                            to_add.append(name)
                        
                    if not exit:
                        #passes all checks, no exit, now add the whole thing to presets
                        presets[variable] += to_add
                        og_value = presets[variable]#reset for remove/modify

                        #maintain paycheck_split/budget_caps
                        if variable == 'budgets':
                            presets['paycheck_split'] += [0] * len(to_add)
                            if presets['budget_caps'] != 'null':
                                presets['budget_caps'] += ['null'] * len(to_add)

                    printLine()
                    print(f"The following are your current {variable}:")
                    for item in og_value:
                        print("\t",item)
                
                #remove
                rem = input(f"\nWould you like to remove one of the above {variable}? Y/N ").lower().strip()
                if rem == 'exit':
                    print(f"Exiting {variable} editing...")
                    continue#going to the next variable in to_change
                
                if rem in {'y', 'yes', 'yee'}:
                    rem_raw = input(f"Please enter the names of the {variable} you "\
                                "would like to remove, separated by commas, or type 'all' "\
                                f"to remove all {variable}: ").strip().lower()
                    
                    rest = True

                    if rem_raw == 'exit':
                        #exit just variable deletion
                        print(f"Exiting {variable} deletion...")
                        rest = False

                    elif rem_raw == 'all':
                        confirm = input(f"Are you sure you would like to remove all {variable}? Y/N ").lower().strip()
                        if confirm in {'y', 'yes', 'yee'}:
                            #set all necessary variables to empty
                            presets[variable] = []
                            og_value = []
                            if variable == 'budgets':#maintain paycheck_split/budget_caps
                                presets['paycheck_split'] = []
                                presets['budget_caps'] = 'null'
                            rest = False

                    if rest:
                        rem = []
                        for r in rem_raw.split(","):
                            rem.append(r.strip())
                    
                        to_rem = list()
                        exit = False
                        for name in rem:
                            #make sure it's an existing name
                            while name not in og_value:
                                name = input(f"{name} is not in {variable}! Please enter an "\
                                            "existing name, or enter 'skip' to move on: ").lower()
                                if name == 'skip':
                                    break
                                elif name == 'exit':
                                    break

                            if name == 'skip':
                                continue
                            elif name == 'exit':
                                exit = True
                                print(f"Exiting {variable} deletion...")
                                break#move on
                            else:
                                #passes checks
                                to_rem.append(name)

                        if not exit:
                            #passes checks, no exit, now make changes
                            for name in to_rem:
                                presets[variable].remove(name)
                            
                            #maintain paycheck_split & budget_caps
                            if variable == 'budgets':
                                #remove the corresponding paycheck split value, and check if it'll mess up total
                                if name in original_budgets:
                                    deleted = presets['paycheck_split'].pop(original_budgets.index(name))
                                    if deleted != 0:
                                        must_edit_paycheck_split = True

                                    if presets['budget_caps'] != 'null':
                                        presets['budget_caps'].pop(original_budgets.index(name))

                                else:
                                    #if it was added this cycle, the split/cap is 0/null appended to end
                                    presets['paycheck_split'].pop()
                                    if presets['budget_caps'] != 'null':
                                        presets['budget_caps'].pop()
                        
                            og_value = presets[variable]#reset for later iterations
                    
                    printLine()
                    print(f"These are your current {variable}:")
                    for item in og_value:
                        print("\t",item)
                    
                #modify
                mod = input(f"\nWould you like to modify one of the above {variable}? Y/N ").lower()
                if mod == 'exit':
                    print(f"Exiting {variable} editing...")
                    continue#go to the next to_change
                
                if mod in {'y','yes','yee'}:
                    mod_raw = input(f"Please enter the names of the {variable} you "\
                                "would like to modify, separated by commas, or type "\
                                f"'all' to modify all {variable}: ").strip().lower()
                                
                    if mod_raw == 'all':
                        mod = og_value[:]

                    elif mod_raw == 'exit':
                        print(f"Exiting {variable} modification...")
                        mod = []

                    else:
                        mod = []
                        for m in mod_raw.split(","):
                            mod.append(m.strip())
                    
                    to_mod = list()
                    exit = False
                    for name in mod:
                        #make sure it's an existing name
                        while name not in og_value:
                            name = input(f"{name} is not in {variable}! Please enter an "\
                                         "existing name, or enter 'skip' to move on: ").lower()
                            if name == 'skip':
                                break
                            elif name == 'exit':
                                break

                        if name == 'skip':
                            continue
                        elif name == 'exit':
                            exit = True
                            print(f"Exiting {variable} modification...")
                            break#move on
                        else:
                            #passes checks
                            to_mod.append(name)

                    #do another loop (if hasn't exited yet) for what to change the names to
                    if not exit:
                        mod_dict = dict()
                        for name in to_mod:
                            printLine()
                            print(f"Working on modifying the {name} {variable[:-1]}.")

                            new_name = input("Please enter the new name you would like to change "\
                                            f"{name} to, or type 'skip' to not modify this {variable}: ").lower().strip()
                            
                            if new_name == 'exit':
                                print(f"Exiting {variable} modification...")
                                exit = True
                                break#move on

                            elif new_name == 'skip':
                                continue

                            #make sure it's a new name
                            while new_name in og_value:
                                new_name = input(f"{new_name} is already in {variable}! Please "\
                                                "enter a different name, or enter 'skip' to move on: ").lower()
                                if new_name == 'skip':
                                    break
                                elif new_name == 'exit':
                                    break

                            if new_name == 'skip':
                                continue
                            elif new_name == 'exit':
                                exit = True
                                print(f"Exiting {variable} modification...")
                                break#move on

                            #passes checks
                            mod_dict[name] = new_name

                    if not exit:
                        #passes checks, no exit, now change stuff
                        for name in mod_dict:
                            
                            #change old name to new_name
                            index = presets[variable].index(name)
                            presets[variable][index] = mod_dict[name]
                        
                        og_value = presets[variable]#reset for later iterations
                        #paycheck_split/budget_caps don't need to be updated here - will maintain from previous budget name
                
                #maintain paycheck_split/budget_caps
                #lengths should be same b/c of maintaining throughout
                if variable == 'budgets':
                    #not necessary to add if it's already been added by the user
                    if 'paycheck_split' not in to_change[i:]:
                        
                        #check if paycheck_splits add to 1
                        if abs(sum(presets['paycheck_split']) - 1) > .0001:
                            print("Due to editing budgets, paycheck_split now needs to be updated.")
                            must_edit_paycheck_split = True
                        
                        else:
                            print("Since you edited budgets, your paycheck split is now the following:")
                            for i, el in enumerate(presets['paycheck_split']):
                                print(f"{og_value[i]}\t{el}")
                            
                            change = input("Would you like to change this split? Y/N ").strip().lower()
                            if change == 'y' or change == 'yes' or change == 'yee':
                                must_edit_paycheck_split = True
                            else:
                                must_edit_paycheck_split = False
                                
                        if must_edit_paycheck_split:
                            #run paycheck_split immediately after this
                            to_change.insert(i+1, 'paycheck_split')

                    if presets['budget_caps'] != 'null':
                        #check if added later
                        if 'budget_caps' not in to_change[i:]:
                            print("Since you edited budgets, your budget caps are now as follows:")
                            for i, el in enumerate(og_value):
                                print(f"{el}\t{presets['budget_caps'][i]}")

                            change = input("Would you like to change any of these caps? Y/N ").strip().lower()
                            if change in {'yes','yee','y'}:
                                #run budget_caps after this
                                to_change.insert(i+1, 'budget_caps')
            
            #for lists, cannot have no entries, must have at least 1
            if presets[variable] == []:
                print("This preset must have at least one entry, so one has been automatically added.")

                if variable == 'paycheck_split':
                    presets[variable] = [1]
                else:
                    presets[variable] = ['filler']
                    print(f"The singular {variable[:-1]} is called 'filler'.")
                    if variable == 'budgets':
                        presets['paycheck_split'] = [1]

        #after modifying each variable in presets dict, write new information to file
        #(restart from scratch and use pandas to create csv)
        
        #put in expected format
        data = []
        for var, val in presets.items():
            #change null budgets in budget_caps back to -1
            if var == 'budget_caps':
                if isinstance(val, list):
                    for i, el in enumerate(val):
                        if el == 'null':
                            val[i] = -1

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


def transfer(filename=presets['transactions_file']):
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

    #check for overcapping budgets
    if isinstance(presets["budget_caps"], list):
        if budget_to != 'null':
            if overcapCheck(budget_to,amount):
                #then the transfer will overcap its destination budget
                split_deposits = overcapProcedure(budget_to,amount)
                if split_deposits is None:
                    return
                for deposit in split_deposits:
                    writeTransaction([date,name,account_to]+deposit)
                #also add withdrawal part
                writeTransaction([date,name,account_from,budget_from,-1*amount])
                return

            elif overcapAmt(budget_to,amount) == 0:
                print(f"The {budget_to} budget is now overcapped at {findBudgetCap(budget_to)}.")

    writeTransfer([date,name,account_from,budget_from,-1*amount], \
                  [date,name,account_to,budget_to,amount])
    
def cappedBudgets(budget_caps):
    """
    given budget caps as a dict, returns a list of budgets that are capped

    Parameters
    ----------
    budget_caps : dict
        the budgets and their caps in the form {budget: cap}
    
    Returns
    -------
    list of capped budgets
    """
    transactions = filepathToTransactionList()

    capped = list()
    for budget in budget_caps:
        cap = budget_caps[budget]
        
        if isinstance(cap, str):
            #if 'null', never capped
            pass
        elif add(totalBudget(budget, transactions)) >= cap:
            #then capped
            capped.append(budget)
    
    return capped

def paycheck(amount, filename=presets['transactions_file'], paycheckFile=presets['income_record_file']):
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
    budgets = presets['budgets'][:]
    round_budget = presets['round_budget']
    overflow_budget = presets['overflow_budget']

    #make paycheck_split dict {budget_name: split}
    paycheck_split = dict()
    for i, budget in enumerate(budgets):
        paycheck_split[budget] = presets['paycheck_split'][i]

    #make budget caps dict {budget_name: budget_cap}, if turned on
    if isinstance(presets['budget_caps'], str):
        budget_caps = 'null'
    else:
        budget_caps = dict()
        for i, budget in enumerate(budgets):
            budget_caps[budget] = presets['budget_caps'][i]
    
    print("Type 'exit' to cancel paycheck input.")
    
    #ask for input
    paydate = input("Date of paycheck (MM-DD): ")
    paydate = checkInput(paydate,"date")
    if paydate is None:
        return
    paycheck_account = input("Account the paycheck is in: ")
    paycheck_account = checkInput(paycheck_account, "account")
    if paycheck_account is None:
        return
    
    #first check for capped budgets
    if isinstance(budget_caps, dict):
        #send to a function that returns a list of budgets that are capped
        capped_budgets = cappedBudgets(budget_caps)

        for budget in budgets[:]:
            if budget in capped_budgets:
                #remove from budgets and paycheck_split
                print(f"The {budget} budget is currently capped at {budget_caps[budget]}.")
                budgets.remove(budget)
                del paycheck_split[budget]

    #this will be the end amounts you add to each budget {budget_name: amount from paycheck}
    total = {overflow_budget: 0, round_budget: 0}#these two must always be in the dict
    for budget in budgets:
        #only add budgets that have a value in paycheck_split
        if paycheck_split[budget] != 0:
            total[budget] = 0

    #set redistribute amount to the initial amount of the paycheck
    redistribute_amount = amount
    overflow = False

    #have to loop to redistribute remaining money into non-capped budgets
    while redistribute_amount > 0:

        #after removing budgets and their splits, paycheck_split might not sum to 1
        #total paycheck_split list, scale up so it sums to 1, then divide paycheck
        total_split = sum(paycheck_split.values())
        if abs(total_split - 1) > .001:#account for float

            #first, if 0, all capped and go into overflow budget
            if total_split == 0:
                print(f"All your budgets are capped. The remaining balance will be added to {overflow_budget}, your overflow budget.")
                overflow = True
            
            #multiply each value by 1/sum(paycheck_split)
            else:
                for budget in paycheck_split:
                    paycheck_split[budget] *= 1/total_split

        #split amount
        if overflow:
            total[overflow_budget] += round(redistribute_amount,2)
        else:
            for budget in budgets:
                total[budget] += round(redistribute_amount*paycheck_split[budget],2)
        redistribute_amount = 0#everything has been distributed

        #check for overcapped budgets - skip if already overflowed
        if budget_caps != 'null' and not overflow:
            for budget in total:
                #skip if this budget does not have a cap
                if budget_caps[budget] != 'null':

                    #find overall total in that budget
                    new_total = add(totalBudget(budget, filepathToTransactionList())) + total[budget]
                    if new_total > budget_caps[budget]:
                        #overcapped
                        overcap_amount = new_total - budget_caps[budget] #find out difference
                        #find about paycheck overcapped it by
                        # (don't want to automatically un-cap manually capped budgets)
                        

                        #remove the extra from what's being added from paycheck
                        # (only if non-negative - )
                        total[budget] = max(total[budget] - overcap_amount, 0)
                        redistribute_amount += overcap_amount #add the extra to be redistributed

                        #also remove that budget from the budgets list and paycheck split dict,
                        # so that it won't get more distributed into it the next loop
                        print(f"The {budget} budget is currently capped at {budget_caps[budget]}.")
                        budgets.remove(budget)
                        del paycheck_split[budget]

    #check total sums to given amount
    if int(round(sum(total.values()), 2)*100) != int(amount*100):
        dif = round(amount - round(sum(total.values()), 2), 2)
        #add to round_budget in total if there, add if not there
        total[round_budget] = total.get(round_budget, 0) + dif

        #idk why this is here but I'm afraid to remove it
        #seems to be at risk of hitting an infinite loop
        #I think this is making it sum to the correct amount
        count = 0
        while round(sum(total.values()), 2) != amount:
            count += 1
            total[round_budget] += .01
        
        if round(sum(total.values()), 2) != amount:
            statement = ""
            for el in total:
                statement += "\n" + str(el) + " = " + str(total[el])
                
            print("Does not add up, ask for help","\ntotal =", sum(total.values()),statement)
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
        for budget in total:
            if total[budget] != 0:
                file = pandas_append(file, ["paycheck",paycheck_account,budget,total[budget]], 
                                     paydate, "date")
                file.to_csv(filename)


def getTransaction():
    """
    ask user for transaction information (no intro print statement) and writes it to the file

    Returns
    -------
    None
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
    
    #check if this transaction will cap the destination budget
    if amount > 0:
        if isinstance(presets['budget_caps'], list):
            if overcapCheck(budget,amount):
                transactions = overcapProcedure(budget, amount)
                #returns None if the user cancelled input, or
                # list of [budget, amount] transactions to handle overcapping
                if transactions is None:
                    return
                
                for transaction in transactions:
                    #write each returned transaction to the file
                    writeTransaction([date, name, account] + transaction)
                return
                    
            elif overcapAmt(budget, amount) == 0:
                print(f"The {budget} budget is now capped at {findBudgetCap(budget)}.")

    writeTransaction([date, name, account, budget, amount])


def weekly(filename=presets['transactions_file']):
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
    if paycheckAsk.lower() in {'yes','y','yee'}:
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
        getTransaction()
        
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
    print("Welcome to Dani's Financial Manager!")
    
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
            budget = input("Please enter which budget you would like to check (type 'all' to see all budgets): ")
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
                getTransaction()
                
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
            incomeList = filepathToTransactionList(presets['income_record_file'], True)
            
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
