from celery import shared_task
from allauth.socialaccount.models import SocialAccount, SocialToken
from django.utils import timezone

from .providers import linkedin, twitter
from .models import Post
import logging

logger = logging.getLogger(__name__)


@shared_task
def publish_post_task(post_id, social_account_ids):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")
        return {"status": "error", "message": "Post not found"}

    for account_id in social_account_ids:
        try:
            social_account = SocialAccount.objects.get(id=account_id, user=post.user)
            provider = social_account.provider  # e.g., 'twitter', 'linkedin'

            social_token = SocialToken.objects.filter(account=social_account).first()
            if not social_token:
                logger.warning(f"No token found for SocialAccount ID {account_id}.")
                continue

            logger.info(
                f"Publishing post {post.id} to {provider} (SocialAccount ID: {account_id})"
            )

            if provider == "twitter":
                result = twitter.post(post.content, social_token)
            elif provider == "linkedin":
                result = linkedin.post(post.content, social_token, social_account.uid)
            else:
                logger.warning(f"Unsupported provider: {provider}")
                continue

            if result.get("success"):
                logger.info(f"Post {post.id} published to {provider}.")
            else:
                logger.error(f"Failed to post to {provider}: {result.get('error')}")

        except SocialAccount.DoesNotExist:
            logger.warning(
                f"SocialAccount with ID {account_id} not found for user {post.user}."
            )
            continue


    post.status = "published"
    post.published_at = timezone.now()
    post.save()

    return {"status": "success", "post_id": post.id}
