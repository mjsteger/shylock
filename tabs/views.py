# Create your views here.
from django.http import HttpResponse
from twilio.rest import TwilioRestClient
from models import User, Tab, Purchasable
import datetime
import re

PATH_TO_PROJECT = "/var/www/html/shylock/"

# Read in Twilio Info
twilioDictionary = {}
twilioInformation = open(PATH_TO_PROJECT + "tabs/" + "twilioInfo", "r")
readInformation = twilioInformation.readlines()
for information in readInformation:
    key, value = information.split("=")
    twilioDictionary[key] = value.strip()
TWILIONUMBER = twilioDictionary['TWILIONUMBER']

client = TwilioRestClient(twilioDictionary['ACCOUNTSID'], twilioDictionary['AUTHTOKEN'])

commandDict = {"price":"Gives price without charging", "create":"Used to created an account", "help":"helps", "balance":"return currentTab", "getusers": "returns all users", "user" : "given a user, tabs them"}

def index(request):
    return HttpResponse("Here you are")


def createAccount(request):
    fromNumber = request.REQUEST['From']
    user = request.REQUEST['Name']
    current_tab = request.REQUEST['currentTab']
    u = User()
    u.name = user
    u.currentTab= current_tab
    u.number = fromNumber[1:]
    u.save()
    return HttpResponse()

def takeText(request):
    textBody = request.REQUEST['Body']
    fromNumber = request.REQUEST['From']
    if fromNumber[0] == "+":
        fromNumber = fromNumber[1:]
    possibleUsers = [user for user in User.objects.all() if user.number.rsplit() == fromNumber.rsplit()]
    textDict = parseText(textBody)
    if textDict.get('command') == "create":
        name = textDict.get('items')[0]
        preference = textDict.get('items')[1]
        if preference.lower() == "false":
            preference = False
        else:
            preference =True
        newUser = User()
        newUser.name = str(name)
        newUser.number = fromNumber
        newUser.currentTab = textDict.get('cash')
        newUser.text_preference = preference
        newUser.save()
        if newUser.text_preference:
            message = client.sms.messages.create(to="+" + fromNumber, from_=TWILIONUMBER, body="Hooray, I have made you an account. Enjoy!")
        return HttpResponse("Yay")
    userToFind = textDict.get('user')
    if len(possibleUsers) == 0:
        message = client.sms.messages.create(to="+" + fromNumber, from_=TWILIONUMBER, body=
                                             "Hey, I see that you are not in our system. Text back the following to add yourself: \'create $YOUR_NAME, $WHETHER_YOU_WANT_TEXT{true, false}, $YOUR_TAB\'")
        return HttpResponse("This is not a valid user ")
    else:
        if userToFind == None:
            # If the tab user doens't exist, we should probably bail out, so I'm okay with this failing
            userToFind = "tab"
            otherUser = [user for user in User.objects.all() if user.name == userToFind.rstrip().lstrip()][0]

        thisUser = possibleUsers[0]
        tab = thisUser.currentTab
        if textDict.get('command') == "help":
            getString = "USAGE: [command] [item1, item2...(where items are normal items to purchase, i.e., skittles)] [number(cash to be debited)]. Commands are: " + "\n"
            for commandKey in commandDict:
                if not commandKey == "help":
                    getString += commandKey
                    getString +=":"
                    getString += commandDict[commandKey]
                    getString += "\n"

            if thisUser.text_preference:
                if len(getString) > 160:
                    currentPosition = 0
                    while currentPosition < len(getString):
                        message = client.sms.messages.create(to="+" +fromNumber, from_=TWILIONUMBER, body=getString[currentPosition:currentPosition+159])
                        currentPosition+= 154
                else:
                    message = client.sms.messages.create(to="+" +fromNumber, from_=TWILIONUMBER, body=getString)
            return HttpResponse("help")

        if textDict.get('command') == "balance":
            if thisUser.text_preference:
                message = client.sms.messages.create(to="+" + fromNumber, from_=TWILIONUMBER, body="Your balance is " + str(tab))
            return HttpResponse("Balance")
        if textDict.get('command') == "getusers":
            users = User.objects.all()
            userString = " ".join([user.name for user in users])
            message = client.sms.messages.create(to="+" + fromNumber, from_=TWILIONUMBER, body=userString)
            return HttpResponse("getUsers")
        thisCost=0
        items = textDict.get('items')
        if not items == None:
            for item in items:
                for purchaseItem in Purchasable.objects.all():
                    isThisItem = re.search(item.lower(), purchaseItem.name.lower())
                    if not isThisItem == None:
                        thisTab = Tab(tabber_name = thisUser.name, tabbee_name = otherUser.name, date_tabbed = datetime.datetime.now(), item = purchaseItem.name, amount=purchaseItem.cost)
                        thisTab.save()
                        thisCost += purchaseItem.cost
                        break
        costs = textDict.get('cash')
        if not costs == None:
            thisTab = Tab(tabber_name=thisUser.name, tabbee_name = otherUser.name, date_tabbed = datetime.datetime.now(), item = "Straight Cash Yo", amount= costs)
            thisTab.save()
            thisCost += costs
        if textDict.get('command') == "user":
            thisUser.currentTab += thisCost
            otherUser.currentTab -= thisCost
            if thisUser.text_preference:
                message = client.sms.messages.create(to="+" + thisUser.number, from_=TWILIONUMBER, body="You have tabbed " + otherUser.name + " for " +str(thisCost))
            if otherUser.text_preference:
                message = client.sms.messages.create(to="+" +otherUser.number, from_=TWILIONUMBER, body="You have been tabbed by " + thisUser.name + " for " + str(thisCost))
            thisUser.save()
            otherUser.save()
        if textDict.get('command') == None:
            thisUser.currentTab += thisCost
            thisUser.save()
            otherUser.currentTab -= thisCost
            otherUser.save()
            if thisUser.text_preference:
                message = client.sms.messages.create(to="+" +fromNumber, from_=TWILIONUMBER, body="After spending " + str(thisCost) + " Your tab is " + str(thisUser.currentTab))
            return HttpResponse(str(thisCost))
        if textDict.get('command') == "price":
            stringCost = str(thisCost)
            if thisUser.text_preference:
                message = client.sms.messages.create(to="+" +fromNumber, from_=TWILIONUMBER, body=stringCost)
            return HttpResponse(str(stringCost))

