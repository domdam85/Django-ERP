// Route Assignment JavaScript

class RouteManager {
    constructor() {
        this.pendingChanges = new Set();
        this.initializeDragAndDrop();
        this.initializeEventListeners();
    }

    initializeDragAndDrop() {
        // Initialize Drag and Drop functionality
        const draggableItems = document.querySelectorAll('.draggable-item');
        const dropTargets = document.querySelectorAll('.drop-target');

        draggableItems.forEach(item => {
            item.addEventListener('dragstart', this.handleDragStart.bind(this));
            item.addEventListener('dragend', this.handleDragEnd.bind(this));
        });

        dropTargets.forEach(container => {
            container.addEventListener('dragover', this.handleDragOver.bind(this));
            container.addEventListener('dragleave', this.handleDragLeave.bind(this));
            container.addEventListener('drop', this.handleDrop.bind(this));
        });
    }

    initializeEventListeners() {
        // Initialize event listeners for buttons and selects
        document.querySelectorAll('.sales-rep-select, .driver-select').forEach(select => {
            select.addEventListener('change', this.handleAssigneeChange.bind(this));
        });

        document.getElementById('saveChanges').addEventListener('click', this.handleSaveChanges.bind(this));
        document.getElementById('optimizeRoutes').addEventListener('click', this.handleOptimizeRoutes.bind(this));
        document.getElementById('balanceLoads').addEventListener('click', this.handleBalanceLoads.bind(this));
    }

    handleDragStart(e) {
        const draggedItem = e.target;

        e.dataTransfer.setData('text/plain', JSON.stringify({
            type: draggedItem.closest('#unassignedCustomers') ? 'customer' : 'stop',
            id: draggedItem.dataset.customerId || draggedItem.dataset.stopId,
            sourceRouteId: draggedItem.closest('.drop-target')?.dataset.routeId
        }));
        
        // Create a clone for visual feedback
        const dragClone = draggedItem.cloneNode(true);
        dragClone.classList.add('drag-clone');
        draggedItem.parentNode.insertBefore(dragClone, draggedItem);
        
        // Set a timeout to remove the original item after a short delay
        setTimeout(() => {
            draggedItem.style.display = 'none'; // Hide original item
        }, 0);


        this.draggedItem = draggedItem; // Store dragged item
        this.classList.add('dragging');
    }

    handleDragEnd(e) {
        this.classList.remove('dragging');
        if (this.draggedItem) {
            this.draggedItem.style.display = ''; // Show original item
            const dragClone = document.querySelector('.drag-clone');
            if (dragClone) {
                dragClone.remove(); // Remove the clone
            }
            this.draggedItem = null; // Clear dragged item
        }
    }

    handleDragOver(e) {
        e.preventDefault();
        this.classList.add('drag-over');
        this.classList.remove('drag-leave'); // Ensure drag-leave class is removed

        // Get the drop position and insert a placeholder
        const dropPosition = this.getDropPosition(e);
        this.insertPlaceholder(dropPosition);
    }

    handleDragLeave(e) {
        this.classList.remove('drag-over');
        this.classList.add('drag-leave'); // Add drag-leave class for animation
        this.clearPlaceholder();
    }

    handleDrop(e) {
        e.preventDefault();
        this.classList.remove('drag-over');
        this.classList.remove('drag-leave'); // Ensure drag-leave class is removed
        this.clearPlaceholder();

        const data = JSON.parse(e.dataTransfer.getData('text/plain'));
        const targetRouteId = this.dataset.routeId;

        if (data.type === 'customer') {
            this.addCustomerToRoute(data.id, targetRouteId);
        } else if (data.type === 'stop') {
            if (data.sourceRouteId === targetRouteId) {
                this.reorderStop(data.id, targetRouteId, this.getDropPosition(e));
            } else {
                this.moveStopBetweenRoutes(data.id, data.sourceRouteId, targetRouteId);
            }
        }
    }

