# StockMaster Pro - User Data Fetcher
# This script fetches user data from the /auth/me endpoint

Write-Host "============================================================="
Write-Host "                 StockMaster Pro User Data Fetcher           "
Write-Host "============================================================="
Write-Host ""
Write-Host "This script will fetch your user data from the /auth/me endpoint."
Write-Host ""

# Check if the server is running
try {
    $pingResponse = Invoke-WebRequest -Uri "http://localhost:5000" -Method GET -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Server is running at http://localhost:5000"
} catch {
    Write-Host "❌ Error: Could not connect to the server at http://localhost:5000"
    Write-Host "   Make sure the Flask server is running."
    exit
}

Write-Host ""
Write-Host "Attempting to fetch user data from /auth/me..."

# Try to fetch user data without authentication first
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/auth/me" -Method GET -UseBasicParsing
    $statusCode = $response.StatusCode
    
    if ($statusCode -eq 200) {
        $userData = $response.Content | ConvertFrom-Json
        Write-Host ""
        Write-Host "User Data:"
        Write-Host ($userData | ConvertTo-Json -Depth 10)
    } else {
        Write-Host "Received status code: $statusCode"
        Write-Host $response.Content
    }
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    
    if ($statusCode -eq 401) {
        Write-Host "Authentication required. You need to be logged in."
        
        # Ask if user wants to try with a token
        $useToken = Read-Host "Do you want to try with a token? (y/n)"
        
        if ($useToken -eq "y") {
            $token = Read-Host "Enter your authentication token"
            
            try {
                $headers = @{
                    "Authorization" = "Bearer $token"
                    "Content-Type" = "application/json"
                }
                
                $response = Invoke-WebRequest -Uri "http://localhost:5000/auth/me" -Method GET -Headers $headers -UseBasicParsing
                $statusCode = $response.StatusCode
                
                if ($statusCode -eq 200) {
                    $userData = $response.Content | ConvertFrom-Json
                    Write-Host ""
                    Write-Host "User Data:"
                    Write-Host ($userData | ConvertTo-Json -Depth 10)
                } else {
                    Write-Host "Received status code: $statusCode"
                    Write-Host $response.Content
                }
            } catch {
                Write-Host "❌ Error fetching user data with token: $_"
            }
        }
    } else {
        Write-Host "❌ Error fetching user data: $_"
        
        if ($statusCode -eq 404) {
            Write-Host ""
            Write-Host "The /auth/me endpoint doesn't seem to exist."
            Write-Host "Make sure the endpoint is properly defined in your Flask application."
        }
    }
}

Write-Host ""
Write-Host "============================================================="
Write-Host "For quick access, you can also run this command directly:"
Write-Host "Invoke-WebRequest -Uri 'http://localhost:5000/auth/me' -Method GET -UseBasicParsing | ConvertFrom-Json | ConvertTo-Json -Depth 10"
Write-Host "=============================================================" 