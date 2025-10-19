# Solia Time Tracking - MVVM Architecture

## Architecture Overview

The application follows the MVVM (Model-View-ViewModel) pattern with clear separation of concerns.

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                       │
│                     (PySide6/Qt Widgets)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                          Views                               │
│  ┌──────────────┐  ┌───────────┐  ┌───────────┐            │
│  │ DashboardView│  │ TimerView │  │ProfilesView│            │
│  └──────────────┘  └───────────┘  └───────────┘            │
│  ┌──────────────┐  ┌─────────────────────────┐             │
│  │ ServicesView │  │     MainWindow          │             │
│  └──────────────┘  │  (Container & Manager)  │             │
│                    └─────────────────────────┘             │
└────────────────────────┬────────────────────────────────────┘
                         │ (Qt Signals/Slots)
┌────────────────────────▼────────────────────────────────────┐
│                       ViewModels                             │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ DashboardViewModel│  │  TimerViewModel  │                │
│  └──────────────────┘  └──────────────────┘                │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ProfilesViewModel │  │ ServicesViewModel│                │
│  └──────────────────┘  └──────────────────┘                │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                        Services                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ StateService │  │ TimerService │  │ExportService │     │
│  │  (Singleton) │  └──────────────┘  └──────────────┘     │
│  └──────┬───────┘                                           │
│         │  ┌──────────────────┐                            │
│         └─▶│ SettingsService  │                            │
│            └──────────────────┘                            │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                         Models                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Repository  │  │   Database   │  │    Schema    │     │
│  │   (CRUD)     │  │  (SQLite)    │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### 1. Views Layer (`src/views/`)

**Purpose**: Pure UI - rendering and user interaction

**Responsibilities**:

- Display data provided by ViewModels
- Capture user input (clicks, text entry)
- Emit signals for user actions
- Subscribe to ViewModel signals for updates
- **NO business logic**

**Files**:

- `dashboard_view.py` - Home screen with navigation tiles
- `timer_view.py` - Timer controls and entries table
- `profiles_view.py` - Profiles management (list + settings)
- `services_view.py` - Services management table
- `main_window.py` - Container managing all views

**Example**:

```python
class TimerView(QWidget):
    def __init__(self, viewmodel: TimerViewModel):
        self.viewmodel = viewmodel
        self._build_ui()
        # Connect ViewModel → View
        viewmodel.elapsed_updated.connect(self._update_elapsed)
        # Connect View → ViewModel
        self.toggle_btn.clicked.connect(viewmodel.toggle_timer)
```

### 2. ViewModels Layer (`src/viewmodels/`)

**Purpose**: Presentation logic and state management

**Responsibilities**:

- Manage view-specific state
- Format data for display
- Handle user actions from views
- Call services for business operations
- Emit signals when state changes
- **NO UI code, NO direct database access**

**Files**:

- `dashboard_viewmodel.py` - Navigation logic
- `timer_viewmodel.py` - Timer logic, progress calculation
- `profiles_viewmodel.py` - Profile CRUD, todos
- `services_viewmodel.py` - Services CRUD

**Example**:

```python
class TimerViewModel(QObject):
    elapsed_updated = Signal(int)

    def __init__(self, state_service, timer_service):
        self.state = state_service
        self.timer_service = timer_service

    def toggle_timer(self, note: str = ""):
        if self.is_running:
            self.timer_service.stop()
        else:
            self.timer_service.start(self.state.current_profile_id, note)
        self.elapsed_updated.emit(self._compute_elapsed())
```

### 3. Services Layer (`src/services/`)

**Purpose**: Business logic and application services

**Responsibilities**:

- Business logic operations
- State management (StateService)
- Data transformations
- External integrations (file export)
- **NO UI code**

**Files**:

- `state_service.py` - Central state manager (Singleton)
- `timer_service.py` - Timer operations
- `export_service.py` - CSV/JSON export
- `settings_service.py` - Settings persistence

**Key Service: StateService**:

```python
class StateService(QObject):
    """Central state manager - Singleton pattern"""

    # Signals for state changes
    profile_changed = Signal(object)
    active_entry_changed = Signal(object)
    entries_updated = Signal()
    profiles_updated = Signal()
    services_updated = Signal()

    def __init__(self, repository, settings_store):
        self._repository = repository
        self._current_profile_id = None
        self._active_entry = None
```

### 4. Models Layer (`src/models/`)

**Purpose**: Data access and persistence

**Responsibilities**:

- Database operations (CRUD)
- Schema management
- Data persistence

**Files**:

- `repository.py` - Data access layer
- `db.py` - Database connection
- `schema.sql` - Database schema

### 5. UI Components (`src/ui/`)

**Purpose**: Reusable UI widgets and dialogs

**Components** (`src/ui/components/`):

- `circular_progress.py` - Progress circle widget
- `tile_button.py` - Dashboard navigation tile

**Dialogs** (`src/ui/dialogs/`):

