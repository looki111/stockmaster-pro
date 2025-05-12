<?php
/**
 * StockMaster Pro - PHP Entry Point
 *
 * This file serves as the main entry point for PHP components of the StockMaster Pro application.
 * It loads environment variables and initializes required libraries.
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

// Initialize PHPMailer for email functionality
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\SMTP;
use PHPMailer\PHPMailer\Exception;

/**
 * Generate a JWT token for authentication
 *
 * @param array $userData User data to include in the token
 * @return string The generated JWT token
 */
function generateJWTToken($userData) {
    $issuedAt = time();
    $expirationTime = $issuedAt + (int)getenv('JWT_EXPIRATION');

    $payload = [
        'iat' => $issuedAt,
        'exp' => $expirationTime,
        'data' => $userData
    ];

    return JWT::encode($payload, getenv('JWT_SECRET'), 'HS256');
}

/**
 * Verify a JWT token
 *
 * @param string $token The JWT token to verify
 * @return object|false The decoded token payload or false if invalid
 */
function verifyJWTToken($token) {
    try {
        $decoded = JWT::decode($token, new Key(getenv('JWT_SECRET'), 'HS256'));
        return $decoded;
    } catch (Exception $e) {
        return false;
    }
}

/**
 * Send an email using PHPMailer
 *
 * @param string $to Recipient email address
 * @param string $subject Email subject
 * @param string $body Email body (HTML)
 * @param string $altBody Plain text alternative body
 * @return bool Whether the email was sent successfully
 */
function sendEmail($to, $subject, $body, $altBody = '') {
    $mail = new PHPMailer(true);

    try {
        // Server settings
        $mail->isSMTP();
        $mail->Host = getenv('MAIL_HOST');
        $mail->SMTPAuth = true;
        $mail->Username = getenv('MAIL_USERNAME');
        $mail->Password = getenv('MAIL_PASSWORD');
        $mail->SMTPSecure = getenv('MAIL_ENCRYPTION') ?: PHPMailer::ENCRYPTION_STARTTLS;
        $mail->Port = getenv('MAIL_PORT');

        // Recipients
        $mail->setFrom(getenv('MAIL_FROM_ADDRESS') ?: 'noreply@example.com', getenv('MAIL_FROM_NAME') ?: 'StockMaster Pro');
        $mail->addAddress($to);

        // Content
        $mail->isHTML(true);
        $mail->Subject = $subject;
        $mail->Body = $body;
        $mail->AltBody = $altBody ?: strip_tags($body);

        $mail->send();
        return true;
    } catch (Exception $e) {
        error_log("Email could not be sent. Mailer Error: {$mail->ErrorInfo}");
        return false;
    }
}

// Example usage
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_GET['action'])) {
    header('Content-Type: application/json');

    switch ($_GET['action']) {
        case 'login':
            // Example login endpoint
            $data = json_decode(file_get_contents('php://input'), true);

            // In a real application, validate credentials against a database
            if (isset($data['username']) && isset($data['password'])) {
                // Example user data - in a real app, this would come from a database
                $userData = [
                    'id' => 1,
                    'username' => $data['username'],
                    'role' => 'admin'
                ];

                $token = generateJWTToken($userData);
                echo json_encode(['success' => true, 'token' => $token]);
            } else {
                echo json_encode(['success' => false, 'message' => 'Invalid credentials']);
            }
            break;

        case 'verify':
            // Example token verification endpoint
            $data = json_decode(file_get_contents('php://input'), true);

            if (isset($data['token'])) {
                $decoded = verifyJWTToken($data['token']);

                if ($decoded) {
                    echo json_encode(['success' => true, 'data' => $decoded->data]);
                } else {
                    echo json_encode(['success' => false, 'message' => 'Invalid token']);
                }
            } else {
                echo json_encode(['success' => false, 'message' => 'No token provided']);
            }
            break;

        default:
            echo json_encode(['success' => false, 'message' => 'Unknown action']);
    }

    exit;
}

// If not a POST request or no action specified, display info page
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StockMaster Pro - PHP API</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        h2 {
            color: #3498db;
        }
        code {
            background: #f4f4f4;
            padding: 2px 5px;
            border-radius: 3px;
        }
        pre {
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        .endpoint {
            margin-bottom: 30px;
            border-left: 3px solid #3498db;
            padding-left: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>StockMaster Pro - PHP API</h1>
        <p>This is the PHP component of StockMaster Pro, providing authentication and email services.</p>

        <h2>Available Endpoints</h2>

        <div class="endpoint">
            <h3>Login</h3>
            <p><strong>URL:</strong> <code>index.php?action=login</code></p>
            <p><strong>Method:</strong> POST</p>
            <p><strong>Description:</strong> Authenticates a user and returns a JWT token</p>
            <p><strong>Request Body:</strong></p>
            <pre>{
  "username": "user@example.com",
  "password": "password123"
}</pre>
            <p><strong>Response:</strong></p>
            <pre>{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}</pre>
        </div>

        <div class="endpoint">
            <h3>Verify Token</h3>
            <p><strong>URL:</strong> <code>index.php?action=verify</code></p>
            <p><strong>Method:</strong> POST</p>
            <p><strong>Description:</strong> Verifies a JWT token and returns the user data</p>
            <p><strong>Request Body:</strong></p>
            <pre>{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}</pre>
            <p><strong>Response:</strong></p>
            <pre>{
  "success": true,
  "data": {
    "id": 1,
    "username": "user@example.com",
    "role": "admin"
  }
}</pre>
        </div>
    </div>
</body>
</html>
