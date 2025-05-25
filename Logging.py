import logging
from datetime import datetime
import csv

# === Setup Logging to File and Console ===
logger = logging.getLogger("CalculatorLogger")
logger.setLevel(logging.DEBUG)

# File Handler
file_handler = logging.FileHandler("calculator.log", mode='w')
file_handler.setLevel(logging.DEBUG)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add Handlers to Logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# === Calculator Class ===
class Calculator:
    def __init__(self):
        self.history = []

    def _log_history(self, a, b, op, result):
        entry = f"{a} {op} {b} = {result}"
        self.history.append(entry)

    def add(self, a, b):
        result = a + b
        logger.info(f"Addition: {a} + {b} = {result}")
        self._log_history(a, b, '+', result)
        return result

    def subtract(self, a, b):
        result = a - b
        logger.info(f"Subtraction: {a} - {b} = {result}")
        self._log_history(a, b, '-', result)
        return result

    def multiply(self, a, b):
        result = a * b
        logger.info(f"Multiplication: {a} * {b} = {result}")
        self._log_history(a, b, '*', result)
        return result

    def divide(self, a, b):
        try:
            result = a / b
            logger.info(f"Division: {a} / {b} = {result}")
            self._log_history(a, b, '/', result)
            return result
        except ZeroDivisionError:
            logger.error("Division by zero attempt")
            return "Error: Division by zero"

    def print_history(self):
        logger.debug("Printing operation history")
        for entry in self.history:
            print(entry)

# === Simulated Run ===
def run_calculator():
    calc = Calculator()
    operations = ['add', 'subtract', 'multiply', 'divide']
    inputs = [(10, 5), (7, 0), (3, 4), (12, 6), ('a', 2)]

    for op_name in operations:
        for a, b in inputs:
            try:
                a_val = float(a)
                b_val = float(b)
                method = getattr(calc, op_name)
                result = method(a_val, b_val)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {op_name.capitalize()} of {a_val} and {b_val} = {result}")
            except ValueError:
                logger.warning(f"Invalid input: {a}, {b}")
            except Exception as e:
                logger.critical(f"Unexpected error: {e}")

    print("\n=== Operation History ===")
    calc.print_history()

"""
# === Custom CSV Formatter ===
class CSVFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()
        self.fields = ['timestamp', 'level', 'message']

    def format(self, record):
        timestamp = datetime.fromtimestamp(record.created).isoformat()
        level = record.levelname
        message = record.getMessage()
        return f'{timestamp},{level},"{message}"'

# === Setup CSV Logging ===
csv_logger = logging.getLogger("CSVLogger")
csv_logger.setLevel(logging.DEBUG)

csv_file_handler = logging.FileHandler("logs.csv", mode='w', encoding='utf-8')
csv_file_handler.setLevel(logging.DEBUG)
csv_file_handler.setFormatter(CSVFormatter())

csv_logger.addHandler(csv_file_handler)

"""

if __name__ == "__main__":
    run_calculator()