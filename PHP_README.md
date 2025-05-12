# StockMaster Pro - PHP Components

This directory contains the PHP components of the StockMaster Pro application, which provide authentication, email functionality, and API endpoints.

## Dependencies

The project uses the following PHP dependencies managed by Composer:

- **firebase/php-jwt**: For JWT-based authentication
- **phpmailer/phpmailer**: For sending emails
- **vlucas/phpdotenv**: For loading environment variables from .env file

## Setup

1. Make sure you have PHP and Composer installed
2. Run `composer install` to install dependencies
3. Create a `.env` file with the required configuration (see below)
4. Test the setup by running `php test.php`

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
APP_NAME="StockMaster Pro"
APP_ENV=development
APP_DEBUG=true
APP_URL=http://localhost

DB_CONNECTION=sqlite
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=stockmaster.db
DB_USERNAME=root
DB_PASSWORD=

JWT_SECRET=your_jwt_secret_key_here
JWT_EXPIRATION=3600

MAIL_DRIVER=smtp
MAIL_HOST=smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=null
MAIL_PASSWORD=null
MAIL_ENCRYPTION=null
MAIL_FROM_ADDRESS=null
MAIL_FROM_NAME="StockMaster Pro"
```

Make sure to replace the placeholder values with your actual configuration.

## Files

- **index.php**: Main entry point for PHP components, includes authentication and email functionality
- **api.php**: API endpoints for the application
- **test.php**: Test script to verify the setup

## Usage

### Authentication

The application uses JWT for authentication. To generate a token:

```php
require __DIR__ . '/vendor/autoload.php';

use Dotenv\Dotenv;
$dotenv = Dotenv::createImmutable(__DIR__);
$dotenv->load();

use Firebase\JWT\JWT;

$userData = [
    'id' => 1,
    'username' => 'user@example.com',
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
```

To verify a token:

```php
use Firebase\JWT\JWT;
use Firebase\JWT\Key;

try {
    $decoded = JWT::decode($token, new Key(getenv('JWT_SECRET'), 'HS256'));
    // Token is valid, $decoded->data contains the user data
} catch (Exception $e) {
    // Token is invalid
}
```

### Sending Emails

The application uses PHPMailer for sending emails:

```php
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\SMTP;
use PHPMailer\PHPMailer\Exception;

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
```

## API Endpoints

The application provides the following API endpoints:

- **POST /api.php?path=auth/login**: Authenticate a user and return a JWT token
- **GET /api.php?path=user/profile**: Get the authenticated user's profile
- **GET /api.php?path=inventory/products**: Get a list of products

## Integration with Python Flask

This PHP component is designed to work alongside the Python Flask application in the StockMaster Pro project. The PHP components handle authentication and email functionality, while the Flask application handles the main business logic.

## Security Considerations

- Make sure to keep your JWT secret key secure
- Store sensitive information in the .env file and ensure it's not committed to version control
- Use HTTPS in production to protect data in transit
- Implement proper input validation and sanitization
- Use prepared statements for database queries to prevent SQL injection
