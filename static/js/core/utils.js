// Utility functions used across the application
const Utils = {
    /**
     * Debounce function calls
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Show loading state for an element
     */
    showLoading(elementId, message = 'Loading...') {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `<div class="loading-spinner">${message}</div>`;
        }
    },

    /**
     * Hide loading state
     */
    hideLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            const spinner = element.querySelector('.loading-spinner');
            if (spinner) {
                spinner.remove();
            }
        }
    },

    /**
     * Safe JSON parse
     */
    safeJsonParse(jsonString, defaultValue = null) {
        try {
            return JSON.parse(jsonString);
        } catch (e) {
            console.warn('Failed to parse JSON:', e);
            return defaultValue;
        }
    },

    /**
     * Format numbers for display
     */
    formatNumber(num, decimals = 1) {
        if (typeof num !== 'number') return num;
        return num.toFixed(decimals);
    },

    /**
     * Get team color based on team type
     */
    getTeamColor(teamType) {
        const colors = {
            home: '#2196f3',
            away: '#f44336',
            home_team: '#2196f3',
            away_team: '#f44336'
        };
        return colors[teamType] || '#90caf9';
    },

    /**
     * Check if element is visible
     */
    isElementVisible(element) {
        if (!element) return false;
        return element.offsetWidth > 0 && element.offsetHeight > 0 && element.offsetParent !== null;
    },

    /**
     * Wait for element to be visible
     */
    waitForElement(selector, timeout = 5000) {
        return new Promise((resolve, reject) => {
            const element = document.querySelector(selector);
            if (element && this.isElementVisible(element)) {
                resolve(element);
                return;
            }

            const observer = new MutationObserver(() => {
                const element = document.querySelector(selector);
                if (element && this.isElementVisible(element)) {
                    observer.disconnect();
                    resolve(element);
                }
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ['class', 'style']
            });

            setTimeout(() => {
                observer.disconnect();
                reject(new Error(`Element ${selector} not found within ${timeout}ms`));
            }, timeout);
        });
    },

    /**
     * Log with timestamp and context
     */
    log(message, context = '', type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const prefix = context ? `[${context}]` : '';
        const fullMessage = `${timestamp} ${prefix} ${message}`;
        
        switch (type) {
            case 'error':
                console.error(fullMessage);
                break;
            case 'warn':
                console.warn(fullMessage);
                break;
            default:
                console.log(fullMessage);
        }
    },

    /**
     * Deep clone object
     */
    deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => this.deepClone(item));
        if (typeof obj === 'object') {
            const clonedObj = {};
            for (const key in obj) {
                if (obj.hasOwnProperty(key)) {
                    clonedObj[key] = this.deepClone(obj[key]);
                }
            }
            return clonedObj;
        }
    },

    /**
     * Throttle function calls
     */
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

window.Utils = Utils;
