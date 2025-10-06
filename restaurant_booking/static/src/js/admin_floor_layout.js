/** @odoo-module **/
import { Component, useState, onWillStart } from '@odoo/owl';
import { rpc } from '@web/core/network/rpc';
import { registry } from '@web/core/registry';

export class AdminFloorLayout extends Component {
    static template = 'restaurant_booking.AdminFloorLayout';

    setup() {
        this.state = useState({ floors: [], activeFloor: null, tables: [], bookings: [], selectedTable: null, selectedBooking: null, loading: false });
        onWillStart(() => this.loadFloors());
    }

    async loadFloors() {
        this.state.loading = true;
        try {
            const data = await rpc('/admin/booking/floors', { method: 'GET' });
            this.state.floors = data.floors || [];
            if (this.state.floors.length) {
                this.selectFloor(this.state.floors[0].id);
            }
        } finally { this.state.loading = false; }
    }

    async selectFloor(evOrId) {
        const floorId = typeof evOrId === 'object' ? parseInt(evOrId.target.value) : evOrId;
        this.state.activeFloor = floorId;
        this.state.selectedTable = null;
        this.state.selectedBooking = null;
        await this.loadTables(floorId);
    }

    async loadTables(floorId) {
        this.state.loading = true;
        try {
            const data = await rpc(`/admin/booking/tables/${floorId}`);
            this.state.tables = data.tables || [];
            this.state.bookings = data.bookings || [];
        } finally { this.state.loading = false; }
    }

    tableStyle(table) {
        const left = (table.position_h || 10) + 'px';
        const top = (table.position_v || 10) + 'px';
        const width = (table.width || 50) + 'px';
        const height = (table.height || 50) + 'px';
        const radius = table.shape === 'round' ? '50%' : '6px';
        return `position:absolute; left:${left}; top:${top}; width:${width}; height:${height}; border-radius:${radius}; display:flex; align-items:center; justify-content:center`;
    }

    onClickTable(ev, table) {
        ev.preventDefault();
        this.state.selectedTable = table.id;
    }

    bookingsForTable(tableId) {
        return this.state.bookings.filter(b => b.table_id && b.table_id[0] === tableId) || [];
    }

    pendingBookingsForFloor() {
        return this.state.bookings.filter(b => b.state === 'pending');
    }

    async assignSelectedBooking() {
        if (!this.state.selectedBooking || !this.state.selectedTable) {
            this.env.services.notification.add("Please select booking & table!", { type: "warning" });
            return;
        }
        this.state.loading = true;
        try {
            const res = await rpc('/admin/booking/assign_table', {
                booking_id: this.state.selectedBooking,
                table_id: this.state.selectedTable,
            });
            if (res.success) {
                await this.loadTables(this.state.activeFloor);
                this.state.selectedBooking = null;
                this.state.selectedTable = null;
                this.env.services.notification.add('Assign success !', { type: "success" });
            } else {
                // handle error
                this.env.services.notification.add(res.error || 'Assign error', { type: "danger" });
            }
        } finally { this.state.loading = false; }
    }

    onHoverBooking(ev, booking) {
        this.hoverTimeout = setTimeout(() => {
            const rect = ev.target.getBoundingClientRect();
            this.state.hoverBooking = booking;
            this.overlayStyle = `top:${rect.top + 30}px; left:${rect.left + 50}px;`;
            this.render();
        }, 700);
    }
    
    hideOverlay() {
        clearTimeout(this.hoverTimeout);
        this.state.hoverBooking = null;
        this.render();
    }


    async onSelectBooking(booking) {
        this.state.selectedBooking = booking.id;
        this.state.selectedTable = null;    
        this.state.tables = [];
        this.state.loading = true;
        try {
            const data = await rpc(`/admin/booking/available_tables/${this.state.activeFloor}`, { booking_id: booking.id});
            this.state.tables = data.tables || [];
        } finally {
            this.state.loading = false;
        }
    }
    
}

registry.category('public_components').add('restaurant_booking.AdminFloorLayout', AdminFloorLayout);