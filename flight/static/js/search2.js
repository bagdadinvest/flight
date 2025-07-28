document.addEventListener("DOMContentLoaded", () => {
    flight_duration();
    //document.querySelector(".filter-price input[type=range]").addEventListener('input', filter); //filter_price
    filter_price();
    document.querySelector(".clr-filter-div button").addEventListener('click', reset_filter);

    initial_click();
    tab_change();
    flight_select();

    // Add responsive event listeners
    setupResponsiveFeatures();

    //document.querySelector(".filter-price2 input[type=range]").addEventListener('input', filter); //filter_price
    if (document.querySelector('#trip-identifier').value === '2') {
        flight_duration2();
        filter_price2();
        document.querySelector(".clr-filter-div2 button").addEventListener('click', reset_filter2);
    }
});

function setupResponsiveFeatures() {
    // Handle window resize
    window.addEventListener('resize', () => {
        // Close mobile filter if screen becomes desktop
        if (window.innerWidth > 768) {
            const filterDiv = document.querySelector('.filter-div.show');
            if (filterDiv) {
                filterDiv.classList.remove('show');
            }
            const overlay = document.querySelector('.mobile-filter-overlay');
            if (overlay) {
                overlay.remove();
            }
        }
    });

    // Add touch-friendly interactions for mobile
    if (window.innerWidth <= 768) {
        // Make flight cards more touch-friendly
        document.querySelectorAll('.each-flight-div').forEach(card => {
            card.style.minHeight = '44px'; // Minimum touch target size
        });
        
        // Add swipe gesture for filters (optional enhancement)
        setupSwipeGestures();
    }
}

function setupSwipeGestures() {
    let startX = 0;
    let startY = 0;
    
    document.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
    });
    
    document.addEventListener('touchend', (e) => {
        if (!startX || !startY) return;
        
        let endX = e.changedTouches[0].clientX;
        let endY = e.changedTouches[0].clientY;
        
        let diffX = startX - endX;
        let diffY = startY - endY;
        
        // Only process horizontal swipes that are significant
        if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
            const filterDiv = document.querySelector('.filter-div.show');
            
            // Swipe left to close filter (for right-to-left languages or RTL layouts)
            if (diffX > 0 && filterDiv) {
                const closeBtn = filterDiv.querySelector('.close-filter button');
                if (closeBtn) closeBtn.click();
            }
        }
        
        startX = 0;
        startY = 0;
    });
}

function flight_duration() {
    document.querySelectorAll(".flight-stops .tooltiptext").forEach(element => {
        let time = element.dataset.value.split(":");
        element.innerText = time[0]+"h "+time[1]+"m";
    });
}

function flight_duration2() {
    document.querySelectorAll(".flight-stops2 .tooltiptext").forEach(element => {
        let time = element.dataset.value.split(":");
        element.innerText = time[0]+"h "+time[1]+"m";
    });
}


function filter(element=null) {
    //reset_filter();
    filter_price();
    if (element) {
        inactive(element);
        active(element);   
    }
    //let type = element.dataset.type;
    let start = null;
    let end = null;
    let flights = null;
    if (true) {
        if(document.querySelector(".departure-time-slot-group .square-box.active")) {
            start = document.querySelector(".departure-time-slot-group .square-box.active").dataset.start;
            end = document.querySelector(".departure-time-slot-group .square-box.active").dataset.end;
            flights = document.querySelectorAll("#flights_div .each-flight-div-box.show");
        }
        departure_slot(flights, start, end);
    }

    flights = null;
    if (true) {
        if(document.querySelector(".arrival-time-slot-group .square-box.active")) {
            start = document.querySelector(".arrival-time-slot-group .square-box.active").dataset.start;
            end = document.querySelector(".arrival-time-slot-group .square-box.active").dataset.end;
            flights = document.querySelectorAll("#flights_div .each-flight-div-box.show");
        }
        arrival_slot(flights, start, end);
    }
    //flights = document.querySelectorAll("#flights_div .each-flight-div-box.show");
}


