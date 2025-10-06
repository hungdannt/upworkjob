/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { Component, useState } from "@odoo/owl";
import { Input } from "@point_of_sale/app/generic_components/inputs/input/input";
import { useHotkey } from "@web/core/hotkeys/hotkey_hook";
import { onWillStart } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class BookingList extends Component {
    static components = { Dialog, Input };
    static template = "pos_restaurant.BookingList";
    static props = {
        booking: { optional: true, type: [{ value: null }, Object] },
        getPayload: { type: Function },
        close: { type: Function },
    };

    setup() {
        this.ui = useState(useService("ui"));
        this.notification = useService("notification");
        this.orm = useService("orm");
        this.pos = usePos();

        this.state = useState({
            query: "",
            previousQuery: "",
            currentOffset: 0,
            bookings: []
        });

        useHotkey("enter", () => this.onEnter());
        onWillStart(async () => {
            this.state.bookings = await this.orm.searchRead(
                "restaurant.booking",
                [["state", "=", "confirmed"]], // domain
                ["id", "customer_name", "name", "state", "customer_email", "customer_phone", "booking_date", "create_date", "slot_id", "guest_count", "partner_id"], // fields
                { limit: 100, order: "create_date desc" } // options
            );
        });
    }

    async updateQuery(ev) {
        this.state.query = ev.target.value;
        await this.loadBookings();
    }

    clickBooking(booking) {
        if (!booking) this.props.close();
        else {
            const booking_model =  this.pos.models["restaurant.booking"].get(booking.id);
            this.props.getPayload(booking_model);
            this.props.close();
        }
    }

    async onEnter() {
        if (!this.state.query) return;
        const result = await this.searchBooking();
        if (result.length > 0) {
            this.notification.add(
                _t('%s booking(s) found for "%s".', result.length, this.state.query),
                3000
            );
        } else {
            this.notification.add(_t('No booking found for "%s".', this.state.query));
        }
    }

    async searchBooking() {
        if (this.state.previousQuery !== this.state.query) {
            this.state.currentOffset = 0;
            this.state.bookings = [];
        }
    
        const result = await this.getNewBookings();
    
        if (result.length > 0) {
            if (this.state.previousQuery === this.state.query) {
                this.state.bookings = [...this.state.bookings, ...result];
                this.state.currentOffset += result.length;
            } else {
                this.state.bookings = result;
                this.state.previousQuery = this.state.query;
                this.state.currentOffset = result.length;
            }
        }
    
        return result;
    }

    async getNewBookings() {
        const limit = 30;
        let domain = [];
        if (this.state.query) {
            domain = [
                "&",
                    ["state", "=", "confirmed"],
                    "|",
                        "|",
                            ["customer_email", "ilike", this.state.query + "%"],
                            ["customer_name", "ilike", this.state.query + "%"],
                        ["customer_phone", "ilike", this.state.query + "%"]
            ];
        }
        return await this.orm.searchRead(
            "restaurant.booking",
            domain,
            ["id", "customer_name", "state", "name", "customer_email", "customer_phone", "create_date", "booking_date", "slot_id", "guest_count", "partner_id"],
            { limit, offset: this.state.currentOffset }
        );
    }

    async loadBookings() {
        let domain = [];
        if (this.state.query) {
            domain = [
                "&",
                    ["state", "=", "confirmed"],
                    "|",
                        "|",
                            ["customer_email", "ilike", this.state.query + "%"],
                            ["customer_name", "ilike", this.state.query + "%"],
                        ["customer_phone", "ilike", this.state.query + "%"]
            ];
        }
        this.state.bookings = await this.orm.searchRead(
            "restaurant.booking",
            domain,
            ["id", "customer_name", "state", "name", "customer_email", "customer_phone", "create_date", "booking_date", "slot_id", "guest_count", "partner_id"],
            { limit: 100, order: "create_date desc" }
        );
    }
}