    getDropPosition(e) {
        // Get the drop position relative to the container
        const container = e.currentTarget;
        const mouseY = e.clientY;
        const items = Array.from(container.querySelectorAll('.draggable-item:not(.dragging)'));

        let closest = null;
        let closestOffset = Number.NEGATIVE_INFINITY;

        items.forEach(item => {
            const box = item.getBoundingClientRect();
            const offset = mouseY - box.top - box.height / 2;
            if (offset > closestOffset) {
                closestOffset = offset;
                closest = item;
            }
        });

        return closest ? items.indexOf(closest) : items.length;
    }

    insertPlaceholder(position) {
        this.clearPlaceholder(); // Clear existing placeholder

        const placeholder = document.createElement('div');
        placeholder.className = 'draggable-item placeholder';
        placeholder.innerHTML = '&nbsp;'; // Add some content to make it visible

        if (position >= this.items.length) {
            this.container.appendChild(placeholder);
        } else {
            this.container.insertBefore(placeholder, this.items[position]);
        }
        this.placeholder = placeholder;
    }

    clearPlaceholder() {
        if (this.placeholder) {
            this.placeholder.remove();
            this.placeholder = null;
        }
    }


    addCustomerToRoute(customerId, routeId) {
        // Add customer to route
        this.pendingChanges.add({
            action: 'add_customer',
            customerId: customerId,
            routeId: routeId
        });
        console.log('Adding customer', customerId, 'to route', routeId);
    }

    reorderStop(stopId, routeId, position) {
        // Reorder stop within the same route
        this.pendingChanges.add({
            action: 'reorder_stop',
            stopId: stopId,
            routeId: routeId,
            position: position
        });
        console.log('Reordering stop', stopId, 'in route', routeId, 'to position', position);
    }

    moveStopBetweenRoutes(stopId, sourceRouteId, targetRouteId) {
        // Move stop between routes
        this.pendingChanges.add({
            action: 'move_stop',
            stopId: stopId,
            sourceRouteId: sourceRouteId,
            targetRouteId: targetRouteId
        });
        console.log('Moving stop', stopId, 'from route', sourceRouteId, 'to route', targetRouteId);
    }

    handleAssigneeChange(e) {
        // Handle changes to sales rep or driver assignments
        const routeId = e.currentTarget.dataset.routeId;
        const assigneeType = e.currentTarget.classList.contains('sales-rep-select') ? 'sales_rep' : 'driver';
        const assigneeId = e.currentTarget.value;

        this.pendingChanges.add({
            action: 'update_assignee',
            routeId: routeId,
            assigneeType: assigneeType,
            assigneeId: assigneeId
        });
        console.log('Updating', assigneeType, 'for route', routeId, 'to', assigneeId);
    }

    handleSaveChanges() {
        // Save all pending changes
        this.saveRouteChanges();
    }

    handleOptimizeRoutes() {
        // Optimize routes
        this.optimizeRoutes();
    }

    handleBalanceLoads() {
        // Balance route loads
        this.balanceRouteLoads();
    }

