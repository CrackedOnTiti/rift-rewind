// Configuration de la map LoL (Summoner's Rift)
const MAP_CONFIG = {
    minX: 0,
    maxX: 14820,
    minY: 0,
    maxY: 14820
};

// Configuration du backend
const BACKEND_URL = 'http://localhost:8000';

let currentMarker = null;
const map = document.getElementById('map');
const mapContainer = document.getElementById('mapContainer');

console.log('Script chargé !');
console.log('Map element:', map);
console.log('Map container:', mapContainer);

/**
 * Convertir les coordonnées pixel en coordonnées du jeu
 */
function pixelToGameCoords(pixelX, pixelY, imageWidth, imageHeight) {
    const gameX = Math.round((pixelX / imageWidth) * (MAP_CONFIG.maxX - MAP_CONFIG.minX) + MAP_CONFIG.minX);
    const gameY = Math.round(((imageHeight - pixelY) / imageHeight) * (MAP_CONFIG.maxY - MAP_CONFIG.minY) + MAP_CONFIG.minY);
    return { x: gameX, y: gameY };
}

/**
 * Afficher un message de status
 */
function showStatus(message, type = 'success') {
    const statusEl = document.getElementById('status');
    statusEl.textContent = message;
    statusEl.className = `status ${type}`;
    statusEl.style.display = 'block';
    
    setTimeout(() => {
        statusEl.style.display = 'none';
    }, 5000);
}

/**
 * Gérer le clic sur la map
 */
map.addEventListener('click', function(e) {
    console.log('Clic détecté !', e);
    
    const rect = map.getBoundingClientRect();
    const pixelX = e.clientX - rect.left;
    const pixelY = e.clientY - rect.top;
    
    console.log('Position pixel:', pixelX, pixelY);
    
    // Supprimer l'ancien marker
    if (currentMarker) {
        currentMarker.remove();
    }
    
    // Créer un nouveau marker
    currentMarker = document.createElement('div');
    currentMarker.className = 'marker';
    currentMarker.style.left = pixelX + 'px';
    currentMarker.style.top = pixelY + 'px';
    mapContainer.appendChild(currentMarker);
    
    // Convertir en coordonnées du jeu
    const gameCoords = pixelToGameCoords(pixelX, pixelY, rect.width, rect.height);
    console.log('Coordonnées jeu:', gameCoords);
    
    // Mettre à jour l'affichage
    document.getElementById('pixelX').textContent = Math.round(pixelX);
    document.getElementById('pixelY').textContent = Math.round(pixelY);
    document.getElementById('gameX').textContent = gameCoords.x;
    document.getElementById('gameY').textContent = gameCoords.y;
    
    // Mettre à jour l'exemple d'API
    updateAPIExample(gameCoords);
});

/**
 * Mettre à jour l'exemple d'API call
 */
function updateAPIExample(coords) {
    const apiExample = `// Appel vers ton backend FastAPI
fetch('${BACKEND_URL}/api/map/position', {
method: 'POST',
headers: {
'Content-Type': 'application/json',
},
body: JSON.stringify({
x: ${coords.x},
y: ${coords.y},
timestamp: ${Date.now()}
})
})
.then(response => response.json())
.then(data => {
console.log('Réponse:', data);
})
.catch(error => {
console.error('Erreur:', error);
});`;
    
    document.getElementById('apiExample').textContent = apiExample;
}

/**
 * Copier les coordonnées dans le presse-papier
 */
function copyCoordinates() {
    const gameX = document.getElementById('gameX').textContent;
    const gameY = document.getElementById('gameY').textContent;
    
    if (gameX === '-') {
        showStatus('Clique d\'abord sur la map !', 'error');
        return;
    }
    
    const coords = `{ "x": ${gameX}, "y": ${gameY} }`;
    navigator.clipboard.writeText(coords).then(() => {
        showStatus('Coordonnées copiées ! ✅', 'success');
    }).catch(err => {
        showStatus('Erreur lors de la copie', 'error');
        console.error('Erreur:', err);
    });
}

/**
 * Appeler l'API backend
 */
async function callAPI() {
    const gameX = document.getElementById('gameX').textContent;
    const gameY = document.getElementById('gameY').textContent;
    
    if (gameX === '-') {
        showStatus('Clique d\'abord sur la map !', 'error');
        return;
    }
    
    const payload = {
        x: parseInt(gameX),
        y: parseInt(gameY),
        timestamp: Date.now()
    };
    
    console.log('Envoi à l\'API:', payload);
    
    try {
        const response = await fetch(`${BACKEND_URL}/api/map/position`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Réponse de l\'API:', data);
        showStatus(`API call réussie ! Réponse: ${JSON.stringify(data)}`, 'success');
        
    } catch (error) {
        console.error('Erreur lors de l\'appel API:', error);
        showStatus(`Erreur: ${error.message}. Vérifie que le backend tourne !`, 'error');
    }
}

// Vérifier que tout est bien chargé
map.addEventListener('load', function() {
    console.log('Image chargée avec succès !');
});

map.addEventListener('error', function() {
    console.error('Erreur de chargement de l\'image !');
    showStatus('Erreur: Image non trouvée à /assets/map.jpeg', 'error');
});

console.log('Map coordinate converter prêt !');
