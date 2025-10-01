 //==========================================
// Page startup
//==========================================
const tableArea = document.getElementById("table-container")

let tables_arr;
let song_ids;
let song_names;
let zipped_arrays;

window.addEventListener("load", async () => {

    document.querySelectorAll('.plotly-graph-div').forEach(div => {
        Plotly.Plots.resize(div)
    });

    const response1 = await fetch('/table_setup', {
                        method: 'GET',
                        headers: {
                        'Content-Type': 'application/json'
                        }
                    })

    tables_arr = await response1.json()
    tableArea.innerHTML = tables_arr[0]

    const response2 = await fetch('/song_info', {
                        method: 'GET',
                        headers: {
                        'Content-Type': 'application/json'
                        }
                    })
    
    let [song_ids,song_names] = await response2.json()

    zipped_arrays = [[song_ids[0], song_names[0]]].concat( song_ids.slice(1).map(function(e, i) {
                        return [e, song_names[i+1]];
                    }));

    const response3 = await fetch('/get_facts', {
                        method: 'GET',
                        headers: {
                        'Content-Type': 'application/json'
                        }
                    })

    factAnswers = await response3.json()

    
    updateFact()
    fillDropdown()


    document.querySelector("#loader").style.display = "none";
    document.querySelector("body").style.visibility = "visible";
});

function fillDropdown() {
    for (pair of zipped_arrays) {
            var opt = document.createElement('option');
            opt.value = pair[0];
            opt.textContent = pair[1];
            songsDropdown.appendChild(opt);
    }

}

//==========================================
// Song Player
//==========================================
const leftPlayerButton = document.getElementById("left-player-button")
const rightPlayerButton = document.getElementById("right-player-button")
const playerBox = document.getElementById("player-box")
const placeholderBox = document.getElementById("widgit-7")
const songSubmitBtn = document.getElementById("song-submit-button")
const player = document.getElementById("player")
const errorMsg = document.getElementById("no-songs-error")

let currentSongIdx = 0;
let songsAdded = Array();
let songData;

leftPlayerButton.addEventListener('click',() => {
    currentSongIdx -= 1
    updateButtons()
    updateEmbed()

})

rightPlayerButton.addEventListener('click',()=> {
    currentSongIdx += 1
    updateButtons()
    updateEmbed() 
})

