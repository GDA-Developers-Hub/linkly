export interface User {
    id: number;
    username: string;
    email: string;
    is_active: boolean;
    is_google_ads_manager: boolean;
    last_login?: string;
}

export interface AddUserRequest {
    email: string;
}

export interface ToggleRoleRequest {
    is_google_ads_manager: boolean;
}

export interface UserResponse {
    success: boolean;
    message: string;
    user?: User;
} 