- `profile_dialog.py` - Profile create/edit
- `entry_dialog.py` - Entry note editing
- `service_dialog.py` - Service create/edit

### 6. Utilities (`src/utils/`)

**Purpose**: Helper functions and utilities

**Files**:

- `formatters.py` - Time, currency, parsing utilities

## Data Flow Patterns

### 1. User Action Flow

```
User clicks button
    ↓
View captures click
    ↓
View calls ViewModel method
    ↓
ViewModel calls Service
    ↓
Service updates Model/Repository
    ↓
Service emits signal via StateService
    ↓
ViewModel receives signal
    ↓
ViewModel updates internal state
    ↓
ViewModel emits signal
    ↓
View receives signal
    ↓
View updates UI
```

### 2. State Change Flow

```
StateService.set_current_profile(profile_id)
    ↓
StateService emits profile_changed signal
    ↓
Multiple ViewModels listening
    ↓
- TimerViewModel updates entries
- ProfilesViewModel loads todos
    ↓
ViewModels emit their own signals
    ↓
Views update UI
```

### 3. Timer Flow

```
User clicks "Start"
    ↓
TimerView → TimerViewModel.toggle_timer()
    ↓
TimerViewModel → TimerService.start()
    ↓
TimerService → Repository.start_entry()
    ↓
TimerService → StateService.refresh_active_entry()
    ↓
StateService emits active_entry_changed
    ↓
TimerViewModel updates state
    ↓
TimerViewModel emits timer_state_changed
    ↓
TimerView updates button text to "Stop"
```

## Dependency Injection

The application uses constructor injection for dependencies:

```python
# main() in app.py
repo = Repository(conn)
settings_store = SettingsStore()

# Services
state_service = StateService(repo, settings_store)
timer_service = TimerService(state_service)

# ViewModels
timer_vm = TimerViewModel(state_service, timer_service)
profiles_vm = ProfilesViewModel(state_service, timer_service)
services_vm = ServicesViewModel(state_service)

# Views
timer_view = TimerView(timer_vm)
profiles_view = ProfilesView(profiles_vm)

# MainWindow
window = MainWindow(
    state_service=state_service,
    timer_service=timer_service,
    dashboard_vm=dashboard_vm,
    timer_vm=timer_vm,
    profiles_vm=profiles_vm,
    services_vm=services_vm,
)
```

## Key Design Patterns

### 1. Singleton Pattern

- **StateService**: Only one instance manages application state

### 2. Observer Pattern

- Qt Signals/Slots throughout for loose coupling
- ViewModels emit signals, Views subscribe

### 3. Repository Pattern

- `Repository` class abstracts database operations

### 4. Dependency Injection

- Constructor injection for all dependencies
- No global state (except StateService singleton)

### 5. Separation of Concerns

- Each layer has single responsibility
- Clear boundaries between layers

## Testing Strategy

### Unit Tests (ViewModels)

```python
def test_timer_toggle():
    state = StateService(mock_repo, mock_settings)
    timer_service = TimerService(state)
    vm = TimerViewModel(state, timer_service)

    vm.toggle_timer()
    assert vm.is_running == True
```

### Integration Tests (Views)

```python
def test_timer_view_updates():
    vm = TimerViewModel(state, timer_service)
    view = TimerView(vm)

    vm.elapsed_updated.emit(3600)
    assert view.elapsed_label.text() == "01:00:00"
```

## Extension Points

### Adding a New Feature

1. **Service** (if needed):

```python
class ReportService:
    def __init__(self, state_service):
        self.state = state_service

    def generate_report(self):
        # Business logic
```

2. **ViewModel**:

```python
class ReportViewModel(QObject):
    report_ready = Signal(object)

    def __init__(self, state_service, report_service):
        self.report_service = report_service

    def load_report(self):
        data = self.report_service.generate_report()
        self.report_ready.emit(data)
```

3. **View**:

```python
class ReportView(QWidget):
    def __init__(self, viewmodel):
        self.viewmodel = viewmodel
        viewmodel.report_ready.connect(self._display_report)
```

4. **Wire up in MainWindow**:

```python
self.report_view = ReportView(report_vm)
self.stack.addWidget(self.report_view)
```

## Best Practices

1. **Views should only**:

   - Build UI
   - Handle user input
   - Update display based on ViewModel signals

2. **ViewModels should only**:

   - Manage presentation state
   - Format data for views
   - Call services
   - Emit signals

3. **Services should only**:

   - Execute business logic
   - Call repository
   - Manage application-wide state

4. **Always use Dependency Injection**:

   - Pass dependencies via constructor
   - No global imports of services/ViewModels

5. **Use Signals for Communication**:
   - Views → ViewModels: method calls
   - ViewModels → Views: signals
   - Services → ViewModels: signals (via StateService)

## Conclusion

This architecture provides:

- ✅ Clear separation of concerns
- ✅ Easy testing
- ✅ Loose coupling
- ✅ High cohesion
- ✅ Scalability
- ✅ Maintainability
