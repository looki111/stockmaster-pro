<?php
/**
 * StockMaster Pro - Test File
 *
 * This file tests the PHP components of the StockMaster Pro application.
 */

// Load Composer autoloader
require __DIR__ . '/vendor/autoload.php';

// Load environment variables
use Dotenv\Dotenv;

// Debug information
echo "Current directory: " . __DIR__ . "\n";
echo "Checking if .env file exists: " . (file_exists(__DIR__ . '/.env') ? 'Yes' : 'No') . "\n";
if (file_exists(__DIR__ . '/.env')) {
    echo "Contents of .env file:\n";
    echo file_get_contents(__DIR__ . '/.env') . "\n";
}

try {
    $dotenv = Dotenv::createImmutable(__DIR__);
    $dotenv->load();
    echo "Environment variables loaded successfully.\n";

    // Check if variables are accessible through different methods
    echo "Checking variable access methods:\n";
    echo "APP_NAME via \$_ENV: " . (isset($_ENV['APP_NAME']) ? $_ENV['APP_NAME'] : 'Not set') . "\n";
    echo "APP_NAME via getenv(): " . (getenv('APP_NAME') ?: 'Not set') . "\n";
    echo "APP_NAME via \$_SERVER: " . (isset($_SERVER['APP_NAME']) ? $_SERVER['APP_NAME'] : 'Not set') . "\n";

    // Make sure variables are accessible through $_ENV
    $dotenv->safeLoad();
    $dotenv->required(['APP_NAME', 'JWT_SECRET'])->notEmpty();
} catch (Exception $e) {
    echo "Error loading environment variables: " . $e->getMessage() . "\n";
}

// Test JWT functionality
use Firebase\JWT\JWT;
use Firebase\JWT\Key;

// Test PHPMailer
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\SMTP;
use PHPMailer\PHPMailer\Exception;

echo "=== StockMaster Pro PHP Components Test ===\n\n";

// Test environment variables
echo "Testing environment variables:\n";
echo "APP_NAME: " . (getenv('APP_NAME') ?: 'Not set') . "\n";
echo "APP_ENV: " . (getenv('APP_ENV') ?: 'Not set') . "\n";
echo "JWT_SECRET: " . (getenv('JWT_SECRET') ? 'Set (hidden)' : 'Not set') . "\n\n";

// Test JWT functionality
echo "Testing JWT functionality:\n";
try {
    $payload = [
        'iat' => time(),
        'exp' => time() + 3600,
        'data' => ['user_id' => 1, 'username' => 'test_user']
    ];

    $jwt_secret = getenv('JWT_SECRET');
    if (!$jwt_secret) {
        throw new Exception("JWT_SECRET environment variable is not set");
    }

    $jwt = JWT::encode($payload, $jwt_secret, 'HS256');
    echo "JWT created successfully: " . substr($jwt, 0, 20) . "...\n";

    $decoded = JWT::decode($jwt, new Key($jwt_secret, 'HS256'));
    echo "JWT decoded successfully. User ID: " . $decoded->data->user_id . "\n";
    echo "JWT test passed.\n\n";
} catch (Exception $e) {
    echo "JWT test failed: " . $e->getMessage() . "\n\n";
}

// Test PHPMailer (configuration only, don't actually send)
echo "Testing PHPMailer configuration:\n";
try {
    $mail = new PHPMailer(true);
    $mail->isSMTP();
    $mail->Host = getenv('MAIL_HOST') ?: 'smtp.example.com';
    $mail->SMTPAuth = true;
    $mail->Username = getenv('MAIL_USERNAME') ?: 'test@example.com';
    $mail->Password = getenv('MAIL_PASSWORD') ?: 'password';
    $mail->SMTPSecure = getenv('MAIL_ENCRYPTION') ?: PHPMailer::ENCRYPTION_STARTTLS;
    $mail->Port = getenv('MAIL_PORT') ?: 587;

    echo "PHPMailer configured successfully with the following settings:\n";
    echo "  Host: " . $mail->Host . "\n";
    echo "  Port: " . $mail->Port . "\n";
    echo "  Username: " . (empty($mail->Username) || $mail->Username === 'null' ? 'Not set' : substr($mail->Username, 0, 3) . '...') . "\n";
    echo "  SMTPSecure: " . $mail->SMTPSecure . "\n";
    echo "PHPMailer test passed.\n\n";
} catch (Exception $e) {
    echo "PHPMailer test failed: " . $e->getMessage() . "\n\n";
}

echo "All tests completed.\n";
