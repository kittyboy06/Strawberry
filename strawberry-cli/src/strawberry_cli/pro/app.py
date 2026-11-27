"""Strawberry Pro interactive Textual Terminal User Interface."""

import sys
from typing import Literal, Optional
from rich.syntax import Syntax
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Button,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
)

from strawberry_cli.models import Experiment, Subject, Year
from strawberry_cli.repository.base import BaseCatalogRepository
from strawberry_cli.repository.sqlite_repo import SQLiteCatalogRepository
from strawberry_cli.services.cache import CacheService, cache_service
from strawberry_cli.services.clipboard import clipboard_service
from strawberry_cli.services.pro_state import ProStateService, pro_state_service
from .theme import PRO_THEME_CSS


class CatalogListItem(ListItem):
    """ListItem carrying the catalog domain ID without risking DOM ID collisions."""

    def __init__(self, label_text: str, item_kind: str, item_id: str):
        super().__init__(Label(label_text))
        self.item_kind = item_kind
        self.item_id = item_id


class StrawberryProApp(App):
    """Interactive Strawberry Pro terminal user interface."""

    CSS = PRO_THEME_CSS
    TITLE = "Strawberry Pro"
    SUB_TITLE = "Pick your program. Paste your code."

    BINDINGS = [
        ("q", "quit_app", "Quit"),
        ("c", "copy_code", "Copy Code"),
        ("b", "toggle_bookmark", "Bookmark"),
        ("a", "mode_all", "All"),
        ("f", "mode_bookmarks", "Bookmarks"),
        ("r", "mode_recent", "Recent"),
        ("1", "select_year_2", "2nd Year"),
        ("2", "select_year_3", "3rd Year"),
        ("3", "select_year_4", "4th Year"),
        ("/", "focus_search", "Search"),
    ]

    def __init__(
        self,
        repository: Optional[BaseCatalogRepository] = None,
        state_service: Optional[ProStateService] = None,
        cache: Optional[CacheService] = None,
    ):
        super().__init__()
        self.repo = repository or SQLiteCatalogRepository()
        self.pro_state = state_service or pro_state_service
        self.cache = cache or cache_service
        self.years: list[Year] = []
        self.selected_year_number: int = 2
        self.view_mode: Literal["all", "bookmarks", "recent"] = "all"
        self.search_query: str = ""
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
            yield Button("All", id="btn-mode-all", classes="mode-btn -active")
            yield Button("★ Bookmarks", id="btn-mode-bookmarks", classes="mode-btn")
            yield Button("🕒 Recent", id="btn-mode-recent", classes="mode-btn")

        with Horizontal(id="main-content"):
            # Left pane: Subjects
            with Vertical(id="subjects-pane"):
                yield Label("SUBJECTS", classes="pane-title")
                yield Input(placeholder="Search subjects or programs...", id="search-input")
                yield ListView(id="subjects-list")

            # Middle pane: Experiments
            with Vertical(id="experiments-pane"):
                yield Label("LAB PROGRAMS", id="experiments-pane-title", classes="pane-title")
                yield ListView(id="experiments-list")

            # Right pane: Details & Source Code
            with Vertical(id="details-pane"):
                yield Label("PROGRAM DETAILS & CODE", classes="pane-title")
                yield Static(id="metadata-box")
                yield Static(id="code-viewer")
                with Horizontal(id="action-row"):
                    yield Button("📋 Copy Code (CTRL + V to Paste)", id="copy-btn")
                    yield Button("☆ Bookmark [B]", id="bookmark-btn")

        yield Label(
            "[↑/↓] Browse | [C] Copy | [B] Bookmark | [A/F/R] All/Fav/Recent | [/] Search | [1-3] Year | [Q] Quit | [ALT] Kill",
            id="footer-bar",
        )

    def on_mount(self) -> None:
        """Called once the app is mounted and ready."""
        self.years = self.repo.get_years()
        self.refresh_view()
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

    def _update_bar_styles(self) -> None:
        for yr in (2, 3, 4):
            btn = self.query_one(f"#btn-year-{yr}", Button)
            if self.view_mode == "all" and yr == self.selected_year_number:
                btn.add_class("-active")
            else:
                btn.remove_class("-active")

        mode_map = {
            "all": "#btn-mode-all",
            "bookmarks": "#btn-mode-bookmarks",
            "recent": "#btn-mode-recent",
        }
        for mode_name, selector in mode_map.items():
            btn = self.query_one(selector, Button)
            if mode_name == self.view_mode:
                btn.add_class("-active")
            else:
                btn.remove_class("-active")

    def _get_all_catalog_experiments(self) -> list[tuple[Subject, Experiment]]:
        """Collects all (Subject, Experiment) pairs across all years."""
        items: list[tuple[Subject, Experiment]] = []
        for yr in self.repo.get_years():
            for sub in self.repo.get_subjects_by_year(yr.year_number):
                for exp in self.repo.get_experiments_by_subject(sub.id):
                    items.append((sub, exp))
        return items

    def _find_subject_for_experiment(self, experiment_id: str) -> Optional[Subject]:
        for sub, exp in self._get_all_catalog_experiments():
            if exp.id == experiment_id:
                return sub
        return None

    def refresh_view(self) -> None:
        """Rebuilds the subject & experiment lists according to active view mode and search."""
        self._update_bar_styles()
        if self.view_mode == "all":
            self.query_one("#experiments-pane-title", Label).update("LAB PROGRAMS")
            self.load_subjects(self.selected_year_number, self.search_query)
            return

        subjects_list = self.query_one("#subjects-list", ListView)
        subjects_list.clear()
        self.subjects = []
        self.selected_subject = None

        q = self.search_query.strip().lower()
        catalog_pairs = self._get_all_catalog_experiments()
        exp_by_id = {exp.id: (sub, exp) for sub, exp in catalog_pairs}

        filtered_exps: list[Experiment] = []
        if self.view_mode == "bookmarks":
            self.query_one("#experiments-pane-title", Label).update("★ BOOKMARKED PROGRAMS")
            bookmark_ids = set(self.pro_state.get_bookmarks())
            for sub, exp in catalog_pairs:
                if exp.id in bookmark_ids and (
                    not q
                    or q in exp.title.lower()
                    or q in sub.subject_code.lower()
                    or q in sub.subject_name.lower()
                ):
                    filtered_exps.append(exp)
        else:
            self.query_one("#experiments-pane-title", Label).update("🕒 RECENTLY COPIED")
            for entry in self.pro_state.get_history():
                pair = exp_by_id.get(entry.get("experiment_id", ""))
                if not pair:
                    continue
                sub, exp = pair
                if (
                    not q
                    or q in exp.title.lower()
                    or q in sub.subject_code.lower()
                    or q in sub.subject_name.lower()
                ):
                    filtered_exps.append(exp)

        self._render_experiments_list(filtered_exps)

    def load_subjects(self, year_number: int, query: str = "") -> None:
        """Loads and filters subjects for the chosen academic year."""
        self.selected_year_number = year_number
        self.search_query = query
        all_subjects = self.repo.get_subjects_by_year(year_number)

        q = query.strip().lower()
        if q:
            matched_subjects: list[Subject] = []
            for s in all_subjects:
                sub_match = q in s.subject_name.lower() or q in s.subject_code.lower()
                exps = self.repo.get_experiments_by_subject(s.id)
                exp_match = any(q in e.title.lower() for e in exps)
                if sub_match or exp_match:
                    matched_subjects.append(s)
            self.subjects = matched_subjects
        else:
            self.subjects = all_subjects

        self._update_bar_styles()

        subjects_list = self.query_one("#subjects-list", ListView)
        subjects_list.clear()

        for s in self.subjects:
            badge = f"[{s.semester_label}]" if s.semester_label else ""
            item_text = f"{s.subject_code} - {s.subject_name} {badge}"
            subjects_list.append(CatalogListItem(item_text, "sub", s.id))

        if self.subjects:
            self.selected_subject = self.subjects[0]
            self.load_experiments(self.selected_subject.id, q)
        else:
            self.selected_subject = None
            self.experiments = []
            self.query_one("#experiments-list", ListView).clear()
            self.update_code_viewer(None)

    def load_experiments(self, subject_id: str, query: str = "") -> None:
        """Loads experiments for the active subject, narrowing by query if only experiment titles match."""
        exps = self.repo.get_experiments_by_subject(subject_id)
        q = query.strip().lower()
        if q and self.selected_subject:
            sub_match = (
                q in self.selected_subject.subject_name.lower()
                or q in self.selected_subject.subject_code.lower()
            )
            if not sub_match:
                exps = [e for e in exps if q in e.title.lower()]
        self._render_experiments_list(exps)

    def _render_experiments_list(self, exps: list[Experiment]) -> None:
        self.experiments = exps
        exp_list = self.query_one("#experiments-list", ListView)
        exp_list.clear()

        bookmarks = set(self.pro_state.get_bookmarks())
        for exp in self.experiments:
            star = "★ " if exp.id in bookmarks else ""
            item_text = f"{star}{exp.formatted_index}. {exp.title}"
            exp_list.append(CatalogListItem(item_text, "exp", exp.id))

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
        bookmark_btn = self.query_one("#bookmark-btn", Button)

        if not experiment:
            meta_box.update("No experiment selected.")
            code_box.update("")
            bookmark_btn.label = "☆ Bookmark [B]"
            bookmark_btn.remove_class("-bookmarked")
            return

        is_fav = self.pro_state.is_bookmarked(experiment.id)
        if is_fav:
            bookmark_btn.label = "★ Bookmarked [B]"
            bookmark_btn.add_class("-bookmarked")
        else:
            bookmark_btn.label = "☆ Bookmark [B]"
            bookmark_btn.remove_class("-bookmarked")

        version = self.repo.get_latest_version(experiment.id)
        if not version:
            meta_box.update(f"[bold]{experiment.title}[/bold]\nNo version published.")
            code_box.update("")
            return

        filename = version.filename
        cached = self.cache.is_cached(filename)
        verified = cached and self.cache.verify_integrity(filename, version.sha256)
        if verified:
            status_color = "green"
            status_text = "Verified (SHA-256)"
        elif cached:
            status_color = "red"
            status_text = "Checksum Mismatch!"
        else:
            status_color = "red"
            status_text = "Not Cached (Sync Needed)"

        fav_badge = " [yellow]★ Bookmarked[/yellow]" if is_fav else ""
        meta_content = (
            f"[bold cyan]{experiment.formatted_index}. {experiment.title}[/bold cyan]{fav_badge}\n"
            f"[dim]{experiment.description}[/dim]\n"
            f"File: [yellow]{filename}[/yellow] | Status: [{status_color}]{status_text}[/{status_color}]\n"
            f"SHA-256: [dim]{version.sha256[:20]}...[/dim]"
        )
        meta_box.update(meta_content)

        if verified:
            source = self.cache.read_source_code(filename)
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "text"
            lexer_map = {
                "py": "python",
                "java": "java",
                "c": "c",
                "cpp": "cpp",
                "sql": "sql",
                "pl": "prolog",
            }
            lexer = lexer_map.get(ext, "text")
            syntax = Syntax(source, lexer, theme="monokai", line_numbers=True)
            code_box.update(syntax)
        elif cached:
            code_box.update("[bold red]SHA-256 mismatch detected. Re-sync required.[/bold red]")
        else:
            code_box.update("[dim red]File not present in local cache.[/dim red]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        self.reset_inactivity()
        btn_id = event.button.id
        if btn_id == "btn-year-2":
            self.view_mode = "all"
            self.selected_year_number = 2
            self.refresh_view()
        elif btn_id == "btn-year-3":
            self.view_mode = "all"
            self.selected_year_number = 3
            self.refresh_view()
        elif btn_id == "btn-year-4":
            self.view_mode = "all"
            self.selected_year_number = 4
            self.refresh_view()
        elif btn_id == "btn-mode-all":
            self.view_mode = "all"
            self.refresh_view()
        elif btn_id == "btn-mode-bookmarks":
            self.view_mode = "bookmarks"
            self.refresh_view()
        elif btn_id == "btn-mode-recent":
            self.view_mode = "recent"
            self.refresh_view()
        elif btn_id == "copy-btn":
            self.action_copy_code()
        elif btn_id == "bookmark-btn":
            self.action_toggle_bookmark()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search filtering."""
        self.reset_inactivity()
        if event.input.id == "search-input":
            self.search_query = event.value
            self.refresh_view()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle item selections in Subject or Experiment lists."""
        self.reset_inactivity()
        if not isinstance(event.item, CatalogListItem):
            return

        if event.item.item_kind == "sub":
            self.selected_subject = next(
                (s for s in self.subjects if s.id == event.item.item_id), None
            )
            if self.selected_subject:
                self.load_experiments(self.selected_subject.id, self.search_query)

        elif event.item.item_kind == "exp":
            self.selected_experiment = next(
                (e for e in self.experiments if e.id == event.item.item_id), None
            )
            if self.selected_experiment:
                self.update_code_viewer(self.selected_experiment)

    def action_copy_code(self) -> None:
        """Verifies SHA-256 integrity, copies source code to clipboard, and records history."""
        self.reset_inactivity()
        if not self.selected_experiment:
            return

        version = self.repo.get_latest_version(self.selected_experiment.id)
        if not version or not self.cache.is_cached(version.filename):
            self.notify("Error: Program file not available in cache", severity="error")
            return

        if not self.cache.verify_integrity(version.filename, version.sha256):
            self.notify(
                f"Integrity verification failed for {version.filename} (SHA-256 mismatch)!",
                title="Blocked!",
                severity="error",
            )
            return

        source = self.cache.read_source_code(version.filename)
        success = clipboard_service.copy_to_clipboard(source)

        if success:
            sub = self.selected_subject or self._find_subject_for_experiment(
                self.selected_experiment.id
            )
            self.pro_state.record_history(
                experiment_id=self.selected_experiment.id,
                title=self.selected_experiment.title,
                subject_code=sub.subject_code if sub else "LAB",
                filename=version.filename,
            )
            self.notify(
                f"[✓] {self.selected_experiment.title} copied to clipboard!\nPress CTRL+V to paste.",
                title="Copied!",
                severity="information",
            )
        else:
            self.notify("Failed to access system clipboard.", severity="warning")

    def action_toggle_bookmark(self) -> None:
        """Toggles bookmark state for the currently selected experiment."""
        self.reset_inactivity()
        if not self.selected_experiment:
            return

        now_fav = self.pro_state.toggle_bookmark(self.selected_experiment.id)
        if self.view_mode == "bookmarks" and not now_fav:
            self.refresh_view()
        else:
            bookmarks = set(self.pro_state.get_bookmarks())
            exp_list = self.query_one("#experiments-list", ListView)
            for item in exp_list.children:
                if isinstance(item, CatalogListItem) and item.item_id == self.selected_experiment.id:
                    star = "★ " if item.item_id in bookmarks else ""
                    label = item.query_one(Label)
                    label.update(
                        f"{star}{self.selected_experiment.formatted_index}. {self.selected_experiment.title}"
                    )
            self.update_code_viewer(self.selected_experiment)

        msg = "Added to Bookmarks ★" if now_fav else "Removed from Bookmarks"
        self.notify(msg, severity="information")

    def action_mode_all(self) -> None:
        self.reset_inactivity()
        self.view_mode = "all"
        self.refresh_view()

    def action_mode_bookmarks(self) -> None:
        self.reset_inactivity()
        self.view_mode = "bookmarks"
        self.refresh_view()

    def action_mode_recent(self) -> None:
        self.reset_inactivity()
        self.view_mode = "recent"
        self.refresh_view()

    def action_select_year_2(self) -> None:
        self.reset_inactivity()
        self.view_mode = "all"
        self.selected_year_number = 2
        self.refresh_view()

    def action_select_year_3(self) -> None:
        self.reset_inactivity()
        self.view_mode = "all"
        self.selected_year_number = 3
        self.refresh_view()

    def action_select_year_4(self) -> None:
        self.reset_inactivity()
        self.view_mode = "all"
        self.selected_year_number = 4
        self.refresh_view()

    def action_focus_search(self) -> None:
        self.reset_inactivity()
        self.query_one("#search-input", Input).focus()

    def action_quit_app(self) -> None:
        self.exit()


def start_pro() -> None:
    """Entry point to launch the Strawberry Pro TUI."""
    app = StrawberryProApp()
    app.run()
