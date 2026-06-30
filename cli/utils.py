from typing import Optional, Sequence


def read_choice(prompt: str, min_value: int, max_value: int) -> int:
    """Read a numeric menu choice and validate the range."""
    while True:
        raw_value = input(prompt).strip()
        if raw_value.isdigit():
            choice = int(raw_value)
            if min_value <= choice <= max_value:
                return choice

        print_error(f"Invalid selection. Enter a number between {min_value} and {max_value}.")


def read_non_empty_text(prompt: str) -> str:
    """Read a non-empty string from the user."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print_error("Value cannot be empty. Please enter valid text.")


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

        print_error("Please enter a positive number.")


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

        print_error(f"Please enter a number between {min_value} and {max_value}.")


def confirm_action(prompt: str = "Confirm action? (Y/N): ") -> bool:
    """Ask the user to confirm a destructive action."""
    while True:
        response = input(prompt).strip().lower()
        if response in {"y", "yes"}:
            return True
        if response in {"n", "no"}:
            return False
        print_error("Please enter Y or N.")


def wait_for_enter(message: str = "Press ENTER to continue...") -> None:
    input(message)


def print_banner(title: str) -> None:
    """Print a styled section banner."""
    width = max(len(title) + 8, 50)
    border = "=" * width
    print(f"\n{border}\n{title.center(width)}\n{border}\n")


def print_menu(title: str, options: Sequence[str]) -> None:
    """Print a framed menu with numbered options."""
    content_width = max(len(title), max((len(option) for option in options), default=0))
    border = "+" + "-" * (content_width + 4) + "+"
    print(border)
    print(f"|  {title.center(content_width)}  |")
    print(border)
    for option in options:
        print(f"|  {option.ljust(content_width)}  |")
    print(border)
    print()


def render_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> None:
    """Render a formatted text table."""
    column_widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            column_widths[index] = max(column_widths[index], len(str(value)))

    separator = "+" + "+".join("-" * (width + 2) for width in column_widths) + "+"
    header_row = "|" + "|".join(f" {header.center(width)} " for header, width in zip(headers, column_widths)) + "|"

    print(separator)
    print(header_row)
    print(separator)
    for row in rows:
        row_text = "|" + "|".join(f" {str(value).ljust(width)} " for value, width in zip(row, column_widths)) + "|"
        print(row_text)
    print(separator)
    print()


def print_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> None:
    """Render a formatted text table with spacing and a separator line."""
    print()
    render_table(headers, rows)


def print_success(message: str) -> None:
    """Print a success message with clear formatting."""
    print(f"\n[SUCCESS] {message}\n")


def print_error(message: str) -> None:
    """Print an error message with clear formatting."""
    print(f"\n[ERROR] {message}\n")


def print_info(message: str) -> None:
    """Print an informational message with spacing."""
    print(f"\n{message}\n")
