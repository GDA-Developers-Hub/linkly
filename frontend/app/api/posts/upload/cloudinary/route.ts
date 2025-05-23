import { NextRequest, NextResponse } from 'next/server';

/**
 * API route handler for Cloudinary media uploads
 * This forwards the request to the Django backend's Cloudinary upload endpoint
 */
export async function POST(request: NextRequest) {
  try {
    // Get the form data from the request
    const formData = await request.formData();
    
    // Get auth token from headers
    const authHeader = request.headers.get('authorization');
    
    // Construct headers for the backend request
    const headers: HeadersInit = {};
    
    // Forward authorization header if present
    if (authHeader) {
      headers['Authorization'] = authHeader;
    }
    
    // URL of your Django backend's Cloudinary upload endpoint
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const cloudinaryEndpoint = `${backendUrl}/api/posts/upload/cloudinary/`;
    
    // Forward the request to the Django backend
    const response = await fetch(cloudinaryEndpoint, {
      method: 'POST',
      headers,
      body: formData,
      credentials: 'include',
    });
    
    // If the backend request fails, return the error
    if (!response.ok) {
      console.error('Backend upload failed:', response.status, response.statusText);
      return NextResponse.json(
        { error: `Upload failed with status: ${response.status}` },
        { status: response.status }
      );
    }
    
    // Parse and return the response from the backend
    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('Error in Cloudinary upload API route:', error);
    return NextResponse.json(
      { error: 'Internal server error during upload' },
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
