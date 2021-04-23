# -----------------------------------------------------------
# This file reads the tracker.json and other files from the sprite bot and produces more web friendly jsons
# + creates the portraits ready to download
#
# Entry means a pokemon
# Form means each unique shape not counting shiny or female
# botPath indicates where are the related files in the SpriteBot Repo
# # -----------------------------------------------------------

import requests, json
from datetime import datetime
from PIL import Image
from io import BytesIO

URL = 'https://raw.githubusercontent.com/PMDCollab/SpriteCollab/master/'

EXPLIST = ["Normal","Happy","Pain","Angry","Worried","Sad","Crying","Shouting","Teary-Eyed","Determined","Joyous","Inspired","Surprised","Dizzy","Special0","Special1","Sigh","Stunned","Special2","Special3"]
EXPREVLIST = ["Normal^","Happy^","Pain^","Angry^","Worried^","Sad^","Crying^","Shouting^","Teary-Eyed^","Determined^","Joyous^","Inspired^","Surprised^","Dizzy^","Special0^","Special1^","Sigh^","Stunned^","Special2^","Special3^"]

#Download the json file that contains the all the poke entries
def loadTrackerFile():
    try:
        response = requests.get(URL + "tracker.json", allow_redirects=True)
        tracker = json.loads(response.content.decode("utf-8"))
    except:
        print("Failed to get tracker.json")
        exit(1001)

    return tracker

def loadLastRunDate():
    try:
        with open("action/lastrun","r") as datefile:
            lastRunDate = datetime.fromisoformat(datefile.read())
    except:
        print("Failed to get lastrun date")
        exit(1002)

    return lastRunDate

def loadlastRunJson():
    try:
        with open("resources/pokemons.json","r") as jsonfile:
            lastRunJson = json.loads(jsonfile.read())
    except:
        print("Failed to get pokemons.json")
        exit(1003)

    return lastRunJson

#Download the txt file that contains a file containing all credits, and turn them into a dictionary
def loadCreditNamesFile():
    try:
        response = requests.get(URL + "credit_names.txt", allow_redirects=True)
        creditsfile = response.content.decode("utf-8")

        result = {}

        creditsfile = creditsfile.split('\n')
        if creditsfile[len(creditsfile)-1] == "": creditsfile.pop()
        for i in range(1,len(creditsfile)):
            creditsfile[i] = creditsfile[i].split('\t')
            
            result[i] = {
                'id': creditsfile[i][1],
                'name': creditsfile[i][0],
                'contact': creditsfile[i][2],
                'worked': []
            }

        return result
        
    except:
        print("Failed to retrieve the main credit file: " + URL + "credit_names.txt")
        exit(1004)

#Download the txt files that contains the individual credits of a portrait set, and turn them into an array of array, + adds link them in the credit names array
def loadCreditFiles(creditsNames, botPath, id):
    try:
        response = requests.get(URL + "portrait" + botPath + 'credits.txt', allow_redirects=True)
        creditsfile = response.content.decode("utf-8")

        creditsfile = creditsfile.split('\n')
        if creditsfile[len(creditsfile)-1] == "": creditsfile.pop()
        for i in range(len(creditsfile)):
            creditsfile[i] = creditsfile[i].split('\t')

            for k in creditsNames:
                if creditsfile[i][1] == creditsNames[k]['id']:
                    creditsfile[i][1] = k
                    creditsNames[k]['worked'] += [id]
                    break

        return creditsfile
        
    except:
        print("Failed to retrieve credit file: " + URL + "portrait" + botPath + "credits.txt")
        return "error"

def writeOutputFile(output):
    try:
        with open('resources/pokemons.json', 'w') as outfile:
            json.dump(output, outfile)
    except:
        print("Failed to write pokemons.json")
        exit(1005)

def writeCreditsName(output):
    try:
        with open('resources/credits.json', 'w') as outfile:
            json.dump(output, outfile)
    except:
        print("Failed to write credits.json")
        exit(1007)

def writeDateofRun():
    try:
        with open("action/lastrun","w") as datefile:
            datefile.write(str(datetime.now()))
    except:
        print("Failed to write lastrun date")
        exit(1006)

#downloads a single portrait
def retrivePortrait(url):
    try:
        response = requests.get(url, allow_redirects=True)
        png = Image.open(BytesIO(response.content))  
    except: 
        print("Failed to retrieve portrait file: " + url)
        png = Image.new("RGBA", (40, 40), (0, 0, 0, 0))

    return png

#gets the neutral of the first form, to fill the sites list
def downloadThumb(id):

    try:
        response = requests.get(URL + "portrait/" + id + "/Normal.png", allow_redirects=True)
        neutral = Image.open(BytesIO(response.content))
        neutral.save("resources/neutrals/" + id + ".png")
    except:
        print("Failed to retrieve thumbnail file: " + URL + "portrait/" + id + "/Normal.png")
        return

def newEntry(id, name):

    entry = {
            'id': id,
            'name': name,
            'complete': 0,
            'forms': {}
        }

    return entry

#generates a dictionary from a form entry
def newForm(formEntry, formEntryName, formEntrybotPath, formId, creditsNames):

    pForm = {
        'name': formEntryName,
        'botPath': formEntrybotPath,
        'complete': formEntry["portrait_complete"],
        'filename': "portrait" + formEntrybotPath.replace("/","-")[0:len(formEntrybotPath)-1] + ".png",
        'portraits': [],
        'preversed': [],
        'credits': [],
        'modified': formEntry["portrait_modified"]
    }
    
    expressions = formEntry["portrait_files"]

    for exp in EXPLIST: #ok, this is dumb, but made more sense in the past with a different tracker
        if exp in expressions:
            pForm['portraits'].append(1)
        else:
            pForm['portraits'].append(0)

    if not pForm['portraits'].count(1): 
        pForm['portraits'] = False
    
    for exp in EXPREVLIST:
        if exp in expressions:
            pForm['preversed'].append(1)
        else:
            pForm['preversed'].append(0)

    if not pForm['preversed'].count(1): 
        pForm['preversed'] = False

    if not pForm['portraits'] and not pForm['preversed']:
        return False
    else:
        pForm['credits'] = loadCreditFiles(creditsNames, formEntrybotPath, formId)
        return pForm

