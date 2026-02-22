import io
import os
import sys
import unittest
from datetime import date, timedelta

from hotel_system import Customer, Hotel, Reservation


class TestHotelSystem(unittest.TestCase):
    """Tests con datos en memoria (sin persistencia en data/)."""

    def test_customer_create_and_load(self):
        c = Customer(
            id="adrian@test.com", name="Adrián López", email="adrian@test.com"
        )
        customers = []
        customers.append(c.to_dict())
        loaded = customers
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["email"], "adrian@test.com")

    def test_hotel_create_modify_reserve_cancel(self):
        h = Hotel(
            id="H001",
            name="Hotel Paraíso",
            city="Monterrey",
            total_rooms=20,
            available_rooms=20,
        )
        hotels = [h.to_dict()]
        hotels[0]["available_rooms"] = 18
        loaded_hotels = [Hotel.from_dict(d) for d in hotels]
        self.assertEqual(loaded_hotels[0].available_rooms, 18)
        self.assertTrue(loaded_hotels[0].reserve_room())
        self.assertEqual(loaded_hotels[0].available_rooms, 17)
        loaded_hotels[0].cancel_reservation()
        self.assertEqual(loaded_hotels[0].available_rooms, 18)

    def test_reservation_flow(self):
        c = Customer("c001@test.com", "Juan Pérez", "c001@test.com")
        h = Hotel("H002", "Hotel Sol", "Cancún", 30, 30)
        tomorrow = date.today() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)
        res = Reservation(
            id="R001",
            customer_id=c.id,
            hotel_id=h.id,
            check_in=tomorrow,
            check_out=day_after,
            created_at=date.today(),
        )
        reservations = [res.to_dict()]
        loaded_res = [
            Reservation.from_dict(d) for d in reservations
        ]
        self.assertEqual(len(loaded_res), 1)
        self.assertEqual(loaded_res[0].hotel_id, "H002")

    def test_invalid_data_handling(self):
        """Datos inválidos (dict incompleto) no deben romper la ejecución."""
        bad = {"id": "x", "customer_id": "y"}  # faltan fechas
        with self.assertRaises((KeyError, ValueError, TypeError)):
            Reservation.from_dict(bad)


class TestPrueba01Altas(unittest.TestCase):
    """Escenario de acciones_prueba_1.txt: solo altas de hoteles y clientes."""

    def test_crear_tres_hoteles_01(self):
        hotels = []
        for hid, name, city, total in [
            ("H001", "Hotel Paraíso", "Monterrey", 15),
            ("H002", "Hotel Sol", "Cancún", 20),
            ("H003", "Hotel Montaña", "San Miguel de Allende", 8),
        ]:
            h = Hotel(
                id=hid, name=name, city=city,
                total_rooms=total, available_rooms=total,
            )
            hotels.append(h.to_dict())
        self.assertEqual(len(hotels), 3)
        self.assertEqual(hotels[0]["id"], "H001")
        self.assertEqual(hotels[0]["name"], "Hotel Paraíso")
        self.assertEqual(hotels[0]["available_rooms"], 15)
        self.assertEqual(hotels[1]["city"], "Cancún")
        self.assertEqual(hotels[2]["total_rooms"], 8)

    def test_crear_tres_clientes_01(self):
        customers = []
        for cid, name, email in [
            ("c001", "Ana García", "ana.garcia@email.com"),
            ("c002", "Luis Pérez", "luis.perez@email.com"),
            ("c003", "María López", "maria.lopez@outlook.com"),
        ]:
            c = Customer(id=cid, name=name, email=email)
            customers.append(c.to_dict())
        self.assertEqual(len(customers), 3)
        self.assertEqual(customers[0]["email"], "ana.garcia@email.com")
        self.assertEqual(customers[1]["name"], "Luis Pérez")
        self.assertEqual(customers[2]["id"], "c003")


