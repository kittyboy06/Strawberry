"""Strawberry Lite end-to-end guided interactive workflow."""

import sys
from typing import Optional
from strawberry_cli.core.input_handler import TimedInputHandler
from strawberry_cli.repository.base import BaseCatalogRepository
from strawberry_cli.repository.sqlite_repo import SQLiteCatalogRepository
from strawberry_cli.services.cache import cache_service
from strawberry_cli.services.clipboard import clipboard_service
from .interface import LiteView


class LiteWorkflow:
    """Executes the guided 4-step Strawberry Lite student journey."""

    def __init__(
        self,
        repository: Optional[BaseCatalogRepository] = None,
        input_handler: Optional[TimedInputHandler] = None,
    ):
        self.repo = repository or SQLiteCatalogRepository()
        self.input_handler = input_handler or TimedInputHandler()
        self.view = LiteView()

    def run(self) -> None:
        """Executes the complete guided flow."""
        # ─────────────────────────────────────────────────────────────
        # STEP 1: Year Selection
        # ─────────────────────────────────────────────────────────────
        years = self.repo.get_years()
        if not years:
            sys.stdout.write("\n\033[91mNo academic years found in the catalog.\033[0m\n")
            sys.exit(1)

        self.view.print_welcome(years)
        valid_year_indices = {str(i) for i in range(1, len(years) + 1)}

        year_choice = self.input_handler.get_input(
            prompt="Select: ",
            validator=lambda val: val in valid_year_indices,
            error_message=f"Invalid selection! Please select a number between 1 and {len(years)}.",
        )
        selected_year = years[int(year_choice) - 1]

        # ─────────────────────────────────────────────────────────────
        # STEP 2: Subject Selection
        # ─────────────────────────────────────────────────────────────
        subjects = self.repo.get_subjects_by_year(selected_year.year_number)
        if not subjects:
            sys.stdout.write(
                f"\n\033[93mNo subjects currently registered for {selected_year.display_name}.\033[0m\n"
            )
            sys.exit(0)

        self.view.print_subjects(selected_year.display_name, subjects)
        valid_subject_indices = {str(i) for i in range(1, len(subjects) + 1)}

        subject_choice = self.input_handler.get_input(
            prompt="Select Subject: ",
            validator=lambda val: val in valid_subject_indices,
            error_message=f"Invalid selection! Please enter 1 to {len(subjects)}.",
        )
        selected_subject = subjects[int(subject_choice) - 1]

        # ─────────────────────────────────────────────────────────────
        # STEP 3: Program Selection
        # ─────────────────────────────────────────────────────────────
        experiments = self.repo.get_experiments_by_subject(selected_subject.id)
        if not experiments:
            sys.stdout.write(
                f"\n\033[93mNo laboratory experiments found for {selected_subject.subject_name}.\033[0m\n"
            )
            sys.exit(0)

        self.view.print_experiments(selected_subject.subject_name, experiments)

        # Allow user to enter '1', '01', etc.
        valid_indexes = {exp.experiment_number for exp in experiments}

        def validate_experiment_input(val: str) -> bool:
            try:
                num = int(val)
                return num in valid_indexes
            except ValueError:
                return False

        exp_choice = self.input_handler.get_input(
            prompt="Enter Program Index: ",
            validator=validate_experiment_input,
            error_message="Invalid selection! Please enter a valid program index from the list.",
        )
        selected_index = int(exp_choice)
        selected_exp = next(e for e in experiments if e.experiment_number == selected_index)

        # ─────────────────────────────────────────────────────────────
        # STEP 4: Program Retrieval & Clipboard Copying
        # ─────────────────────────────────────────────────────────────
        version = self.repo.get_latest_version(selected_exp.id)
        if not version:
            sys.stdout.write(
                f"\n\033[91mError: No program file published for {selected_exp.title}.\033[0m\n"
            )
            sys.exit(1)

        filename = version.filename
        cached_file = cache_service.get_file_path(filename)

        if not cache_service.is_cached(filename):
            sys.stdout.write(
                f"\n\033[91mError: Program file '{filename}' is not in local cache.\033[0m\n"
                "Please connect to the internet to allow background synchronization.\n"
            )
            sys.exit(1)

        # Verify integrity using SHA-256
        if not cache_service.verify_integrity(filename, version.sha256):
            sys.stdout.write(
                f"\n\033[91mIntegrity verification failed for {filename} (SHA-256 mismatch)!\033[0m\n"
            )
            sys.exit(1)

        # Read source code and copy to clipboard
        source_code = cache_service.read_source_code(filename)
        copied = clipboard_service.copy_to_clipboard(source_code)

        # Print success screen
        self.view.print_success(
            program_title=selected_exp.title,
            file_path=str(cached_file),
            copied_to_clipboard=copied,
        )


def start_lite() -> None:
    """Entrypoint function to run Strawberry Lite."""
    workflow = LiteWorkflow()
    workflow.run()
