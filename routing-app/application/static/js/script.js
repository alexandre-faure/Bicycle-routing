// Définition des layers
var layerControl = L.control.layers({}, {});

var osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
});

layerControl.addBaseLayer(osm, "OpenStreetMap");

// Création de la carte
var map = L.map('map', {center:[48.71, 2.17], zoom:14, layers:[osm]});

// Ajout du contrôle des layers
layerControl.addTo(map);

// Personnaliser les icones
var FlagIcon = L.Icon.extend({
    options: {
        iconSize:     [40, 40],
        iconAnchor:   [0, 40],
        popupAnchor:  [20, -40]
    }
});

var greenFlag = new FlagIcon({iconUrl: "/static/img/green_flag_icon.png"}),
    redFlag = new FlagIcon({iconUrl: "/static/img/red_flag_icon.png"});


// Gestion de la sélection du début ou de la fin du trajet
var selection_road_state = null;

const changeStateRoadSelection = (newState) => {
    if (selection_road_state === newState) {
        selection_road_state = null;
        document.getElementById("road_start").classList.remove("selected");
        document.getElementById("road_end").classList.remove("selected");
    }
    else{
        if (newState === "start"){
            selection_road_state = "start";
            document.getElementById("road_start").classList.add("selected");
            document.getElementById("road_end").classList.remove("selected");
        }
        else{
            selection_road_state = "end";
            document.getElementById("road_start").classList.remove("selected");
            document.getElementById("road_end").classList.add("selected");
        }
    }
}

document.getElementById("road_start").addEventListener("click", function(){
    changeStateRoadSelection("start")
});

document.getElementById("road_end").addEventListener("click", function(){
    changeStateRoadSelection("end")
});

// Ajout des markers de début et fin de trajet
var road_markers = {
    start:null,
    end:null
}

// Gestion du boutton permettant de déterminer le trajet optimal
const updateRoadCalculationButton = () => {
    if (road_markers.start !== null && road_markers.end !== null){
        // Autoriser le calcul du trajet
        document.getElementById("calculate_road").classList.remove("disabled");
    }
    else{
        // Interdire le calcul du trajet
        document.getElementById("calculate_road").classList.add("disabled");
    }
}

function updateCounter(message) {
    // Display 'message' on the page
    document.getElementById("countdown").textContent = message;
  }

document.getElementById("calculate_road").addEventListener("click", function(){
    // Afficher le loader
    document.getElementById("loader").style.display = "block";
    // Lancer le compteur
    updateCounter("Calcul du trajet optimal en cours...");
    // Calcul du trajet optimal
    const start = Object.values(road_markers.start._latlng);
    const end = Object.values(road_markers.end._latlng);
    fetch('/calculate_road', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json' // Définit le type de contenu comme JSON
        },
        body: JSON.stringify({
            start : start,
            end : end
        }) // Convertit le dictionnaire en JSON
    })
    .then(response => response.text())
    .then(data => {
        console.log(data)
        var res = JSON.parse(data);
        console.log("Routage effectué avec succès")
        console.log(res)
        // Cacher le loader
        document.getElementById("loader").style.display = "none";
        // Afficher le tracé de la route
        var myLines = {
            "type": "LineString",
            "coordinates": res["coordinates"]
        };
        
        var myStyle = {
            "color": "#b30000",
            "weight": 5,
            "opacity": 0.65
        };
        
        L.geoJSON(myLines, {
            style: myStyle
        }).addTo(map);

        // Afficher le détail du trajet
        document.getElementById("start_street_text").textContent = res["start_street"];

        document.getElementById("end_street_text").textContent = res["end_street"];

        if (res["length"] < 1000){
            document.getElementById("distance_text").textContent = res["length"] + " m";
        }
        else{
            document.getElementById("distance_text").textContent = (res["length"]/1000).toFixed(1) + " km";
        }

        if (res["estimated_time"] == -1){
            document.getElementById("estimated_time_text").textContent = "Aucune estimation disponible";
        }
        else if (res["estimated_time"] < 60){
            document.getElementById("estimated_time_text").textContent = res["estimated_time"] + "s";
        }
        else{
            document.getElementById("estimated_time_text").textContent = (res["estimated_time"]/60).toFixed(0) + " min";
        }

        document.getElementById("info_route").style.display = "block";
    })
    .catch(error => {
        console.error('Erreur :', error)
        // Cacher le loader
        document.getElementById("loader").style.display = "none";}
        );
})

// Gestion du clic sur la carte
const addRoadMarker = (e) => {
    if (selection_road_state !== null){
        if (road_markers[selection_road_state] !== null){
            map.removeLayer(road_markers[selection_road_state]);
        }

        var lat = e.latlng.lat;
        var lng = e.latlng.lng;
        var marker = L.marker([lat, lng], {icon: selection_road_state === "start" ? greenFlag : redFlag}).addTo(map);
        road_markers[selection_road_state] = marker;
        updateRoadCalculationButton();

        // Remove the marker from the map
        marker.on('click', function() {
            // Remove the marker from the map
            map.removeLayer(marker);
            road_markers[selection_road_state] = null;
            updateRoadCalculationButton();
        });
    }
}

map.on('click', function(e) {
    addRoadMarker(e);
});

// Gestion du boutton permettant de fermer le détail d'un trajet
document.getElementById("close_info_route").addEventListener("click", function(){
    if (document.getElementById("info_route").classList.contains("hidden")){
        document.getElementById("info_route").classList.remove("hidden");
    }
    else{
        document.getElementById("info_route").classList.add("hidden");
    }
})