'use client';

import React, { useEffect, useState } from 'react';
import { googleAdsService } from '@/services/googleAdsService';
import { userService } from '@/services/userService';
import { PerformanceMetrics } from '@/components/google-ads/dashboard/PerformanceMetrics';
import { CampaignsList } from '@/components/google-ads/dashboard/CampaignsList';
import { KeywordPerformance } from '@/components/google-ads/dashboard/KeywordPerformance';
import { UserManagement } from '@/components/google-ads/dashboard/UserManagement';
import { Campaign, PerformanceSummary, KeywordMetrics } from '@/types/google-ads';
import { User } from '@/types/user';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';

export default function GoogleAdsPage() {
    const [campaigns, setCampaigns] = useState<Campaign[]>([]);
    const [performanceSummary, setPerformanceSummary] = useState<PerformanceSummary>({
        total_impressions: 0,
        total_clicks: 0,
        total_cost: 0,
        total_conversions: 0,
    });
    const [keywords, setKeywords] = useState<KeywordMetrics[]>([]);
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState({
        campaigns: true,
        performance: true,
        keywords: true,
        users: true,
    });
    const [selectedDays, setSelectedDays] = useState(30);
    const [activeTab, setActiveTab] = useState('overview');
    const { toast } = useToast();

    const fetchData = async () => {
        try {
            // Fetch campaigns
            setLoading((prev) => ({ ...prev, campaigns: true }));
            const campaignsData = await googleAdsService.getCampaigns();
            setCampaigns(campaignsData);
            setLoading((prev) => ({ ...prev, campaigns: false }));

            // Fetch performance summary
            setLoading((prev) => ({ ...prev, performance: true }));
            const summaryData = await googleAdsService.getPerformanceSummary(selectedDays);
            setPerformanceSummary(summaryData);
            setLoading((prev) => ({ ...prev, performance: false }));

            // Fetch keywords
            setLoading((prev) => ({ ...prev, keywords: true }));
            const keywordsData = await googleAdsService.getKeywordMetrics(selectedDays);
            setKeywords(keywordsData);
            setLoading((prev) => ({ ...prev, keywords: false }));

            // Fetch users
            setLoading((prev) => ({ ...prev, users: true }));
            const usersData = await userService.getUsers();
            setUsers(usersData);
            setLoading((prev) => ({ ...prev, users: false }));
        } catch (error) {
            console.error('Error fetching data:', error);
            toast({
                title: 'Error',
                description: 'Failed to fetch data. Please try again later.',
                variant: 'destructive',
            });
        }
    };

    useEffect(() => {
        fetchData();
    }, [selectedDays]);

    const handleCampaignSync = async (campaignId: string) => {
        try {
            await googleAdsService.syncCampaign(campaignId);
            toast({
                title: 'Success',
                description: 'Campaign data synchronized successfully.',
            });
            fetchData();
        } catch (error) {
            console.error('Error syncing campaign:', error);
            toast({
                title: 'Error',
                description: 'Failed to sync campaign data. Please try again later.',
                variant: 'destructive',
            });
        }
    };

    const handleCampaignSelect = (campaign: Campaign) => {
        // Navigate to campaign details page or open modal
        console.log('Selected campaign:', campaign);
    };

    const handleAddUser = async (email: string) => {
        try {
            const response = await userService.addUser(email);
            if (response.success) {
                toast({
                    title: 'Success',
                    description: 'User added successfully.',
                });
                fetchData();
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            console.error('Error adding user:', error);
            toast({
                title: 'Error',
                description: 'Failed to add user. Please try again later.',
                variant: 'destructive',
            });
        }
    };

    const handleToggleRole = async (userId: number, isManager: boolean) => {
        try {
            const response = await userService.toggleUserRole(userId, isManager);
            if (response.success) {
                toast({
                    title: 'Success',
                    description: `User role ${isManager ? 'granted' : 'revoked'} successfully.`,
                });
                fetchData();
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            console.error('Error toggling user role:', error);
            toast({
                title: 'Error',
                description: 'Failed to update user role. Please try again later.',
                variant: 'destructive',
            });
        }
    };

    const handleRemoveUser = async (userId: number) => {
        try {
            const response = await userService.removeUser(userId);
            if (response.success) {
                toast({
                    title: 'Success',
                    description: 'User removed successfully.',
                });
                fetchData();
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            console.error('Error removing user:', error);
            toast({
                title: 'Error',
                description: 'Failed to remove user. Please try again later.',
                variant: 'destructive',
            });
        }
    };

    return (
        <div className="container mx-auto py-6 space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold">Google Ads Dashboard</h1>
                <div className="flex items-center gap-4">
                    <Tabs
                        value={selectedDays.toString()}
                        onValueChange={(value) => setSelectedDays(parseInt(value))}
                    >
                        <TabsList>
                            <TabsTrigger value="7">7 Days</TabsTrigger>
                            <TabsTrigger value="30">30 Days</TabsTrigger>
                            <TabsTrigger value="90">90 Days</TabsTrigger>
                        </TabsList>
                    </Tabs>
                    <Tabs value={activeTab} onValueChange={setActiveTab}>
                        <TabsList>
                            <TabsTrigger value="overview">Overview</TabsTrigger>
                            <TabsTrigger value="users">Users</TabsTrigger>
                        </TabsList>
                    </Tabs>
                </div>
            </div>

            {activeTab === 'overview' ? (
                <>
                    <Card>
                        <CardHeader>
                            <CardTitle>Performance Overview</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <PerformanceMetrics
                                data={performanceSummary}
                                loading={loading.performance}
                            />
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Campaigns</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <CampaignsList
                                campaigns={campaigns}
                                loading={loading.campaigns}
                                onSync={handleCampaignSync}
                                onSelect={handleCampaignSelect}
                            />
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Keyword Performance</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <KeywordPerformance
                                keywords={keywords}
                                loading={loading.keywords}
                            />
                        </CardContent>
                    </Card>
                </>
            ) : (
                <Card>
                    <CardHeader>
                        <CardTitle>User Management</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <UserManagement
                            users={users}
                            loading={loading.users}
                            onAddUser={handleAddUser}
                            onToggleRole={handleToggleRole}
                            onRemoveUser={handleRemoveUser}
                        />
                    </CardContent>
                </Card>
            )}
        </div>
    );
} 