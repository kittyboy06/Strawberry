# PROJECT: STRAWBERRY 🍓
## Standalone Windows CLI-Based Laboratory Program Retrieval System

You are an expert Python developer, CLI application architect, terminal UI designer and Windows application packaging engineer.

Your task is to design and develop a complete, functional application named **Strawberry**.

Do not create just a prototype or a collection of disconnected Python scripts. Build a properly structured, maintainable application that can eventually be distributed to students as a standalone Windows executable.

Follow the requirements below carefully.

---

# 1. PROJECT OVERVIEW

Strawberry is a department-specific laboratory program retrieval application.

Its purpose is to help students quickly retrieve laboratory programs without manually searching through folders, WhatsApp messages, GitHub repositories or other sources.

Students launch Strawberry through Windows Command Prompt or PowerShell.

The application guides them through:

1. Selecting their academic year.
2. Selecting their subject.
3. Selecting their required laboratory program.
4. Automatically retrieving the selected program.
5. Automatically copying its source code into the system clipboard.

The student can then paste the code anywhere using CTRL + V.

The application should be extremely lightweight, straightforward and quick to use.

## Product identity

- Product name: Strawberry
- Command name: strawberry
- Executable name: strawberry.exe
- Repository name: strawberry-cli
- Free edition: Strawberry Lite
- Advanced edition: Strawberry Pro
- Tagline: "Pick your program. Paste your code."

Both editions must be freely accessible to everyone.

They are NOT different subscription tiers or access privileges. They are two different interfaces for the same application.

---

# 2. ACADEMIC STRUCTURE

The application is intended exclusively for one department.

There are exactly three academic years:

- 2nd Year
- 3rd Year
- 4th Year

Each academic year contains two semesters.

Academic mapping:

2nd Year:
- Semester 3
- Semester 4

3rd Year:
- Semester 5
- Semester 6

4th Year:
- Semester 7
- Semester 8

The academic hierarchy must be:

Department
  └── Academic Year
        └── Semester
              └── Subject
                    └── Laboratory Programs
                          └── Source Files

IMPORTANT:

The student should select only their academic year during the Lite workflow.

Do not introduce a separate semester selection screen.

After year selection, display all subjects belonging to both semesters of that year.

Each subject should display its semester label so students can distinguish them.

Do not invent real subject names. Use clearly marked demonstration data until the actual department catalog is supplied.

---

# 3. STRAWBERRY LITE — PRIMARY EXPERIENCE

Strawberry Lite is the default application experience.

It is intended for students who are unfamiliar with command-line interfaces.

The interface must be guided, simple and minimal.

The student should not need to remember complicated commands.

When the user opens CMD and types:

strawberry

The application should launch the Lite interface.

## STEP 1: Welcome screen

Display:

🍓 Welcome to Strawberry!

Your laboratory programs, one command away.

Enter Your Yr:

1. 2nd Year
2. 3rd Year
3. 4th Year

Select:

Display a seven-second countdown while waiting for input.

## STEP 2: Subject selection

After a valid year selection, retrieve the subjects associated with that year from the remote repository.

Example:

🍓 STRAWBERRY

Available Subjects — 2nd Year

1. Computer Networks (Semester 3)
2. Database Management Systems (Semester 3)
3. Java Programming (Semester 3)
4. Operating Systems (Semester 4)

Select Subject:

The list must be dynamically generated from the repository.

Do not hardcode the actual subject catalog into the application.

## STEP 3: Program selection

After a valid subject selection, retrieve the experiments belonging to that subject.

Example:

🍓 COMPUTER NETWORKS

Available Laboratory Programs:

01. Socket Programming
02. TCP Client Server
03. UDP Communication
04. Routing Algorithm
05. DNS Resolution

Enter Program Index:

Every experiment must have a unique index within its subject.

Display the program index and descriptive name.

## STEP 4: Program retrieval and clipboard

After the student selects a valid program:

1. Retrieve the selected program from the remote repository.
2. Download its source file.
3. Verify the downloaded file using its SHA-256 checksum.
4. Read the source code using the correct encoding.
5. Copy the complete source code into the Windows system clipboard.
6. Save a local cached copy of the program.
7. Display a successful completion message.

Example:

🍓 STRAWBERRY

Program: Socket Programming

[✓] Program downloaded
[✓] Integrity verified
[✓] Copied to clipboard!

Your program is ready.

Press CTRL + V to paste anywhere.

Closing Strawberry...

