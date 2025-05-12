/**
 * Supabase Client Initialization Script
 * This ensures the Supabase client is properly initialized before any other scripts run
 */

// Initialize supabase client immediately, not waiting for DOM load
(function() {
  try {
    console.log('[Supabase Init] Initialization starting...');
    
    // Create a backup initialization function for when DOM is ready
    window.initSupabase = function() {
      try {
        console.log('[Supabase Init] DOM ready initialization starting');
        
        // Get Supabase credentials from meta tags
        const supabaseUrl = document.querySelector('meta[name="supabase-url"]')?.content;
        const supabaseKey = document.querySelector('meta[name="supabase-key"]')?.content;
        
        if (!supabaseUrl || !supabaseKey) {
          console.error('[Supabase Init] Supabase URL or API key not found in meta tags');
          console.log('[Supabase Init] Meta tags available:', 
            Array.from(document.querySelectorAll('meta')).map(el => el.name).filter(Boolean).join(', '));
          
          // Display error message on the page if we're on login/register
          const loginError = document.getElementById('login-error');
          const errorMessage = document.getElementById('error-message');
          if (loginError && errorMessage) {
            errorMessage.textContent = 'Missing Supabase configuration. Please contact the administrator.';
            loginError.style.display = 'flex';
          }
          return false;
        }
        
        // Log credentials format (without exposing full key)
        console.log(`[Supabase Init] URL format: ${supabaseUrl}`);
        console.log(`[Supabase Init] Key format: ${supabaseKey.substring(0, 10)}...${supabaseKey.substring(supabaseKey.length - 5)}`);
        
        // Validate the URL format
        if (!supabaseUrl.match(/^https:\/\/[a-zA-Z0-9-]+\.supabase\.co$/)) {
          console.error('[Supabase Init] Invalid Supabase URL format:', supabaseUrl);
          
          // Display error message on the page if we're on login/register
          const loginError = document.getElementById('login-error');
          const errorMessage = document.getElementById('error-message');
          if (loginError && errorMessage) {
            errorMessage.textContent = 'Invalid Supabase URL format. Please check your configuration.';
            loginError.style.display = 'flex';
          }
          return false;
        }
        
        // Initialize the client with detected credentials
        console.log('[Supabase Init] Initializing Supabase client with credentials from meta tags');
        try {
          window.supabaseClient = window.supabase.createClient(supabaseUrl, supabaseKey);
          console.log('[Supabase Init] Client initialized successfully!');
          
          // Test the connection by getting the auth user (will be null if not logged in)
          window.supabaseClient.auth.getUser()
            .then(response => {
              if (response.error) {
                console.warn('[Supabase Init] Auth test warning:', response.error.message);
              } else {
                console.log('[Supabase Init] Auth connection test successful');
              }
            })
            .catch(err => {
              console.warn('[Supabase Init] Auth test error:', err.message);
            });
            
          return true;
        } catch (initError) {
          console.error('[Supabase Init] Client initialization error:', initError);
          return false;
        }
      } catch (error) {
        console.error('[Supabase Init] Error during DOM init:', error);
        return false;
      }
    };
    
    // Check if supabase SDK is available
    if (typeof window.supabase === 'undefined') {
      console.warn('[Supabase Init] Supabase SDK not found. Waiting for it to load...');
      
      // Set up a check to initialize once the SDK is loaded
      let checkCount = 0;
      const checkInterval = setInterval(function() {
        checkCount++;
        if (typeof window.supabase !== 'undefined') {
          console.log('[Supabase Init] Supabase SDK found after waiting');
          clearInterval(checkInterval);
          
          // Initialize with meta tags if available, otherwise wait for DOM
          const supabaseUrl = document.querySelector('meta[name="supabase-url"]')?.content;
          const supabaseKey = document.querySelector('meta[name="supabase-key"]')?.content;
          
          if (supabaseUrl && supabaseKey) {
            window.supabaseClient = window.supabase.createClient(supabaseUrl, supabaseKey);
            console.log('[Supabase Init] Created client with meta tag values');
          } else {
            console.log('[Supabase Init] Meta tags not available yet, waiting for DOM');
            document.addEventListener('DOMContentLoaded', window.initSupabase);
          }
        } else if (checkCount > 10) {
          clearInterval(checkInterval);
          console.error('[Supabase Init] Supabase SDK not found after multiple attempts');
          
          // Display error on DOM load if we're on a login page
          document.addEventListener('DOMContentLoaded', function() {
            const loginError = document.getElementById('login-error');
            const errorMessage = document.getElementById('error-message');
            if (loginError && errorMessage) {
              errorMessage.textContent = 'Could not load Supabase SDK. Please check your internet connection.';
              loginError.style.display = 'flex';
            }
          });
        }
      }, 100);
    } else {
      // Supabase is already available
      console.log('[Supabase Init] Supabase SDK already loaded');
      const supabaseUrl = document.querySelector('meta[name="supabase-url"]')?.content;
      const supabaseKey = document.querySelector('meta[name="supabase-key"]')?.content;
      
      if (supabaseUrl && supabaseKey) {
        try {
          window.supabaseClient = window.supabase.createClient(supabaseUrl, supabaseKey);
          console.log('[Supabase Init] Created client with meta tag values');
        } catch (e) {
          console.error('[Supabase Init] Error creating client:', e);
        }
      } else {
        console.log('[Supabase Init] Meta tags not available yet, waiting for DOM');
        document.addEventListener('DOMContentLoaded', window.initSupabase);
      }
      
      // Set up auth state change listener when DOM is ready
      document.addEventListener('DOMContentLoaded', function() {
        if (!window.supabaseClient) {
          window.initSupabase();
        }
        
        // Set up auth state change listener
        if (window.supabaseClient) {
          window.supabaseClient.auth.onAuthStateChange((event, session) => {
            if (event === 'SIGNED_IN') {
              console.log('[Supabase Auth] User signed in');
            } else if (event === 'SIGNED_OUT') {
              console.log('[Supabase Auth] User signed out');
            }
          });
        }
      });
    }
    
    console.log('[Supabase Init] Initialization script completed');
  } catch (error) {
    console.error('[Supabase Init] Critical initialization error:', error);
    
    // Display error on DOM load if we're on a login page
    document.addEventListener('DOMContentLoaded', function() {
      const loginError = document.getElementById('login-error');
      const errorMessage = document.getElementById('error-message');
      if (loginError && errorMessage) {
        errorMessage.textContent = 'Failed to initialize Supabase: ' + error.message;
        loginError.style.display = 'flex';
      }
    });
  }
})(); 