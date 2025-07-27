/**
 * Amadeus API Integration for Flight Search
 * Provides functions to search flights and airports using Amadeus data
 */

class AmadeusClient {
    constructor() {
        this.baseUrl = '/amadeus';
        this.isLoading = false;
        this.debug = true; // Enable debugging
    }

    /**
     * Log debug information to console
     */
    log(message, data = null) {
        if (this.debug) {
            console.log(`[AMADEUS DEBUG] ${message}`, data || '');
        }
    }

    /**
     * Log error information to console
     */
    logError(message, error = null) {
        console.error(`[AMADEUS ERROR] ${message}`, error || '');
    }

    /**
     * Search flights using Amadeus API
     */
    async searchFlights(searchParams) {
        this.log('=== AMADEUS FLIGHT SEARCH START ===');
        this.log('Input parameters:', searchParams);
        
        this.isLoading = true;
        
        try {
            const params = new URLSearchParams({
                Origin: searchParams.origin,
                Destination: searchParams.destination,
                DepartDate: searchParams.departDate,
                SeatClass: searchParams.seatClass || 'economy',
                Adults: searchParams.adults || 1,
                TripType: searchParams.tripType || '1'
            });
            
            if (searchParams.returnDate && searchParams.tripType === '2') {
                params.append('ReturnDate', searchParams.returnDate);
            }
            
            const requestUrl = `${this.baseUrl}/search?${params}`;
            this.log('Request URL:', requestUrl);
            this.log('Request Parameters:', Object.fromEntries(params));
            
            this.log('Making fetch request...');
            const response = await fetch(requestUrl);
            
            this.log('Response status:', response.status);
            this.log('Response headers:', Object.fromEntries(response.headers.entries()));
            
            if (!response.ok) {
                this.logError(`HTTP Error: ${response.status} ${response.statusText}`);
                const errorText = await response.text();
                this.logError('Error response body:', errorText);
                
                this.isLoading = false;
                return {
                    error: true,
                    message: `HTTP Error: ${response.status} - ${response.statusText}`,
                    flights: []
                };
            }
            
            const data = await response.json();
            this.log('Response data received:', data);
            this.log('Number of flights:', data.flights ? data.flights.length : 0);
            
            this.isLoading = false;
            this.log('=== AMADEUS FLIGHT SEARCH END ===');
            return data;
            
        } catch (error) {
            this.isLoading = false;
            this.logError('Network or parsing error:', error);
            this.logError('Error stack:', error.stack);
            
            return {
                error: true,
                message: `Network error: ${error.message}`,
                flights: []
            };
        }
    }

    /**
     * Get airport suggestions from Amadeus
     */
    async getAirportSuggestions(query) {
        this.log('=== AMADEUS AIRPORT SEARCH START ===');
        this.log('Search query:', query);
        
        if (query.length < 2) {
            this.log('Query too short, returning empty results');
            return [];
        }
        
        try {
            const requestUrl = `${this.baseUrl}/airports/${encodeURIComponent(query)}`;
            this.log('Request URL:', requestUrl);
            
            const response = await fetch(requestUrl);
            this.log('Response status:', response.status);
            
            if (!response.ok) {
                this.logError(`HTTP Error: ${response.status} ${response.statusText}`);
                return [];
            }
            
            const suggestions = await response.json();
            this.log('Airport suggestions received:', suggestions);
            this.log('Number of suggestions:', suggestions.length);
            
            this.log('=== AMADEUS AIRPORT SEARCH END ===');
            return suggestions;
            
        } catch (error) {
            this.logError('Airport search error:', error);
            return [];
        }
    }

    /**
     * Get flight price analysis
     */
    async getPriceAnalysis(origin, destination, departDate) {
        try {
            const params = new URLSearchParams({
                Origin: origin,
                Destination: destination,
                DepartDate: departDate
            });
            
            const response = await fetch(`${this.baseUrl}/price-analysis?${params}`);
            const data = await response.json();
            return data;
            
        } catch (error) {
            console.error('Amadeus price analysis error:', error);
            return { error: true, message: 'Price analysis failed' };
        }
    }

