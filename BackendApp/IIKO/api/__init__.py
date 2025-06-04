from BackendApp.IIKO.api.customer import Customer
from BackendApp.IIKO.api.order import Order
from BackendApp.IIKO.api.reserves import Reservation


class Client(Customer, Order, Reservation):
    pass