    async saveRouteChanges() {
        // Send pending changes to the server
        const saveButton = document.getElementById('saveChanges');
        saveButton.classList.add('btn-loading');

        try {
            const response = await fetch('/management/save_route_changes/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({ changes: Array.from(this.pendingChanges) })
            });

            if (response.ok) {
                console.log('Route changes saved successfully');
                this.pendingChanges.clear();
                location.reload();
            } else {
                console.error('Failed to save route changes');
            }
        } catch (error) {
            console.error('Error saving route changes:', error);
        } finally {
            saveButton.classList.remove('btn-loading');
        }
    }

    async optimizeRoutes() {
        // Send request to optimize routes
        const optimizeButton = document.getElementById('optimizeRoutes');
        optimizeButton.classList.add('btn-loading');

        try {
            const response = await fetch('/management/optimize_routes/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });

            if (response.ok) {
                const data = await response.json();
                console.log('Routes optimized successfully', data);
                
                // Reorder stops in UI based on optimized data
                if (data.optimized_routes) {
                    this.applyOptimizedRoutes(data.optimized_routes);
                }

            } else {
                console.error('Failed to optimize routes');
            }
        } catch (error) {
            console.error('Error optimizing routes:', error);
        } finally {
            optimizeButton.classList.remove('btn-loading');
        }
    }

    applyOptimizedRoutes(optimizedRoutes) {
        // Apply optimized route data to the UI
        for (const routeId in optimizedRoutes) {
            const optimizedStops = optimizedRoutes[routeId];
            const routeContainer = document.querySelector(`.drop-container[data-route-id="${routeId}"]`);
            if (routeContainer) {
                // Create a document fragment to minimize DOM updates
                const fragment = document.createDocumentFragment();
                optimizedStops.forEach(stopData => {
                    const stopElement = routeContainer.querySelector(`.draggable-item[data-stop-id="${stopData.stop_id}"]`);
                    if (stopElement) {
                        fragment.appendChild(stopElement);
                    }
                });
                // Append the fragment to the route container
                routeContainer.appendChild(fragment);

                // Renumber the stop numbers in the UI
                this.renumberStops(routeContainer);
            }
        }
    }

    renumberStops(routeContainer) {
        const stopElements = routeContainer.querySelectorAll('.draggable-item');
        stopElements.forEach((stopElement, index) => {
            const stopNumberSpan = stopElement.querySelector('.stop-number');
            if (stopNumberSpan) {
                stopNumberSpan.textContent = `${index + 1}.`;
            }
        });
    }

    async balanceRouteLoads() {
        // Send request to balance route loads
        const balanceButton = document.getElementById('balanceLoads');
        balanceButton.classList.add('btn-loading');

        try {
            const response = await fetch('/management/balance_loads/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });

            if (response.ok) {
                const data = await response.json();
                console.log('Route loads balanced successfully', data);
                if (data.balanced_routes) {
                    this.applyBalancedRoutes(data.balanced_routes);
                }
            } else {
                console.error('Failed to balance route loads');
            }
        } catch (error) {
            console.error('Error balancing route loads:', error);
        } finally {
            balanceButton.classList.remove('btn-loading');
        }
    }

    applyBalancedRoutes(balancedRoutes) {
        // Apply balanced route data to the UI
        for (const routeId in balancedRoutes) {
            const balancedStops = balancedRoutes[routeId];
            const routeContainer = document.querySelector(`.drop-container[data-route-id="${routeId}"]`);
            if (routeContainer) {
                // Clear existing stops
                routeContainer.innerHTML = '';
                // Create a document fragment to minimize DOM updates
                const fragment = document.createDocumentFragment();
                balancedStops.forEach(stopData => {
                    const stopElement = this.createStopElement(stopData);
                    fragment.appendChild(stopElement);
                });
                // Append the fragment to the route container
                routeContainer.appendChild(fragment);

                // Renumber the stop numbers in the UI
                this.renumberStops(routeContainer);
            }
        }
    }

    createStopElement(stopData) {
        const stopElement = document.createElement('div');
        stopElement.className = 'draggable-item';
        stopElement.draggable = true;
        stopElement.dataset.stopId = stopData.stop_id;
        stopElement.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <i class="fas fa-grip-lines me-2"></i>
                    <span class="stop-number">${stopData.sequence}.</span>
                    ${stopData.customer_name}
                </div>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-outline-danger remove-stop">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
        // Re-attach event listeners to the newly created stop element
        stopElement.addEventListener('dragstart', this.handleDragStart.bind(this));
        stopElement.addEventListener('dragend', this.handleDragEnd.bind(this));
        return stopElement;
    }

    getCookie(name) {
        // Helper function to get CSRF token
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    new RouteManager();
});
