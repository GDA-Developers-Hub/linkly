import { NextRequest, NextResponse } from 'next/server';

/**
 * API route handler for legacy media uploads
 * This directly connects to the Django backend Cloudinary endpoint
 */
export async function POST(request: NextRequest) {
  try {
    console.log('Legacy upload endpoint called - forwarding directly to Django backend');
    
    // Get the form data from the request
    const formData = await request.formData();
    
    // Get auth token from headers
    const authHeader = request.headers.get('authorization');
    
    // Construct headers for the Django backend request
    const headers: HeadersInit = {};
    
    // Forward authorization header if present
    if (authHeader) {
      headers['Authorization'] = authHeader;
    }
    
    // URL of the Django backend Cloudinary endpoint
    const djangoBackendUrl = 'http://localhost:8000';
    const cloudinaryEndpoint = `${djangoBackendUrl}/api/posts/upload/cloudinary/`;
    
    console.log('Forwarding to Django backend at:', cloudinaryEndpoint);
    
    // Forward the request directly to the Django backend
    const response = await fetch(cloudinaryEndpoint, {
      method: 'POST',
      headers,
      body: formData,
    });
    
    console.log('Django backend response status:', response.status);
    
    // If the Django request fails, log detailed error and return the error
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Django upload failed:', response.status, errorText);
      return NextResponse.json(
        { error: `Upload failed with status: ${response.status}`, details: errorText },
        { status: response.status }
      );
    }
    
    // Parse and return the response from Django
    const data = await response.json();
    console.log('Successfully uploaded to Django backend', data);
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('Error in legacy upload API route:', error);
    return NextResponse.json(
      { error: 'Internal server error during upload', details: String(error) },
      { status: 500 }
    );
  }
}

// Set the maximum content length for file uploads (default: 4MB, adjust as needed)
export const config = {
  api: {
    bodyParser: false,
    responseLimit: '10mb',
  },
};