#making it a function to decluter the main loop
def testTime(entry,lastrun):

    if entry != "":
        if datetime.strptime(entry,"%Y-%m-%d %H:%M:%S.%f") > lastrun:
            return True

    return False

#Generates the big mozaic of portraits
def generatePortrait(portraits,preversed,botPath,filename):
    if portraits.count(1) == 1 and not preversed:
        compilation = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
        compilation.paste(retrivePortrait(URL + "portrait" + botPath + "Normal.png"), (0,0))
        compilation.save("resources/portraits/" + filename)
        return
    else:
        if preversed:
            compilation = Image.new("RGBA", (200, 320), (0, 0, 0, 0))
        else:
            compilation = Image.new("RGBA", (200, 160), (0, 0, 0, 0))

    x,y = 0,0
    for i in range(20):
        if portraits[i]:
            compilation.paste(retrivePortrait(URL + "portrait" + botPath + EXPLIST[i] + ".png"), (x,y))
            
        x += 40
        if x == 200:
            x = 0
            y += 40
    if preversed:
        for i in range(20):
            if preversed[i]:
                compilation.paste(retrivePortrait(URL + "portrait" + botPath + EXPREVLIST[i] + ".png"), (x,y))
            
            x += 40
            if x == 200:
                x = 0
                y += 40

    compilation.save("resources/portraits/" + filename)

#start of the sctript itself ####################################################

tracker = loadTrackerFile()
lastRunDate = loadLastRunDate()
lastRunJson = loadlastRunJson()
creditsNames = loadCreditNamesFile()

for jentry in tracker:# the hella important main loop

    if jentry not in lastRunJson: #add missing entry
        print(jentry + " new")
        lastRunJson[jentry] = newEntry(jentry, tracker[jentry]['name'])

    lastRunJson[jentry]['complete'] = tracker[jentry]['portrait_complete']

    for jform in tracker[jentry]['subgroups']: #Track all forms

        #normal form
        if testTime(tracker[jentry]['portrait_modified'],lastRunDate):

            if jform == "0000": #form 0000 is special, has no info but its on the main entry
                form = newForm(tracker[jentry], "Normal", "/"+ jentry + "/", jentry, creditsNames)
                if form:
                    lastRunJson[jentry]['forms'][jform] = form
                    generatePortrait(form["portraits"],form["preversed"],"/"+ jentry + "/",form["filename"])
            
            else:
                form = newForm(tracker[jentry]['subgroups'][jform], tracker[jentry]['subgroups'][jform]['name'], "/"+ jentry + "/" + jform + "/", jentry, creditsNames)
                if form:
                    lastRunJson[jentry]['forms'][jform] = form
                    generatePortrait(form["portraits"],form["preversed"],"/"+ jentry + "/" + jform + "/",form["filename"])

        #check for female
        if '0000' in tracker[jentry]['subgroups'][jform]['subgroups']:
            if '0002' in tracker[jentry]['subgroups'][jform]['subgroups']['0000']['subgroups']:
                if testTime(tracker[jentry]['subgroups'][jform]['subgroups']['0000']['subgroups']['0002']['portrait_modified'],lastRunDate):
                    form = newForm(tracker[jentry]['subgroups'][jform]['subgroups']['0000']['subgroups']['0002'], "Female", "/"+ jentry + "/" + jform + "/0000/0002/", jentry + "f", creditsNames)
                    if form:
                        lastRunJson[jentry]['forms'][jform+"f"] = form
                        generatePortrait(form["portraits"],form["preversed"],"/"+ jentry + "/" + jform + "/0000/0002/",form["filename"])

        #check for shiny
        if '0001' in tracker[jentry]['subgroups'][jform]['subgroups']:
            if testTime(tracker[jentry]['subgroups'][jform]['subgroups']['0001']['portrait_modified'],lastRunDate):
                form = newForm(tracker[jentry]['subgroups'][jform]['subgroups']['0001'], "Shiny", "/"+ jentry + "/" + jform + "/0001/", jentry + "s", creditsNames)
                if form:
                    lastRunJson[jentry]['forms'][jform+"s"] = form
                    generatePortrait(form["portraits"],form["preversed"],"/"+ jentry + "/" + jform + "/0001/",form["filename"])

        #check for female shiny
                if '0002' in tracker[jentry]['subgroups'][jform]['subgroups']['0001']['subgroups']:
                    if testTime(tracker[jentry]['subgroups'][jform]['subgroups']['0001']['subgroups']['0002']['portrait_modified'],lastRunDate):
                        form = newForm(tracker[jentry]['subgroups'][jform]['subgroups']['0001']['subgroups']['0002'], "Female Shiny", "/"+ jentry + "/" + jform + "/0001/0002/", jentry + "fs", creditsNames)
                        if form:
                            lastRunJson[jentry]['forms'][jform+"fs"] = form
                            generatePortrait(form["portraits"],form["preversed"],"/"+ jentry + "/" + jform + "/0001/0002/",form["filename"])

        #if it has at least at least one form, download a thumb
        if len(lastRunJson[jentry]['forms']):
            downloadThumb(lastRunJson[jentry]['id'])

        print(lastRunJson[jentry]["id"])

writeOutputFile(lastRunJson)
writeCreditsName(creditsNames)
writeDateofRun()