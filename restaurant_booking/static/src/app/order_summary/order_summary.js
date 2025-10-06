/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { OrderSummary } from "@point_of_sale/app/screens/product_screen/order_summary/order_summary";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { BookingList } from "../booking_list/booking_list"; 

patch(OrderSummary.prototype, {
    async bookTable() {
        const currentOrder = this.pos.get_order();
        if (!currentOrder) return;

        const payload = await makeAwaitable(this.dialog, BookingList, {
            booking: currentOrder.get_booking(),
            getPayload: (booking) => currentOrder.set_booking(booking),
        });

        if (payload) {
            currentOrder.set_booking(payload);
            currentOrder.set_partner(payload.partner_id);
            
            currentOrder.setBooked(true);
            this.pos.showScreen("FloorScreen");
            setTimeout(() => {
                this.env.services.orm.write('restaurant.booking', [payload.id], {state: 'occupied'});
            }, 1000);
        }
        else {
            currentOrder.set_booking(false);
        }
    },

    async unbookTable() {
        const order = this.pos.get_order();
        await this.env.services.orm.write('restaurant.booking', [order.booking_id.id], { state: 'done' });
        await this.pos.deleteOrders([order]);
        this.pos.showScreen(this.pos.firstScreen);
    }
});