    /**
     * Format Amadeus flight data for display
     */
    formatFlightForDisplay(flight) {
        return {
            id: flight.amadeus_id,
            airline: flight.airline_name,
            flightNumber: flight.flight_number,
            aircraft: flight.aircraft,
            
            // Times
            departTime: this.formatTime(flight.departure_time),
            arrivalTime: this.formatTime(flight.arrival_time),
            duration: this.formatDuration(flight.duration),
            
            // Locations
            origin: {
                code: flight.origin_code,
                terminal: flight.origin_terminal
            },
            destination: {
                code: flight.destination_code,
                terminal: flight.destination_terminal
            },
            
            // Pricing
            price: {
                total: flight.price.total,
                currency: flight.price.currency,
                base: flight.price.base
            },
            
            // Additional info
            stops: flight.stops,
            isDirect: flight.is_direct,
            availableSeats: flight.available_seats,
            bookingClass: flight.booking_class,
            
            // For booking
            offerId: flight.offer_id,
            source: 'amadeus'
        };
    }

    /**
     * Format ISO datetime to time string
     */
    formatTime(isoDateTime) {
        if (!isoDateTime) return '--:--';
        
        try {
            const date = new Date(isoDateTime);
            return date.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            });
        } catch (error) {
            return '--:--';
        }
    }

    /**
     * Format ISO duration to readable format
     */
    formatDuration(isoDuration) {
        if (!isoDuration) return 'N/A';
        
        try {
            // Parse ISO 8601 duration format (PT2H30M)
            const match = isoDuration.match(/PT(?:(\d+)H)?(?:(\d+)M)?/);
            if (!match) return isoDuration;
            
            const hours = parseInt(match[1] || 0);
            const minutes = parseInt(match[2] || 0);
            
            if (hours > 0 && minutes > 0) {
                return `${hours}h ${minutes}m`;
            } else if (hours > 0) {
                return `${hours}h`;
            } else if (minutes > 0) {
                return `${minutes}m`;
            }
            
            return isoDuration;
        } catch (error) {
            return isoDuration;
        }
    }

    /**
     * Compare prices between local and Amadeus results
     */
    compareWithLocalFlights(amadeusFlights, localFlights) {
        const comparison = {
            amadeus: {
                count: amadeusFlights.length,
                minPrice: Math.min(...amadeusFlights.map(f => f.price.total)),
                maxPrice: Math.max(...amadeusFlights.map(f => f.price.total)),
                avgPrice: amadeusFlights.reduce((sum, f) => sum + f.price.total, 0) / amadeusFlights.length
            },
            local: {
                count: localFlights.length,
                // Add local flight price comparison logic here
            }
        };
        
        return comparison;
    }
}

// Global instance
const amadeusClient = new AmadeusClient();

/**
 * Enhanced flight search that combines local and Amadeus results
 */
async function enhancedFlightSearch(searchParams) {
    const showLoading = () => {
        // Show loading indicator
        document.querySelector('#flight-search-loading')?.classList.remove('d-none');
    };
    
    const hideLoading = () => {
        // Hide loading indicator  
        document.querySelector('#flight-search-loading')?.classList.add('d-none');
    };
    
    showLoading();
    
    try {
        // Search both local database and Amadeus in parallel
        const [amadeusResults, localResults] = await Promise.allSettled([
            amadeusClient.searchFlights(searchParams),
            searchLocalFlights(searchParams) // Assume this function exists
        ]);
        
        const results = {
            amadeus: {
                success: amadeusResults.status === 'fulfilled' && !amadeusResults.value.error,
                data: amadeusResults.status === 'fulfilled' ? amadeusResults.value : { flights: [] },
                error: amadeusResults.status === 'rejected' ? amadeusResults.reason : null
            },
            local: {
                success: localResults.status === 'fulfilled',
                data: localResults.status === 'fulfilled' ? localResults.value : { flights: [] },
                error: localResults.status === 'rejected' ? localResults.reason : null
            }
        };
        
        // Display results from both sources
        displayCombinedResults(results, searchParams);
        
    } catch (error) {
        console.error('Enhanced flight search error:', error);
        showErrorMessage('Flight search failed. Please try again.');
    } finally {
        hideLoading();
    }
}

/**
 * Display combined results from both local and Amadeus sources
 */