function filter2(element=null) {
    //reset_filter2();
    filter_price2();
    if (element) {
        inactive2(element);
        active2(element);   
    }
    //let type = element.dataset.type;
    let start = null;
    let end = null;
    let flights = null;
    if (true) {
        if(document.querySelector(".departure-time-slot-group2 .square-box.active")) {
            start = document.querySelector(".departure-time-slot-group2 .square-box.active").dataset.start;
            end = document.querySelector(".departure-time-slot-group2 .square-box.active").dataset.end;
            flights = document.querySelectorAll("#flights_div2 .each-flight-div-box.show");
        }
        departure_slot2(flights, start, end);
    }

    flights = null;
    if (true) {
        if(document.querySelector(".arrival-time-slot-group2 .square-box.active")) {
            start = document.querySelector(".arrival-time-slot-group2 .square-box.active").dataset.start;
            end = document.querySelector(".arrival-time-slot-group2 .square-box.active").dataset.end;
            flights = document.querySelectorAll("#flights_div2 .each-flight-div-box.show");
        }
        arrival_slot2(flights, start, end);
    }
    //flights = document.querySelectorAll("#flights_div2 .each-flight-div-box.show");
}


function departure_slot(flights, start, end) {
    if (flights) {
        for (let i = 0; i < flights.length; i++) {
            let timeElement;
            
            // Check if it's an Amadeus flight or local flight
            if (flights[i].classList.contains('amadeus-flight')) {
                // For Amadeus flights, try to get time from h5 element
                timeElement = flights[i].querySelector(".flight-origin-time .flight-time h5");
            } else {
                // For local flights, use existing logic
                timeElement = flights[i].querySelector(".flight-origin-time .flight-time h5");
            }
            
            if (timeElement && timeElement.innerText && timeElement.innerText !== '--:--') {
                let time = timeElement.innerText.split(":");
                if (time.length >= 2 && (parseInt(time[0]) >= parseInt(start)) && (parseInt(time[0]) < parseInt(end))) {
                    flights[i].classList.add('show');
                    flights[i].classList.remove('hide');
                }
                else {
                    flights[i].classList.add('hide');
                    flights[i].classList.remove('show');
                }
            }
        }
    }
}

function arrival_slot(flights, start, end) {
    if (flights) {
        for (let i = 0; i < flights.length; i++) {
            let timeElement;
            
            // Check if it's an Amadeus flight or local flight
            if (flights[i].classList.contains('amadeus-flight')) {
                // For Amadeus flights, try to get time from h5 element
                timeElement = flights[i].querySelector(".flight-destination-time .flight-time h5");
            } else {
                // For local flights, use existing logic
                timeElement = flights[i].querySelector(".flight-destination-time .flight-time h5");
            }
            
            if (timeElement && timeElement.innerText && timeElement.innerText !== '--:--') {
                let time = timeElement.innerText.split(":");
                if (time.length >= 2 && (parseInt(time[0]) >= parseInt(start)) && (parseInt(time[0]) < parseInt(end))) {
                    flights[i].classList.add('show');
                    flights[i].classList.remove('hide');
                }
                else {
                    flights[i].classList.add('hide');
                    flights[i].classList.remove('show');
                }
            }
        }
    }
}


function arrival_slot2(flights, start, end) {
    if (flights) {
        for (let i = 0; i < flights.length; i++) {
            time = flights[i].querySelector(".flight-destination-time2 .flight-time h5").innerText.split(":");
            if((parseInt(time[0]) >= parseInt(start)) && (parseInt(time[0]) < parseInt(end))) {
                //flights[i].style.display = 'block';
                flights[i].classList.add('show');
                flights[i].classList.remove('hide');
            }
            else {
                //flights[i].style.display = 'none';
                flights[i].classList.add('hide');
                flights[i].classList.remove('show');
            }
        }
    }
}
function departure_slot2(flights, start, end) {
    if (flights) {
        for (let i = 0; i < flights.length; i++) {
            time = flights[i].querySelector(".flight-origin-time .flight-time h5").innerText.split(":");
            if((parseInt(time[0]) >= parseInt(start)) && (parseInt(time[0]) < parseInt(end))) {
                //flights[i].style.display = 'block';
                flights[i].classList.add('show');
                flights[i].classList.remove('hide');
            }
            else {
                //flights[i].style.display = 'none';
                flights[i].classList.add('hide');
                flights[i].classList.remove('show');
            }
        }
    }
}


