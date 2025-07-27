//function esc(element) {
//    document.addEventListener('keydown', event => {
//        if(event.key === 'Escape') {
//            element.style.display = 'none';
//        }
//    });
//    element.parentElement.querySelector('input[type=text]').addEventListener("blur", () => {
//        setTimeout(() => {
//            element.style.display = 'none';
//        },80);
//    });
//}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelector("#flight-from").addEventListener("input", event => {
        flight_from(event);
    });

    document.querySelector("#flight-to").addEventListener("input", event => {
        flight_to(event);
    });

    document.querySelector("#flight-from").addEventListener("focus", event => {
        flight_from(event, true);
    });

    document.querySelector("#flight-to").addEventListener("focus", event => {
        flight_to(event, true);
    });

    document.querySelectorAll('.trip-type').forEach(type => {
        type.onclick = trip_type;
    });

});


function showplaces(input) {
    let box = input.parentElement.querySelector(".places_box");
    box.style.display = 'block';
}

function hideplaces(input) {
    let box = input.parentElement.querySelector(".places_box");
    setTimeout(() => {
        box.style.display = 'none';
    }, 300);
}

function selectplace(option) {
    let input = option.parentElement.parentElement.querySelector('input[type=text]');
    input.value = option.dataset.value.toUpperCase();
    input.dataset.value = option.dataset.value;
}

function flight_to(event, focus=false) {
    let input = event.target;
    let list = document.querySelector('#places_to');
    showplaces(input);
    if(!focus) {
        input.dataset.value = '';
    }
    if(input.value.length > 0) {
        // Search both local and Amadeus sources
        searchBothAirportSources(input.value, list);
    }
}

function flight_from(event, focus=false) {
    let input = event.target;
    let list = document.querySelector('#places_from');
    showplaces(input);
    if(!focus) {
        input.dataset.value = '';
    }
    if(input.value.length > 0) {
        // Search both local and Amadeus sources
        searchBothAirportSources(input.value, list);
    }
}