After a successful operation, terminate the Strawberry process automatically.

The application must never execute the downloaded source code.

It must only retrieve, verify, cache and copy it.

If clipboard access fails, do not falsely display success. Inform the user and show the location of the downloaded file.

---

# 4. CRITICAL REQUIREMENT: SEVEN-SECOND INPUT TIMER

This is one of the most important requirements.

Every input prompt must have a seven-second countdown.

Implement a reliable timeout-aware input handler.

Rules:

1. Every new input prompt starts a fresh seven-second countdown.
2. If the user enters a valid selection, move to the next screen and restart the timer.
3. If the user enters an invalid selection, display an error and restart the timer at seven seconds.
4. If seven seconds pass without a complete input, terminate the Strawberry application automatically.
5. Do not wait indefinitely for input.
6. The timeout must work even when the user is typing an incomplete response.
7. The timer must be visible in the terminal.
8. The timer should update smoothly without repeatedly printing new lines.
9. Clear or update the previous prompt cleanly when transitioning to another screen.

Example:

Enter Your Yr:

Time remaining: 7s

Time remaining: 6s

Time remaining: 5s

Time remaining: 4s

Time remaining: 3s

Time remaining: 2s

Time remaining: 1s

Session expired.

Closing Strawberry...

## Invalid input example

Enter Your Yr:

9

Invalid selection! Please select 1, 2 or 3.

Time remaining: 7s

The timer must restart after invalid input.

## Implementation requirements

Do not use ordinary blocking Python input() without a timeout mechanism.

Implement a reliable input handler that supports:

- Keyboard input.
- Enter key detection.
- Backspace.
- Invalid selection handling.
- Countdown rendering.
- Timeout detection.
- Graceful termination.

For Windows, consider using msvcrt with a polling loop and time.monotonic().

Keep input handling separate from business logic.

The seven-second timeout applies to user interaction, not to network download duration.

Network operations should have their own bounded request timeouts.

---

# 5. ALT KEY KILL SWITCH

Implement an emergency exit mechanism.

The user must be able to terminate Strawberry immediately by pressing the standalone ALT key.

Requirements:

- Detect the standalone left or right ALT key.
- Terminate the Strawberry process immediately.
- Do not wait for the seven-second countdown.
- Restore terminal state before exiting.
- Do not leave background keyboard hooks or worker threads running.
- Do not accidentally terminate the entire Windows Command Prompt process.

IMPORTANT WINDOWS BEHAVIOUR:

ALT is also a modifier key used for combinations such as ALT + TAB.

Implement standalone ALT detection carefully.

Prefer a Windows low-level keyboard hook or another reliable Windows keyboard listener.

Treat ALT as a kill switch when it is pressed and released without another key being used during that press.

Do not trigger the kill switch for ALT + TAB or ALT + F4.

Make the implementation Windows-specific and isolate it behind a keyboard-controller abstraction so future operating-system support is possible.

Document any limitations.

---

# 6. STRAWBERRY PRO — ADVANCED INTERFACE

Strawberry Pro is another interface to the same application.

It is not a paid version.

Everyone can access it.

It must use the same:

- Remote repository.
- Academic catalog.
- Download engine.
- Clipboard engine.
- Local storage.
- Program versions.

Use Python Textual to build an interactive terminal user interface.

The interface should look polished, modern and professional.

## Visual direction

Theme: Strawberry-inspired.

Suggested visual identity:

- Dark charcoal background.
- Strawberry red accents.
- Soft pink highlights.
- White typography.
- Subtle borders.
- Clean spacing.
- Minimal visual clutter.

Avoid excessive animations and unnecessary graphics.

## Pro features

1. Interactive year navigation.
2. Interactive semester and subject navigation.
3. Experiment browsing.
4. Search programs by name and keyword.
5. Program details and descriptions.
6. Download history.
7. Bookmarks or favourites.
8. Local cache status.
9. Program version information.
10. Refresh repository catalog.
11. Custom terminal themes.
12. Keyboard navigation.

Example layout:

STRAWBERRY PRO

Academic Library

Select Academic Year:

[ 2nd Year ] [ 3rd Year ] [ 4th Year ]

Subjects

Computer Networks
Database Management Systems
Java Programming
Operating Systems

Recent Downloads

Socket Programming
DNS Resolution

Navigation:
UP / DOWN = Navigate
ENTER = Select
ESC = Back
ALT = Exit

The Pro interface must also implement the seven-second inactivity rule for every selection/input screen.

