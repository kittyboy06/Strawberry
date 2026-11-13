"""Visual identity and styling rules for Strawberry Pro."""

PRO_THEME_CSS = """
Screen {
    background: #090d16;
    color: #f1f5f9;
}

#header-container {
    height: 4;
    background: #0f172a;
    border-bottom: heavy #e11d48;
    padding: 0 1;
}

#header-title {
    text-style: bold;
    color: #f43f5e;
    width: 25;
}

#header-tagline {
    color: #94a3b8;
    text-style: italic;
    width: 35;
}

#timer-badge {
    color: #fb7185;
    text-style: bold;
    background: #1e293b;
    border: round #f43f5e;
    padding: 0 1;
    width: 14;
    text-align: center;
}

#year-bar {
    height: 3;
    background: #0f172a;
    border-bottom: solid #1e293b;
    padding: 0 1;
    align: center middle;
}

.year-btn {
    margin: 0 1;
    min-width: 14;
    background: #1e293b;
    color: #94a3b8;
    border: none;
}

.year-btn.-active {
    background: #e11d48;
    color: #ffffff;
    text-style: bold;
}

#main-content {
    height: 1fr;
    layout: horizontal;
}

#subjects-pane {
    width: 32;
    background: #090d16;
    border-right: solid #1e293b;
    padding: 1;
}

#experiments-pane {
    width: 38;
    background: #0b0f19;
    border-right: solid #1e293b;
    padding: 1;
}

#details-pane {
    width: 1fr;
    background: #090d16;
    padding: 1;
}

.pane-title {
    color: #f43f5e;
    text-style: bold;
    margin-bottom: 1;
}

#search-input {
    margin-bottom: 1;
    background: #1e293b;
    border: tall #334155;
    color: #ffffff;
}

#search-input:focus {
    border: tall #f43f5e;
}

ListView {
    background: transparent;
    border: none;
    height: 1fr;
}

ListItem {
    padding: 0 1;
    height: auto;
    background: #0f172a;
    margin-bottom: 1;
    border: solid #1e293b;
}

ListItem:hover {
    background: #1e293b;
    border: solid #e11d48;
}

ListItem.-selected {
    background: #e11d48;
    color: #ffffff;
    text-style: bold;
}

#code-viewer {
    height: 1fr;
    background: #020617;
    border: solid #1e293b;
    padding: 1;
    overflow-y: auto;
}

#metadata-box {
    height: auto;
    background: #0f172a;
    border: solid #1e293b;
    padding: 1;
    margin-bottom: 1;
}

#copy-btn {
    width: 100%;
    background: #e11d48;
    color: #ffffff;
    text-style: bold;
    margin-top: 1;
}

#copy-btn:hover {
    background: #f43f5e;
}

#footer-bar {
    height: 1;
    background: #0f172a;
    color: #64748b;
    text-align: center;
}
"""
