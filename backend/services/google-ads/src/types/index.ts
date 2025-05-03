export interface GoogleAdsConfig {
  clientId: string;
  clientSecret: string;
  developerToken: string;
  accountId: string;
  refreshToken: string;
}

export interface Campaign {
  id: string;
  name: string;
  status: 'ENABLED' | 'PAUSED' | 'REMOVED';
  budget: number;
  startDate: string;
  endDate?: string;
}

export interface AdGroup {
  id: string;
  campaignId: string;
  name: string;
  status: 'ENABLED' | 'PAUSED' | 'REMOVED';
  type: string;
}

export interface Ad {
  id: string;
  adGroupId: string;
  headline: string;
  description: string;
  finalUrl: string;
  status: 'ENABLED' | 'PAUSED' | 'REMOVED';
}

export interface PerformanceReport {
  campaignId: string;
  impressions: number;
  clicks: number;
  cost: number;
  conversions: number;
  date: string;
}

export interface KeywordMetrics {
  keyword: string;
  matchType: 'EXACT' | 'PHRASE' | 'BROAD';
  impressions: number;
  clicks: number;
  cost: number;
  conversions: number;
}

export interface ApiError {
  code: string;
  message: string;
  status: number;
} 