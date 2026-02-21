"""Módulo del modelo Customer para el sistema de reservas."""

from dataclasses import dataclass


@dataclass
class Customer:
    """Representa un cliente que puede hacer reservas."""

    id: str
    name: str
    email: str

    @classmethod
    def from_dict(cls, data: dict) -> 'Customer':
        """Construye un Customer desde un diccionario."""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            email=data.get('email', '')
        )

    def to_dict(self) -> dict:
        """Devuelve el cliente como diccionario."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }
