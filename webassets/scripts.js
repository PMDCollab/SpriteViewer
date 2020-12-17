let sourcePath = 'https://raw.githubusercontent.com/PMDCollab/SpriteCollab/master/';
let expresionNames = ["Normal","Happy","Pain","Angry","Worried","Sad","Crying","Shouting","Teary-Eyed","Determined","Joyous","Inspired","Surprised","Dizzy","Special0","Special1","Sigh","Stunned","Special2","Special3"]

function findGetParameter(parameterName) {

    let result = null, tmp = [];
    location.search.substr(1).split("&").forEach(function (item) {
        tmp = item.split("=");
        if (tmp[0] === parameterName) result = decodeURIComponent(tmp[1]);
    });
    return result;
}

async function loadTracker(){

    return await fetch(sourcePath + 'tracker.json').then(response => response.json());
}

async function loadCredits(){

    let credits = {};
    let text = await fetch(sourcePath + 'credit_names.txt').then(response => response.text());

    text = text.split("\n");
    text.shift(); //remove the table titles
    for (i in text){
        if (text[i] == "") continue;
        let entry = text[i].split("\t");
        credits[entry[1]] = entry;
    }

    return credits;
}

async function parseCredits(credit){

        let creditsList = await loadCredits();
        let author = creditsList[credit];
        let aElement;

        if (!author) {
            aElement = "unknown";
        } else if (!author[0]) { //I dont know what to do with these authors that has a discord ID but no names
            aElement = "Discord ID: "+ author[1];
        } else {
            if (author[2].substr(0,4) == "http"){
                aElement = "<a href="+author[2]+">"+author[0]+"</a>";
            } else if (author[2].substr(0,1) == "@") {
                aElement = "<a href="+author[2]+">"+author[0]+"</a>";
            } else if (author[2].substr(0,3) == "/u/"){
                aElement = "<a href=http://reddit.com"+author[2]+">"+author[0]+"</a>";
            } else if (author[2].includes("@")) {
                aElement = "<a href=mailto:"+author[2]+">"+author[0]+"</a>";
            } else if (author[2].includes("#")) {
                aElement = author[0] + " (Discord ID: " + author[2] + ")";
            }
        }

        return aElement;
}

function entriesUnfolding(entry,path = "/"){ //I dont even know, dont read this, you dont deserve the migraine

    let entries = [];
    
    if (entry.name && entry.portrait_credit){
        let nentry = Object.assign({}, entry);
        nentry.path = path;
        delete nentry.subgroups;
        entries = entries.concat(nentry);
    }
    
    for (let i in entry.subgroups){
        ipath = path + i + "/";
        if (entry.subgroups[i].subgroups) {
            entries = entries.concat(entriesUnfolding(entry.subgroups[i],ipath));
        }
    }
    
    return entries;
}

function parseExpresions(pjson){

    let existing = pjson["portrait_files"];
    let portraits = [], portraitsr = [], result = [];

    for (i in expresionNames){

        if (existing.includes(expresionNames[i]+".png")){
            portraits.push(expresionNames[i]);
        }else{
            portraits.push(false);
        }
    }

    for (i in expresionNames){

        if (existing.includes(expresionNames[i]+"^.png")){
            portraitsr.push(expresionNames[i]);
        }else{
            portraitsr.push(false);
        }
    }

    if(portraitsr.every(isfalse => isfalse === false) == false){ //check if there is at least 1 reverse portrait
        result = [portraits,portraitsr];
    }else{
        result = [portraits,false];
    }
    
    return result;
}

function fetchImage(context,cell,id,path,expresion,reverse,row,col){

    let img =  new Image();
    if(expresion){
        if (reverse) expresion += "^", row += 8;
        img.src = sourcePath + "portrait/" + id + path + expresion +".png";
        img.onload = function() {
            context.drawImage(img,40*col,40*row/2);
        };
    } else {
        img.src = "webassets/empty.png";
    }
    cell.appendChild(img);
}

function downloadCanvas(element){
    let canvas = element.parentElement.getElementsByTagName("canvas")[0];
    let link = document.createElement('a');
    link.download = 'filename.png';
    link.href = canvas.toDataURL()
    link.click();
}

