# StockMaster Pro - Fixed Version

This document outlines the issues that were fixed in the StockMaster Pro application.

## Issues Fixed

1. **Redirect Loop in Logout Flow**
   - Fixed infinite redirect loops when accessing the logout endpoint
   - Updated form action URLs to use the correct blueprint paths
   - Added client-side redirection to escape redirect loops

2. **Missing Dependencies**
   - Created improved dependency installation script
   - Made sure pandas and numpy are properly installed
   - Added validation of installed dependencies

3. **Blueprint Path Consistency**
   - Fixed form action URLs to properly point to blueprint routes
   - Ensured all routes use the correct URL patterns

## How to Run the Application

### Option 1: Using the Launcher Script
The simplest way to run the application is to use the launcher script:

```bash
python run_app.py
```

This script will:
1. Install all required dependencies
2. Start the application

### Option 2: Manual Steps

If you prefer to run the steps manually:

1. **Install Dependencies**:
   ```bash
   python install_dependencies.py
   ```
   
2. **Run the Application**:
   ```bash
   python app.py
   ```

## Login Information

After the application starts, you can access it at: http://127.0.0.1:5000

### Default Admin Account
- **Username**: admin
- **Password**: admin123

If you don't have an admin account yet, you can create one by running:
```bash
python reset_db_with_admin.py
```

## Troubleshooting

### Dependency Issues
If you encounter dependency issues:

1. Make sure you have a working Python installation (3.8 or newer)
2. Try installing dependencies manually:
   ```bash
   pip install -r requirements.txt
   ```

### Database Issues
If you have database-related errors:

1. Reset the database:
   ```bash
   python reset_db.py
   ```
   
2. Create an admin user:
   ```bash
   python create_admin_direct.py
   ```

### Redirect Loop Issues
If you encounter redirect loops:

1. Clear your browser cache and cookies
2. Try a different browser
3. Access the login page directly at: http://127.0.0.1:5000/auth/login
