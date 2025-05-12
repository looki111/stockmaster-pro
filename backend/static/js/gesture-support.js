/**
 * Gesture Support for StockMaster Pro
 * Adds touch gestures for tablet and mobile devices
 */

// Gesture types
const GESTURE_TYPES = {
    SWIPE_LEFT: 'swipe_left',
    SWIPE_RIGHT: 'swipe_right',
    SWIPE_UP: 'swipe_up',
    SWIPE_DOWN: 'swipe_down',
    DOUBLE_TAP: 'double_tap',
    LONG_PRESS: 'long_press',
    PINCH_IN: 'pinch_in',
    PINCH_OUT: 'pinch_out',
    ROTATE: 'rotate'
};

// Gesture settings
const GESTURE_SETTINGS = {
    swipeThreshold: 50,         // Minimum distance for a swipe
    swipeTimeThreshold: 300,    // Maximum time for a swipe (ms)
    doubleTapDelay: 300,        // Maximum delay between taps (ms)
    longPressDelay: 500,        // Minimum time for a long press (ms)
    pinchThreshold: 0.1,        // Scale change required for pinch
    rotateThreshold: 15         // Degrees change required for rotate
};

// Gesture state
let gestureState = {
    touchStartX: 0,
    touchStartY: 0,
    touchEndX: 0,
    touchEndY: 0,
    touchStartTime: 0,
    touchEndTime: 0,
    lastTapTime: 0,
    longPressTimer: null,
    initialPinchDistance: 0,
    initialRotation: 0,
    isMultiTouch: false,
    activeElement: null
};

// Gesture handlers
const gestureHandlers = {
    [GESTURE_TYPES.SWIPE_LEFT]: [],
    [GESTURE_TYPES.SWIPE_RIGHT]: [],
    [GESTURE_TYPES.SWIPE_UP]: [],
    [GESTURE_TYPES.SWIPE_DOWN]: [],
    [GESTURE_TYPES.DOUBLE_TAP]: [],
    [GESTURE_TYPES.LONG_PRESS]: [],
    [GESTURE_TYPES.PINCH_IN]: [],
    [GESTURE_TYPES.PINCH_OUT]: [],
    [GESTURE_TYPES.ROTATE]: []
};

// Initialize gesture support
function initGestureSupport() {
    // Only initialize on touch devices
    if (!('ontouchstart' in window)) {
        console.log('Touch not supported, gesture support disabled');
        return;
    }
    
    console.log('Initializing gesture support');
    
    // Add touch event listeners to document
    document.addEventListener('touchstart', handleTouchStart, false);
    document.addEventListener('touchmove', handleTouchMove, false);
    document.addEventListener('touchend', handleTouchEnd, false);
    
    // Set up default gestures
    setupDefaultGestures();
}

// Handle touch start event
function handleTouchStart(event) {
    // Store the active element
    gestureState.activeElement = event.target;
    
    // Reset gesture state
    gestureState.touchStartX = event.touches[0].clientX;
    gestureState.touchStartY = event.touches[0].clientY;
    gestureState.touchStartTime = Date.now();
    
    // Check for multi-touch
    gestureState.isMultiTouch = event.touches.length > 1;
    
    // Handle multi-touch gestures
    if (gestureState.isMultiTouch && event.touches.length === 2) {
        // Calculate initial pinch distance
        const touch1 = event.touches[0];
        const touch2 = event.touches[1];
        gestureState.initialPinchDistance = getPinchDistance(touch1, touch2);
        
        // Calculate initial rotation
        gestureState.initialRotation = getRotation(touch1, touch2);
    } else {
        // Start long press timer
        gestureState.longPressTimer = setTimeout(() => {
            triggerGesture(GESTURE_TYPES.LONG_PRESS, {
                element: gestureState.activeElement,
                x: gestureState.touchStartX,
                y: gestureState.touchStartY
            });
        }, GESTURE_SETTINGS.longPressDelay);
    }
}