function createTable(id, pjson ,path){

    let expresions = parseExpresions(pjson);

    let div = document.createElement("div");

    let title = document.createElement("h2");       //title
    title.innerHTML = pjson.name
    title.setAttribute("class", "port-title");
    div.appendChild(title);

    let canvas = document.createElement("canvas");  //canvas
    canvas.setAttribute("class", "port-canvas");
    canvas.setAttribute("width", "200");
    canvas.setAttribute("height", "160");
    canvas.setAttribute("hidden","true")
    let context = canvas.getContext('2d');
    div.appendChild(canvas);

    let table = document.createElement("table");    //table
    table.setAttribute("class", "port-table");
    
    let trev = null;
    if (expresions[1]) {
        trev = document.createElement("tbody");
        canvas.setAttribute("height", "320");
    }

    for (i = 0, row = 0; row < 8; row = row + 2){

        rowpic = table.insertRow(row);
        rowtext = table.insertRow(row + 1);

        if (expresions[1]) {

            rowpicr = trev.insertRow(row);
            rowtextr = trev.insertRow(row + 1);
        }
        
        for (col = 0; col < 5; col++, i++){

            expname = expresions[0][i];
            
            cell = rowpic.insertCell(col);
            fetchImage(context,cell,id,path,expname,false,row,col)
            cell = rowtext.insertCell(col);
            cell.innerHTML = expresionNames[i];

            if (expresions[1]) {

                expname = expresions[1][i];
                
                cell = rowpicr.insertCell(col);
                fetchImage(context,cell,id,path,expname,true,row,col)
                cell = rowtextr.insertCell(col);
                cell.innerHTML = expresionNames[i];
            }
        }
    
    }


    if (expresions[1]) {
        table.appendChild(trev);
    }

    let credcell = table.insertRow(-1).insertCell(0);
    credcell.setAttribute("class", "port-credit");
    credcell.setAttribute("colspan", "5");
    parseCredits(pjson.portrait_credit).then(cred=>credcell.innerHTML = "Credits: " + cred);
    div.appendChild(table);
    
    let donwload = document.createElement("div");
    donwload.innerHTML = "<p>Download!</p>"
    donwload.setAttribute("onclick", "downloadCanvas(this)");
    donwload.setAttribute("class", "port-button");
    donwload.setAttribute("hidden", "true");
    div.appendChild(donwload);

    return div;
}

async function populateListTable(tablebody,creator,gen,official,filled,incomplete,missing){
		
    let gens = [["0001","0898"],
                ["0001","0151"],
                ["0152","0251"],
                ["0252","0386"],
                ["0387","0493"],
                ["0494","0649"],
                ["0650","0721"],
                ["0722","0809"],
                ["0810","0898"]]
                
    let tracker = await loadTracker();
    
    for (const entry in tracker){
    
        if (entry < gens[gen][0] || entry > gens[gen][1]) continue;
        if (!missing && tracker[entry]["portrait_files"].length == 0) continue;
        if (!official && tracker[entry]["portrait_credit"] == "CHUNSOFT") continue;
        if (!filled && tracker[entry]["portrait_complete"] == 2) continue;
        if (!incomplete && tracker[entry]["portrait_complete"] == 1) continue;
        if (!incomplete && (tracker[entry]["portrait_files"].length != 0) && tracker[entry]["portrait_complete"] == 0) continue;
        if (creator && tracker[entry]["portrait_credit"] != creator) continue;
    
        let row = tablebody.insertRow();
        
        let pkdex = row.insertCell(0);
        pkdex.innerHTML = entry;
        
        let portrait = row.insertCell(1);
        
        let name = row.insertCell(2);
        name.innerHTML = tracker[entry]["name"];
        
        let status = row.insertCell(3);
        let st, stn;
        if (tracker[entry]["portrait_complete"] == 2) {
            st = "Fully Featured";
            stn = 2;
        } else if(tracker[entry]["portrait_files"].length == 0){
            st = "Missing";
            stn = 0;
        } else {
            st = "Exists";
            stn = 1;
        }
        status.innerHTML = st;
        status.attributes = "class=\"status-"+stn+"\""
        
        let link = row.insertCell(4);
        if (stn != 0){
            portrait.innerHTML = "<img src=\"https://raw.githubusercontent.com/PMDCollab/SpriteCollab/master/portrait/"+entry+"/Normal.png\"></img>"
            link.innerHTML = "<a href=\"portrait.html?id="+entry+"\">Portrait</a>";
        } else {
            portrait.innerHTML = "<img src=\"webassets/empty.png\"></img>"
            link.innerHTML = "";
        }
    }
}

async function populatePortraits(id){

    let container = document.getElementById("container");

    let tracker = await loadTracker();

    let entry = tracker[id];
    if (!entry) entry = tracker["0000"];

    let entries = entriesUnfolding(entry);

    for(form in entries){

        container.appendChild(createTable(id, entries[form], entries[form].path));
    }
}
