/** @odoo-module **/

import { TableBooking } from './booking';
import { mount } from "@odoo/owl";

document.addEventListener('DOMContentLoaded', function() {
    const appElement = document.getElementById('table-booking-app');
    if (appElement) {
        mount(TableBooking, appElement);
    }
});