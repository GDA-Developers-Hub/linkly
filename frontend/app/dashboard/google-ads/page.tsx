'use client';

import React, { useState, useEffect } from 'react';
import { GoogleAdsAuth } from '@/components/google-ads/auth/GoogleAdsAuth';
import { GoogleAdsOverview } from '@/components/google-ads/dashboard/GoogleAdsOverview';
import { UserManagement } from '@/components/google-ads/dashboard/UserManagement';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card } from '@/components/ui/card';
import axios from 'axios';

export default function GoogleAdsDashboard() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        checkAuthStatus();
    }, []);

    const checkAuthStatus = async () => {
        try {
            const response = await axios.get('/api/google-ads/account/');
            setIsAuthenticated(Array.isArray(response.data) && response.data.length > 0);
        } catch (err) {
            setIsAuthenticated(false);
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (!isAuthenticated) {
        return <GoogleAdsAuth onAuthSuccess={() => setIsAuthenticated(true)} />;
    }

    return (
        <div className="container mx-auto py-6 space-y-6">
            <h1 className="text-3xl font-bold">Google Ads Dashboard</h1>
            
            <Tabs defaultValue="overview" className="w-full">
                <TabsList>
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="users">User Management</TabsTrigger>
                </TabsList>

                <TabsContent value="overview">
                    <Card className="p-6">
                        <GoogleAdsOverview />
                    </Card>
                </TabsContent>

                <TabsContent value="users">
                    <Card className="p-6">
                        <UserManagement
                            users={[]}
                            onAddUser={async () => {}}
                            onToggleRole={async () => {}}
                            onRemoveUser={async () => {}}
                        />
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
} 