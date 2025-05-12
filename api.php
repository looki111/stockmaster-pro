<?php
/**
 * StockMaster Pro - API Endpoints
 *
 * This file provides API endpoints for the StockMaster Pro application.
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

// Set response content type to JSON
header('Content-Type: application/json');

/**
 * Authenticate the request using JWT
 *
 * @return object|false The decoded token payload or false if authentication fails
 */
function authenticateRequest() {
    $headers = getallheaders();

    if (!isset($headers['Authorization'])) {
        return false;
    }

    $authHeader = $headers['Authorization'];
    $token = str_replace('Bearer ', '', $authHeader);

    try {
        $decoded = JWT::decode($token, new Key(getenv('JWT_SECRET'), 'HS256'));
        return $decoded;
    } catch (Exception $e) {
        return false;
    }
}

/**
 * Send a JSON response
 *
 * @param array $data The data to send
 * @param int $statusCode HTTP status code
 */
function sendResponse($data, $statusCode = 200) {
    http_response_code($statusCode);
    echo json_encode($data);
    exit;
}

// Get the request method and path
$method = $_SERVER['REQUEST_METHOD'];
$path = isset($_GET['path']) ? $_GET['path'] : '';

// API routes
switch ($path) {
    case 'auth/login':
        if ($method !== 'POST') {
            sendResponse(['error' => 'Method not allowed'], 405);
        }

        $data = json_decode(file_get_contents('php://input'), true);

        if (!isset($data['username']) || !isset($data['password'])) {
            sendResponse(['error' => 'Username and password are required'], 400);
        }

        // In a real application, validate credentials against a database
        // For this example, we'll accept any credentials
        $userData = [
            'id' => 1,
            'username' => $data['username'],
            'role' => 'admin'
        ];

        $issuedAt = time();
        $expirationTime = $issuedAt + (int)getenv('JWT_EXPIRATION');

        $payload = [
            'iat' => $issuedAt,
            'exp' => $expirationTime,
            'data' => $userData
        ];

        $token = JWT::encode($payload, getenv('JWT_SECRET'), 'HS256');

        sendResponse([
            'success' => true,
            'token' => $token,
            'expires' => $expirationTime,
            'user' => $userData
        ]);
        break;

    case 'user/profile':
        if ($method !== 'GET') {
            sendResponse(['error' => 'Method not allowed'], 405);
        }

        $auth = authenticateRequest();

        if (!$auth) {
            sendResponse(['error' => 'Unauthorized'], 401);
        }

        // In a real application, fetch user profile from database
        sendResponse([
            'success' => true,
            'profile' => [
                'id' => $auth->data->id,
                'username' => $auth->data->username,
                'role' => $auth->data->role,
                'name' => 'John Doe',
                'email' => 'john.doe@example.com'
            ]
        ]);
        break;

    case 'inventory/products':
        if ($method !== 'GET') {
            sendResponse(['error' => 'Method not allowed'], 405);
        }

        $auth = authenticateRequest();

        if (!$auth) {
            sendResponse(['error' => 'Unauthorized'], 401);
        }

        // In a real application, fetch products from database
        sendResponse([
            'success' => true,
            'products' => [
                [
                    'id' => 1,
                    'name' => 'Espresso',
                    'price' => 2.50,
                    'stock' => 100
                ],
                [
                    'id' => 2,
                    'name' => 'Cappuccino',
                    'price' => 3.50,
                    'stock' => 80
                ],
                [
                    'id' => 3,
                    'name' => 'Latte',
                    'price' => 4.00,
                    'stock' => 75
                ]
            ]
        ]);
        break;

    default:
        sendResponse(['error' => 'Endpoint not found'], 404);
}