function timeslot(slot) {
    inactive(slot);
    active(slot);

    let type = slot.dataset.type;
    let start = slot.dataset.start;
    let end = slot.dataset.end;
    let div = document.querySelector("#flights_div");
    let flights = div.querySelectorAll(".each-flight-div-box");
    if (type === 'departure') {
        for (let i = 0; i < flights.length; i++) {
            time = flights[i].querySelector(".flight-origin-time .flight-time h5").innerText.split(":");
            if((parseInt(time[0]) >= parseInt(start)) && (parseInt(time[0]) < parseInt(end))) {
                flights[i].style.display = 'block';
            }
            else {
                flights[i].style.display = 'none';
            }
        }
    }
    if (type === 'arrival') {
        for (let i = 0; i < flights.length; i++) {
            time = flights[i].querySelector(".flight-destination-time .flight-time h5").innerText.split(":");
            if((parseInt(time[0]) >= parseInt(start)) && (parseInt(time[0]) < parseInt(end))) {
                flights[i].style.display = 'block';
            }
            else {
                flights[i].style.display = 'none';
            }
        }
    }

}

function active(slot) {
    slot.classList.add('active');
    slot.querySelectorAll('img').forEach(image => {
        if(image.dataset.statefor === 'inactive') {
            image.style.display = 'none';
        }
        else {
            image.style.display = 'block';
        }
    });
}
function inactive(slot) {
    if (slot) {
        slot.parentElement.querySelectorAll('.active').forEach(element => {
            element.classList.remove('active');
            element.querySelectorAll('img').forEach(image => {
                if(image.dataset.statefor === 'inactive') {
                    image.style.display = 'block';
                }
                else {
                    image.style.display = 'none';
                }
            })
        });
    }
}


/////////////////////////////
function active2(slot) {
    slot.classList.add('active');
    slot.querySelectorAll('img').forEach(image => {
        if(image.dataset.statefor === 'inactive') {
            image.style.display = 'none';
        }
        else {
            image.style.display = 'block';
        }
    });
}
function inactive2(slot) {
    if (slot) {
        slot.parentElement.querySelectorAll('.active').forEach(element => {
            element.classList.remove('active');
            element.querySelectorAll('img').forEach(image => {
                if(image.dataset.statefor === 'inactive') {
                    image.style.display = 'block';
                }
                else {
                    image.style.display = 'none';
                }
            })
        });
    }
}
/////////////////////////////


function filter_price() {
    let value = document.querySelector(".filter-price input[type=range]").value;
    document.querySelector(".filter-price .final-price-value").innerText = value;

    let div = document.querySelector("#flights_div");
    let flights = div.querySelectorAll(".each-flight-div-box");
    for (let i = 0; i < flights.length; i++) {
        let price = 0;
        
        // Check if it's an Amadeus flight
        if (flights[i].classList.contains('amadeus-flight')) {
            // For Amadeus flights, get price from data attribute
            price = parseFloat(flights[i].dataset.amadeusPrice) || 0;
        } else {
            // For local flights, get price from span
            let priceSpan = flights[i].querySelector(".flight-price span");
            price = priceSpan ? parseFloat(priceSpan.innerText) : 0;
        }
        
        if (price > parseInt(value)) {
            flights[i].classList.add('hide');
            flights[i].classList.remove('show');
        }
        else {
            flights[i].classList.add('show');
            flights[i].classList.remove('hide');
        }
    }
}