Keyboard navigation should reset the inactivity timer when the user interacts with the interface.

A completed selection must move to the next screen and start a fresh seven-second timer.

Do not make Pro dependent on a subscription or authentication system.

## Launching editions

The default command:

strawberry

Launches Strawberry Lite.

The advanced interface:

strawberry pro

Launches Strawberry Pro.

Also support:

strawberry --help
strawberry --version

---

# 7. REMOTE REPOSITORY ARCHITECTURE

All actual laboratory programs must be maintained centrally.

Use Supabase as the proposed backend.

Use:

- Supabase PostgreSQL for catalog metadata.
- Supabase Storage for program files.
- Public read access for published academic content.
- A trusted administrator-only publishing workflow.

Students should not need accounts or authentication.

The application should be able to retrieve:

- Available academic years.
- Semesters.
- Subjects.
- Experiment names.
- Experiment indexes.
- Program descriptions.
- Source file locations.
- Program versions.
- SHA-256 checksums.

## Suggested database structure

TABLE: years

- id
- name

TABLE: semesters

- id
- year_id
- name

TABLE: subjects

- id
- semester_id
- subject_code
- subject_name

TABLE: experiments

- id
- subject_id
- experiment_number
- experiment_name
- description
- current_version_id
- is_published

TABLE: experiment_versions

- id
- experiment_id
- version_number
- storage_path
- primary_filename
- sha256
- published_at

Do not store the actual source code in PostgreSQL rows.

Store source files in Supabase Storage and keep their paths and metadata in the database.

## Security

- Public users can read published catalog entries.
- Public users can download published programs.
- Only trusted administrators can publish or modify programs.
- Never embed a Supabase service-role key in the executable.
- Use an appropriately restricted public/anonymous key if required.
- Enforce read-only public access through database and storage policies.
- Never expose administrator credentials.

## Configuration

Keep repository configuration separate from application code.

Use a configurable repository URL and environment-specific configuration.

Do not invent production credentials.

If Supabase credentials are unavailable, implement a mock repository provider with sample data so the application can be tested completely.

The application must clearly identify demo mode and must never pretend that sample programs came from a real remote repository.

---

# 8. LOCAL STORAGE AND OFFLINE SUPPORT

Strawberry should maintain a local cache.

Use the Windows user application-data directory.

Suggested location:

%LOCALAPPDATA%\Strawberry\

Directory structure:

Strawberry/
    config.json
    catalog.db
    cache/
    downloads/
    history.db

Requirements:

- Cache downloaded programs.
- Store catalog metadata locally.
- Avoid downloading identical program versions repeatedly.
- Verify cached files before reuse.
- Preserve downloaded files between sessions.
- Allow previously downloaded programs to remain accessible without internet.
- Refresh catalog information when an internet connection is available.

If a student has already downloaded a program, use the verified cached copy when appropriate.

Do not delete cached programs automatically.

---

# 9. CLIPBOARD IMPLEMENTATION

Clipboard functionality is central to Strawberry.

The application must copy the actual source code, not merely the filename or file path.

Use a reliable Windows clipboard library such as Pyperclip or a native Windows clipboard implementation.

Requirements:

- Copy the complete source text.
- Preserve line breaks and indentation.
- Preserve UTF-8 characters.
- Verify clipboard operations.
- Handle clipboard access errors.
- Never report successful copying unless the operation succeeds.

For programs containing multiple files:

- Identify one primary source file for clipboard copying.
- Cache all associated supporting files.
- Clearly identify the primary file.
- Inform the user that additional files are available locally.

---

# 10. WINDOWS STANDALONE EXECUTABLE

This project must ultimately be distributed as a standalone Windows application.

Students should not need to install Python, pip or any project dependencies.

Use PyInstaller.

Target executable:

strawberry.exe

Build requirements:

- Include all Python dependencies.
- Include required application assets.
- Include Textual resources.
- Include clipboard dependencies.
- Include required Windows keyboard-handling components.
- Include configuration defaults.
- Avoid requiring an external Python installation.
- Support Windows CMD and PowerShell.

Prefer a single standalone executable for the initial release, with both Lite and Pro modes accessible through the same executable.

Use PyInstaller's one-file mode unless a demonstrated dependency or startup issue makes one-folder mode more reliable.

Test the executable on a Windows environment without relying on the development Python environment.

---

# 11. WINDOWS INSTALLER

Use Inno Setup to create:

