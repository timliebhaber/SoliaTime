# ⏱️ SoliaTime

> A modern, elegant time tracking desktop application for Windows built with Python and PySide6.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/PySide6-6.6+-green.svg)](https://pypi.org/project/PySide6/)

## ✨ Features

### 🎯 Core Functionality

- **⏱️ Smart Timer** - Start/stop time tracking with a single click
- **👥 Profile Management** - Organize time by clients with contact information
- **📋 Project Tracking** - Track time against specific projects with deadlines and estimates
- **💼 Service Management** - Define billable services with custom rates
- **📊 Dashboard** - Quick overview of your time tracking activity

### 🔧 Advanced Features

- **✏️ Inline Editing** - Double-click any cell to edit profiles, projects, timestamps, or notes
- **📤 Smart Export** - Export to CSV/JSON with dynamic filenames based on selected filters
- **🎨 Clean UI** - Modern, intuitive interface with circular progress indicators
- **🔔 System Tray** - Minimize to tray for quick access
- **💾 Auto-Save** - All changes are automatically persisted to SQLite database
- **🔍 Flexible Filtering** - Filter entries by profile and project

### 📈 Data Management

- **Profile Organization** - Track multiple clients with contact details and notes
- **Project Planning** - Set time estimates and deadlines for projects
- **Service Catalog** - Define reusable services with hourly rates
- **Time Entry History** - Complete audit trail of all time entries
- **Todo Lists** - Per-profile and per-project task management

## 🏗️ Architecture

Built with clean **MVVM architecture** (Model-View-ViewModel) for maintainability and testability:

```
📦 SoliaTime
 ┣ 📂 models         # Data layer (SQLite, Repository pattern)
 ┣ 📂 viewmodels     # Business logic and state management
 ┣ 📂 views          # UI components (PySide6 widgets)
 ┣ 📂 services       # Application services (Timer, Export, Settings)
 ┗ 📂 ui             # Reusable UI components and dialogs
```

Key design patterns:

- **Repository Pattern** for data access abstraction
- **Service Layer** for business logic
- **Singleton State Service** for centralized state management
- **Signal-based communication** for loose coupling

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Windows OS (for .exe builds)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/timely-time-tracking.git
   cd timely-time-tracking
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
pyinstaller SoliaTime.spec
```

The executable will be available at `dist/SoliaTime.exe` - no installation required!

## 💡 Usage

### Quick Start

1. **Create a Profile** - Add a client or project profile
2. **Add Projects** (Optional) - Define specific projects under a profile
3. **Start Timer** - Select profile/project and click Start
4. **Track Time** - Timer runs in the background, minimize to tray
5. **Edit Entries** - Double-click any cell in the timer view to edit
6. **Export Data** - Export filtered data to CSV or JSON

### Keyboard Shortcuts

- `Ctrl+T` - Toggle timer
- `Delete` - Delete selected entries
- Double-click any cell to edit

### Export Formats

**CSV Export:**

```csv
profile,project,start,end,duration,note,tags
ClientA,Website Redesign,[20.10.25] - 09:00,[20.10.25] - 11:30,02:30:00,Design work,design
```

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

## 🗄️ Data Storage

All data is stored locally in an SQLite database:

- **Location**: `%LOCALAPPDATA%/Solia/data/solia.db`
- **Settings**: `%LOCALAPPDATA%/Solia/settings.json`

Your data never leaves your machine! 🔒

## 🛠️ Technology Stack

- **Framework**: [PySide6](https://pypi.org/project/PySide6/) (Qt for Python)
- **Database**: SQLite3
- **Packaging**: PyInstaller
- **Architecture**: MVVM (Model-View-ViewModel)
- **Language**: Python 3.10+

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
