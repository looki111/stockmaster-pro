/**
 * Supabase Authentication Client for StockMaster Pro
 * Handles user authentication with Supabase and token validation with Flask backend
 */

// Initialize the client if not already done
function getSupabaseClient() {
  // Check if global client exists
  if (window.supabaseClient) {
    return window.supabaseClient;
  }
  
  // Try to create a client if the global one doesn't exist
  try {
    const supabaseUrl = document.querySelector('meta[name="supabase-url"]')?.content;
    const supabaseKey = document.querySelector('meta[name="supabase-key"]')?.content;
    
    if (!supabaseUrl || !supabaseKey) {
      console.error('Supabase credentials not found in meta tags');
      throw new Error('Supabase credentials not found. Check your meta tags.');
    }
    
    // Create and store the client
    if (window.supabase) {
      const client = window.supabase.createClient(supabaseUrl, supabaseKey);
      window.supabaseClient = client;
      return client;
    } else {
      throw new Error('Supabase SDK not loaded. Make sure the script is included before this one.');
    }
  } catch (error) {
    console.error('Failed to initialize Supabase client:', error);
    throw error;
  }
}

/**
 * Sign in with email and password
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise} - Authentication result
 */
async function loginWithEmail(email, password) {
  try {
    // Get or initialize Supabase client
    const supabaseClient = getSupabaseClient();
    
    // Sign in with Supabase
    const { data, error } = await supabaseClient.auth.signInWithPassword({
      email: email,
      password: password
    });

    if (error) {
      return { success: false, error: error.message };
    }

    // Send token to backend for validation
    return await validateTokenWithBackend(data.session.access_token);
  } catch (error) {
    console.error('Login error:', error);
    return { success: false, error: error.message || 'An error occurred during login' };
  }
}

/**
 * Sign up with email and password
 * @param {string} email - User email
 * @param {string} password - User password
 * @param {object} metadata - Additional user metadata
 * @returns {Promise} - Registration result
 */
async function signUpWithEmail(email, password, metadata = {}) {
  try {
    // Get or initialize Supabase client
    const supabaseClient = getSupabaseClient();
    
    // Sign up with Supabase
    const { data, error } = await supabaseClient.auth.signUp({
      email: email,
      password: password,
      options: {
        data: metadata
      }
    });

    if (error) {
      return { success: false, error: error.message };
    }

    // If email confirmation is required
    if (data.user && data.user.confirmation_sent_at) {
      return { 
        success: true, 
        message: 'Confirmation email sent. Please check your email to complete registration.',
        requiresEmailConfirmation: true
      };
    }

    // If email confirmation not required, validate token with backend
    return await validateTokenWithBackend(data.session.access_token);
  } catch (error) {
    console.error('Signup error:', error);
    return { success: false, error: error.message || 'An error occurred during registration' };
  }
}

/**
 * Sign out the current user
 * @returns {Promise} - Sign out result
 */
async function logout() {
  try {
    // Get or initialize Supabase client
    const supabaseClient = getSupabaseClient();
    
    // Sign out from Supabase
    const { error } = await supabaseClient.auth.signOut();
    
    if (error) {
      return { success: false, error: error.message };
    }

    // Sign out from backend
    const response = await fetch('/auth/logout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const result = await response.json();
    return { success: result.success };
  } catch (error) {
    console.error('Logout error:', error);
    return { success: false, error: error.message || 'An error occurred during logout' };
  }
}

/**
 * Get the current user session
 * @returns {Promise} - Current session
 */
async function getCurrentSession() {
  try {
    // Get or initialize Supabase client
    const supabaseClient = getSupabaseClient();
    
    const { data, error } = await supabaseClient.auth.getSession();
    
    if (error) {
      return { success: false, error: error.message };
    }
    
    return { success: true, session: data.session };
  } catch (error) {
    console.error('Get session error:', error);
    return { success: false, error: error.message || 'An error occurred getting session' };
  }
}

/**
 * Validate token with backend
 * @param {string} token - JWT token from Supabase
 * @returns {Promise} - Token validation result
 */
async function validateTokenWithBackend(token) {
  try {
    console.log('Sending token to backend for validation...');
    
    if (!token) {
      console.error('No token provided for validation');
      return { success: false, error: 'No authentication token provided' };
    }
    
    // Log token format for debugging (only first few chars)
    const tokenPreview = token.substring(0, 10) + '...' + token.substring(token.length - 10);
    console.log(`Token format: ${tokenPreview}`);
    
    // Clear any previous errors from localStorage
    localStorage.removeItem('auth_error');
    
    // Send token to backend for validation
    const response = await fetch('/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ token }),
      credentials: 'include' // Include cookies in the request
    });

    // Check if response is valid
    if (!response.ok) {
      const statusText = response.statusText || 'Unknown error';
      console.error(`Backend validation failed with status ${response.status}: ${statusText}`);
      
      // Try to parse error response
      let errorMessage;
      let errorDetails = '';
      try {
        const errorData = await response.json();
        errorMessage = errorData.error || `Server error: ${response.status}`;
        errorDetails = errorData.details || '';
        
        // Save error to localStorage for debugging
        localStorage.setItem('auth_error', JSON.stringify({
          message: errorMessage,
          details: errorDetails,
          status: response.status,
          timestamp: new Date().toISOString()
        }));
        
        console.error('Error details:', errorDetails);
      } catch (e) {
        errorMessage = `Server error: ${response.status}`;
        console.error('Failed to parse error response:', e);
      }
      
      return { 
        success: false, 
        error: errorMessage,
        details: errorDetails,
        status: response.status
      };
    }

    // Parse success response
    try {
      const result = await response.json();
      console.log('Backend validation response:', result);
      
      if (result.success) {
        // Clear any previous errors
        localStorage.removeItem('auth_error');
        
        // If successful, return user data
        return { 
          success: true, 
          user: result.user,
          redirectUrl: '/dashboard'
        };
      } else {
        // If backend validation failed
        const errorMessage = result.error || 'Token validation failed';
        const errorDetails = result.details || '';
        
        console.error('Token validation failed:', errorMessage);
        
        // Save error for debugging
        localStorage.setItem('auth_error', JSON.stringify({
          message: errorMessage,
          details: errorDetails,
          timestamp: new Date().toISOString()
        }));
        
        return { 
          success: false, 
          error: errorMessage,
          details: errorDetails
        };
      }
    } catch (parseError) {
      console.error('Failed to parse JSON response:', parseError);
      return { 
        success: false, 
        error: 'Failed to parse server response',
        details: parseError.message
      };
    }
  } catch (error) {
    console.error('Token validation error:', error);
    
    // Save error for debugging
    localStorage.setItem('auth_error', JSON.stringify({
      message: error.message || 'Unknown error',
      timestamp: new Date().toISOString()
    }));
    
    return { 
      success: false, 
      error: error.message || 'An error occurred validating token',
      details: error.stack || ''
    };
  }
}

// Expose functions globally
window.SupabaseAuth = {
  loginWithEmail,
  signUpWithEmail,
  logout,
  getCurrentSession,
  validateTokenWithBackend,
  getSupabaseClient
}; 