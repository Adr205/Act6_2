"""Paquete del sistema de hoteles"""

from .hotel import Hotel
from .customer import Customer
from .reservation import Reservation

__all__ = [
    "Hotel",
    "Customer",
    "Reservation",
]
