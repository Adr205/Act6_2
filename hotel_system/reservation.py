"""Módulo del modelo Reservation para el sistema de reservas."""
from dataclasses import dataclass
from datetime import date


@dataclass
class Reservation:
    """Representa una reserva de un hotel."""

    id: str
    customer_id: str
    hotel_id: str
    check_in: date
    check_out: date
    created_at: date

    @classmethod
    def from_dict(cls, data: dict) -> 'Reservation':
        """Construye una Reservation desde un diccionario."""
        return cls(
            id=data.get('id', ''),
            customer_id=data.get('customer_id', ''),
            hotel_id=data.get('hotel_id', ''),
            check_in=date.fromisoformat(data['check_in']),
            check_out=date.fromisoformat(data['check_out']),
            created_at=date.fromisoformat(data['created_at'])
        )

    def to_dict(self) -> dict:
        """Devuelve la reserva como diccionario."""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'hotel_id': self.hotel_id,
            'check_in': self.check_in.isoformat(),
            'check_out': self.check_out.isoformat(),
            'created_at': self.created_at.isoformat()
        }

    def __str__(self) -> str:
        """Representación en texto de la reserva."""
        return f"Reserva {self.id} - {self.customer_id} @ \
        {self.hotel_id} ({self.check_in} → {self.check_out})"