class TestPrueba02FlujoReserva(unittest.TestCase):
    """Escenario de acciones_prueba_2.txt: reservas y cancelación."""

    def test_flujo_reserva_y_cancelacion(self):
        state = {"hotels": [], "customers": [], "reservations": []}
        # H004 30 hab, H005 40 hab
        for hid, name, city, total in [
            ("H004", "Hotel Centro", "CDMX", 30),
            ("H005", "Hotel Playa Azul", "Puerto Vallarta", 40),
        ]:
            h = Hotel(id=hid, name=name, city=city, total_rooms=total, available_rooms=total)
            state["hotels"].append(h.to_dict())
        for cid, name, email in [
            ("c004", "Sofía Ramírez", "sofia.r@email.com"),
            ("c005", "Carlos Mendoza", "carlos.m@email.com"),
        ]:
            state["customers"].append(Customer(id=cid, name=name, email=email).to_dict())

        h4 = Hotel.from_dict(state["hotels"][0])
        h5 = Hotel.from_dict(state["hotels"][1])
        self.assertTrue(h4.reserve_room())
        state["hotels"][0]["available_rooms"] = h4.available_rooms
        self.assertTrue(h5.reserve_room())
        self.assertTrue(h5.reserve_room())
        state["hotels"][1]["available_rooms"] = h5.available_rooms

        self.assertEqual(state["hotels"][0]["available_rooms"], 29)
        self.assertEqual(state["hotels"][1]["available_rooms"], 38)

        # Cancelar R001 (una hab en H004)
        h4 = Hotel.from_dict(state["hotels"][0])
        h4.cancel_reservation()
        state["hotels"][0]["available_rooms"] = h4.available_rooms
        self.assertEqual(state["hotels"][0]["available_rooms"], 30)

        # Cancelar una habitación en H005
        h5 = Hotel.from_dict(state["hotels"][1])
        h5.cancel_reservation()
        state["hotels"][1]["available_rooms"] = h5.available_rooms
        self.assertEqual(state["hotels"][1]["available_rooms"], 39)


class TestReservarSinDisponibilidad(unittest.TestCase):
    """Escenario de acciones_prueba_04: sobre-reservar (sin habitaciones)."""

    def test_reserve_room_devuelve_false_cuando_no_hay_habitaciones(self):
        h = Hotel("H013", "Hotel Colonial", "Oaxaca", 12, 12)
        for _ in range(12):
            self.assertTrue(h.reserve_room())
        self.assertFalse(h.reserve_room())
        self.assertEqual(h.available_rooms, 0)

    def test_can_reserve_false_cuando_cero_habitaciones(self):
        h = Hotel("HX", "Hotel X", "City", 5, 0)
        self.assertFalse(h.can_reserve())
        self.assertFalse(h.reserve_room())


class TestCustomerHotelFromDict(unittest.TestCase):
    """from_dict con datos parciales o por defecto."""

    def test_customer_from_dict_parcial(self):
        c = Customer.from_dict({"id": "c007", "email": "a@b.com"})
        self.assertEqual(c.id, "c007")
        self.assertEqual(c.name, "")
        self.assertEqual(c.email, "a@b.com")

    def test_hotel_from_dict_parcial(self):
        h = Hotel.from_dict({"id": "H009", "total_rooms": 10})
        self.assertEqual(h.id, "H009")
        self.assertEqual(h.name, "")
        self.assertEqual(h.available_rooms, 0)
        self.assertEqual(h.total_rooms, 10)


class TestEjecutarArchivoAcciones(unittest.TestCase):
    """Ejecuta main.run() con archivos de tests y valida el resultado."""

    def test_ejecutar_acciones_prueba_01(self):
        from main import run
        ruta = os.path.join(os.path.dirname(__file__), "acciones_prueba_1.txt")
        out = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = out
        try:
            run(ruta)
        finally:
            sys.stdout = old_stdout
        text = out.getvalue()
        self.assertIn("3 hotel", text)
        self.assertIn("3 cliente", text)
        self.assertIn("0 reserva", text)
        self.assertIn("Hotel Paraíso", text)
        self.assertIn("Ana García", text)

    def test_ejecutar_acciones_prueba_02(self):
        from main import run
        ruta = os.path.join(os.path.dirname(__file__), "acciones_prueba_2.txt")
        out = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = out
        try:
            run(ruta)
        finally:
            sys.stdout = old_stdout
        text = out.getvalue()
        self.assertIn("2 hotel", text)
        self.assertIn("2 cliente", text)
        self.assertIn("Reserva creada", text)
        self.assertIn("cancelada", text)


if __name__ == "__main__":
    unittest.main()
