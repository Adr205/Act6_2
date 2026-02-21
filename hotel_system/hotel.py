"""Módulo del modelo Hotel para el sistema de reservas."""

from dataclasses import dataclass


@dataclass
class Hotel:
    """Representa un hotel con habitaciones disponibles para reservar."""

    id: str
    name: str
    city: str
    total_rooms: int
    available_rooms: int

    @classmethod
    def from_dict(cls, data: dict) -> 'Hotel':
        """Construye un Hotel desde un diccionario."""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            city=data.get('city', ''),
            total_rooms=data.get('total_rooms', 0),
            available_rooms=data.get('available_rooms', 0)
        )

    def to_dict(self) -> dict:
        """Devuelve el hotel como diccionario."""
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'total_rooms': self.total_rooms,
            'available_rooms': self.available_rooms
        }

    def can_reserve(self) -> bool:
        """Indica si hay habitaciones disponibles para reservar."""
        return self.available_rooms > 0

    def reserve_room(self) -> bool:
        """Reserva una habitación. Devuelve True si había disponibilidad."""
        if self.can_reserve():
            self.available_rooms -= 1
            return True
        return False

    def cancel_reservation(self) -> None:
        """Libera una habitación (cancela una reserva)."""
        if self.available_rooms < self.total_rooms:
            self.available_rooms += 1

    def __str__(self) -> str:
        """Representación en texto del hotel."""
        return f"{self.name} ({self.city}) - Habitaciones: \
        {self.available_rooms}/{self.total_rooms}"