def parseText(text):
    """
    Parses the text, and returns a dictionary of values, which contains
    items(the strings to look up in the database)
    cash(the float which represents the cash amount(positive or negative) to be debited
    command(whatever command to be done)
    user(if the command is user, the user to be tabbed), else it is the tab-board
    """
    # Make sure that shit is lowercase
    text = text.lower()
    returnDict = {'items':[]}
    if len(text) == 0:
        return returnDict
    # If we have a command, then put it in the dict
    if not isFloat(text):
        for command in commandDict.keys():
            if text.count(command) > 0:
                textStart = text.index(command)
                textEnd = len(command)
                text = text[textEnd:]
                returnDict['command'] = command
                if command == "user":
                    newText = text.split(" ")
                    #1 because we have a space, so it'll be like "", $USER, otherstuff
                    returnDict['user'] = newText[1]
                    #TODO Make sure theres more stuff here
                    text = " ".join(newText[2:])
    splittedText = re.split("[\,]", text)
    # For each of the other items, if they are not a float, put them in items
    for item in splittedText:
        if isFloat(item):
            returnDict['cash'] = float(item)
        else:
            returnDict['items'].append(item.lstrip().rstrip())
    return returnDict

def isFloat(text):
    """
    Returns true if it is a float, false otherwise
    """
    try:
        float(text)
        return True
    except:
        return False
