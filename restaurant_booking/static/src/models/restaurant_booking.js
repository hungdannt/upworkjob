import { registry } from "@web/core/registry";
import { Base } from "@point_of_sale/app/models/related_models";


export class RestaurantBooking extends Base {
    static pythonModel = "restaurant.booking";
}

registry.category("pos_available_models").add(RestaurantBooking.pythonModel, RestaurantBooking);
