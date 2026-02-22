"""
Punto de entrada del sistema de hoteles.
Recibe un archivo con las acciones a ejecutar. Los datos solo existen en memoria
durante la ejecución.
El output se muestra en consola y se guarda en output/resultado.txt.
"""

import os
import sys
from datetime import date

from hotel_system import Customer, Hotel, Reservation

OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "resultado.txt")


class _Tee:
    """Escribe en consola y en un archivo a la vez."""

    def __init__(self, stream, path):
        self._stream = stream
        self._path = path
        self._file = None
        self._old_stdout = None

    def __enter__(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        self._file = open(self._path, "w", encoding="utf-8")
        self._old_stdout = sys.stdout
        sys.stdout = self
        return self

    def __exit__(self, *args):
        sys.stdout = self._old_stdout
        if self._file:
            self._file.close()

    def write(self, data):
        self._stream.write(data)
        if self._file:
            self._file.write(data)
            self._file.flush()

    def flush(self):
        self._stream.flush()
        if self._file:
            self._file.flush()


# Formato del archivo de acciones: una acción por línea, campos separados por |
# CREAR_HOTEL|id|nombre|ciudad|total_rooms
# CREAR_CLIENTE|id|nombre|email
# CREAR_RESERVA|id|customer_id|hotel_id|check_in|check_out
# RESERVAR_HABITACION|hotel_id
# CANCELAR_HABITACION|hotel_id
# CANCELAR_RESERVA|reservation_id
# Líneas vacías y las que empiezan con # se ignoran.


def _ejecutar_crear_hotel(partes, state):
    """CREAR_HOTEL|id|nombre|ciudad|total_rooms"""
    if len(partes) != 5:
        print(f"  [Error] CREAR_HOTEL requiere 5 campos: {partes}")
        return
    hid, nombre, ciudad = partes[1].strip(), partes[2].strip(), partes[3].strip()
    try:
        total_rooms = int(partes[4].strip())
    except ValueError:
        print(f"  [Error] total_rooms debe ser número: {partes[4]}")
        return
    hotels = state["hotels"]
    if any(h.get("id") == hid for h in hotels):
        print(f"  [Info] Hotel {hid} ya existe, se omite.")
        return
    hotel = Hotel(
        id=hid, name=nombre, city=ciudad,
        total_rooms=total_rooms, available_rooms=total_rooms,
    )
    hotels.append(hotel.to_dict())
    print(f"  [OK] Hotel creado: {hid} - {nombre} ({ciudad})")


def _ejecutar_crear_cliente(partes, state):
    """CREAR_CLIENTE|id|nombre|email"""
    if len(partes) != 4:
        print(f"  [Error] CREAR_CLIENTE requiere 4 campos: {partes}")
        return
    cid, nombre, email = partes[1].strip(), partes[2].strip(), partes[3].strip()
    customers = state["customers"]
    if any(c.get("id") == cid for c in customers):
        print(f"  [Info] Cliente {cid} ya existe, se omite.")
        return
    customer = Customer(id=cid, name=nombre, email=email)
    customers.append(customer.to_dict())
    print(f"  [OK] Cliente creado: {cid} - {nombre}")


def _ejecutar_crear_reserva(partes, state):
    """CREAR_RESERVA|id|customer_id|hotel_id|check_in|check_out"""
    if len(partes) != 6:
        print(f"  [Error] CREAR_RESERVA requiere 6 campos: {partes}")
        return
    rid, cid, hid = partes[1].strip(), partes[2].strip(), partes[3].strip()
    try:
        check_in = date.fromisoformat(partes[4].strip())
        check_out = date.fromisoformat(partes[5].strip())
    except ValueError as e:
        print(f"  [Error] Fechas inválidas: {e}")
        return
    hotels, customers, reservations = state["hotels"], state["customers"], state["reservations"]
    if not any(c.get("id") == cid for c in customers):
        print(f"  [Error] Cliente {cid} no existe.")
        return
    hotel_dict = next((h for h in hotels if h.get("id") == hid), None)
    if not hotel_dict:
        print(f"  [Error] Hotel {hid} no existe.")
        return
    hotel = Hotel.from_dict(hotel_dict)
    if not hotel.can_reserve():
        print(f"  [Error] No hay habitaciones en {hid}.")
        return
    if any(r.get("id") == rid for r in reservations):
        print(f"  [Error] Reserva {rid} ya existe.")
        return
    res = Reservation(
        id=rid, customer_id=cid, hotel_id=hid,
        check_in=check_in, check_out=check_out, created_at=date.today(),
    )
    reservations.append(res.to_dict())
    hotel.reserve_room()
    for h in hotels:
        if h.get("id") == hid:
            h["available_rooms"] = hotel.available_rooms
            break
    print(f"  [OK] Reserva creada: {rid} ({cid} @ {hid})")


def _ejecutar_reservar_habitacion(partes, state):
    """RESERVAR_HABITACION|hotel_id"""
    if len(partes) != 2:
        print(f"  [Error] RESERVAR_HABITACION requiere hotel_id: {partes}")
        return
    hid = partes[1].strip()
    hotels = state["hotels"]
    for h in hotels:
        if h.get("id") == hid:
            obj = Hotel.from_dict(h)
            if obj.reserve_room():
                h["available_rooms"] = obj.available_rooms
                print(f"  [OK] Habitación reservada en {hid}")
            else:
                print(f"  [Error] No hay habitaciones en {hid}")
            return
    print(f"  [Error] Hotel {hid} no existe.")


def _ejecutar_cancelar_habitacion(partes, state):
    """CANCELAR_HABITACION|hotel_id"""
    if len(partes) != 2:
        print(f"  [Error] CANCELAR_HABITACION requiere hotel_id: {partes}")
        return
    hid = partes[1].strip()
    hotels = state["hotels"]
    for h in hotels:
        if h.get("id") == hid:
            obj = Hotel.from_dict(h)
            obj.cancel_reservation()
            h["available_rooms"] = obj.available_rooms
            print(f"  [OK] Habitación liberada en {hid}")
            return
    print(f"  [Error] Hotel {hid} no existe.")


def _ejecutar_cancelar_reserva(partes, state):
    """CANCELAR_RESERVA|reservation_id"""
    if len(partes) != 2:
        print(f"  [Error] CANCELAR_RESERVA requiere reservation_id: {partes}")
        return
    rid = partes[1].strip()
    reservations = state["reservations"]
    res_data = next((r for r in reservations if r.get("id") == rid), None)
    if not res_data:
        print(f"  [Error] Reserva {rid} no existe.")
        return
    hotel_id = res_data.get("hotel_id")
    state["reservations"] = [r for r in reservations if r.get("id") != rid]
    hotels = state["hotels"]
    for h in hotels:
        if h.get("id") == hotel_id:
            obj = Hotel.from_dict(h)
            obj.cancel_reservation()
            h["available_rooms"] = obj.available_rooms
            break
    print(f"  [OK] Reserva {rid} cancelada.")


def _ejecutar_acciones(ruta_archivo, state):
    """Lee el archivo de acciones y ejecuta cada línea. Todo en memoria."""
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            lineas = f.readlines()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta_archivo}'.")
        return False
    except OSError as e:
        print(f"Error al leer '{ruta_archivo}': {e}")
        return False

    acciones = {
        "CREAR_HOTEL": _ejecutar_crear_hotel,
        "CREAR_CLIENTE": _ejecutar_crear_cliente,
        "CREAR_RESERVA": _ejecutar_crear_reserva,
        "RESERVAR_HABITACION": _ejecutar_reservar_habitacion,
        "CANCELAR_HABITACION": _ejecutar_cancelar_habitacion,
        "CANCELAR_RESERVA": _ejecutar_cancelar_reserva,
    }

    print(f"Ejecutando acciones desde: {ruta_archivo}")
    print("-" * 50)
    for num, linea in enumerate(lineas, 1):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        partes = linea.split("|")
        if not partes:
            continue
        comando = partes[0].strip().upper()
        if comando not in acciones:
            print(f"  Línea {num}: Acción desconocida '{comando}'. Se omite.")
            continue
        try:
            acciones[comando](partes, state)
        except Exception as e:
            print(f"  Línea {num}: Error al ejecutar {comando}: {e}. Se continúa.")
    print("-" * 50)
    return True


