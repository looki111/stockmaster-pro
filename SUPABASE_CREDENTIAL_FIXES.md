# Supabase Credential Configuration Guide

This guide explains how to properly configure Supabase credentials in the StockMaster Pro application and how to fix common issues.

## Common Issues

### "Supabase credentials not found. Check your meta tags."

This error occurs when the frontend JavaScript cannot find the Supabase URL or API key in the meta tags of the HTML.

### "Invalid API key"

This error occurs when the Supabase API key is not properly formatted or is invalid. Supabase requires a valid JWT token as an API key.

## Solutions

We have provided several scripts to help you fix these issues:

### 1. Fix Environment Variables - `fix_supabase_env.py`

This script updates your `.env` file to ensure that Supabase credentials are properly formatted without line breaks.

```bash
python fix_supabase_env.py
```

### 2. Generate Test Token - `create_test_token.py`

This script creates a test JWT token with the correct format for Supabase. This is useful for testing the frontend when you don't have real Supabase credentials yet.

```bash
python create_test_token.py
```

### 3. Input Your Real Credentials - `generate_supabase_credentials.py`

This script helps you input your real Supabase credentials from your Supabase dashboard and tests their validity.

```bash
python generate_supabase_credentials.py
```

### 4. Test Your Configuration - `/test/supabase`

Visit the `/test/supabase` route in your browser to test your Supabase configuration. This page will show you if your credentials are correctly set up.

## File Changes

We've made the following changes to fix the issues:

1. Updated `base.html` to include meta tags for Supabase URL and key
2. Added scripts to properly load environment variables in the Flask app
3. Created utilities to generate valid JWT tokens
4. Added error handling and debugging information

## How Supabase Authentication Works

1. The Flask application loads Supabase credentials from the `.env` file
2. The Flask app passes these credentials to the frontend via meta tags
3. The frontend JavaScript initializes the Supabase client with these credentials
4. The Supabase client uses the API key to authenticate requests to the Supabase server

## Getting Real Credentials

To get real Supabase credentials:

1. Sign up at [supabase.io](https://supabase.io) 
2. Create a new project
3. Go to Project Settings > API
4. Copy the URL and anon key (public API key)
5. Use these in your `.env` file or run `generate_supabase_credentials.py`

## Troubleshooting

If you're still having issues:

1. Check that your `.env` file has valid credentials without line breaks
2. Ensure your Flask app is loading the environment variables
3. Verify that the meta tags in the HTML have the correct values
4. Check the browser console for specific error messages
5. Use the `/test/supabase` route to diagnose issues
6. Try using the scripts provided to regenerate credentials

For more help, refer to the [Supabase documentation](https://supabase.io/docs). 