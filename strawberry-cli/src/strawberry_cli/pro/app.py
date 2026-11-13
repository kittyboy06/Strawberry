"""Strawberry Pro interactive Textual Terminal User Interface."""

import sys
from typing import Optional
from rich.syntax import Syntax
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
)

from strawberry_cli.core.config import config
from strawberry_cli.models import Experiment, Subject, Year
from strawberry_cli.repository.base import BaseCatalogRepository
from strawberry_cli.repository.sqlite_repo import SQLiteCatalogRepository
from strawberry_cli.services.cache import cache_service
from strawberry_cli.services.clipboard import clipboard_service
from .theme import PRO_THEME_CSS


class StrawberryProApp(App):
    """Interactive Strawberry Pro terminal user interface."""

    CSS = PRO_THEME_CSS
    TITLE = "Strawberry Pro"
    SUB_TITLE = "Pick your program. Paste your code."

    BINDINGS = [
        ("q", "quit_app", "Quit"),
        ("c", "copy_code", "Copy Code"),
        ("1", "select_year_2", "2nd Year"),
        ("2", "select_year_3", "3rd Year"),
        ("3", "select_year_4", "4th Year"),
        ("/", "focus_search", "Search"),
    ]

    def __init__(self, repository: Optional[BaseCatalogRepository] = None):
        super().__init__()
        self.repo = repository or SQLiteCatalogRepository()
        self.years: list[Year] = []
        self.selected_year_number: int = 2
        self.subjects: list[Subject] = []
        self.selected_subject: Optional[Subject] = None
        self.experiments: list[Experiment] = []
        self.selected_experiment: Optional[Experiment] = None
        self.inactivity_seconds: int = 7
        self._timer_handle = None

    def compose(self) -> ComposeResult:
        """Construct the visual hierarchy."""
        with Horizontal(id="header-container"):
            yield Label("🍓 STRAWBERRY PRO", id="header-title")
            yield Label("Pick your program. Paste your code.", id="header-tagline")
            yield Label("⏱ 7s", id="timer-badge")

        with Horizontal(id="year-bar"):
            yield Button("2nd Year", id="btn-year-2", classes="year-btn -active")
            yield Button("3rd Year", id="btn-year-3", classes="year-btn")
            yield Button("4th Year", id="btn-year-4", classes="year-btn")

        with Horizontal(id="main-content"):
            # Left pane: Subjects
            with Vertical(id="subjects-pane"):
                yield Label("SUBJECTS", classes="pane-title")
                yield Input(placeholder="Search subjects...", id="search-input")
                yield ListView(id="subjects-list")

            # Middle pane: Experiments
            with Vertical(id="experiments-pane"):
                yield Label("LAB PROGRAMS", classes="pane-title")
                yield ListView(id="experiments-list")

            # Right pane: Details & Source Code
            with Vertical(id="details-pane"):
                yield Label("PROGRAM DETAILS & CODE", classes="pane-title")
                yield Static(id="metadata-box")
                yield Static(id="code-viewer")
                yield Button("📋 Copy Code (CTRL + V to Paste)", id="copy-btn")

        yield Label(
            "Navigation: [↑/↓] Browse | [ENTER/C] Copy | [Search: /] | [1-3] Switch Year | [Q] Exit | [ALT] Instant Kill",
            id="footer-bar",
        )

    def on_mount(self) -> None:
        """Called once the app is mounted and ready."""
        self.years = self.repo.get_years()
        self.load_subjects(self.selected_year_number)
        # Start the 7-second interaction timer
        self._timer_handle = self.set_interval(1.0, self._tick_inactivity_timer)

    def on_key(self) -> None:
        """Reset the inactivity countdown on any user keystroke."""
        self.reset_inactivity()

    def reset_inactivity(self) -> None:
        """Reset countdown to 7 seconds and update badge."""
        self.inactivity_seconds = 7
        timer_badge = self.query_one("#timer-badge", Label)
        timer_badge.update("⏱ 7s")

    def _tick_inactivity_timer(self) -> None:
        """Decrements inactivity timer every second; exits on zero."""
        self.inactivity_seconds -= 1
        timer_badge = self.query_one("#timer-badge", Label)

        if self.inactivity_seconds <= 0:
            timer_badge.update("⏱ Expired")
            self.exit()
            sys.stdout.write("\n\033[91mSession expired.\033[0m\nClosing Strawberry Pro...\n")
            sys.exit(0)
        else:
            timer_badge.update(f"⏱ {self.inactivity_seconds}s")

    def load_subjects(self, year_number: int, query: str = "") -> None:
        """Loads and filters subjects for the chosen academic year."""
        self.selected_year_number = year_number
        self.subjects = self.repo.get_subjects_by_year(year_number)

        if query:
            q = query.lower()
            self.subjects = [
                s for s in self.subjects
                if q in s.subject_name.lower() or q in s.subject_code.lower()
            ]

        # Update year buttons active state
        for yr in (2, 3, 4):
            btn = self.query_one(f"#btn-year-{yr}", Button)
            if yr == year_number:
                btn.add_class("-active")
            else:
                btn.remove_class("-active")

        # Populate subjects list
        subjects_list = self.query_one("#subjects-list", ListView)
        subjects_list.clear()

        for s in self.subjects:
            badge = f"[{s.semester_label}]" if s.semester_label else ""
            item_text = f"{s.subject_code} - {s.subject_name} {badge}"
            subjects_list.append(ListItem(Label(item_text), id=f"sub-{s.id}"))

        if self.subjects:
            self.selected_subject = self.subjects[0]
            self.load_experiments(self.selected_subject.id)
        else:
            self.selected_subject = None
            self.query_one("#experiments-list", ListView).clear()
            self.update_code_viewer(None)

    def load_experiments(self, subject_id: str) -> None:
        """Loads all experiments for the active subject."""
        self.experiments = self.repo.get_experiments_by_subject(subject_id)
        exp_list = self.query_one("#experiments-list", ListView)
        exp_list.clear()

        for exp in self.experiments:
            item_text = f"{exp.formatted_index}. {exp.title}"
            exp_list.append(ListItem(Label(item_text), id=f"exp-{exp.id}"))

        if self.experiments:
            self.selected_experiment = self.experiments[0]
            self.update_code_viewer(self.selected_experiment)
        else:
            self.selected_experiment = None
            self.update_code_viewer(None)

    def update_code_viewer(self, experiment: Optional[Experiment]) -> None:
        """Renders experiment metadata and syntax-highlighted code."""
        meta_box = self.query_one("#metadata-box", Static)
        code_box = self.query_one("#code-viewer", Static)

        if not experiment:
            meta_box.update("No experiment selected.")
            code_box.update("")
            return

        version = self.repo.get_latest_version(experiment.id)
        if not version:
            meta_box.update(f"[bold]{experiment.title}[/bold]\nNo version published.")
            code_box.update("")
            return

        filename = version.filename
        cached = cache_service.is_cached(filename)
        status_color = "green" if cached else "red"
        status_text = "Cached Locally" if cached else "Not Cached (Sync Needed)"

        meta_content = (
            f"[bold cyan]{experiment.formatted_index}. {experiment.title}[/bold cyan]\n"
            f"[dim]{experiment.description}[/dim]\n"
            f"File: [yellow]{filename}[/yellow] | Status: [{status_color}]{status_text}[/{status_color}]\n"
            f"SHA-256: [dim]{version.sha256[:20]}...[/dim]"
        )
        meta_box.update(meta_content)

        if cached:
            source = cache_service.read_source_code(filename)
            # Detect lexer language from extension
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "text"
            lexer_map = {"py": "python", "java": "java", "c": "c", "cpp": "cpp", "sql": "sql"}
            lexer = lexer_map.get(ext, "text")
            syntax = Syntax(source, lexer, theme="monokai", line_numbers=True)
            code_box.update(syntax)
        else:
            code_box.update("[dim red]File not present in local cache.[/dim red]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        self.reset_inactivity()
        btn_id = event.button.id
        if btn_id == "btn-year-2":
            self.load_subjects(2)
        elif btn_id == "btn-year-3":
            self.load_subjects(3)
        elif btn_id == "btn-year-4":
            self.load_subjects(4)
        elif btn_id == "copy-btn":
            self.action_copy_code()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search filtering."""
        self.reset_inactivity()
        if event.input.id == "search-input":
            self.load_subjects(self.selected_year_number, event.value)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle item selections in Subject or Experiment lists."""
        self.reset_inactivity()
        item_id = event.item.id or ""

        if item_id.startswith("sub-"):
            sub_id = item_id.replace("sub-", "")
            self.selected_subject = next((s for s in self.subjects if s.id == sub_id), None)
            if self.selected_subject:
                self.load_experiments(self.selected_subject.id)

        elif item_id.startswith("exp-"):
            exp_id = item_id.replace("exp-", "")
            self.selected_experiment = next((e for e in self.experiments if e.id == exp_id), None)
            if self.selected_experiment:
                self.update_code_viewer(self.selected_experiment)

    def action_copy_code(self) -> None:
        """Copies the selected experiment source code to the clipboard."""
        self.reset_inactivity()
        if not self.selected_experiment:
            return

        version = self.repo.get_latest_version(self.selected_experiment.id)
        if not version or not cache_service.is_cached(version.filename):
            self.notify("Error: Program file not available in cache", severity="error")
            return

        source = cache_service.read_source_code(version.filename)
        success = clipboard_service.copy_to_clipboard(source)

        if success:
            self.notify(
                f"[✓] {self.selected_experiment.title} copied to clipboard!\nPress CTRL+V to paste.",
                title="Copied!",
                severity="information",
            )
        else:
            self.notify("Failed to access system clipboard.", severity="warning")

    def action_select_year_2(self) -> None:
        self.reset_inactivity()
        self.load_subjects(2)

    def action_select_year_3(self) -> None:
        self.reset_inactivity()
        self.load_subjects(3)

    def action_select_year_4(self) -> None:
        self.reset_inactivity()
        self.load_subjects(4)

    def action_focus_search(self) -> None:
        self.reset_inactivity()
        self.query_one("#search-input", Input).focus()

    def action_quit_app(self) -> None:
        self.exit()


def start_pro() -> None:
    """Entry point to launch the Strawberry Pro TUI."""
    app = StrawberryProApp()
    app.run()
