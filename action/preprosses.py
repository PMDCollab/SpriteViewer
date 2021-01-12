import requests, json, datetime
from PIL import Image
from io import BytesIO

URL = 'https://raw.githubusercontent.com/PMDCollab/SpriteCollab/master/'

EXPLIST = ["Normal.png","Happy.png","Pain.png","Angry.png","Worried.png","Sad.png","Crying.png","Shouting.png","Teary-Eyed.png","Determined.png","Joyous.png","Inspired.png","Surprised.png","Dizzy.png","Special0.png","Special1.png","Sigh.png","Stunned.png","Special2.png","Special3.png"]
EXPREVLIST = ["Normal^.png","Happy^.png","Pain^.png","Angry^.png","Worried^.png","Sad^.png","Crying^.png","Shouting^.png","Teary-Eyed^.png","Determined^.png","Joyous^.png","Inspired^.png","Surprised^.png","Dizzy^.png","Special0^.png","Special1^.png","Sigh^.png","Stunned^.png","Special2^.png","Special3^.png"]

def loadCreditsFile(path):
    try:
        response = requests.get(URL + "portrait" + path + 'credits.txt', allow_redirects=True)
        creditsfile = response.content.decode("utf-8")

        creditsfile = creditsfile.split('\n')
        if creditsfile[len(creditsfile)-1] == "": creditsfile.pop()
        for i in range(len(creditsfile)):
            creditsfile[i] = creditsfile[i].split('\t')

        return creditsfile
        
    except:
        print("Failed to retrieve credit file: " + URL + "portrait" + path + "credits.txt")
        return "error"


def getForm(formEntry, formEntryName, formEntryPath):

    pForm = {
        'name': formEntryName,
        'path': formEntryPath,
        'complete': formEntry["portrait_complete"],
        'filename': "portrait" + formEntryPath.replace("/","-")[0:len(formEntryPath)-1] + ".png",
        'portraits': [],
        'preversed': [],
        'credits': [],
        'modified': formEntry["portrait_modified"]
    }
    
    expressions = formEntry["portrait_files"]

    for exp in EXPLIST:
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
        pForm['credits'] = loadCreditsFile(formEntryPath)
        return pForm

def retrivePortrait(url):
    try:
        response = requests.get(url, allow_redirects=True)
        png = Image.open(BytesIO(response.content))  
    except: 
        print("Failed to retrieve portrait file: " + url)
        return

    return png

def generatePortrait(portraits,preversed,path,filename):

    return
    
    if portraits.count(1) == 1 and not preversed:
        compilation = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
        compilation.paste(retrivePortrait(URL + "portrait" + path + "Normal.png"), (0,0))
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
            compilation.paste(retrivePortrait(URL + "portrait" + path + EXPLIST[i]), (x,y))
            
        x += 40
        if x == 200:
            x = 0
            y += 40
    if preversed:
        for i in range(20):
            if preversed[i]:
                compilation.paste(retrivePortrait(URL + "portrait" + path + EXPREVLIST[i]), (x,y))
            
            x += 40
            if x == 200:
                x = 0
                y += 40

    compilation.save("resources/portraits/" + filename)

try:
    response = requests.get(URL + "tracker.json", allow_redirects=True)
    tracker = json.loads(response.content.decode("utf-8"))
except:
    print("Failed to get tracker.json")
    exit(1001)

with open("action/lastrun","r") as datefile:
    lastRunDate = datetime.datetime.fromisoformat(datefile.read())

result = {}

for jentry in tracker:

    if jentry == "0000": continue #lets skip the first one as its differnet and unneded
    #if int(jentry) < 586: continue

    pentry = {
        'id': jentry,
        'name': tracker[jentry]['name'],
        'forms': {}
    }

    for jform in tracker[jentry]['subgroups']:
        
        if jform == "0000": # this entry works different from the rest, the male unshiny one is in the root of the entry
            form = getForm(tracker[jentry], "Normal", "/"+ jentry + "/")
            if form:
                pentry['forms'][jform] = form
                generatePortrait(form["portraits"],form["preversed"],form["path"],form["filename"])
        else:
            form = getForm(tracker[jentry]['subgroups'][jform], tracker[jentry]['subgroups'][jform]['name'], "/"+ jentry + "/" + jform + "/")
            if form:
                pentry['forms'][jform] = form
                generatePortrait(form["portraits"],form["preversed"],form["path"],form["filename"])
        
        if '0000' in tracker[jentry]['subgroups'][jform]['subgroups']: # check for female
            if '0002' in tracker[jentry]['subgroups'][jform]['subgroups']['0000']['subgroups']:
                form = getForm(tracker[jentry]['subgroups'][jform]['subgroups']['0000']['subgroups']['0002'], "Female", "/"+ jentry + "/" + jform + "/0000/0002/")
                if form:
                    pentry['forms'][jform+"f"] = form
                    generatePortrait(form["portraits"],form["preversed"],form["path"],form["filename"])
            
        if '0001' in tracker[jentry]['subgroups'][jform]['subgroups']: # check for shiny
            form = getForm(tracker[jentry]['subgroups'][jform]['subgroups']['0001'], "Shiny", "/"+ jentry + "/" + jform + "/0001/")
            if form:
                pentry['forms'][jform+"s"] = form
                generatePortrait(form["portraits"],form["preversed"],form["path"],form["filename"])

            if '0002' in tracker[jentry]['subgroups'][jform]['subgroups']['0001']['subgroups']: # check for female shiny
                form = getForm(tracker[jentry]['subgroups'][jform]['subgroups']['0001']['subgroups']['0002'], "Female Shiny", "/"+ jentry + "/" + jform + "/0001/0002/")
                if form:
                    pentry['forms'][jform+"fs"] = form
                    generatePortrait(form["portraits"],form["preversed"],form["path"],form["filename"])

    if len(pentry['forms']):
        response = requests.get(URL + "portrait/" + pentry['id'] + "/Normal.png", allow_redirects=True)
        neutral = Image.open(BytesIO(response.content))
        neutral.save("resources/neutrals/" + pentry['id'] + ".png")
    
    result[jentry] = pentry
    print(pentry["id"])

with open('resources/pokemons.json', 'w') as outfile:
    json.dump(result, outfile)

with open("action/lastrun","w") as datefile:
    datefile.write(str(datetime.datetime.now()))


    