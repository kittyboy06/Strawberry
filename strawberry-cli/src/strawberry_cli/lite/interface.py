"""Strawberry Lite terminal screens and view formatters."""

import sys
from strawberry_cli.models import Year, Subject, Experiment


class LiteView:
    """Renders formatted screens and banners for the Strawberry Lite experience."""

    @staticmethod
    def print_welcome(years: list[Year]) -> None:
        """Step 1: Welcome Screen."""
        sys.stdout.write("\n\033[91m🍓 Welcome to Strawberry!\033[0m\n")
        sys.stdout.write("Your laboratory programs, one command away.\n\n")
        sys.stdout.write("Enter Your Yr:\n\n")
        for idx, yr in enumerate(years, 1):
            sys.stdout.write(f"{idx}. {yr.display_name}\n")
        sys.stdout.flush()

    @staticmethod
    def print_subjects(year_name: str, subjects: list[Subject]) -> None:
        """Step 2: Subject Selection Screen."""
        sys.stdout.write("\n\033[91m🍓 STRAWBERRY\033[0m\n\n")
        sys.stdout.write(f"Available Subjects — \033[1m{year_name}\033[0m\n\n")
        for idx, sub in enumerate(subjects, 1):
            sem_info = f" ({sub.semester_label})" if sub.semester_label else ""
            sys.stdout.write(f"{idx}. {sub.subject_name}{sem_info}\n")
        sys.stdout.flush()

    @staticmethod
    def print_experiments(subject_name: str, experiments: list[Experiment]) -> None:
        """Step 3: Laboratory Program Selection Screen."""
        sys.stdout.write(f"\n\033[91m🍓 {subject_name.upper()}\033[0m\n\n")
        sys.stdout.write("Available Laboratory Programs:\n\n")
        for exp in experiments:
            sys.stdout.write(f"{exp.formatted_index}. {exp.title}\n")
        sys.stdout.flush()

    @staticmethod
    def print_success(program_title: str, file_path: str, copied_to_clipboard: bool) -> None:
        """Step 4: Successful Retrieval and Completion Screen."""
        sys.stdout.write("\n\033[91m🍓 STRAWBERRY\033[0m\n\n")
        sys.stdout.write(f"Program: \033[1m{program_title}\033[0m\n\n")
        sys.stdout.write("\033[92m[✓] Program retrieved\033[0m\n")
        sys.stdout.write("\033[92m[✓] Integrity verified (SHA-256)\033[0m\n")

        if copied_to_clipboard:
            sys.stdout.write("\033[92m[✓] Copied to clipboard!\033[0m\n\n")
            sys.stdout.write("Your program is ready.\n\n")
            sys.stdout.write("\033[1mPress CTRL + V to paste anywhere.\033[0m\n\n")
        else:
            sys.stdout.write("\033[93m[!] Clipboard access was unavailable.\033[0m\n\n")
            sys.stdout.write(f"Source file saved at:\n{file_path}\n\n")

        sys.stdout.write("Closing Strawberry...\n")
        sys.stdout.flush()
