import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";

patch(PosOrder.prototype, {

    set_booking(booking) {
        if (!booking) {
            this.assert_editable();
            this.update({ booking_id: false });
        }
        this.assert_editable();
        this.update({ booking_id: booking });
    },

    get_booking() {
        return this.booking_id;
    },

});
