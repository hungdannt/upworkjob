/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";

export class TableBooking extends Component {
    static template = "restaurant_booking.TableBookingTemplate";
    
    setup() {
        this.rpc = rpc;
        const today = new Date().toISOString().split("T")[0]; 
        this.state = useState({
            loading: false,
            date: today, 
            timeSlots: []
        });
        this.orm = useService("orm");

        onMounted(this.loadTimeSlots);
    }

    async onDateChange(ev) {
        this.state.date = ev.target.value;
        await this.loadTimeSlots();      
    }

    
    async loadTimeSlots() {
        if (!this.state.date) return;   // không có date thì thôi
        try {
            this.state.loading = true;
            const result = await this.rpc("/restaurant/timeslots", {
                date: this.state.date,
            });
            this.state.timeSlots = result.slots;
        } finally {
            this.state.loading = false;
        }
    }



    async onSubmitBooking(ev) {
        ev.preventDefault();
        const formData = new FormData(ev.target);
        this.state.loading = true;

        try {
            const result = await this.rpc("/create_booking", {
                customer_name: formData.get('customer_name'),
                customer_phone: formData.get('customer_phone'),  
                customer_email: formData.get('customer_email'),
                booking_date: formData.get('booking_date'),
                booking_time: formData.get('booking_time'),
                guest_count: parseInt(formData.get('guest_count')),
                notes: formData.get('notes'),
            });
            
            if (result.success) {
                window.location.href = `/booking_success/${result.booking_id}`;
            }
        } catch (error) {
            console.error("Booking error:", error);
        } finally {
            this.state.loading = false;
        }
    }
}

registry.category("public_components").add("restaurant_booking.TableBooking", TableBooking);
