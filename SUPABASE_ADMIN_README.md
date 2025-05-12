# Supabase Admin Operations Guide

This guide explains how to perform administrative operations with Supabase in your StockMaster Pro application, particularly setting users as admins.

## Overview of Changes

We've made the following key changes to support Supabase admin operations:

1. Added `SUPABASE_SERVICE_ROLE_KEY` to the environment variables
2. Created separate client initialization functions for regular and admin operations
3. Updated the `set_user_as_admin` function to use the admin client

## Setup Instructions

### 1. Update Your .env File

Your `.env` file should include the following Supabase-related variables:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

To get your service role key:
1. Log in to your Supabase dashboard
2. Go to your project
3. Navigate to Project Settings > API
4. Copy the "service_role key" (not the anon/public key)

> ⚠️ **IMPORTANT**: The service role key has admin privileges and should be kept secret. Never expose it in client-side code.

### 2. Fix Script

We've provided a script to fix your `.env` file:

```
python fix_env_file.py
```

This script:
- Fixes any formatting issues with `SUPABASE_KEY`
- Adds a placeholder `SUPABASE_SERVICE_ROLE_KEY` if it doesn't exist

After running the script, you'll need to manually update the service role key with your actual key from Supabase.

### 3. Testing Admin Functionality

To test setting a user as admin:

```
python test_admin_role.py <user_id>
```

Replace `<user_id>` with the actual user ID from Supabase.

## Code Reference

### Admin Client Initialization

```python
def get_supabase_admin_client() -> Client:
    """
    Get the admin Supabase client instance (using service role key).
    """
    global supabase_admin
    
    if not supabase_admin:
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")
        
        try:
            supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        except Exception as e:
            logger.error(f"Error initializing Supabase admin client: {e}")
            raise
    
    return supabase_admin
```

### Setting a User as Admin

```python
def set_user_as_admin(user_id: str) -> bool:
    """
    Set a user as an admin in Supabase.
    """
    try:
        client = get_supabase_admin_client()  # Use admin client for auth admin operations
        response = client.auth.admin.update_user_by_id(
            user_id,
            user_metadata={},
            app_metadata={"is_admin": True}
        )
        return response.user is not None
    except Exception as e:
        logger.error(f"Error setting user as admin: {e}")
        return False
```

## Troubleshooting

If you encounter issues:

1. Verify that your `.env` file has the correct Supabase keys
2. Run `python check_service_role_key.py` to validate your environment variables
3. Check that your service role key has the "service_role" claim in the JWT payload
4. Ensure you're using the latest version of the supabase-js library
5. Check the console logs for any authentication or authorization errors

## Additional Resources

- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [Managing User Roles in Supabase](https://supabase.com/docs/guides/auth/managing-user-data)
- [Supabase Service Role Security](https://supabase.com/docs/guides/auth/auth-helpers/nextjs#role-based-access-control-rbac) 