import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useGoogleAdsData } from '@/hooks/useGoogleAdsData';
import { PerformanceMetrics } from './PerformanceMetrics';
import { CampaignsList } from './CampaignsList';
import { KeywordPerformance } from './KeywordPerformance';
import { PerformanceReport, PerformanceSummary, KeywordMetrics } from '@/types/google-ads';

// Function to transform PerformanceReport[] to PerformanceSummary
const createPerformanceSummary = (reports: PerformanceReport[]): PerformanceSummary => {
  return reports.reduce(
    (summary, report) => {
      return {
        total_impressions: summary.total_impressions + report.impressions,
        total_clicks: summary.total_clicks + report.clicks,
        total_cost: summary.total_cost + report.cost,
        total_conversions: summary.total_conversions + report.conversions
      };
    },
    {
      total_impressions: 0,
      total_clicks: 0,
      total_cost: 0,
      total_conversions: 0
    }
  );
};

export const GoogleAdsOverview: React.FC = () => {
  const { campaigns, performance, loading, error } = useGoogleAdsData();

  // Create performance summary from the reports array
  const performanceSummary = createPerformanceSummary(performance);

  // Mock keywords data with proper KeywordMetrics type
  const keywordsData: KeywordMetrics[] = [
    { 
      id: 1, 
      ad_group: "ad_group_1",
      keyword: 'digital marketing', 
      match_type: 'BROAD',
      date: new Date().toISOString().split('T')[0],
      clicks: 520, 
      impressions: 12400, 
      ctr: 4.19, 
      cost: 620, 
      conversions: 18,
      created_at: new Date().toISOString(),
      cpc: 1.19
    },
    { 
      id: 2, 
      ad_group: "ad_group_1",
      keyword: 'social media management', 
      match_type: 'PHRASE',
      date: new Date().toISOString().split('T')[0],
      clicks: 380, 
      impressions: 9200, 
      ctr: 4.13, 
      cost: 450, 
      conversions: 12,
      created_at: new Date().toISOString(),
      cpc: 1.18
    },
    { 
      id: 3, 
      ad_group: "ad_group_2",
      keyword: 'content marketing', 
      match_type: 'EXACT',
      date: new Date().toISOString().split('T')[0],
      clicks: 290, 
      impressions: 7800, 
      ctr: 3.72, 
      cost: 320, 
      conversions: 9,
      created_at: new Date().toISOString(),
      cpc: 1.10
    },
    { 
      id: 4, 
      ad_group: "ad_group_2",
      keyword: 'seo services', 
      match_type: 'BROAD',
      date: new Date().toISOString().split('T')[0],
      clicks: 410, 
      impressions: 11000, 
      ctr: 3.73, 
      cost: 550, 
      conversions: 15,
      created_at: new Date().toISOString(),
      cpc: 1.34
    },
    { 
      id: 5, 
      ad_group: "ad_group_3",
      keyword: 'ppc advertising', 
      match_type: 'EXACT',
      date: new Date().toISOString().split('T')[0],
      clicks: 250, 
      impressions: 5600, 
      ctr: 4.46, 
      cost: 380, 
      conversions: 8,
      created_at: new Date().toISOString(),
      cpc: 1.52
    }
  ];

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
          <PerformanceMetrics data={performanceSummary} />
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
          <KeywordPerformance keywords={keywordsData} />
        </CardContent>
      </Card>
    </div>
  );
}; 