Strawberry_Setup.exe

Installation requirements:

1. Install Strawberry into a per-user application directory.
2. Register the executable directory in the current user's PATH.
3. Avoid requiring administrator privileges where possible.
4. Notify Windows of the PATH update.
5. Provide a clear installation success message.
6. Support clean uninstallation.
7. Remove only Strawberry-owned PATH entries during uninstall.
8. Preserve the user's other environment variables.
9. Provide an option to create a desktop shortcut.

After installation, the student should be able to open a new CMD or PowerShell window and type:

strawberry

No manual environment-variable editing should be necessary.

---

# 12. TECHNOLOGY STACK

Use the following stack unless there is a strong technical reason to change it.

Core:
- Python 3.11 or newer, choosing a version compatible with all dependencies and PyInstaller.
- Modular Python architecture.

Lite interface:
- Typer for command routing if needed.
- Rich for terminal formatting.

Pro interface:
- Textual.
- Rich.

Input handling:
- msvcrt.
- time.monotonic().
- Windows keyboard hook for standalone ALT detection.

Clipboard:
- Pyperclip or native Windows clipboard APIs.

Backend:
- Supabase PostgreSQL.
- Supabase Storage.
- HTTPX for HTTP communication.

Local storage:
- SQLite.
- Windows Local AppData.

Packaging:
- PyInstaller.
- Inno Setup.

Testing:
- Pytest.

---

# 13. PROJECT STRUCTURE

Create a clean and maintainable architecture.

Suggested structure:

strawberry-cli/
│
├── src/
│   └── strawberry/
│       │
│       ├── main.py
│       ├── cli.py
│       │
│       ├── core/
│       │   ├── application.py
│       │   ├── config.py
│       │   ├── input_handler.py
│       │   ├── timer.py
│       │   ├── keyboard_controller.py
│       │   └── shutdown.py
│       │
│       ├── lite/
│       │   ├── interface.py
│       │   └── workflow.py
│       │
│       ├── pro/
│       │   ├── app.py
│       │   ├── screens/
│       │   ├── widgets/
│       │   └── theme.py
│       │
│       ├── repository/
│       │   ├── base.py
│       │   ├── supabase.py
│       │   ├── mock.py
│       │   └── catalog.py
│       │
│       ├── services/
│       │   ├── downloader.py
│       │   ├── clipboard.py
│       │   ├── cache.py
│       │   └── checksum.py
│       │
│       └── models/
│           ├── academic.py
│           ├── subject.py
│           └── experiment.py
│
├── assets/
├── tests/
│   ├── test_timer.py
│   ├── test_input_handler.py
│   ├── test_clipboard.py
│   ├── test_repository.py
│   ├── test_download.py
│   └── test_workflows.py
│
├── installer/
│   └── strawberry.iss
│
├── scripts/
│   ├── build.py
│   └── publish_catalog.py
│
├── docs/
│   ├── architecture.md
│   ├── installation.md
│   └── admin-guide.md
│
├── pyproject.toml
├── README.md
├── .gitignore
└── LICENSE

You may improve this structure if necessary, but keep the Lite, Pro, repository and core logic clearly separated.

---

# 14. ERROR HANDLING

Handle these scenarios gracefully:

- No internet connection.
- Repository unavailable.
- Invalid year selection.
- Invalid subject selection.
- Invalid program index.
- Program not found.
- File download failure.
- Checksum mismatch.
- Clipboard access denied.
- Empty repository.
- Missing local cache.
- Corrupted cached program.
- Keyboard listener initialization failure.
- Application interrupted by CTRL + C.
- Missing configuration.
- Unsupported operating system.

Never silently fail.

Never copy an unverified or incomplete source file.

Use clear, student-friendly error messages.

---

# 15. TESTING REQUIREMENTS

Write actual automated tests.

Test:

1. Year selection.
2. Subject filtering by year.
3. Correct semester association.
4. Experiment indexing.
5. Seven-second input timeout.
6. Valid input transitions.
7. Invalid input timer reset.
8. Incomplete input timeout.
9. ALT kill-switch behaviour on Windows.
10. ALT + TAB does not trigger the kill switch.
11. Clipboard content correctness.
12. SHA-256 verification.
13. Remote download.
14. Local caching.
15. Offline cache access.
16. Lite workflow.
17. Pro workflow.
18. Application shutdown.
19. Standalone executable startup.
20. Installer PATH registration and uninstall.

Use mocked repositories for automated tests.