function reset_filter() {
    document.querySelectorAll('.time-slot').forEach(slot => {
        inactive(slot.querySelector(".square-box.active"));
    });
    let max = document.querySelector(".filter-price input[type=range]").getAttribute('max');
    document.querySelector(".filter-price input[type=range]").value = max;
    document.querySelector(".filter-price .final-price-value").innerText = max;

    let flights = document.querySelector("#flights_div").querySelectorAll(".each-flight-div-box");
    for (let i = 0; i < flights.length; i++) {
            //flights[i].style.display = 'block';
            flights[i].classList.add('show');
            flights[i].classList.remove('hide');
    }
}







////////////////////////////////
function filter_price2() {
    let value = document.querySelector(".filter-price2 input[type=range]").value;
    document.querySelector(".filter-price2 .final-price-value").innerText = value;

    let div = document.querySelector("#flights_div2");
    let flights = div.querySelectorAll(".each-flight-div-box");
    for (let i = 0; i < flights.length; i++) {
        if (flights[i].querySelector(".flight-price span").innerText > parseInt(value)) {
            //flights[i].style.display = 'none';
            flights[i].classList.add('hide');
            flights[i].classList.remove('show');
        }
        else {
            //flights[i].style.display = 'block';
            flights[i].classList.add('show');
            flights[i].classList.remove('hide');
        }
    }
    
}

function reset_filter2() {
    document.querySelectorAll('.time-slot2').forEach(slot => {
        inactive2(slot.querySelector(".square-box.active"));
    });
    let max = document.querySelector(".filter-price2 input[type=range]").getAttribute('max');
    document.querySelector(".filter-price2 input[type=range]").value = max;
    document.querySelector(".filter-price2 .final-price-value").innerText = max;

    let flights = document.querySelector("#flights_div2").querySelectorAll(".each-flight-div-box");
    for (let i = 0; i < flights.length; i++) {
            //flights[i].style.display = 'block';
            flights[i].classList.add('show');
            flights[i].classList.remove('hide');
    }
}

////////////////////////////////





function trip_type_flight(element) {
    if(element.dataset.trip_type === '1') {
        document.querySelector(".query-result-div-2").style.display = 'none';
        document.querySelector(".query-result-div").style.display = 'block';
        //element.classList.add('active-div');
        //document.querySelector('#flight2-btn-div').classList.remove('active-div');
    }
    else if(element.dataset.trip_type === '2') {
        document.querySelector(".query-result-div").style.display = 'none';
        document.querySelector(".query-result-div-2").style.display = 'block';
        //element.classList.add('active-div');
        //document.querySelector('#flight1-btn-div').classList.remove('active-div');
    }
}



function flight_select() {
    document.querySelectorAll(".flight1-radio").forEach(radio => {
        radio.addEventListener('click', e => {
            document.querySelectorAll('#flt1').forEach(flt1 => {
                flt1.value = e.target.value;
            });
            document.querySelector("#select-f1-plane").innerText = e.target.dataset.plane;
            document.querySelector("#select-f1-depart").innerText = e.target.dataset.depart;
            document.querySelector("#select-f1-arrive").innerText = e.target.dataset.arrive;
            document.querySelector("#select-f1-fare").innerText = e.target.dataset.fare;
            document.querySelector("#select-total-fare").innerText = parseInt(e.target.dataset.fare) + parseInt(document.querySelector("#select-f2-fare").innerText);
            document.querySelector("#select-total-fare-media").innerText = parseInt(e.target.dataset.fare) + parseInt(document.querySelector("#select-f2-fare").innerText);
        });
    });
    document.querySelectorAll(".flight2-radio").forEach(radio => {
        radio.addEventListener('click', e => {
            document.querySelectorAll('#flt2').forEach(flt2 => {
                flt2.value = e.target.value;
            })
            document.querySelector("#select-f2-plane").innerText = e.target.dataset.plane;
            document.querySelector("#select-f2-depart").innerText = e.target.dataset.depart;
            document.querySelector("#select-f2-arrive").innerText = e.target.dataset.arrive;
            document.querySelector("#select-f2-fare").innerText = e.target.dataset.fare;
            document.querySelector("#select-total-fare").innerText = parseInt(e.target.dataset.fare) + parseInt(document.querySelector("#select-f1-fare").innerText);
            document.querySelector("#select-total-fare-media").innerText = parseInt(e.target.dataset.fare) + parseInt(document.querySelector("#select-f1-fare").innerText);
        });
    });
}


