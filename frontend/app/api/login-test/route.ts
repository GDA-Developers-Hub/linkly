import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { email, password } = body;
    
    if (!email || !password) {
      return NextResponse.json({
        status: 'error',
        message: 'Email and password are required'
      }, { status: 400 });
    }
    
    // Use Next.js routing for testing instead of direct Django URL
    // This will go through our rewrite layer
    const loginUrl = '/api/users/login/';
    console.log(`Testing login with credentials via frontend proxy to: ${loginUrl}`);
    
    // Make the request through our frontend proxy
    const response = await fetch(loginUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });
    
    // We'll always return the response regardless of status
    const contentType = response.headers.get('content-type');
    let data;
    
    // Try to parse as JSON or text depending on content type
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = { text: await response.text() };
    }
    
    return NextResponse.json({
      status: response.ok ? 'success' : 'error',
      statusCode: response.status,
      statusText: response.statusText,
      headers: Object.fromEntries(response.headers.entries()),
      data,
    }, { status: response.ok ? 200 : 502 });
  } catch (error) {
    console.error('Error in login test:', error);
    return NextResponse.json({
      status: 'error',
      message: (error as Error).message,
    }, { status: 500 });
  }
} 