songSubmitBtn.addEventListener('click', async () => {
    playerBox.style.visibility = "hidden"
    playerBox.style.display = "none"

    if (errorMsg) {
        errorMsg.remove()
    }

    if (songsAdded.length == 0) {
        const errorMsg = document.createElement("h2")
        errorMsg.textContent = "Please add at least 1 song"
        errorMsg.setAttribute("id","no-songs-error")
        document.getElementById("error-container").appendChild(errorMsg)
    }

    else {
        playerBox.style.visibility = "visible"
        playerBox.style.display = "flex"

        if (songsAdded.length == 1) {
            percs = ['100']
        }

        const response = await fetch('/process', {
                                    method: 'POST',
                                    headers: {
                                    'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify({ splits: percs, ids:songsAdded })
                                })

        const data = await response.json()
        songData = data.result.map((s) => s.replace(/'/g,'').replace(/ /g,''));
        currentSongIdx = 0
        updateButtons()
        updateEmbed()
        }
    });

function updateEmbed () {
    player.setAttribute('src',`https://open.spotify.com/embed/track/${songData[currentSongIdx]}?utm_source=generator`)
}

function updateButtons () {
    leftPlayerButton.disabled = currentSongIdx <= 0
    rightPlayerButton.disabled = currentSongIdx >= songData.length - 1
}


//==========================================
// Song Tags
//==========================================
const addSongBtn = document.getElementById("add-song-button")
const songsDropdown = document.getElementById("song-selection-dropdown")
const tagArea = document.getElementById("song-area")

addSongBtn.addEventListener("click", () => addSong())

function deleteTag(id) {
    const tagDiv = document.getElementById(id+"-div")
    tagDiv.remove()

    const index = songsAdded.indexOf(id);
    if (index > -1) { 
        songsAdded.splice(index, 1); 
    }

    addSongBtn.disabled = false
    handleCount -= 1
    update_slider()

    if (handleCount == 0) {
        songSubmitBtn.disabled = true
    }

}


function addSong(ev) {
    const song_id = songsDropdown.value
    const song_name = songsDropdown.options[songsDropdown.selectedIndex].text

    if (!songsAdded.includes(song_id) && song_id != "DEFAULT") {

        const newNode = document.createElement("div")
        newNode.setAttribute("class","song-tag")
        newNode.id = song_id + "-div"

        const text = document.createElement("h3")
        text.textContent = song_name

        const contrib = document.createElement("h3")
        contrib.setAttribute("class", "contribution-value")

        
        const deleteBtn = document.createElement("button")
        deleteBtn.textContent = "X"
        deleteBtn.id = song_id 
        deleteBtn.addEventListener("click", () => deleteTag(song_id));

        newNode.append(text,deleteBtn,contrib)
        tagArea.appendChild(newNode)

        songsAdded.push(song_id)
        handleCount += 1
        update_slider()
    }

    console.log(handleCount)

    if (handleCount > 4) {
        addSongBtn.disabled = true
    }

    if (handleCount > 0) {
        songSubmitBtn.disabled = false
    }
}

//==========================================
// Slider
//==========================================
const slider = document.getElementById('multiSlider');
const tags = document.getElementsByClassName("contribution-value");
const emptyMsg = document.getElementById("empty-song-msg")
const sliderInstruction = document.getElementById("slider-instruction-1")
const slider_div = document.getElementById("slider-container")
const sliderInstructionText = "Control how much you want each song to contribute:"
const emptyMsgText = "None! You can pick up to 5 songs"
const colours = ["#E00000",'darkgreen','blue','#ffa915ff','pink'];

let handleCount = 0
let percs;

function slider_create() {
    const splits = []
    const jumps = parseInt(100 / (handleCount))
    for (let i = 1; i <= handleCount - 1; i++) {
        splits.push(i*jumps);
    }


    noUiSlider.create(slider, {
        start: splits, 
        connect: Array(handleCount).fill(true), 
        range: {min: 0, max: 100},
        step:1,
        margin:10,
        padding : [10,10],
    });

    segmentColours()

    slider.noUiSlider.on('update', (values) => {
        const percs_calcs = [...values.map(Number)];

        percs_calcs.unshift(0);
        percs_calcs.push(100);

        percs = percs_calcs.slice(1).map((value, index) => {
            return value - percs_calcs[index];
        });

        Array.from(tags).forEach((tag, index) => {
            tag.textContent = `(${percs[index]}%)`;
        });

})}

function segmentColours() {
            const segments = slider.querySelectorAll('.noUi-connect');
        for (let i = 0; i < handleCount; i++) {
            segments[i].style.background = colours[i]
        }
}

function update_slider() {
    if (slider.noUiSlider !== undefined) {
        slider.noUiSlider.destroy();
    }

    if (handleCount > 1) {
        slider_create();
        sliderInstruction.textContent = sliderInstructionText
        const equal_perc = String(parseInt(100 / handleCount))

        Array.from(tags).forEach((tag,index) => {
            tag.textContent = "(" + equal_perc + "%)";
            tag.style.color = colours[index];
        });
    }
    else {
        sliderInstruction.textContent = ""
        for (const tag of tags) {
            tag.textContent = ""
        }
    }

    if (handleCount > 0) {
        emptyMsg.textContent = ""
    }
    else {
        emptyMsg.textContent = emptyMsgText
    }
}


// slider.noUiSlider.on('update', (values, handle) => {
// values = values.map(Number); // convert to numbers
// const lastHandle = values.length - 1;

// if (handle === lastHandle && values[lastHandle] > maxValue - limitForLastHandle) {
//     values[lastHandle] = maxValue - limitForLastHandle;
//     slider.noUiSlider.set(values);
// })

//==========================================
// Quick Stats box
//==========================================
const leftFactButton = document.getElementById("left-button-stats")
const rightFactButton = document.getElementById("right-button-stats")
const statDescr = document.getElementById("stat-description-text")
const statValue = document.getElementById("stat-value-text")
const tableDropdown = document.getElementById("dropdown-menu")
const factText = ["Average liked <br>song length ", "Songs in the <br>past week",
                    "Songs in the <br>past 30 days", "Average songs <br>per day"];

let factIdx = 0;
let factAnswers;

rightFactButton.addEventListener('click',() => {
    factIdx = (factIdx + 1) % 4;
    updateFact()
})

leftFactButton.addEventListener('click',() => {
    factIdx = (factIdx + 3) % 4;
    updateFact()
})

tableDropdown.addEventListener('change',() => {
    let choice = parseInt(tableDropdown.value)
    tableArea.innerHTML = tables_arr[choice]
});

function updateFact() {
    statDescr.innerHTML = factText[factIdx];
    statValue.textContent = factAnswers[factIdx];
}