//a.dispatchEvent(new Event('click', { 'bubbles': true }));


function media_click(element) {
    if (window.matchMedia("(max-width: 376px)").matches) {
        if (document.querySelector('#trip-identifier').value === '1') {
            element.querySelector('.o-b').click();
        }
        else {
            element.querySelector('.r-b').click();
            element.parentElement.parentElement.querySelectorAll('.blue').forEach(flt => {
                flt.classList.remove('blue');
            });
            element.classList.add('blue');
        }
    }
    else {
        return;
    }
}

function initial_click() {
    if (window.matchMedia("(max-width: 376px)").matches) {
        if (document.querySelector('#trip-identifier').value === '2'){
            document.querySelector(".query-result-div .each-flight-div").classList.add('blue');
            document.querySelector(".query-result-div-2 .each-flight-div").classList.add('blue');
        }
    }
}


function close_filter(element) {
    const filterDiv = element.parentElement.parentElement;
    
    // Check if we're on mobile (screen width <= 768px)
    if (window.innerWidth <= 768) {
        filterDiv.classList.remove('show');
        // Remove overlay if it exists
        const overlay = document.querySelector('.mobile-filter-overlay');
        if (overlay) {
            overlay.classList.remove('show');
            setTimeout(() => overlay.remove(), 300);
        }
    } else {
        filterDiv.style.display = 'none';
    }
}

function show_filter() {
    // Check if we're on mobile (screen width <= 768px)
    if (window.innerWidth <= 768) {
        // Create overlay for mobile
        const overlay = document.createElement('div');
        overlay.className = 'mobile-filter-overlay';
        overlay.onclick = () => {
            const filterDiv = document.querySelector('.filter-div.show');
            if (filterDiv) {
                filterDiv.classList.remove('show');
            }
            overlay.classList.remove('show');
            setTimeout(() => overlay.remove(), 300);
        };
        document.body.appendChild(overlay);
        
        // Show filter and overlay
        setTimeout(() => {
            overlay.classList.add('show');
            const targetFilter = getActiveFilterDiv();
            if (targetFilter) {
                targetFilter.classList.add('show');
            }
        }, 10);
    } else {
        // Desktop behavior
        const targetFilter = getActiveFilterDiv();
        if (targetFilter) {
            targetFilter.style.display = 'block';
        }
    }
}

function getActiveFilterDiv() {
    if(Boolean(document.querySelector(".query-result-div-2"))) {
        let r1 = document.querySelector(".query-result-div");
        let r2 = document.querySelector(".query-result-div-2");
        if(r2.style.display === 'none') {
            return r1.querySelector(".filter-div");
        } else {
            return r2.querySelector(".filter-div");
        }
    } else {
        return document.querySelector(".query-result-div .filter-div");
    }
}














function tab_change() {
    var tabs = $('.tabs');
    var selector = $('.tabs').find('a').length;
    //var selector = $(".tabs").find(".selector");
    var activeItem = tabs.find('.active-div');
    var activeWidth = activeItem.innerWidth();
    $(".selector").css({
    "left": activeItem.position.left + "px", 
    "width": activeWidth + "px"
    });

    $(".tabs").on("click","a",function(e){
    e.preventDefault();
    $('.tabs a').removeClass("active-div");
    $(this).addClass('active-div');
    var activeWidth = $(this).innerWidth();
    var itemPos = $(this).position();
    $(".selector").css({
        "left":itemPos.left + "px", 
        "width": activeWidth + "px"
    });
    setTimeout(() => {trip_type_flight(e.target);},400);
    });
}
