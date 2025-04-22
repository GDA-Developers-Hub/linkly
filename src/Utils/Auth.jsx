import axios from 'axios';
import API_BASE_URL from './BaseUrl';

// Function to check if user is logged in
export const isAuthenticated = () => {
  const token = localStorage.getItem('accessToken');
  return !!token;
};

// Function to get the current user
export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch (e) {
      console.error('Error parsing user data from localStorage', e);
      return null;
    }
  }
  return null;
};

// Function to get access token
export const getAccessToken = () => {
  return localStorage.getItem('accessToken');
};

// Function to get refresh token
export const getRefreshToken = () => {
  return localStorage.getItem('refreshToken');
};

// Function to set auth tokens
export const setAuthTokens = (accessToken, refreshToken, user = null) => {
  console.log('Setting auth tokens:', { accessToken: accessToken?.slice(0, 10) + '...', refreshToken: refreshToken?.slice(0, 10) + '...', hasUser: !!user });
  
  try {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
    
    if (user) {
      localStorage.setItem('user', JSON.stringify(user));
    }
    
    // Set axios default header
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
    
    // Verify tokens were set correctly
    const storedAccessToken = localStorage.getItem('accessToken');
    const storedRefreshToken = localStorage.getItem('refreshToken');
    console.log('Tokens stored in localStorage:', { 
      accessTokenStored: !!storedAccessToken, 
      refreshTokenStored: !!storedRefreshToken,
      accessTokenMatch: storedAccessToken === accessToken
    });
  } catch (error) {
    console.error('Error storing tokens in localStorage:', error);
  }
};

// Function to clear auth tokens and user data (logout)
export const clearAuth = () => {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user');
  
  // Clear axios default header
  delete axios.defaults.headers.common['Authorization'];
};

// Function to refresh access token using refresh token
export const refreshAccessToken = async () => {
  const refreshToken = getRefreshToken();
  
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }
  
  try {
    const response = await axios.post(`${API_BASE_URL}/users/refresh/`, {
      refresh: refreshToken
    });
    
    if (response.data.access) {
      const newAccessToken = response.data.access;
      
      // Update access token in storage and axios headers
      localStorage.setItem('accessToken', newAccessToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
      
      return newAccessToken;
    } else {
      throw new Error('Failed to refresh token');
    }
  } catch (error) {
    console.error('Token refresh failed:', error);
    // If refresh fails, clear auth and redirect to login
    clearAuth();
    window.location.href = '/login';
    throw error;
  }
};

// Initialize axios interceptor for token refresh
export const setupAxiosInterceptors = () => {
  axios.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;
      
      // If error is 401 (Unauthorized) and not already retrying
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        
        try {
          // Try to refresh the token
          await refreshAccessToken();
          
          // Retry the original request with new token
          return axios(originalRequest);
        } catch (refreshError) {
          // If refresh failed, clear auth and redirect to login
          clearAuth();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
      
      return Promise.reject(error);
    }
  );
};

// Function to login user
export const loginUser = async (email, password, twoFactorCode = null) => {
  console.log('Login attempt:', { email, hasPassword: !!password, hasTwoFactorCode: !!twoFactorCode });
  
  try {
    const response = await axios.post(`${API_BASE_URL}/users/login/`, {
      email,
      password,
      ...(twoFactorCode && { two_factor_code: twoFactorCode }),
    });
    
    console.log('Login response received:', { 
      hasAccessToken: !!response.data.access,
      hasRefreshToken: !!response.data.refresh,
      hasUser: !!response.data.user,
      requires2FA: !!response.data.requires_2fa
    });
    
    if (response.data.access) {
      setAuthTokens(
        response.data.access,
        response.data.refresh,
        response.data.user
      );
      return response.data;
    } else if (response.data.requires_2fa) {
      return { requires2FA: true, userId: response.data.user_id };
    }
    
    throw new Error('Login failed: no tokens or 2FA requirement in response');
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

// Initialize axios with auth header on app start
export const initializeAuth = () => {
  const token = getAccessToken();
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }
  
  // Setup token refresh interceptor
  setupAxiosInterceptors();
};

export default {
  isAuthenticated,
  getCurrentUser,
  getAccessToken,
  getRefreshToken,
  setAuthTokens,
  clearAuth,
  refreshAccessToken,
  loginUser,
  initializeAuth
}; 