/** @odoo-module **/

import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

export class TableBooking extends Component {
    static template = "restaurant_booking.TableBookingTemplate";
    
    setup() {
        this.rpc = rpc;
        this.modalRef = useRef("bookingModal");
        this.state = useState({
            floors: [],
            tables: [],
            selectedFloor: null,
            selectedTables: [],
			modalAnimating: false,
            loading: false
        });

        onMounted(this.loadFloors);
    }

    async loadFloors() {
        try {
            const result = await this.rpc("/get_floors", {});
            this.state.floors = result.floors;
            
            if (this.state.floors.length > 0) {
                this.state.selectedFloor = this.state.floors[0].id;
                await this.loadTables(this.state.selectedFloor);
            }
        } catch (error) {
            console.error("Error loading floors:", error);
        }
    }

    async onFloorChange(ev) {
        const floorId = parseInt(ev.target.value);
        this.state.selectedFloor = floorId;
        this.state.selectedTables = [];
        
        if (floorId) {
            await this.loadTables(floorId);
        } else {
            this.state.tables = [];
        }
    }

    async loadTables(floorId) {
        try {
            const result = await this.rpc(`/get_tables/${floorId}`, {});
            this.state.tables = result.tables;
        } catch (error) {
            console.error("Error loading tables:", error);
        }
    }

    onTableClick(tableId) {
        const index = this.state.selectedTables.indexOf(tableId);
        if (index > -1) {
            this.state.selectedTables.splice(index, 1);
        } else {
            this.state.selectedTables.push(tableId);
        }
    }

    isTableSelected(tableId) {
        return this.state.selectedTables.includes(tableId);
    }

    get canProceed() {
        return this.state.selectedTables.length > 0;
    }

	async onNextClick() {
        if (this.canProceed) {
        	this.showModal();
        }
    }

    showModal() {
		const modal = this.modalRef.el;
		if (modal) {
			modal.classList.add('show');
			modal.style.display = 'block';
			document.body.classList.add('modal-open');
		}
		// this.state.showModal = true;
    }

    closeModal() {
        const modal = this.modalRef.el;
        
        if (modal) {
            modal.classList.remove('show');
            
            setTimeout(() => {
                this.state.showModal = false;
                modal.style.display = 'none';
                document.body.classList.remove('modal-open');
            }, 300);
        } else {
            // this.state.showModal = false;
        }
    }

    // Handle backdrop click
    onBackdropClick(ev) {
        if (ev.target.classList.contains('modal')) {
            this.closeModal();
        }
    }

    async onSubmitBooking(ev) {
        ev.preventDefault();
        const formData = new FormData(ev.target);
        
        // Add loading animation
        this.state.loading = true;
        
        // Simulate loading delay for better UX
        await new Promise(resolve => setTimeout(resolve, 500));
        
        try {
            const result = await this.rpc("/create_booking", {
                customer_name: formData.get('customer_name'),
                customer_phone: formData.get('customer_phone'),  
                customer_email: formData.get('customer_email'),
                booking_date: formData.get('booking_date'),
                booking_time: formData.get('booking_time'),
                guest_count: parseInt(formData.get('guest_count')),
                notes: formData.get('notes'),
                table_ids: this.state.selectedTables,
            });
            
            if (result.success) {
                window.location.href = `/booking_success/${result.booking_id}`;
            } else {
            }
        } catch (error) {
            console.error("Booking error:", error);
        } finally {
            this.state.loading = false;
        }
    }

    getSelectedTableNames() {
        return this.state.tables
            .filter(table => this.state.selectedTables.includes(table.id))
            .map(table => `T${table.table_number}`)
            .join(', ');
    }
}

// Register the component
registry.category("public_components").add("restaurant_booking.TableBooking", TableBooking);