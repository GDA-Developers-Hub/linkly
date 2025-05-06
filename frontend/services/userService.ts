import axios from 'axios';
import { User, AddUserRequest, ToggleRoleRequest, UserResponse } from '@/types/user';

// Use a function to ensure the API URL has the correct protocol
const getApiBaseUrl = () => {
  let baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  // Add protocol if missing
  if (!baseUrl.startsWith('http://') && !baseUrl.startsWith('https://')) {
    baseUrl = `https://${baseUrl}`;
  }
  
  console.log(`UserService API URL: ${baseUrl}`);
  return baseUrl;
};

const API_BASE_URL = getApiBaseUrl();

class UserService {
    private async get<T>(endpoint: string): Promise<T> {
        const response = await axios.get<T>(`${API_BASE_URL}/api/users${endpoint}`);
        return response.data;
    }

    private async post<T>(endpoint: string, data?: any): Promise<T> {
        const response = await axios.post<T>(`${API_BASE_URL}/api/users${endpoint}`, data);
        return response.data;
    }

    private async patch<T>(endpoint: string, data: any): Promise<T> {
        const response = await axios.patch<T>(`${API_BASE_URL}/api/users${endpoint}`, data);
        return response.data;
    }

    private async delete<T>(endpoint: string): Promise<T> {
        const response = await axios.delete<T>(`${API_BASE_URL}/api/users${endpoint}`);
        return response.data;
    }

    async getUsers(): Promise<User[]> {
        return this.get<User[]>('/');
    }

    async addUser(email: string): Promise<UserResponse> {
        return this.post<UserResponse>('/', { email });
    }

    async toggleUserRole(userId: number, isManager: boolean): Promise<UserResponse> {
        return this.patch<UserResponse>(`/${userId}/role/`, {
            is_google_ads_manager: isManager,
        });
    }

    async removeUser(userId: number): Promise<UserResponse> {
        return this.delete<UserResponse>(`/${userId}/`);
    }
}

export const userService = new UserService(); 