// Handle touch move event
function handleTouchMove(event) {
    // Clear long press timer on movement
    if (gestureState.longPressTimer) {
        clearTimeout(gestureState.longPressTimer);
        gestureState.longPressTimer = null;
    }
    
    // Handle multi-touch gestures
    if (gestureState.isMultiTouch && event.touches.length === 2) {
        const touch1 = event.touches[0];
        const touch2 = event.touches[1];
        
        // Handle pinch gesture
        const currentPinchDistance = getPinchDistance(touch1, touch2);
        const pinchRatio = currentPinchDistance / gestureState.initialPinchDistance;
        
        if (pinchRatio > 1 + GESTURE_SETTINGS.pinchThreshold) {
            triggerGesture(GESTURE_TYPES.PINCH_OUT, {
                element: gestureState.activeElement,
                scale: pinchRatio
            });
            gestureState.initialPinchDistance = currentPinchDistance;
        } else if (pinchRatio < 1 - GESTURE_SETTINGS.pinchThreshold) {
            triggerGesture(GESTURE_TYPES.PINCH_IN, {
                element: gestureState.activeElement,
                scale: pinchRatio
            });
            gestureState.initialPinchDistance = currentPinchDistance;
        }
        
        // Handle rotation gesture
        const currentRotation = getRotation(touch1, touch2);
        const rotationDiff = currentRotation - gestureState.initialRotation;
        
        if (Math.abs(rotationDiff) > GESTURE_SETTINGS.rotateThreshold) {
            triggerGesture(GESTURE_TYPES.ROTATE, {
                element: gestureState.activeElement,
                rotation: rotationDiff
            });
            gestureState.initialRotation = currentRotation;
        }
    }
}

// Handle touch end event
function handleTouchEnd(event) {
    // Clear long press timer
    if (gestureState.longPressTimer) {
        clearTimeout(gestureState.longPressTimer);
        gestureState.longPressTimer = null;
    }
    
    // Update gesture state
    gestureState.touchEndX = event.changedTouches[0].clientX;
    gestureState.touchEndY = event.changedTouches[0].clientY;
    gestureState.touchEndTime = Date.now();
    
    // Calculate touch duration
    const touchDuration = gestureState.touchEndTime - gestureState.touchStartTime;
    
    // Handle single touch gestures
    if (!gestureState.isMultiTouch) {
        // Handle double tap
        const timeSinceLastTap = gestureState.touchEndTime - gestureState.lastTapTime;
        if (timeSinceLastTap < GESTURE_SETTINGS.doubleTapDelay) {
            triggerGesture(GESTURE_TYPES.DOUBLE_TAP, {
                element: gestureState.activeElement,
                x: gestureState.touchEndX,
                y: gestureState.touchEndY
            });
            gestureState.lastTapTime = 0; // Reset to prevent triple tap
        } else {
            gestureState.lastTapTime = gestureState.touchEndTime;
        }
        
        // Handle swipe gestures
        if (touchDuration < GESTURE_SETTINGS.swipeTimeThreshold) {
            const deltaX = gestureState.touchEndX - gestureState.touchStartX;
            const deltaY = gestureState.touchEndY - gestureState.touchStartY;
            
            // Check if the swipe distance is significant
            if (Math.abs(deltaX) > GESTURE_SETTINGS.swipeThreshold || 
                Math.abs(deltaY) > GESTURE_SETTINGS.swipeThreshold) {
                
                // Determine swipe direction
                if (Math.abs(deltaX) > Math.abs(deltaY)) {
                    // Horizontal swipe
                    if (deltaX > 0) {
                        triggerGesture(GESTURE_TYPES.SWIPE_RIGHT, {
                            element: gestureState.activeElement,
                            distance: deltaX
                        });
                    } else {
                        triggerGesture(GESTURE_TYPES.SWIPE_LEFT, {
                            element: gestureState.activeElement,
                            distance: -deltaX
                        });
                    }
                } else {
                    // Vertical swipe
                    if (deltaY > 0) {
                        triggerGesture(GESTURE_TYPES.SWIPE_DOWN, {
                            element: gestureState.activeElement,
                            distance: deltaY
                        });
                    } else {
                        triggerGesture(GESTURE_TYPES.SWIPE_UP, {
                            element: gestureState.activeElement,
                            distance: -deltaY
                        });
                    }
                }
            }
        }
    }
    
    // Reset multi-touch flag
    gestureState.isMultiTouch = false;
}

