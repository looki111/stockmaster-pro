# Database Migration Guide for StockMaster Pro

This guide explains how to properly handle database schema changes in the StockMaster Pro application using Flask-Migrate.

## Why Database Migrations Matter

When you modify database models (add, remove, or change fields), the changes need to be reflected in the actual database schema. Without proper migrations:

- The application will try to access columns that don't exist in the database
- This leads to `OperationalError` exceptions like `no such column: users.theme_color`
- Development is slowed down by unnecessary debugging
- Data might be lost when manually altering the schema

## Initial Setup

If you haven't set up Flask-Migrate yet, run:

```bash
python setup_migrations.py
```

This will:
1. Initialize the migrations directory
2. Create an initial migration based on the current models
3. Apply the migration to the database

## Workflow for Making Schema Changes

### 1. Modify the Model

When you need to change the database schema, first update the model in `database/models.py` or other model files:

```python
# Example: Adding a new field to the User model
class User(db.Model):
    # Existing fields...
    
    # New field
    new_field = db.Column(db.String(50), default='default_value')
```

### 2. Create a Migration

After modifying the model, create a migration to capture the changes:

```bash
cd backend
flask db migrate -m "Add new_field to User model"
```

This command:
- Compares the models with the current database schema
- Generates a migration script in `migrations/versions/`
- The script contains the necessary SQL commands to update the database

### 3. Review the Migration

**IMPORTANT**: Always review the generated migration script before applying it!

- Open the newly created file in `migrations/versions/`
- Make sure it correctly captures your changes
- Alembic might miss some changes (especially for indexes, constraints, etc.)
- Add any missing operations manually if needed

### 4. Apply the Migration

After reviewing the migration script, apply it to update the database:

```bash
cd backend
flask db upgrade
```

This command executes the migration script to update the database schema.

### 5. Test the Changes

After applying the migration:
- Run the application
- Test the affected functionality
- Verify that no `OperationalError` exceptions occur

## Common Migration Commands

### Create a Migration

```bash
flask db migrate -m "Description of changes"
```

### Apply Migrations

```bash
flask db upgrade
```

### Rollback to Previous Migration

```bash
flask db downgrade
```

### View Migration History

```bash
flask db history
```

### View Current Migration

```bash
flask db current
```

## Best Practices

1. **Always create migrations for schema changes** - Never modify the database schema manually

2. **One migration per feature** - Group related model changes into a single migration

3. **Descriptive migration messages** - Use clear messages that describe what the migration does

4. **Review migrations before applying** - Alembic might not detect all changes

5. **Test after migration** - Verify that the application works correctly with the new schema

6. **Commit migrations to version control** - Migration scripts should be tracked in git

7. **Coordinate with team members** - Make sure everyone applies migrations when pulling changes

## Troubleshooting

### OperationalError: no such column

If you encounter an error like `OperationalError: no such column: users.theme_color`:

1. Check if you've created and applied a migration for the column
2. Run `flask db migrate` followed by `flask db upgrade`
3. If the issue persists, check if the migration script correctly adds the column

### Migration conflicts

If you get conflicts when multiple developers create migrations:

1. Communicate with your team about schema changes
2. Pull the latest changes before creating new migrations
3. Merge migrations carefully, considering the order of operations

## Need Help?

If you encounter issues with migrations, contact the lead developer or database administrator for assistance.

Remember: **Always run migrations after pulling changes that include model modifications!**
