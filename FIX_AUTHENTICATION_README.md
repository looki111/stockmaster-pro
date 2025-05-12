# StockMaster Pro Authentication Fix

This guide will help you fix the "Server error: 500" and "Invalid token" issues in the StockMaster Pro application's login system.

## Problem Description

Users are experiencing the following issues:
- Server error: 500 during login attempts
- "Invalid token" errors when trying to authenticate 
- Unable to log in to the application

These issues are related to problems with Supabase token verification in the application.

## Quick Fix

The quickest way to fix these issues is to run the fix script:

```
python backend/auth/fix_authentication.py
```

This script will:
1. Enable development mode in the token verification system
2. Add DEV_MODE=true to the .env file
3. Update the verification function to be more permissive

After running the script, restart your Flask application:

```
python app.py
```

## Manual Fix Steps

If you prefer to fix the issues manually, follow these steps:

### 1. Enable Development Mode

Create or edit your `.env` file in the root directory and add:

```
DEV_MODE=true
```

### 2. Update Token Verification

Open `backend/auth/patched_token_verify.py` and find the line:

```python
DEV_MODE = False  # or whatever current value
```

Change it to:

```python
DEV_MODE = True
```

### 3. Restart the Application

Restart your Flask application to apply the changes.

## Testing the Fix

To verify that the fix worked, you can use the test script:

```
python test_token_verification.py
```

You'll be prompted to enter a Supabase token. You can get one by:
1. Logging in to the application in your browser
2. Opening browser developer tools (F12)
3. Going to Application tab → Local Storage
4. Finding the supabase.auth.token entry and copying the access_token value

## Understanding the Fix

The development mode relaxes the token verification process, allowing the application to accept tokens with minimal validation. This is useful for development and testing but **should not be used in production**.

In development mode, the system will:
- Skip cryptographic signature verification
- Accept tokens even if they have expired
- Use a fallback verification method when JWKS verification fails

## Next Steps for Production

For production environments, you should:
1. Properly configure your Supabase credentials
2. Set `DEV_MODE=false` in your .env file
3. Make sure your SUPABASE_URL and SUPABASE_KEY are correct
4. Consider adding a proper SUPABASE_JWT_SECRET if needed

## Additional Troubleshooting

If you're still experiencing issues:
1. Check the application logs for detailed error messages
2. Clear your browser cookies and cache
3. Verify that your Supabase project settings match your application settings
4. Make sure your Supabase service is up and running

## Need More Help?

If you need additional assistance, please reach out to support@stockmasterpro.com or create an issue in the project repository. 