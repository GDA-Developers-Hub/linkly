import React, { useEffect, useRef } from 'react';
import { useDispatch } from 'react-redux';
import axios from 'axios';
import { API_ENDPOINTS } from '../../constants/endpoints';
import { showNotification } from '../../redux/actions/uiActions';
import './SocialAuth.css';

const TelegramLogin = ({ onSuccess, onError, botName = 'LinklyApp_bot' }) => {
  const containerRef = useRef(null);
  const dispatch = useDispatch();

  useEffect(() => {
    // Create script element for Telegram Login Widget
    const script = document.createElement('script');
    script.src = 'https://telegram.org/js/telegram-widget.js?21';
    script.async = true;
    script.setAttribute('data-telegram-login', botName);
    script.setAttribute('data-size', 'large');
    script.setAttribute('data-radius', '8');
    script.setAttribute('data-request-access', 'write');
    script.setAttribute('data-userpic', 'false');
    script.setAttribute('data-onauth', 'onTelegramAuth(user)');
    
    // Cleanup any existing scripts
    if (containerRef.current) {
      containerRef.current.innerHTML = '';
      containerRef.current.appendChild(script);
    }

    // Define global callback function for Telegram widget
    window.onTelegramAuth = (user) => {
      handleTelegramAuth(user);
    };

    return () => {
      // Cleanup
      delete window.onTelegramAuth;
    };
  }, [botName]);

  const handleTelegramAuth = async (userData) => {
    try {
      // Send auth data to backend
      const response = await axios.post(API_ENDPOINTS.TELEGRAM_CALLBACK, userData);
      
      if (response.data.success) {
        dispatch(showNotification({
          type: 'success',
          message: 'Telegram account connected successfully!',
          position: 'top-left'
        }));
        
        if (onSuccess) {
          onSuccess(response.data);
        }
      }
    } catch (error) {
      console.error('Telegram auth error:', error);
      const errorMessage = error.response?.data?.error || 'Failed to connect Telegram account';
      
      dispatch(showNotification({
        type: 'error',
        message: errorMessage,
        position: 'top-left'
      }));
      
      if (onError) {
        onError(errorMessage);
      }
    }
  };

  return (
    <div className="telegram-login-container">
      <div ref={containerRef} className="telegram-login-widget"></div>
    </div>
  );
};

export default TelegramLogin; 