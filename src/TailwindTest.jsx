import React from 'react';
import API_BASE_URL from './Utils/BaseUrl';

function TailwindTest() {
  const testApi = async () => {
    try {
      // Test a simple GET endpoint first
      console.log('Testing API GET request...');
      const response = await fetch(`${API_BASE_URL}/users/subscription/plans/`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      });
      
      const contentType = response.headers.get('content-type');
      console.log('Response content type:', contentType);
      console.log('Response status:', response.status);
      
      if (contentType && contentType.includes('application/json')) {
        const data = await response.json();
        console.log('API test response:', data);
        alert('API test successful! Check console for details.');
      } else {
        const text = await response.text();
        console.error('Non-JSON response:', text.substring(0, 500));
        alert('API test failed: received HTML instead of JSON. Check console for details.');
      }
    } catch (error) {
      console.error('API test error:', error);
      alert(`API test failed: ${error.message}`);
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-indigo-100 flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-lg overflow-hidden p-8">
        <h1 className="text-2xl font-bold text-center text-indigo-600 mb-6">
          Tailwind CSS Test Page
        </h1>
        
        <div className="space-y-4">
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg text-blue-700">
            This page tests that Tailwind CSS is working properly.
          </div>
          
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-red-100 p-4 rounded-lg text-red-700 text-center">Red</div>
            <div className="bg-green-100 p-4 rounded-lg text-green-700 text-center">Green</div>
            <div className="bg-blue-100 p-4 rounded-lg text-blue-700 text-center">Blue</div>
          </div>
          
          <button 
            onClick={testApi}
            className="w-full py-2 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors"
          >
            Test API Connection
          </button>
        </div>
      </div>
    </div>
  );
}

export default TailwindTest; 