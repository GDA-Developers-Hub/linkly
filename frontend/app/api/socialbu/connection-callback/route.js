export async function GET(request) {
  const searchParams = request.nextUrl.searchParams;
  
  // Extract parameters from the request
  const platform = searchParams.get('platform');
  const accountId = searchParams.get('account_id');
  const accountName = searchParams.get('account_name');
  const status = searchParams.get('status') || 'connected';
  const userId = searchParams.get('user_id');
  
  if (!platform || !accountId || !userId) {
    return new Response(
      JSON.stringify({ error: 'Missing required parameters' }),
      { 
        status: 400,
        headers: { 'Content-Type': 'application/json' } 
      }
    );
  }
  
  try {
    // Return success page with JavaScript to close the popup
    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Connection Successful</title>
        <style>
          body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            background-color: #f9fafb;
            color: #111827;
          }
          .success-container {
            text-align: center;
            padding: 2rem;
            background-color: white;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            max-width: 24rem;
          }
          .success-icon {
            color: #10b981;
            font-size: 3rem;
            margin-bottom: 1rem;
          }
          h1 {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
          }
          p {
            color: #6b7280;
            margin-bottom: 1.5rem;
          }
        </style>
      </head>
      <body>
        <div class="success-container">
          <div class="success-icon">✓</div>
          <h1>Connection Successful</h1>
          <p>Your ${platform} account has been connected successfully. This window will close automatically.</p>
        </div>
        <script>
          // Close the popup window after a short delay
          setTimeout(function() {
            window.opener.postMessage({
              type: 'SOCIAL_CONNECTION_SUCCESS',
              platform: '${platform}',
              accountId: '${accountId}',
              accountName: '${accountName || `${platform.charAt(0).toUpperCase() + platform.slice(1)} Account`}'
            }, '*');
            window.close();
          }, 2000);
        </script>
      </body>
      </html>
    `;
    
    return new Response(html, {
      headers: {
        'Content-Type': 'text/html',
      },
    });
  } catch (error) {
    console.error('Error in connection callback:', error);
    return new Response(
      JSON.stringify({ error: 'Failed to process connection callback' }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' } 
      }
    );
  }
} 