import { useState, useEffect } from 'react';
import axios from 'axios';
import { Campaign, PerformanceReport } from '@/types/google-ads';

interface UseGoogleAdsDataReturn {
  campaigns: Campaign[];
  performance: PerformanceReport[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

const API_BASE_URL = '/api/google-ads';

export const useGoogleAdsData = (): UseGoogleAdsDataReturn => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [performance, setPerformance] = useState<PerformanceReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get active campaigns
      const campaignsResponse = await axios.get(`${API_BASE_URL}/campaigns`);
      setCampaigns(campaignsResponse.data);

      // Get performance data for all campaigns
      const performancePromises = campaignsResponse.data.map((campaign: Campaign) =>
        axios.get(`${API_BASE_URL}/campaigns/${campaign.id}/performance`, {
          params: {
            start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // Last 30 days
            end: new Date().toISOString().split('T')[0],
          },
        })
      );

      const performanceResponses = await Promise.all(performancePromises);
      const allPerformanceData = performanceResponses.flatMap(response => response.data);
      setPerformance(allPerformanceData);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch Google Ads data'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return {
    campaigns,
    performance,
    loading,
    error,
    refetch: fetchData,
  };
}; 