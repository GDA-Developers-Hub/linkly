import axios from 'axios';
import {
    Campaign,
    CampaignDetail,
    AdGroup,
    AdGroupDetail,
    Ad,
    PerformanceReport,
    KeywordMetrics,
    PerformanceSummary
} from '../types/google-ads';

// Use a function to ensure the API URL has the correct protocol
const getApiBaseUrl = () => {
  let baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  // Add protocol if missing
  if (!baseUrl.startsWith('http://') && !baseUrl.startsWith('https://')) {
    baseUrl = `https://${baseUrl}`;
  }
  
  console.log(`GoogleAdsService API URL: ${baseUrl}`);
  return baseUrl;
};

const API_BASE_URL = getApiBaseUrl();

class GoogleAdsService {
    private async get<T>(endpoint: string): Promise<T> {
        const response = await axios.get<T>(`${API_BASE_URL}/api/google-ads${endpoint}`);
        return response.data;
    }

    private async post<T>(endpoint: string, data?: any): Promise<T> {
        const response = await axios.post<T>(`${API_BASE_URL}/api/google-ads${endpoint}`, data);
        return response.data;
    }

    private async patch<T>(endpoint: string, data: any): Promise<T> {
        const response = await axios.patch<T>(`${API_BASE_URL}/api/google-ads${endpoint}`, data);
        return response.data;
    }

    // Campaigns
    async getCampaigns(): Promise<Campaign[]> {
        return this.get<Campaign[]>('/campaigns/');
    }

    async getCampaign(id: string): Promise<CampaignDetail> {
        return this.get<CampaignDetail>(`/campaigns/${id}/`);
    }

    async getCampaignPerformance(id: string, days: number = 30): Promise<PerformanceReport[]> {
        return this.get<PerformanceReport[]>(`/campaigns/${id}/performance/?days=${days}`);
    }

    async syncCampaign(id: string): Promise<any> {
        return this.post(`/campaigns/${id}/sync/`);
    }

    // Ad Groups
    async getAdGroups(): Promise<AdGroup[]> {
        return this.get<AdGroup[]>('/ad-groups/');
    }

    async getAdGroup(id: string): Promise<AdGroupDetail> {
        return this.get<AdGroupDetail>(`/ad-groups/${id}/`);
    }

    async getAdGroupKeywords(id: string, days: number = 30): Promise<KeywordMetrics[]> {
        return this.get<KeywordMetrics[]>(`/ad-groups/${id}/keywords/?days=${days}`);
    }

    async syncKeywords(id: string): Promise<any> {
        return this.post(`/ad-groups/${id}/sync-keywords/`);
    }

    // Ads
    async getAds(): Promise<Ad[]> {
        return this.get<Ad[]>('/ads/');
    }

    async getAd(id: string): Promise<Ad> {
        return this.get<Ad>(`/ads/${id}/`);
    }

    async toggleAdStatus(id: string, status: 'ENABLED' | 'PAUSED' | 'REMOVED'): Promise<Ad> {
        return this.post<Ad>(`/ads/${id}/toggle-status/`, { status });
    }

    // Performance Reports
    async getPerformanceReports(days: number = 30): Promise<PerformanceReport[]> {
        return this.get<PerformanceReport[]>(`/performance-reports/?days=${days}`);
    }

    async getPerformanceSummary(days: number = 30): Promise<PerformanceSummary> {
        return this.get<PerformanceSummary>(`/performance-reports/summary/?days=${days}`);
    }

    // Keyword Metrics
    async getKeywordMetrics(days: number = 30): Promise<KeywordMetrics[]> {
        return this.get<KeywordMetrics[]>(`/keyword-metrics/?days=${days}`);
    }
}

export const googleAdsService = new GoogleAdsService(); 