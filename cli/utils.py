from typing import Optional


def read_choice(prompt: str, min_value: int, max_value: int) -> int:
    """Read a numeric menu choice and validate the range."""
    while True:
        raw_value = input(prompt).strip()
        if raw_value.isdigit():
            choice = int(raw_value)
            if min_value <= choice <= max_value:
                return choice

        print(f"Invalid selection. Please enter a number between {min_value} and {max_value}.")


def read_non_empty_text(prompt: str) -> str:
    """Read a non-empty string from the user."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Value cannot be empty. Please enter valid text.")


def read_optional_text(prompt: str) -> Optional[str]:
    """Read optional text from the user. Blank input returns None."""
    value = input(prompt).strip()
    return value if value else None


def read_positive_int(prompt: str, allow_empty: bool = False) -> Optional[int]:
    """Read a positive integer from the user, optionally allowing blank input."""
    while True:
        raw_value = input(prompt).strip()
        if allow_empty and raw_value == "":
            return None

        if raw_value.isdigit():
            value = int(raw_value)
            if value > 0:
                return value

        print("Please enter a positive number.")


def read_int_range(prompt: str, min_value: int, max_value: int, allow_empty: bool = False) -> Optional[int]:
    """Read an integer value in a defined range, optionally allowing blank input."""
    while True:
        raw_value = input(prompt).strip()
        if allow_empty and raw_value == "":
            return None

        if raw_value.isdigit():
            value = int(raw_value)
            if min_value <= value <= max_value:
                return value

        print(f"Please enter a number between {min_value} and {max_value}.")


def confirm_action(prompt: str = "Confirm action? (Y/N): ") -> bool:
    """Ask the user to confirm a destructive action."""
    while True:
        response = input(prompt).strip().lower()
        if response in {"y", "yes"}:
            return True
        if response in {"n", "no"}:
            return False
        print("Please enter Y or N.")


def wait_for_enter(message: str = "Press ENTER to continue...") -> None:
    input(message)
