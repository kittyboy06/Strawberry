import pytest
from strawberry_cli.pro.app import StrawberryProApp
from strawberry_cli.repository.sqlite_repo import SQLiteCatalogRepository
import tempfile
from pathlib import Path


@pytest.mark.anyio
async def test_strawberry_pro_app_mount():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_pro.db"
        repo = SQLiteCatalogRepository(db_path=db_path)
        app = StrawberryProApp(repository=repo)

        async with app.run_test() as pilot:
            # Check that header, year bar and panes are mounted
            assert app.query_one("#header-title") is not None
            assert app.query_one("#subjects-list") is not None
            assert app.query_one("#experiments-list") is not None
            assert app.query_one("#code-viewer") is not None

            # Check initial state
            assert app.selected_year_number == 2
            assert app.selected_subject is not None
            assert app.selected_experiment is not None

            # Test switching year via button
            await pilot.click("#btn-year-3")
            assert app.selected_year_number == 3

            # Test resetting inactivity
            app.reset_inactivity()
            assert app.inactivity_seconds == 7
