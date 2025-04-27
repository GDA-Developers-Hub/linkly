import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';

/**
 * Telegram Login Widget Component
 * 
 * This component renders the official Telegram Login Widget.
 * https://core.telegram.org/widgets/login
 */
const TelegramLoginWidget = ({ 
  botName, 
  buttonSize = 'large', 
  cornerRadius = 4,
  requestAccess = 'write', 
  showUserPhoto = true,
  onAuth,
  redirectUrl,
  origin
}) => {
  const containerRef = useRef(null);
  
  useEffect(() => {
    // Clean up any existing script
    const existingScript = document.getElementById('telegram-login-script');
    if (existingScript) {
      document.body.removeChild(existingScript);
    }
    
    // Create and append the Telegram login script
    const script = document.createElement('script');
    script.id = 'telegram-login-script';
    script.src = 'https://telegram.org/js/telegram-widget.js?22';
    script.setAttribute('data-telegram-login', botName);
    script.setAttribute('data-size', buttonSize);
    script.setAttribute('data-radius', cornerRadius.toString());
    script.setAttribute('data-request-access', requestAccess);
    script.setAttribute('data-userpic', showUserPhoto.toString());
    
    if (redirectUrl) {
      script.setAttribute('data-auth-url', redirectUrl);
    } else {
      // If no redirect URL, use callback function
      script.setAttribute('data-onauth', 'TelegramLoginCallback');
      
      // Define the global callback function
      window.TelegramLoginCallback = (user) => {
        if (user && onAuth) {
          console.log('Telegram auth successful:', user);
          onAuth(user);
        }
      };
    }
    
    if (origin) {
      script.setAttribute('data-telegram-login-origin', origin);
    }
    
    // Append the script to the container
    if (containerRef.current) {
      containerRef.current.appendChild(script);
    }
    
    // Cleanup
    return () => {
      delete window.TelegramLoginCallback;
      if (existingScript) {
        document.body.removeChild(existingScript);
      }
    };
  }, [botName, buttonSize, cornerRadius, requestAccess, showUserPhoto, onAuth, redirectUrl, origin]);
  
  return <div ref={containerRef} className="telegram-login-widget"></div>;
};

TelegramLoginWidget.propTypes = {
  botName: PropTypes.string.isRequired,
  buttonSize: PropTypes.oneOf(['large', 'medium', 'small']),
  cornerRadius: PropTypes.number,
  requestAccess: PropTypes.oneOf(['write', 'read']),
  showUserPhoto: PropTypes.bool,
  onAuth: PropTypes.func,
  redirectUrl: PropTypes.string,
  origin: PropTypes.string
};

export default TelegramLoginWidget; 