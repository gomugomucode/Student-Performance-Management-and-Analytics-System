# Student Performance Management and Analytics System

## Introduction

A terminal-based Python application for managing student records, entering marks, generating analytics, and exporting CSV reports. This project is designed for academic administrators and instructors who need a lightweight, easy-to-run system for student performance tracking.

## Features

- Student CRUD operations (Create, Read, Update, Delete)
- Marks CRUD management with subject uniqueness per student
- Analytics reporting for student averages, class averages, and pass/fail status
- CSV export for student and marks data
- Input validation and structured error handling
- Simple terminal-based interface with formatted menus and tables

## Technologies Used

- Python 3.10+
- SQLite for local data storage
- pandas for analytics and CSV export
- NumPy for numeric calculations
- Standard library modules for terminal UI and file handling

## Folder Structure

```text
.
├── cli
│   ├── actions.py
│   ├── menu.py
│   └── utils.py
├── database
│   ├── connection.py
│   └── schema.py
├── models
│   ├── marks.py
│   └── student.py
├── reports
├── services
│   ├── analytics.py
│   ├── export.py
│   └── validation.py
├── tests
│   ├── test_marks.py
│   └── test_student.py
├── main.py
├── README.md
└── requirements.txt
```

## Installation

1. Clone the repository or download the project folder.
2. Open a terminal in the project root directory.
3. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

4. Install dependencies:

```powershell
pip install -r requirements.txt
```

5. Run unit tests (optional):

```powershell
python -m unittest discover tests
```

## Database Schema

The application uses a local SQLite database file named `database.db` stored in the project root.

### `students` table

| Column      | Type    | Notes                        |
|-------------|---------|------------------------------|
| student_id  | INTEGER | Primary key                  |
| name        | TEXT    | Required                     |
| gender      | TEXT    | Optional                     |
| semester    | INTEGER | Optional                     |
| department  | TEXT    | Optional                     |
| age         | INTEGER | Optional                     |
| grade       | TEXT    | Optional                     |

### `marks` table

| Column     | Type    | Notes                                                   |
|------------|---------|---------------------------------------------------------|
| mark_id    | INTEGER | Primary key                                             |
| student_id | INTEGER | Foreign key to `students(student_id)`                   |
| subject    | TEXT    | Required                                                |
| marks      | INTEGER | Required, constrained between 0 and 100                 |

Constraints:

- `marks` has a foreign key relationship to `students`
- Each `(student_id, subject)` pair is unique
- `marks` values are enforced between `0` and `100`

## How to Run

1. Make sure the virtual environment is activated.
2. Initialize the database schema (this runs automatically when `main.py` starts).
3. Start the application:

```powershell
python main.py
```

4. Navigate the terminal menus to manage students, enter marks, view analytics, and export CSV reports.
<!-- 
## Screenshots Placeholder

> Add application screenshots here once available.

- Screenshot 1: Main menu view
- Screenshot 2: Add student workflow
- Screenshot 3: Marks entry form
- Screenshot 4: Analytics output
- Screenshot 5: CSV export confirmation -->

## Manual Testing Checklist

### Student CRUD

| Test Case | Steps | Expected Result |
|-----------|-------|-----------------|
| Add student with valid data | Use `Student Management` → `Add student` and provide valid Student ID, name, age, gender, semester, department, grade | Student added successfully message appears, student is saved in DB |
| Add student with duplicate ID | Enter an ID already in use | Error message indicates duplicate student ID |
| View all students | Choose `View all students` | Table displays all student records with headers |
| Search student by name | Use search with partial name string | Matching student rows are displayed |
| Search student by ID | Use search with exact student ID | Matching record is displayed |
| Update student record | Select an existing student and change one or more fields | Success message on update, updated values visible in view flow |
| Delete student record | Select an existing student and confirm deletion | Student deletion success message, record removed from list |

### Marks CRUD

| Test Case | Steps | Expected Result |
|-----------|-------|-----------------|
| Add marks valid record | Use `Marks Management` → `Add marks` with existing student ID, valid subject and 0–100 marks | Success message and marks saved |
| Add duplicate subject for same student | Add the same subject again for same student | Error message about duplicate subject entry |
| View marks for student | Use `View marks` with student ID | Table displays marks records for that student |
| Update marks record | Enter existing mark record ID and change subject or marks | Success message and new record values appear |
| Delete marks record | Delete an existing mark record and confirm | Success message and record no longer appears |

### Analytics

| Test Case | Steps | Expected Result |
|-----------|-------|-----------------|
| Calculate student average | Use `Analytics` → `Student average` and enter valid student ID | Display average formatted number if marks exist |
| Calculate class average | Use `Analytics` → `Class average` | Display class average if at least one mark record exists |
| Missing student analytics | Use invalid or missing student ID | Clear error message for missing student or no marks |

### CSV Export

| Test Case | Steps | Expected Result |
|-----------|-------|-----------------|
| Export students | Use `Export` → `Export students to CSV` | Success message and file path printed, CSV created in `Reports/` |
| Export marks | Use `Export` → `Export marks to CSV` | Success message and file path printed, CSV created in `Reports/` |
| Export with empty data | Run export with no records present | Informational or error message if no data available |

### Validation

| Test Case | Steps | Expected Result |
|-----------|-------|-----------------|
| Student ID invalid | Enter non-numeric or negative Student ID | Error message requiring a positive number |
| Required name missing | Submit empty student name | Error message requiring non-empty name |
| Invalid marks entry | Enter marks outside 0–100 or non-numeric value | Validation error displayed |
| Empty optional fields | Leave optional fields blank | Input accepted and record saved successfully |

### Error Handling

| Test Case | Steps | Expected Result |
|-----------|-------|-----------------|
| Invalid menu selection | Enter out-of-range menu option | Error prompt requesting valid selection |
| Delete cancel confirmation | Choose to cancel a delete action | Message indicates cancellation and no deletion occurs |
| Database unavailable | Temporarily block database file or corrupt schema and run action | Friendly error message about connection issues |

## Future Improvements

- Add automated unit tests and integration tests
- Add more analytics views (grade distribution, subject trends, top/bottom performers)
- Add multi-user login or role-based access control
- Add richer export options (Excel, PDF)
- Add data import from CSV or Excel

## License

This project is available under the MIT License.
