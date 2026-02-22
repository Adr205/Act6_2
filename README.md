# Sistema de Hoteles

## Hotels (`hotel_system/hotel.py`)

- **Flake8:**
  ```bash
  python3 -m flake8 hotel_system/hotel.py --max-line-length=88
  ```
- **Pylint:**
  ```bash
  python3 -m pylint hotel_system/hotel.py
  ```

## Customer (`hotel_system/customer.py`)

- **Flake8:**
  ```bash
  python3 -m flake8 hotel_system/customer.py --max-line-length=88
  ```
- **Pylint:**
  ```bash
  python3 -m pylint hotel_system/customer.py
  ```

## Reservation (`hotel_system/reservation.py`)

- **Flake8:**
  ```bash
  python3 -m flake8 hotel_system/reservation.py --max-line-length=88
  ```
- **Pylint:**
  ```bash
  python3 -m pylint hotel_system/reservation.py
  ```

## Main (`main.py`)

- **Flake8:**
  ```bash
  flake8 main.py --max-line-length=88 --statistics
  ```
- **Pylint:**
  ```bash
  pylint main.py
  ```

## Tests

- **Ejecutar tests:**
  ```bash
  python3 -m unittest tests.test_hotel_system -v
  ```

## Instalar herramientas

```bash
pip install flake8 pylint
# o
pip3 install flake8 pylint
```