def _resumen_desde_state(state):
    """Convierte el estado en memoria a listas de objetos para el resumen."""
    hoteles = [Hotel.from_dict(d) for d in state["hotels"]]
    clientes = [Customer.from_dict(d) for d in state["customers"]]
    reservas = []
    for d in state["reservations"]:
        try:
            r = Reservation(
                id=d.get("id", ""),
                customer_id=d.get("customer_id", ""),
                hotel_id=d.get("hotel_id", ""),
                check_in=date.fromisoformat(d["check_in"]),
                check_out=date.fromisoformat(d["check_out"]),
                created_at=date.fromisoformat(d["created_at"]),
            )
            reservas.append(r)
        except (KeyError, ValueError, TypeError):
            continue
    return hoteles, clientes, reservas


def _imprimir_resumen(hoteles, clientes, reservas):
    sep = "=" * 60
    print()
    print(sep)
    print("  RESUMEN AL FINALIZAR - SISTEMA DE HOTELES")
    print(sep)
    print()
    print("--- HOTELES ---")
    if not hoteles:
        print("  (ninguno)")
    else:
        for h in hoteles:
            print(f"  • {h}")
    print()
    print("--- CLIENTES ---")
    if not clientes:
        print("  (ninguno)")
    else:
        for c in clientes:
            print(f"  • {c.id}: {c.name} <{c.email}>")
    print()
    print("--- RESERVAS ---")
    if not reservas:
        print("  (ninguna)")
    else:
        for r in reservas:
            print(f"  • {r}")
    print()
    print(sep)
    print(f"  Total: {len(hoteles)} hotel(es) | {len(clientes)} cliente(s) | {len(reservas)} reserva(s)")
    print(sep)
    print()


def run(ruta_archivo_acciones):
    """
    Estado vacío al inicio. Ejecuta las acciones del archivo solo en memoria
    y muestra el resumen. No se guarda nada en disco entre ejecuciones.
    """
    state = {"hotels": [], "customers": [], "reservations": []}
    if not _ejecutar_acciones(ruta_archivo_acciones, state):
        return
    hoteles, clientes, reservas = _resumen_desde_state(state)
    _imprimir_resumen(hoteles, clientes, reservas)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 main.py <archivo_acciones.txt>")
        print("Ejemplo: python3 main.py acciones_prueba_1.txt")
        sys.exit(1)
    with _Tee(sys.stdout, OUTPUT_FILE):
        run(sys.argv[1])
        print(f"Output guardado en: {OUTPUT_FILE}")
