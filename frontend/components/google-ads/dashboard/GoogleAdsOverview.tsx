import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useGoogleAdsData } from '@/hooks/useGoogleAdsData';
import { PerformanceMetrics } from './PerformanceMetrics';
import { CampaignsList } from './CampaignsList';
import { KeywordPerformance } from './KeywordPerformance';

export const GoogleAdsOverview: React.FC = () => {
  const { campaigns, performance, loading, error } = useGoogleAdsData();

  if (loading) {
    return <div>Loading Google Ads data...</div>;
  }

  if (error) {
    return <div>Error loading Google Ads data: {error.message}</div>;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <Card>
        <CardHeader>
          <CardTitle>Campaign Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <PerformanceMetrics data={performance} />
        </CardContent>
      </Card>

      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Active Campaigns</CardTitle>
        </CardHeader>
        <CardContent>
          <CampaignsList campaigns={campaigns} />
        </CardContent>
      </Card>

      <Card className="lg:col-span-3">
        <CardHeader>
          <CardTitle>Keyword Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <KeywordPerformance />
        </CardContent>
      </Card>
    </div>
  );
}; 