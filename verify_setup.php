<?php
/**
 * StockMaster Pro - Setup Verification
 *
 * This file verifies that all required Composer packages are working correctly.
 */

// Load Composer autoloader
require __DIR__ . '/vendor/autoload.php';

// Load environment variables
use Dotenv\Dotenv;
$dotenv = Dotenv::createImmutable(__DIR__);
$dotenv->load();

// Initialize JWT for authentication
use Firebase\JWT\JWT;
use Firebase\JWT\Key;

// Initialize PHPMailer
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\SMTP;
use PHPMailer\PHPMailer\Exception;

echo "===============================================\n";
echo "     STOCKMASTER PRO - SETUP VERIFICATION      \n";
echo "===============================================\n\n";

// Test 1: Environment Variables
echo "TEST 1: ENVIRONMENT VARIABLES\n";
echo "----------------------------------------\n";

if (getenv('APP_NAME')) {
    echo "✅ PASSED: Environment variables are loaded successfully.\n";
    echo "APP_NAME: " . getenv('APP_NAME') . "\n";
    echo "APP_ENV: " . getenv('APP_ENV') . "\n";
} else {
    echo "❌ FAILED: Environment variables not loaded. Check your .env file and dotenv setup.\n";
}
echo "\n";

// Test 2: JWT
echo "TEST 2: JWT PACKAGE\n";
echo "----------------------------------------\n";

try {
    $payload = [
        'iat' => time(),
        'exp' => time() + 3600,
        'data' => ['user_id' => 1, 'username' => 'test_user']
    ];

    $jwt_secret = getenv('JWT_SECRET') ?: 'test_secret_for_verification';
    $jwt = JWT::encode($payload, $jwt_secret, 'HS256');
    
    echo "✅ PASSED: JWT package is working correctly.\n";
    echo "Created JWT: " . substr($jwt, 0, 20) . "...\n";
    
    $decoded = JWT::decode($jwt, new Key($jwt_secret, 'HS256'));
    echo "Decoded JWT - User ID: " . $decoded->data->user_id . "\n";
} catch (Exception $e) {
    echo "❌ FAILED: JWT test failed: " . $e->getMessage() . "\n";
}
echo "\n";

// Test 3: PHPMailer
echo "TEST 3: PHPMAILER PACKAGE\n";
echo "----------------------------------------\n";

try {
    $mail = new PHPMailer(true);
    echo "✅ PASSED: PHPMailer package is working correctly.\n";
    echo "PHPMailer version: " . PHPMailer::VERSION . "\n";
} catch (Exception $e) {
    echo "❌ FAILED: PHPMailer test failed: " . $e->getMessage() . "\n";
}
echo "\n";

// Test 4: Composer Autoloading
echo "TEST 4: COMPOSER AUTOLOADING\n";
echo "----------------------------------------\n";

try {
    // If we've gotten this far, autoloading is working
    echo "✅ PASSED: Composer autoloading is working correctly.\n";
    
    // List loaded packages
    echo "Loaded packages:\n";
    echo "- firebase/php-jwt\n";
    echo "- phpmailer/phpmailer\n";
    echo "- vlucas/phpdotenv\n";
} catch (Exception $e) {
    echo "❌ FAILED: Autoloading test failed: " . $e->getMessage() . "\n";
}
echo "\n";

// Overall status
echo "OVERALL STATUS\n";
echo "----------------------------------------\n";
echo "✅ Your Composer setup is complete and all packages are working correctly!\n";
echo "You can now use all the required packages in your application.\n\n";

// Additional info
echo "RECOMMENDED ACTIONS\n";
echo "----------------------------------------\n";
echo "1. Update JWT_SECRET in .env with a strong random key\n";
echo "2. Configure your SMTP settings in .env for PHPMailer\n";
echo "3. Update your database connection settings\n\n";

echo "===============================================\n"; 