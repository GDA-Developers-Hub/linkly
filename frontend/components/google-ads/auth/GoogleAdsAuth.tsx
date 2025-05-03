import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle, CheckCircle2 } from 'lucide-react';
import { useRouter } from 'next/router';
import axios from 'axios';

interface GoogleAdsAuthProps {
    onAuthSuccess?: () => void;
}

export const GoogleAdsAuth: React.FC<GoogleAdsAuthProps> = ({ onAuthSuccess }) => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const router = useRouter();

    useEffect(() => {
        // Check if we have a Google Ads account
        const checkAuth = async () => {
            try {
                const response = await axios.get('/api/google-ads/account/');
                setIsAuthenticated(response.data.length > 0);
            } catch (err) {
                setIsAuthenticated(false);
            }
        };

        checkAuth();
    }, []);

    useEffect(() => {
        // Handle OAuth callback
        const { code, state } = router.query;
        if (code && state) {
            handleOAuthCallback();
        }
    }, [router.query]);

    const handleOAuthCallback = async () => {
        try {
            setIsLoading(true);
            const response = await axios.get('/api/google-ads/auth/callback/' + window.location.search);
            setIsAuthenticated(true);
            if (onAuthSuccess) {
                onAuthSuccess();
            }
            // Clean up URL
            router.replace('/dashboard/google-ads', undefined, { shallow: true });
        } catch (err) {
            setError('Failed to complete authentication. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const initiateAuth = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await axios.get('/api/google-ads/auth/init/');
            window.location.href = response.data.authorization_url;
        } catch (err) {
            setError('Failed to initiate authentication. Please try again.');
            setIsLoading(false);
        }
    };

    return (
        <Card className="w-full max-w-2xl mx-auto">
            <CardHeader>
                <CardTitle>Google Ads Authentication</CardTitle>
                <CardDescription>
                    Connect your Google Ads account to access campaign management features
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                {error && (
                    <Alert variant="destructive">
                        <AlertCircle className="h-4 w-4" />
                        <AlertTitle>Error</AlertTitle>
                        <AlertDescription>{error}</AlertDescription>
                    </Alert>
                )}

                {isAuthenticated ? (
                    <Alert>
                        <CheckCircle2 className="h-4 w-4" />
                        <AlertTitle>Connected</AlertTitle>
                        <AlertDescription>
                            Your Google Ads account is connected and ready to use
                        </AlertDescription>
                    </Alert>
                ) : (
                    <Button
                        onClick={initiateAuth}
                        disabled={isLoading}
                        className="w-full"
                    >
                        {isLoading ? 'Connecting...' : 'Connect Google Ads Account'}
                    </Button>
                )}
            </CardContent>
        </Card>
    );
}; 