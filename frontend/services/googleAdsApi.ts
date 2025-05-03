import axios from 'axios';
import { Campaign, AdGroup, Ad, PerformanceReport, KeywordMetrics } from '@/types/google-ads';

const API_BASE_URL = `${process.env.NEXT_PUBLIC_API_URL}/api/google-ads`;

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

export const googleAdsApi = {
  // Campaigns
  getCampaigns: async () => {
    const response = await api.get<Campaign[]>('/campaigns/');
    return response.data;
  },

  getCampaign: async (id: string) => {
    const response = await api.get<Campaign>(`/campaigns/${id}/`);
    return response.data;
  },

  createCampaign: async (campaign: Omit<Campaign, 'id'>) => {
    const response = await api.post<Campaign>('/campaigns/', campaign);
    return response.data;
  },

  updateCampaign: async (id: string, campaign: Partial<Campaign>) => {
    const response = await api.patch<Campaign>(`/campaigns/${id}/`, campaign);
    return response.data;
  },

  deleteCampaign: async (id: string) => {
    await api.delete(`/campaigns/${id}/`);
  },

  getCampaignPerformance: async (id: string, days: number = 30) => {
    const response = await api.get<PerformanceReport[]>(`/campaigns/${id}/performance/`, {
      params: { days },
    });
    return response.data;
  },

  // Ad Groups
  getAdGroups: async () => {
    const response = await api.get<AdGroup[]>('/ad-groups/');
    return response.data;
  },

  getAdGroup: async (id: string) => {
    const response = await api.get<AdGroup>(`/ad-groups/${id}/`);
    return response.data;
  },

  createAdGroup: async (adGroup: Omit<AdGroup, 'id'>) => {
    const response = await api.post<AdGroup>('/ad-groups/', adGroup);
    return response.data;
  },

  updateAdGroup: async (id: string, adGroup: Partial<AdGroup>) => {
    const response = await api.patch<AdGroup>(`/ad-groups/${id}/`, adGroup);
    return response.data;
  },

  deleteAdGroup: async (id: string) => {
    await api.delete(`/ad-groups/${id}/`);
  },

  // Ads
  getAds: async () => {
    const response = await api.get<Ad[]>('/ads/');
    return response.data;
  },

  createAd: async (ad: Omit<Ad, 'id'>) => {
    const response = await api.post<Ad>('/ads/', ad);
    return response.data;
  },

  updateAd: async (id: string, ad: Partial<Ad>) => {
    const response = await api.patch<Ad>(`/ads/${id}/`, ad);
    return response.data;
  },

  deleteAd: async (id: string) => {
    await api.delete(`/ads/${id}/`);
  },

  toggleAdStatus: async (id: string, status: Ad['status']) => {
    const response = await api.post<Ad>(`/ads/${id}/toggle_status/`, { status });
    return response.data;
  },

  // Performance Reports
  getPerformanceSummary: async (days: number = 30) => {
    const response = await api.get('/performance/summary/', {
      params: { days },
    });
    return response.data;
  },

  // Keywords
  getKeywordMetrics: async (adGroupId: string, days: number = 30) => {
    const response = await api.get<KeywordMetrics[]>(`/ad-groups/${adGroupId}/keywords/`, {
      params: { days },
    });
    return response.data;
  },
}; 