function displayCombinedResults(results, searchParams) {
    const resultsContainer = document.querySelector('#flight-results');
    if (!resultsContainer) return;
    
    let html = '';
    
    // Add tabs for switching between sources
    html += `
        <div class="flight-source-tabs mb-3">
            <ul class="nav nav-tabs" role="tablist">
                <li class="nav-item">
                    <a class="nav-link active" data-toggle="tab" href="#local-flights" role="tab">
                        Local Database (${results.local.data.flights?.length || 0})
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" data-toggle="tab" href="#amadeus-flights" role="tab">
                        Live Results - Amadeus (${results.amadeus.data.flights?.length || 0})
                    </a>
                </li>
            </ul>
        </div>
    `;
    
    // Tab content
    html += `
        <div class="tab-content">
            <div class="tab-pane active" id="local-flights" role="tabpanel">
                ${renderFlightList(results.local.data.flights || [], 'local')}
            </div>
            <div class="tab-pane" id="amadeus-flights" role="tabpanel">
                ${renderAmadeusFlightList(results.amadeus.data.flights || [])}
            </div>
        </div>
    `;
    
    resultsContainer.innerHTML = html;
    
    // Show comparison if both sources have results
    if (results.amadeus.success && results.local.success) {
        showPriceComparison(results.amadeus.data.flights, results.local.data.flights);
    }
}

/**
 * Render Amadeus flight list
 */
function renderAmadeusFlightList(flights) {
    if (!flights || flights.length === 0) {
        return `
            <div class="no-flights-found text-center py-4">
                <i class="fas fa-plane-slash fa-3x text-muted mb-3"></i>
                <h4>No live flights found</h4>
                <p class="text-muted">Try adjusting your search criteria or check local database results.</p>
            </div>
        `;
    }
    
    return flights.map(flight => {
        const formatted = amadeusClient.formatFlightForDisplay(flight);
        return `
            <div class="flight-result-card amadeus-flight" data-offer-id="${formatted.offerId}">
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-3">
                                <div class="airline-info">
                                    <strong>${formatted.airline}</strong>
                                    <div class="text-muted">${formatted.flightNumber}</div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="flight-route">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <div class="departure">
                                            <div class="time">${formatted.departTime}</div>
                                            <div class="airport">${formatted.origin.code}</div>
                                        </div>
                                        <div class="route-info text-center">
                                            <div class="duration">${formatted.duration}</div>
                                            <div class="stops">
                                                ${formatted.isDirect ? 'Direct' : `${formatted.stops} stop(s)`}
                                            </div>
                                        </div>
                                        <div class="arrival">
                                            <div class="time">${formatted.arrivalTime}</div>
                                            <div class="airport">${formatted.destination.code}</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3 text-right">
                                <div class="price-info">
                                    <div class="price">
                                        ${formatted.price.currency} ${formatted.price.total}
                                    </div>
                                    <div class="text-muted small">
                                        ${formatted.availableSeats} seats left
                                    </div>
                                    <button class="btn btn-primary btn-sm mt-2" 
                                            onclick="selectAmadeusFlight('${formatted.offerId}')">
                                        Select Flight
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Handle Amadeus flight selection
 */
function selectAmadeusFlight(offerId) {
    // Store selected Amadeus offer for booking process
    sessionStorage.setItem('selectedAmadeusOffer', offerId);
    
    // Show booking form or redirect to booking page
    alert(`Selected Amadeus flight offer: ${offerId}\nThis would proceed to booking in the full implementation.`);
    
    // In full implementation, you would:
    // 1. Validate the offer with Amadeus
    // 2. Proceed to passenger details collection
    // 3. Create booking via Amadeus booking API
}

/**
 * Show price comparison between sources
 */
function showPriceComparison(amadeusFlights, localFlights) {
    const comparison = amadeusClient.compareWithLocalFlights(amadeusFlights, localFlights);
    
    // Create comparison widget
    const comparisonHtml = `
        <div class="price-comparison-widget mt-3">
            <div class="card">
                <div class="card-header">
                    <h6 class="mb-0">Price Comparison</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-6">
                            <strong>Live Results (Amadeus)</strong>
                            <div>Min: ${comparison.amadeus.minPrice}</div>
                            <div>Avg: ${comparison.amadeus.avgPrice.toFixed(2)}</div>
                        </div>
                        <div class="col-6">
                            <strong>Local Database</strong>
                            <div>${comparison.local.count} flights</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.querySelector('#flight-results').insertAdjacentHTML('beforeend', comparisonHtml);
}

// Make functions available globally
window.amadeusClient = amadeusClient;
window.enhancedFlightSearch = enhancedFlightSearch;
window.selectAmadeusFlight = selectAmadeusFlight;
