# Test Supabase Page Script
# This script tests the Supabase test page to verify that the Supabase client is properly initialized

Write-Host "Testing Supabase test page at http://localhost:5000/test/supabase..."
Write-Host ""

try {
    # Make the HTTP request to the test page
    $response = Invoke-WebRequest -Uri "http://localhost:5000/test/supabase" -UseBasicParsing

    # Check if the request was successful
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Successfully retrieved the Supabase test page!"
        
        # Extract meta tags from the HTML content
        $content = $response.Content
        
        # Check for Supabase URL
        if ($content -match 'meta\s+name="supabase-url"\s+content="([^"]+)"') {
            $supabaseUrl = $matches[1]
            Write-Host "✅ Supabase URL found: $supabaseUrl"
        } else {
            Write-Host "❌ Supabase URL meta tag not found in the page!"
        }
        
        # Check for Supabase Key
        if ($content -match 'meta\s+name="supabase-key"\s+content="([^"]+)"') {
            $supabaseKey = $matches[1]
            $maskedKey = if ($supabaseKey.Length -gt 20) {
                $supabaseKey.Substring(0, 10) + "..." + $supabaseKey.Substring($supabaseKey.Length - 10)
            } else {
                "[Key too short to display safely]"
            }
            Write-Host "✅ Supabase Key found: $maskedKey"
        } else {
            Write-Host "❌ Supabase Key meta tag not found in the page!"
        }
        
        Write-Host ""
        Write-Host "To complete the test, visit http://localhost:5000/test/supabase in your browser and click the 'Test Client Initialization' button."
    } else {
        Write-Host "❌ Failed to retrieve the Supabase test page. Status code: $($response.StatusCode)"
    }
} catch {
    Write-Host "❌ Error testing Supabase page: $_"
    
    if ($_.Exception.Message -match "Unable to connect to the remote server") {
        Write-Host ""
        Write-Host "Make sure the Flask application is running. Use the following command in a terminal:"
        Write-Host "python app.py"
    }
} 