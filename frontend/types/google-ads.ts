export interface Campaign {
  id: string;
  name: string;
  status: 'ENABLED' | 'PAUSED' | 'REMOVED';
  budget: number;
  start_date: string;
  end_date?: string;
  created_at: string;
  updated_at: string;
}

export interface AdGroup {
  id: string;
  campaign: string;
  name: string;
  status: 'ENABLED' | 'PAUSED' | 'REMOVED';
  type: 'SEARCH' | 'DISPLAY' | 'VIDEO' | 'SHOPPING';
  created_at: string;
  updated_at: string;
}

export interface Ad {
  id: string;
  ad_group: string;
  headline: string;
  description: string;
  final_url: string;
  status: 'ENABLED' | 'PAUSED' | 'REMOVED';
  created_at: string;
  updated_at: string;
}

export interface PerformanceReport {
  id: number;
  campaign: string;
  date: string;
  impressions: number;
  clicks: number;
  cost: number;
  conversions: number;
  created_at: string;
  ctr: number;
  cpc: number;
}

export interface KeywordMetrics {
  id: number;
  ad_group: string;
  keyword: string;
  match_type: 'EXACT' | 'PHRASE' | 'BROAD';
  date: string;
  impressions: number;
  clicks: number;
  cost: number;
  conversions: number;
  created_at: string;
  ctr: number;
  cpc: number;
}

export interface CampaignDetail extends Campaign {
  performance_reports: PerformanceReport[];
  ad_groups: AdGroup[];
}

export interface AdGroupDetail extends AdGroup {
  ads: Ad[];
  keyword_metrics: KeywordMetrics[];
}

export interface PerformanceSummary {
  total_impressions: number;
  total_clicks: number;
  total_cost: number;
  total_conversions: number;
} 