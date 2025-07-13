// Backward compatibility layer for dropdowns.js
// This file maintains the original functionality while delegating to the new DropdownService

console.warn('Using compatibility layer for dropdowns.js - consider updating to use the new DropdownService');

// Wait for the app and dropdown service to be ready
function waitForDropdownService(callback) {
    if (window.app && window.app.services && window.app.services.dropdownService) {
        callback(window.app.services.dropdownService);
    } else {
        setTimeout(() => waitForDropdownService(callback), 100);
    }
}

// Legacy jQuery document ready handler for backward compatibility
$(document).ready(() => {
    console.log("Document is ready (compatibility layer).");
    
    // Wait for the new dropdown service to be ready
    waitForDropdownService((dropdownService) => {
        console.log("✅ Dropdown service is ready (compatibility layer)");
        
        // The new service handles all the initialization automatically
        // This compatibility layer just ensures existing code doesn't break
        
        // Legacy global functions for backward compatibility
        window.loadCompetitions = () => {
            return dropdownService.loadCompetitions();
        };
        
        window.loadSeasons = (competitionName) => {
            return dropdownService.loadSeasons(competitionName);
        };
        
        window.loadMatches = (seasonId) => {
            return dropdownService.loadMatches(seasonId);
        };
        
        window.getSelectedValues = () => {
            return dropdownService.getSelectedValues();
        };
        
        window.clearAllSelections = () => {
            return dropdownService.clearAllSelections();
        };
        
        window.refreshDropdowns = () => {
            return dropdownService.refresh();
        };
    });
});

// Export legacy functions for backward compatibility
window.waitForDropdownService = waitForDropdownService;
