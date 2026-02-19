# ⏱️ SoliaTime

> A modern, elegant time tracking desktop application for Windows built with Python and PySide6.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/PySide6-6.6+-green.svg)](https://pypi.org/project/PySide6/)

## ✨ Features

### 🎯 Core Functionality

- **⏱️ Smart Timer** - Start/stop time tracking with a single click
- **👥 Profile Management** - Organize time by clients with comprehensive contact information
- **📋 Project Tracking** - Track time against specific projects with deadlines, estimates, and invoice tracking
- **💼 Service Management** - Define billable services with custom hourly rates and time estimates
- **🏠 Dashboard** - Modern tile-based navigation for quick access to all features

### 📅 Time Management

- **⏱️ Active Timer Display** - Real-time elapsed time counter with circular progress indicator
- **📊 Weekly Overview** - View time tracked by calendar week (CW) with start/end dates and totals
- **📄 Invoices** - Invoice management module (Coming Soon)
- **🧮 MwSt Calculator** - Beautiful German VAT calculator supporting 19% and 7% rates with real-time calculation
- **🔄 Running Totals** - Automatic calculation of time spent per profile, project, and service
- **📆 Multi-Week Tracking** - Track and review time across multiple calendar weeks

### 🔧 Advanced Features

- **✏️ Inline Editing** - Double-click any cell to edit timestamps, notes, profiles, or projects directly in tables
- **📤 Smart Export** - Export to CSV/JSON with optional profile/project filtering
- **🎨 Modern UI** - Clean, intuitive interface with circular progress indicators and visual feedback
- **🔔 System Tray** - Minimize to tray for quick access; tray icon shows timer status
- **💾 Auto-Save** - All changes are automatically persisted to SQLite database
- **🔍 Flexible Filtering** - Filter time entries by profile and project
- **📐 Window Memory** - Remembers window size and position between sessions
- **⌨️ Keyboard Shortcuts** - Space to toggle timer, Ctrl+N for new profile, Delete to remove entries
- **🖱️ Context Menus** - Right-click menus for quick actions on profiles, projects, and entries

### 📈 Profile Management

- **👤 Contact Information** - Store contact person, email, phone, and business address
- **📝 Profile Notes** - Add custom notes for each client/profile
- **🎨 Profile Organization** - List-based navigation with detailed panel view
- **📋 Profile Projects** - View all projects associated with a profile
- **📑 Profile Todos** - Manage per-profile task lists (visible in profile details)
- **🔄 Profile Duplication** - Quickly duplicate profiles with all settings
- **🗑️ Safe Deletion** - Delete profiles with cascade deletion of associated data

### 📋 Project Features

- **📊 Project Details** - Track project name, profile, estimated time, service, deadlines, and start dates
- **💰 Invoice Tracking** - Mark invoice sent/paid status and store invoice numbers
- **📝 Project Notes** - Add detailed notes with inline editing and save functionality
- **✅ Project Todos** - Manage checkable to-do items with strikethrough for completed tasks
- **🔍 Profile Filtering** - Filter projects by profile with three-column layout
- **📅 Deadline Management** - Set and track project deadlines
- **⏱️ Time Estimates** - Set estimated time in HH:MM format per project
- **🔗 Service Association** - Link projects to specific services for rate tracking

### 💼 Service Catalog

- **💶 Hourly Rates** - Define service rates in EUR (stored as cents for precision)
- **⏱️ Service Estimates** - Set estimated time per service in HH:MM format
- **📝 Service CRUD** - Full Create, Read, Update, Delete operations
- **📊 Service Table** - Clean table view showing service name, rate, and estimates
- **🔗 Project Integration** - Services can be assigned to projects for billing

### 🗄️ Data Management

- **📤 CSV Export** - Export entries with formatted timestamps [DD.MM.YY] - HH:MM and durations HH:MM:SS
- **📤 JSON Export** - Export with full data including IDs, timestamps (Unix), and metadata
- **🔍 Filtered Export** - Export data filtered by specific profile and/or project
- **💾 SQLite Database** - Robust local storage with foreign keys and cascading deletes
- **🔐 Data Privacy** - All data stored locally on your machine (LOCALAPPDATA/Solia/)
- **📊 Time Entry Auditing** - Complete history with profile, project, start, end, duration, and notes
- **🏷️ Tag Support** - Tag entries for additional organization (stored in database)

## 🏗️ Architecture

Built with clean **MVVM architecture** (Model-View-ViewModel) for maintainability and testability:

```
📦 SoliaTime
 ┣ 📂 models         # Data layer (SQLite, Repository pattern)
 ┣ 📂 viewmodels     # Business logic and state management
 ┣ 📂 views          # UI components (PySide6 widgets)
 ┣ 📂 services       # Application services (Timer, Export, Settings)
 ┣ 📂 ui             # Reusable UI components and dialogs
 ┗ 📂 utils          # Helper functions and formatters
```

Key design patterns:

- **Repository Pattern** for data access abstraction
- **Service Layer** for business logic
- **Singleton State Service** for centralized state management
- **Signal-based communication** for loose coupling
- **Dependency Injection** for testability

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Windows OS (for .exe builds)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/SoliaTime.git
   cd SoliaTime
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python -m src.app
   ```

### 📦 Building Standalone Executable

Create a single-file Windows executable:

```bash
python -m PyInstaller SoliaTime.spec
```

The executable will be available at `dist/SoliaTime.exe` - no installation required!

## 💡 Usage

### Quick Start

1. **Create a Profile** - Click "Profiles" tile, add a client with contact information
2. **Add Projects** (Optional) - Navigate to "Projects", create projects with estimates and deadlines
3. **Define Services** (Optional) - Set up your billable services with hourly rates
4. **Start Timer** - Go to "Timer", select profile/project, add optional note, and click Start
5. **Track Time** - Timer runs in the background; app can be minimized to system tray
6. **Edit Entries** - Double-click any cell in the timer table to edit timestamps, notes, or assignments
7. **Export Data** - Use File menu to export filtered data to CSV or JSON
8. **Review Weekly** - Check "Weekly" view for calendar week summaries

### Detailed Workflows

#### Profile Management
1. Add profiles with full contact information (name, person, email, phone, address)
2. Add notes specific to each client
3. View all projects associated with a profile
4. Duplicate profiles to quickly create similar entries
5. Delete profiles (all associated data is removed)

#### Project Management
1. Create projects linked to profiles
2. Set time estimates in hours (converted to HH:MM format)
3. Assign services for rate tracking
4. Set deadlines and start dates
5. Track invoice status (sent/paid) and invoice numbers
6. Add project notes and manage todo lists
7. Mark todos as complete with checkbox (strikethrough styling)

#### Time Tracking
1. Select profile and optionally a project
2. Add a note (optional, can be edited later)
3. Click Start (or press Space)
4. Timer displays elapsed time with circular progress indicator
5. Click Stop to end session
6. All entries appear in the table below
7. Double-click cells to edit timestamps, notes, profile, or project
8. Select entries and press Delete to remove them

#### VAT Calculation
1. Navigate to MwSt Calculator
2. Choose tax rate: 19% or 7% (toggle buttons)
3. Enter any field (Netto, MwSt, or Brutto)
4. Press Enter or click "Berechnen" to calculate
5. Results auto-update bidirectionally
6. German number format supported (comma as decimal separator)

### Keyboard Shortcuts

| Shortcut | Action                     |
| -------- | -------------------------- |
| `Space`  | Toggle timer               |
| `Ctrl+N` | Create new profile         |
| `Delete` | Delete selected entries    |
| `Enter`  | Edit todo/entry (on focus) |

### Navigation

The dashboard provides quick access to all modules:

| Module      | Description                                                                      |
| ----------- | -------------------------------------------------------------------------------- |
| ⏱️ Timer    | Time tracking with start/stop controls, real-time display, and entry management |
| 👥 Profiles | Client/profile management with full contact details, notes, and associated todos |
| 📋 Projects | Project tracking with deadlines, estimates, invoice status, and project todos    |
| 💼 Services | Service catalog with hourly rates and time estimates                            |
| 📅 Weekly   | Weekly time summaries by calendar week (CW) with date ranges and totals         |
| 📄 Invoices | Invoice management (Coming Soon)                                                 |
| 🧮 MwSt     | Beautiful German VAT calculator with 19%/7% rates and bidirectional calculation  |

### Export Formats

**CSV Export:**

```csv
profile,project,start,end,duration,note,tags
ClientA,Website Redesign,[20.10.25] - 09:00,[20.10.25] - 11:30,02:30:00,Design work,design
ClientB,—,[21.10.25] - 14:00,[21.10.25] - 15:45,01:45:00,Consultation,
```

- Timestamps formatted as `[DD.MM.YY] - HH:MM`
- Duration formatted as `HH:MM:SS`
- Projects without assignment shown as `—`
- Can be filtered by profile and/or project before export

**JSON Export:**

```json
[
  {
    "id": 1,
    "profile_id": 1,
    "profile": "ClientA",
    "project_id": 1,
    "project": "Website Redesign",
    "start_ts": 1729418400,
    "end_ts": 1729427400,
    "duration_sec": 9000,
    "note": "Design work",
    "tags": "design"
  }
]
```

- Full data export with IDs and metadata
- Unix timestamps for easy processing
- Duration in seconds for precise calculations
- Null-safe project fields (null if not assigned)

## 🗄️ Data Storage

All data is stored locally in an SQLite database with a robust schema:

- **Database**: `%LOCALAPPDATA%/Solia/data/solia.db`
- **Settings**: `%LOCALAPPDATA%/Solia/settings.json`

### Database Schema

The application uses a normalized relational database with the following tables:

- **profiles** - Client information with contact details, notes, and business addresses
- **time_entries** - Time tracking records with profile/project associations
- **projects** - Project details with deadlines, estimates, and invoice tracking
- **project_todos** - Per-project task lists with completion status
- **services** - Service catalog with hourly rates (in cents) and time estimates
- **profile_services** - Service instances assigned to profiles (for future use)
- **profile_service_todos** - Todos for profile service instances (for future use)
- **profile_todos** - Per-profile task lists (for future use)

**Data Safety:**
- Foreign key constraints with CASCADE deletion
- Indexed for fast queries on profiles and date ranges
- Your data never leaves your machine! 🔒

## 🛠️ Technology Stack

| Component    | Technology                                                   |
| ------------ | ------------------------------------------------------------ |
| Framework    | [PySide6](https://pypi.org/project/PySide6/) (Qt for Python) |
| Database     | SQLite3                                                      |
| Packaging    | PyInstaller                                                  |
| Architecture | MVVM (Model-View-ViewModel)                                  |
| Language     | Python 3.10+                                                 |

### Dependencies

- **PySide6** - Qt bindings for Python
- **appdirs** - Platform-specific application directories
- **python-dateutil** - Date/time utilities
- **typing-extensions** - Type hint support
- **watchfiles** - File watching for development

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Feel free to:

- 🐛 Report bugs
- 💡 Suggest new features
- 🔧 Submit pull requests

## 🙏 Acknowledgments

Built with:

- [PySide6](https://doc.qt.io/qtforpython/) - Python bindings for Qt
- [PyInstaller](https://pyinstaller.org/) - Python application bundler

---

<div align="center">

**[⬆ Back to Top](#-soliatime)**

Made with ❤️ for time tracking

</div>
