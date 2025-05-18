"""
Google Ads OAuth2 views for Django Allauth.
"""
import requests
import logging
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView,
    OAuth2LoginView,
)
from .provider import GoogleAdsProvider

logger = logging.getLogger(__name__)

class GoogleAdsOAuth2Adapter(GoogleOAuth2Adapter):
    """Google Ads OAuth2 adapter extending Google OAuth2 adapter"""
    provider_id = GoogleAdsProvider.id  # Now 'googleads' instead of 'google_ads'
    
    def complete_login(self, request, app, token, **kwargs):
        """
        Complete the login process and fetch Google Ads-specific data
        """
        # First get the Google user info using the parent adapter
        login = super().complete_login(request, app, token, **kwargs)
        
        # Now try to get Google Ads-specific data
        try:
            headers = {
                'Authorization': f'Bearer {token.token}',
                'Content-Type': 'application/json'
            }
            
            # For Google Ads, we need to use the Google Ads API
            # This requires a developer token and additional setup
            # Simplified version for now, focusing on accessing account information
            
            # Update extra_data with Google Ads specific markers
            login.account.extra_data.update({
                'is_google_ads_account': True,
                'google_ads_access_level': 'pending_setup'
            })
            
            # Try to get customer list if possible
            try:
                # Note: Real implementation would use the Google Ads API client library
                # This is a placeholder for demonstration
                ads_url = 'https://googleads.googleapis.com/v15/customers:listAccessibleCustomers'
                ads_response = requests.get(ads_url, headers=headers)
                
                if ads_response.status_code == 200:
                    ads_data = ads_response.json()
                    if 'resourceNames' in ads_data:
                        customer_ids = []
                        for resource_name in ads_data['resourceNames']:
                            # Format is 'customers/{customer_id}'
                            customer_id = resource_name.split('/')[-1]
                            customer_ids.append(customer_id)
                        
                        login.account.extra_data.update({
                            'google_ads_customer_ids': customer_ids,
                            'google_ads_customer_count': len(customer_ids),
                            'google_ads_access_level': 'active'
                        })
            except Exception as e:
                logger.warning(f"Could not retrieve Google Ads customer IDs: {str(e)}")
                # Try fallback approach - Analytics accounts
                try:
                    analytics_url = 'https://www.googleapis.com/analytics/v3/management/accounts'
                    analytics_response = requests.get(analytics_url, headers=headers)
                    
                    if analytics_response.status_code == 200:
                        analytics_data = analytics_response.json()
                        analytics_accounts = []
                        
                        if 'items' in analytics_data:
                            for account in analytics_data['items']:
                                analytics_accounts.append({
                                    'id': account.get('id'),
                                    'name': account.get('name'),
                                    'type': 'analytics'
                                })
                            
                            login.account.extra_data.update({
                                'google_analytics_accounts': analytics_accounts,
                                'google_analytics_account_count': len(analytics_accounts)
                            })
                except Exception as analytics_error:
                    logger.warning(f"Could not retrieve Google Analytics accounts: {str(analytics_error)}")
        
        except Exception as e:
            logger.exception(f"Error enriching Google Ads profile data: {str(e)}")
        
        return login


oauth2_login = OAuth2LoginView.adapter_view(GoogleAdsOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(GoogleAdsOAuth2Adapter)