// Enhanced airport search combining local and Amadeus sources
async function searchBothAirportSources(query, listElement) {
    // Clear existing results
    listElement.innerHTML = '<div class="text-center p-2"><small>Searching...</small></div>';
    
    try {
        // Search local database
        const localPromise = fetch('query/places/' + query)
            .then(response => response.json())
            .catch(() => []);
        
        // Search Amadeus API if available
        const amadeusPromise = typeof amadeusClient !== 'undefined' ? 
            amadeusClient.getAirportSuggestions(query).catch(() => []) : 
            Promise.resolve([]);
        
        // Wait for both searches
        const [localPlaces, amadeusPlaces] = await Promise.all([localPromise, amadeusPromise]);
        
        // Clear loading message
        listElement.innerHTML = '';
        
        // Combine and deduplicate results
        const combinedResults = combineAirportResults(localPlaces, amadeusPlaces);
        
        if (combinedResults.length === 0) {
            listElement.innerHTML = '<div class="text-center p-2 text-muted"><small>No airports found</small></div>';
            return;
        }
        
        // Display results
        combinedResults.forEach(element => {
            let div = document.createElement('div');
            div.setAttribute('class', element.source === 'amadeus' ? 'each_places_amadeus_list' : 'each_places_local_list');
            div.classList.add('places__list');
            div.setAttribute('onclick', "selectplace(this)");
            div.setAttribute('data-value', element.code);
            
            // Enhanced display with source indicator
            const sourceIcon = element.source === 'amadeus' ? '🌐' : '📍';
            div.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${element.code}</strong> - ${element.city}
                        <br><small class="text-muted">${element.country}</small>
                    </div>
                    <small class="text-muted">${sourceIcon}</small>
                </div>
            `;
            
            listElement.append(div);
        });
        
    } catch (error) {
        console.error('Airport search error:', error);
        
        // Fallback to local search only
        fetch('query/places/' + query)
        .then(response => response.json())
        .then(places => {
            listElement.innerHTML = '';
            places.forEach(element => {
                let div = document.createElement('div');
                div.setAttribute('class', 'each_places_local_list');
                div.classList.add('places__list');
                div.setAttribute('onclick', "selectplace(this)");
                div.setAttribute('data-value', element.code);
                div.innerText = `${element.city} (${element.country})`;
                listElement.append(div);
            });
        });
    }
}

// Combine and deduplicate airport results from multiple sources
function combineAirportResults(localPlaces, amadeusPlaces) {
    const seen = new Set();
    const combined = [];
    
    // Add local places first (priority)
    localPlaces.forEach(place => {
        if (place.code && !seen.has(place.code.toUpperCase())) {
            seen.add(place.code.toUpperCase());
            combined.push({
                code: place.code.toUpperCase(),
                city: place.city,
                country: place.country,
                source: 'local'
            });
        }
    });
    
    // Add Amadeus places (avoid duplicates)
    amadeusPlaces.forEach(place => {
        if (place.code && !seen.has(place.code.toUpperCase())) {
            seen.add(place.code.toUpperCase());
            combined.push({
                code: place.code.toUpperCase(),
                city: place.city || place.name,
                country: place.country,
                source: 'amadeus'
            });
        }
    });
    
    // Sort by relevance (local first, then alphabetical)
    return combined.sort((a, b) => {
        if (a.source !== b.source) {
            return a.source === 'local' ? -1 : 1;
        }
        return a.city.localeCompare(b.city);
    });
}

function trip_type() {
    document.querySelectorAll('.trip-type').forEach(type => {
        if(type.checked) {
            if(type.value === "1") {
                document.querySelector('#return_date').value = '';
                document.querySelector('#return_date').disabled = true;
            }
            else if(type.value === "2") {
                document.querySelector('#return_date').disabled = false;
            }
        }
    })
}

function flight_search() {
    const fromInput = document.querySelector("#flight-from");
    const toInput = document.querySelector("#flight-to");
    const departDate = document.querySelector("#depart_date");
    const returnDate = document.querySelector("#return_date");
    
    // Check origin - either dataset.value (from dropdown) or input value (typed in)
    if(!fromInput.dataset.value && !fromInput.value.trim()) {
        alert("Please enter or select flight origin.");
        return false;
    }
    
    // Check destination - either dataset.value (from dropdown) or input value (typed in)
    if(!toInput.dataset.value && !toInput.value.trim()) {
        alert("Please enter or select flight destination.");
        return false;
    }
    
    // Check departure date for both trip types
    if(!departDate.value) {
        alert("Please select departure date.");
        return false;
    }
    
    // Check return date only for round trips
    if(document.querySelector("#round-trip").checked) {
        if(!returnDate.value) {
            alert("Please select return date.");
            return false;
        }
    }
    
    // If we get here, validation passed
    return true;
}

function enhancedSearch() {
    // Validate inputs first
    if(!document.querySelector("#flight-from").dataset.value) {
        alert("Please select flight origin.");
        return false;
    }
    if(!document.querySelector("#flight-to").dataset.value) {
        alert("Please select flight destination.");
        return false;
    }
    if(!document.querySelector("#depart_date").value) {
        alert("Please select departure date.");
        return false;
    }
    
    // Check return date for round trip
    if(document.querySelector("#round-trip").checked) {
        if(!document.querySelector("#return_date").value) {
            alert("Please select return date.");
            return false;
        }
    }
    
    // Build URL parameters for enhanced search
    const params = new URLSearchParams({
        Origin: document.querySelector("#flight-from").dataset.value,
        Destination: document.querySelector("#flight-to").dataset.value,
        DepartDate: document.querySelector("#depart_date").value,
        SeatClass: document.querySelector("#SeatType").value,
        TripType: document.querySelector("input[name='TripType']:checked").value
    });
    
    // Add return date if round trip
    if(document.querySelector("#round-trip").checked && document.querySelector("#return_date").value) {
        params.append('ReturnDate', document.querySelector("#return_date").value);
    }
    
    // Redirect to enhanced search page
    window.location.href = `/enhanced-search?${params}`;
}