import { GoogleAdsApi } from 'google-ads-api';
import { OAuth2Client } from 'google-auth-library';
import { 
  GoogleAdsConfig, 
  Campaign, 
  AdGroup, 
  Ad, 
  PerformanceReport, 
  KeywordMetrics 
} from '../types';
import logger from '../utils/logger';

export class GoogleAdsService {
  private client: GoogleAdsApi;
  private oauth2Client: OAuth2Client;
  private config: GoogleAdsConfig;

  constructor(config: GoogleAdsConfig) {
    this.config = config;
    this.oauth2Client = new OAuth2Client({
      clientId: config.clientId,
      clientSecret: config.clientSecret,
    });
    
    this.client = new GoogleAdsApi({
      client_id: config.clientId,
      client_secret: config.clientSecret,
      developer_token: config.developerToken,
      refresh_token: config.refreshToken,
    });
  }

  async createCampaign(campaign: Omit<Campaign, 'id'>): Promise<Campaign> {
    try {
      logger.info('Creating new campaign', { campaignName: campaign.name });
      const customer = this.client.Customer({
        customer_id: this.config.accountId,
      });

      const result = await customer.campaigns.create({
        name: campaign.name,
        status: campaign.status,
        campaign_budget: campaign.budget.toString(),
        start_date: campaign.startDate,
        end_date: campaign.endDate,
      });

      return {
        id: result.id!,
        ...campaign,
      };
    } catch (error) {
      logger.error('Error creating campaign', { error });
      throw error;
    }
  }

  async createAdGroup(adGroup: Omit<AdGroup, 'id'>): Promise<AdGroup> {
    try {
      logger.info('Creating new ad group', { adGroupName: adGroup.name });
      const customer = this.client.Customer({
        customer_id: this.config.accountId,
      });

      const result = await customer.adGroups.create({
        campaign_id: adGroup.campaignId,
        name: adGroup.name,
        status: adGroup.status,
        type: adGroup.type,
      });

      return {
        id: result.id!,
        ...adGroup,
      };
    } catch (error) {
      logger.error('Error creating ad group', { error });
      throw error;
    }
  }

  async createAd(ad: Omit<Ad, 'id'>): Promise<Ad> {
    try {
      logger.info('Creating new ad', { adHeadline: ad.headline });
      const customer = this.client.Customer({
        customer_id: this.config.accountId,
      });

      const result = await customer.ads.create({
        ad_group_id: ad.adGroupId,
        headline: ad.headline,
        description: ad.description,
        final_urls: [ad.finalUrl],
        status: ad.status,
      });

      return {
        id: result.id!,
        ...ad,
      };
    } catch (error) {
      logger.error('Error creating ad', { error });
      throw error;
    }
  }

  async getPerformanceReport(campaignId: string, dateRange: { start: string; end: string }): Promise<PerformanceReport[]> {
    try {
      logger.info('Fetching performance report', { campaignId, dateRange });
      const customer = this.client.Customer({
        customer_id: this.config.accountId,
      });

      const report = await customer.report({
        entity: 'campaign',
        attributes: ['campaign.id', 'metrics.impressions', 'metrics.clicks', 'metrics.cost_micros', 'metrics.conversions'],
        constraints: {
          'campaign.id': campaignId,
          date_range: dateRange,
        },
      });

      return report.map((row: any) => ({
        campaignId: row.campaign.id,
        impressions: row.metrics.impressions,
        clicks: row.metrics.clicks,
        cost: row.metrics.cost_micros / 1000000,
        conversions: row.metrics.conversions,
        date: row.segments.date,
      }));
    } catch (error) {
      logger.error('Error fetching performance report', { error });
      throw error;
    }
  }

  async getKeywordMetrics(adGroupId: string): Promise<KeywordMetrics[]> {
    try {
      logger.info('Fetching keyword metrics', { adGroupId });
      const customer = this.client.Customer({
        customer_id: this.config.accountId,
      });

      const metrics = await customer.report({
        entity: 'keyword_view',
        attributes: [
          'keyword_view.keyword_text',
          'keyword_view.match_type',
          'metrics.impressions',
          'metrics.clicks',
          'metrics.cost_micros',
          'metrics.conversions',
        ],
        constraints: {
          'ad_group.id': adGroupId,
        },
      });

      return metrics.map((row: any) => ({
        keyword: row.keyword_view.keyword_text,
        matchType: row.keyword_view.match_type,
        impressions: row.metrics.impressions,
        clicks: row.metrics.clicks,
        cost: row.metrics.cost_micros / 1000000,
        conversions: row.metrics.conversions,
      }));
    } catch (error) {
      logger.error('Error fetching keyword metrics', { error });
      throw error;
    }
  }
} 