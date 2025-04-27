import { NextResponse } from 'next/server';

// Create a simple route to test if Next.js API routes are working
export async function GET() {
  return NextResponse.json({
    status: 'ok',
    time: new Date().toISOString(),
    message: 'Next.js API route is working'
  });
}

// Create a route to test the Django API connection
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { endpoint } = body;
    
    if (!endpoint) {
      return NextResponse.json({
        status: 'error',
        message: 'No endpoint provided'
      }, { status: 400 });
    }
    
    const url = `http://localhost:8000/api/${endpoint.replace(/^\/+/, '')}`;
    console.log(`Attempting to connect to Django at: ${url}`);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (response.ok) {
      const data = await response.json();
      return NextResponse.json({
        status: 'success',
        djangoStatus: response.status,
        data
      });
    } else {
      return NextResponse.json({
        status: 'error',
        djangoStatus: response.status,
        djangoStatusText: response.statusText,
        message: `Django API returned ${response.status} ${response.statusText}`
      }, { status: 502 });
    }
  } catch (error) {
    console.error('Error connecting to Django:', error);
    return NextResponse.json({
      status: 'error',
      message: (error as Error).message
    }, { status: 500 });
  }
} 