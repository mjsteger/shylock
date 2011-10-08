# Create your views here.
from django.http import HttpResponse
from models import User, Tab, Purchasable
import re

def index(request):
    return HttpResponse("Here you are")

def addTabCall(request):
    if request.method == "GET":
        textBody = request.GET['Body']
        fromNumber = request.GET['From']
        possibleUsers = [user for user in User.objects.all() if user.number == fromNumber]
        if possibleUsers == None:
            # TODO: Send a text saying we dont have that user
            return HttpResponse("This is not a valid user " + user.number + " " +  fromNumber)
        else:
            thisUser = possibleUsers[0]
            tab = thisUser.currentTab
            textDict = parseText(textBody)
            items = textDict.get('items')
            if not items == None:
                for item in items:
                    for purchaseItem in Purchasable.objects.all():
                        isThisItem = re.search(purchaseItem.name.lower(), item.lower())
                        if not isThisItem == None:
                            tab += purchaseItem.cost
                            break
            costs = textDict.get('cash')
            if not costs == None:
                tab += costs
            thisUser.currentTab = tab
            thisUser.save()
            return HttpResponse("Yay")

def parseText(text):
    """
    Parses the text, and returns a dictionary of values, which contains
    items(the strings to look up in the database)
    cash(the float which represents the cash amount(positive or negative) to be debited
    """
    #TODO
    pass