For Windows-specific functionality, include real Windows integration tests where possible.

Do not rely only on unit tests. Perform an end-to-end workflow test.

---

# 16. DEVELOPMENT PHASES

Do not attempt to build every feature in one unstructured step.

Implement in these phases:

PHASE 1 — FOUNDATION

- Initialize Python project.
- Create modular architecture.
- Implement data models.
- Implement mock repository.
- Implement Lite workflow.
- Implement seven-second timeout.
- Implement invalid-input handling.

PHASE 2 — CORE FUNCTIONALITY

- Implement remote repository interface.
- Integrate Supabase.
- Implement downloading.
- Implement checksum verification.
- Implement clipboard copying.
- Implement local caching.

PHASE 3 — WINDOWS FEATURES

- Implement standalone ALT kill switch.
- Implement graceful application shutdown.
- Test CMD and PowerShell.
- Verify seven-second behaviour.

PHASE 4 — PRO INTERFACE

- Build Textual application.
- Create Strawberry theme.
- Implement interactive navigation.
- Add search, history and bookmarks.
- Connect to the shared core engine.

PHASE 5 — DISTRIBUTION

- Configure PyInstaller.
- Generate strawberry.exe.
- Test without a Python installation.
- Create Inno Setup installer.
- Register PATH automatically.
- Test installation and uninstallation.

PHASE 6 — DOCUMENTATION AND RELEASE

- Write README.
- Document installation.
- Document repository administration.
- Document how to add new subjects and experiments.
- Document how to publish new program versions.
- Create release build instructions.

---

# 17. IMPORTANT DEVELOPMENT RULES

Follow these rules throughout implementation:

1. Do not create unnecessary features outside the specified scope.
2. Keep the application lightweight.
3. Prioritize reliability over visual effects.
4. Do not hardcode actual department subjects or programs.
5. Use demonstration data only for development.
6. Never expose administrator credentials.
7. Never automatically execute retrieved programs.
8. Keep both interfaces connected to the same shared core.
9. Do not duplicate the downloader or repository implementation.
10. Keep all user-facing messages simple and understandable.
11. Make all important settings configurable.
12. Do not claim a feature is complete without testing it.
13. Do not create fake download success messages.
14. Do not leave placeholder functions in features claimed as complete.
15. Document Windows-specific limitations.

---

# 18. FINAL ACCEPTANCE CRITERIA

The project is considered ready for its first release when:

[ ] Typing `strawberry` launches Lite.

[ ] Typing `strawberry pro` launches Pro.

[ ] Both editions are free.

[ ] Both editions access the same academic repository.

[ ] All three academic years are supported.

[ ] Both semesters are correctly associated with each year.

[ ] Subjects load dynamically.

[ ] Programs load dynamically.

[ ] Every Lite input prompt has a seven-second countdown.

[ ] Invalid inputs restart the countdown.

[ ] Timeout terminates Strawberry automatically.

[ ] Standalone ALT terminates Strawberry immediately.

[ ] ALT + TAB does not accidentally trigger termination.

[ ] Program selection downloads the correct source file.

[ ] SHA-256 integrity verification works.

[ ] Source code is automatically copied into the clipboard.

[ ] The program is cached locally.

[ ] Previously downloaded programs can be accessed offline.

[ ] Pro provides a polished interactive interface.

[ ] The executable runs without Python installed.

[ ] The Windows installer registers Strawberry in PATH.

[ ] A student can install it and launch it by typing `strawberry`.

[ ] Documentation and tests are included.

---

# 19. YOUR FIRST TASK

Before writing code:

1. Analyze the complete requirements.
2. Produce a technical implementation plan.
3. Identify any technical conflicts or Windows-specific limitations.
4. Propose the final architecture.
5. Break the work into implementation tasks.
6. Identify the dependencies.
7. Explain how the seven-second timer and standalone ALT detection will work reliably.
8. Explain how Supabase will be configured without exposing privileged credentials.

Wait for implementation-plan approval before beginning large-scale implementation.

Once approved, implement the application phase by phase.

After every phase:

- Run relevant tests.
- Fix errors.
- Verify the implementation.
- Update documentation.
- Report what is complete and what remains.

At the end, build and test the standalone Windows executable and installer.

Do not stop at a visual prototype.

The final result must be a functional Strawberry application that students can install and use.

**Build Strawberry as a real, reliable, lightweight Windows application.**

🍓 Strawberry — Pick your program. Paste your code.