// Calculate distance between two touch points
function getPinchDistance(touch1, touch2) {
    const deltaX = touch1.clientX - touch2.clientX;
    const deltaY = touch1.clientY - touch2.clientY;
    return Math.sqrt(deltaX * deltaX + deltaY * deltaY);
}

// Calculate rotation angle between two touch points
function getRotation(touch1, touch2) {
    return Math.atan2(
        touch2.clientY - touch1.clientY,
        touch2.clientX - touch1.clientX
    ) * 180 / Math.PI;
}

// Trigger a gesture event
function triggerGesture(gestureType, data) {
    // Call all registered handlers for this gesture type
    gestureHandlers[gestureType].forEach(handler => {
        if (typeof handler === 'function') {
            handler(data);
        }
    });
    
    // Dispatch a custom event
    const event = new CustomEvent('stockmaster-gesture', {
        detail: {
            type: gestureType,
            ...data
        },
        bubbles: true,
        cancelable: true
    });
    
    if (data.element) {
        data.element.dispatchEvent(event);
    } else {
        document.dispatchEvent(event);
    }
}

// Register a gesture handler
function registerGestureHandler(gestureType, handler) {
    if (gestureHandlers[gestureType]) {
        gestureHandlers[gestureType].push(handler);
        return true;
    }
    return false;
}

// Remove a gesture handler
function removeGestureHandler(gestureType, handler) {
    if (gestureHandlers[gestureType]) {
        const index = gestureHandlers[gestureType].indexOf(handler);
        if (index !== -1) {
            gestureHandlers[gestureType].splice(index, 1);
            return true;
        }
    }
    return false;
}

// Set up default gestures
function setupDefaultGestures() {
    // Sidebar toggle on swipe right from left edge
    registerGestureHandler(GESTURE_TYPES.SWIPE_RIGHT, (data) => {
        if (data.element && data.distance > 100 && gestureState.touchStartX < 30) {
            const sidebar = document.querySelector('.sidebar');
            if (sidebar && typeof toggleSidebar === 'function') {
                toggleSidebar();
            }
        }
    });
    
    // Close sidebar on swipe left
    registerGestureHandler(GESTURE_TYPES.SWIPE_LEFT, (data) => {
        if (data.element && data.distance > 100) {
            const sidebar = document.querySelector('.sidebar');
            if (sidebar && sidebar.classList.contains('open') && typeof toggleSidebar === 'function') {
                toggleSidebar();
            }
        }
    });
    
    // Double tap to zoom on images
    registerGestureHandler(GESTURE_TYPES.DOUBLE_TAP, (data) => {
        if (data.element && (data.element.tagName === 'IMG' || data.element.classList.contains('zoomable'))) {
            toggleElementZoom(data.element);
        }
    });
    
    // Swipe down to refresh on top of page
    registerGestureHandler(GESTURE_TYPES.SWIPE_DOWN, (data) => {
        if (window.scrollY < 10 && data.distance > 150) {
            // Show refresh indicator
            showRefreshIndicator();
            
            // Reload page after animation
            setTimeout(() => {
                window.location.reload();
            }, 500);
        }
    });
}

// Toggle zoom on an element
function toggleElementZoom(element) {
    if (element.classList.contains('zoomed')) {
        element.classList.remove('zoomed');
    } else {
        element.classList.add('zoomed');
    }
}

// Show refresh indicator
function showRefreshIndicator() {
    let indicator = document.getElementById('pullToRefreshIndicator');
    
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'pullToRefreshIndicator';
        indicator.className = 'fixed top-0 left-0 right-0 bg-blue-500 text-white text-center py-2 transform -translate-y-full transition-transform z-50';
        indicator.innerHTML = '<i class="ri-refresh-line animate-spin mr-2"></i> Refreshing...';
        document.body.appendChild(indicator);
    }
    
    // Show the indicator
    setTimeout(() => {
        indicator.style.transform = 'translateY(0)';
    }, 10);
    
    // Hide after refresh
    setTimeout(() => {
        indicator.style.transform = 'translateY(-100%)';
    }, 2000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initGestureSupport);

// Export functions to global scope
window.GestureSupport = {
    register: registerGestureHandler,
    remove: removeGestureHandler,
    types: GESTURE_TYPES
};
