import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faFacebook, 
  faLinkedin, 
  faTwitter, 
  faInstagram, 
  faTiktok, 
  faGoogle 
} from '@fortawesome/free-brands-svg-icons';
import { openOAuthPopup, createOAuthURL, processOAuthData } from '../Utils/OAuthUtils';
import Swal from 'sweetalert2';

// Platform-specific configurations
const PLATFORM_CONFIG = {
  facebook: {
    icon: faFacebook,
    color: '#1877F2',
    name: 'Facebook'
  },
  linkedin: {
    icon: faLinkedin,
    color: '#0077B5',
    name: 'LinkedIn'
  },
  twitter: {
    icon: faTwitter,
    color: '#1DA1F2',
    name: 'Twitter'
  },
  instagram: {
    icon: faInstagram,
    color: '#E1306C',
    name: 'Instagram'
  },
  tiktok: {
    icon: faTiktok,
    color: '#000000',
    name: 'TikTok'
  },
  google: {
    icon: faGoogle,
    color: '#DB4437',
    name: 'Google'
  }
};

/**
 * OAuth Login Button Component
 * 
 * @param {Object} props - Component props
 * @param {string} props.platform - Social platform identifier (e.g., 'facebook', 'linkedin')
 * @param {Function} props.onSuccess - Callback function when OAuth succeeds
 * @param {Function} props.onError - Callback function when OAuth fails
 * @param {Function} props.onClick - Custom click handler for advanced initialization
 * @param {Object} props.additionalParams - Additional parameters to include in the OAuth URL
 * @param {string} props.buttonText - Custom button text (defaults to "Connect with [Platform]")
 * @param {Object} props.style - Additional styles for the button
 */
const OAuthLoginButton = ({ 
  platform, 
  onSuccess, 
  onError, 
  onClick,
  additionalParams = {}, 
  buttonText,
  style = {}
}) => {
  const [loading, setLoading] = useState(false);
  
  if (!PLATFORM_CONFIG[platform]) {
    console.error(`Unsupported platform: ${platform}`);
    return null;
  }
  
  const { icon, color, name } = PLATFORM_CONFIG[platform];
  const defaultText = `Connect with ${name}`;
  
  const handleClick = () => {
    // If a custom click handler is provided, use it instead of the default flow
    if (onClick) {
      onClick();
      return;
    }
    
    setLoading(true);
    
    try {
      // Create the OAuth URL
      const authUrl = createOAuthURL(platform, additionalParams);
      
      // Open the popup
      openOAuthPopup(
        authUrl,
        platform,
        (data) => {
          setLoading(false);
          const processedData = processOAuthData(platform, data);
          
          if (processedData.connected) {
            Swal.fire({
              position: 'top-start',
              icon: 'success',
              title: `Connected to ${name}`,
              text: processedData.username ? `Connected as ${processedData.username}` : undefined,
              showConfirmButton: false,
              timer: 2000
            });
          }
          
          if (onSuccess) {
            onSuccess(processedData);
          }
        },
        (error) => {
          setLoading(false);
          
          Swal.fire({
            position: 'top-start',
            icon: 'error',
            title: `Failed to connect to ${name}`,
            text: error.message || 'Please try again later',
            showConfirmButton: false,
            timer: 3000
          });
          
          if (onError) {
            onError(error);
          }
        }
      );
    } catch (error) {
      setLoading(false);
      console.error('Error initiating OAuth flow:', error);
      
      if (onError) {
        onError(error);
      }
    }
  };
  
  return (
    <button
      onClick={handleClick}
      disabled={loading}
      className="oauth-button"
      style={{
        backgroundColor: color,
        color: '#fff',
        border: 'none',
        borderRadius: '4px',
        padding: '10px 20px',
        fontSize: '14px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: loading ? 'wait' : 'pointer',
        opacity: loading ? 0.8 : 1,
        transition: 'all 0.3s ease',
        ...style
      }}
    >
      <FontAwesomeIcon icon={icon} style={{ marginRight: '8px' }} />
      {loading ? 'Connecting...' : (buttonText || defaultText)}
    </button>
  );
};

export default OAuthLoginButton; 