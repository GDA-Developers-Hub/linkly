from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from django.conf import settings
from datetime import datetime, timedelta
from .models import Campaign, AdGroup, Ad, PerformanceReport, KeywordMetrics, GoogleAdsAccount

class GoogleAdsService:
    def __init__(self, user=None):
        self.user = user
        self.client = None
        if user:
            self._initialize_client()

    def _initialize_client(self):
        try:
            account = GoogleAdsAccount.objects.get(user=self.user)
            self.client = GoogleAdsClient.load_from_dict({
                'developer_token': settings.GOOGLE_ADS_DEVELOPER_TOKEN,
                'client_id': settings.GOOGLE_OAUTH2_CLIENT_CONFIG['web']['client_id'],
                'client_secret': settings.GOOGLE_OAUTH2_CLIENT_CONFIG['web']['client_secret'],
                'refresh_token': account.refresh_token,
                'use_proto_plus': True,
            })
            self.customer_id = account.customer_id
        except GoogleAdsAccount.DoesNotExist:
            raise ValueError("User does not have Google Ads credentials")

    def sync_campaign(self, campaign_id):
        """Sync campaign data from Google Ads API"""
        if not self.client:
            raise ValueError("Google Ads client not initialized")
        
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            query = f"""
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign_budget.amount_micros,
                    campaign.start_date,
                    campaign.end_date,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions
                FROM campaign
                WHERE campaign.id = {campaign_id}
            """

            response = ga_service.search(customer_id=self.customer_id, query=query)
            
            for row in response:
                campaign = Campaign.objects.get(id=campaign_id)
                campaign.name = row.campaign.name
                campaign.status = row.campaign.status
                campaign.budget = row.campaign_budget.amount_micros / 1000000
                campaign.start_date = datetime.strptime(row.campaign.start_date, '%Y-%m-%d').date()
                if row.campaign.end_date:
                    campaign.end_date = datetime.strptime(row.campaign.end_date, '%Y-%m-%d').date()
                campaign.save()

                # Create performance report
                PerformanceReport.objects.create(
                    campaign=campaign,
                    date=datetime.now().date(),
                    impressions=row.metrics.impressions,
                    clicks=row.metrics.clicks,
                    cost=row.metrics.cost_micros / 1000000,
                    conversions=row.metrics.conversions
                )

                return {
                    'status': 'success',
                    'campaign_id': campaign_id,
                    'updated_at': campaign.updated_at
                }

        except GoogleAdsException as ex:
            return {
                'status': 'error',
                'message': ex.failure.message,
                'campaign_id': campaign_id
            }

    def sync_keywords(self, ad_group_id):
        """Sync keyword metrics from Google Ads API"""
        if not self.client:
            raise ValueError("Google Ads client not initialized")
        
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            query = f"""
                SELECT
                    ad_group_criterion.criterion_id,
                    ad_group_criterion.keyword.text,
                    ad_group_criterion.keyword.match_type,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions
                FROM keyword_view
                WHERE ad_group.id = {ad_group_id}
            """

            response = ga_service.search(customer_id=self.customer_id, query=query)
            
            today = datetime.now().date()
            keywords = []

            for row in response:
                keyword = KeywordMetrics.objects.create(
                    ad_group_id=ad_group_id,
                    keyword=row.ad_group_criterion.keyword.text,
                    match_type=row.ad_group_criterion.keyword.match_type,
                    impressions=row.metrics.impressions,
                    clicks=row.metrics.clicks,
                    cost=row.metrics.cost_micros / 1000000,
                    conversions=row.metrics.conversions,
                    date=today
                )
                keywords.append(keyword)

            return {
                'status': 'success',
                'ad_group_id': ad_group_id,
                'keywords_synced': len(keywords)
            }

        except GoogleAdsException as ex:
            return {
                'status': 'error',
                'message': ex.failure.message,
                'ad_group_id': ad_group_id
            }

    def get_performance_report(self, campaign_id, days=30):
        """Get performance report for a campaign"""
        if not self.client:
            raise ValueError("Google Ads client not initialized")
        
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)

            query = f"""
                SELECT
                    campaign.id,
                    segments.date,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions
                FROM campaign
                WHERE 
                    campaign.id = {campaign_id}
                    AND segments.date BETWEEN '{start_date}' AND '{end_date}'
            """

            response = ga_service.search(customer_id=self.customer_id, query=query)
            reports = []

            for row in response:
                report = PerformanceReport.objects.create(
                    campaign_id=campaign_id,
                    date=datetime.strptime(row.segments.date, '%Y-%m-%d').date(),
                    impressions=row.metrics.impressions,
                    clicks=row.metrics.clicks,
                    cost=row.metrics.cost_micros / 1000000,
                    conversions=row.metrics.conversions
                )
                reports.append(report)

            return {
                'status': 'success',
                'campaign_id': campaign_id,
                'reports_created': len(reports)
            }

        except GoogleAdsException as ex:
            return {
                'status': 'error',
                'message': ex.failure.message,
                'campaign_id': campaign_id
            }

    def sync_ad_group(self, ad_group_id):
        """Sync ad group data from Google Ads API"""
        if not self.client:
            raise ValueError("Google Ads client not initialized")
        
        # Implementation of ad group sync logic
        pass

    def sync_ads(self, ad_group_id):
        """Sync ads data from Google Ads API"""
        if not self.client:
            raise ValueError("Google Ads client not initialized")
        
        # Implementation of ads sync logic
        pass

    def sync_performance_metrics(self, campaign_id=None, date_from=None, date_to=None):
        """Sync performance metrics from Google Ads API"""
        if not self.client:
            raise ValueError("Google Ads client not initialized")
        
        # Implementation of performance metrics sync logic
        pass

    def sync_keyword_metrics(self, ad_group_id=None, date_from=None, date_to=None):
        """Sync keyword metrics from Google Ads API"""
        if not self.client:
            raise ValueError("Google Ads client not initialized")
        
        # Implementation of keyword metrics sync logic
        pass 