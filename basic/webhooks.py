import os
import httpx
from typing import Optional, Dict, Any


def create_webhook(url: str) -> Dict[str, Any]:
    """
    Configure a webhook endpoint to receive real-time scan completion notifications.
    
    Webhooks enable Flow 2 (async integration) by allowing Encephalon to notify your
    application when AI analysis completes. This eliminates the need for polling.
    
    Args:
        url: Your server endpoint that will receive POST notifications
    
    Returns:
        Dict containing webhook configuration including UUID and secret token
    
    Example:
        # Set up webhook for async notifications (one-time setup)
        webhook = create_webhook("https://myapp.com/encephalon-webhook")
        print(f"Created webhook: {webhook['uuid']}")
        print(f"Webhook URL: {webhook['url']}")
        print(f"Secret token: {webhook['token']}")
        
        # IMPORTANT: Store the token securely for signature verification
        webhook_token = webhook['token']
        # Save this token - you'll need it to verify webhook authenticity
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Token {token}",  # Use 'Token' format for API_TOKEN authentication
        "Content-Type": "application/json"
    }
    
    data = {"url": url}
    
    response = httpx.post(
        f"{api_url}/api/v2/webhook/",
        headers=headers,
        json=data
    )
    response.raise_for_status()
    return response.json()


def get_webhooks(
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> Dict[str, Any]:
    """
    Retrieve list of configured webhook endpoints.
    
    Use this function to audit your webhook configuration, find existing endpoints,
    or verify webhook status.
    
    Args:
        page: Page number for pagination (optional)
        page_size: Number of webhooks per page (optional)
    
    Returns:
        Dict with 'results' containing webhook configurations
    
    Example:
        # Check all configured webhooks
        webhooks = get_webhooks()
        print(f"You have {webhooks['count']} webhooks configured")
        
        for webhook in webhooks['results']:
            print(f"Webhook {webhook['uuid']}:")
            print(f"  URL: {webhook['url']}")
            print(f"  Created: {webhook['created_at']}")
            print(f"  Active: {webhook.get('is_active', True)}")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Token {token}",  # Use 'Token' format for API_TOKEN authentication
        "Content-Type": "application/json"
    }
    
    params = {}
    if page:
        params["page"] = page
    if page_size:
        params["page_size"] = page_size
    
    response = httpx.get(
        f"{api_url}/api/v2/webhook/",
        headers=headers,
        params=params
    )
    response.raise_for_status()
    return response.json()


def get_webhook(uuid: str) -> Dict[str, Any]:
    """
    Retrieve detailed information about a specific webhook configuration.
    
    Use this function to check webhook details, verify configuration,
    or retrieve the secret token for signature verification.
    
    Args:
        uuid: The unique identifier of the webhook
    
    Returns:
        Dict containing complete webhook configuration and metadata
    
    Example:
        # Get detailed webhook information
        webhook = get_webhook("abc123-def456-789")
        print(f"Webhook URL: {webhook['url']}")
        print(f"Token: {webhook['token']}")
        print(f"Created: {webhook['created_at']}")
        
        # Use the token for signature verification
        webhook_token = webhook['token']
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Token {token}",  # Use 'Token' format for API_TOKEN authentication
        "Content-Type": "application/json"
    }
    
    response = httpx.get(
        f"{api_url}/api/v2/webhook/{uuid}/",
        headers=headers
    )
    response.raise_for_status()
    return response.json()


def update_webhook(uuid: str, url: str) -> Dict[str, Any]:
    """
    Update the URL of an existing webhook endpoint.
    
    Use this function when your webhook endpoint URL changes (e.g., new domain,
    deployment updates) while keeping the same secret token.
    
    Args:
        uuid: The unique identifier of the webhook to update
        url: The new URL for webhook notifications
    
    Returns:
        Dict containing updated webhook configuration
    
    Example:
        # Update webhook URL after deployment
        webhook = update_webhook(
            "abc123-def456-789",
            "https://new-domain.com/encephalon-webhook"
        )
        print(f"Updated webhook URL: {webhook['url']}")
        print(f"Token unchanged: {webhook['token']}")
        
        # The secret token remains the same for signature verification
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Token {token}",  # Use 'Token' format for API_TOKEN authentication
        "Content-Type": "application/json"
    }
    
    data = {"url": url}
    
    response = httpx.patch(
        f"{api_url}/api/v2/webhook/{uuid}/",
        headers=headers,
        json=data
    )
    response.raise_for_status()
    return response.json()


def delete_webhook(uuid: str) -> None:
    """
    Permanently remove a webhook endpoint configuration.
    
    Use this function to clean up unused webhooks or when transitioning
    from webhook-based to polling-based integration.
    
    Args:
        uuid: The unique identifier of the webhook to delete
    
    Returns:
        None (raises exception if deletion fails)
    
    Example:
        # Remove unused webhook
        webhook_uuid = "abc123-def456-789"
        
        # Optionally verify webhook details first
        webhook = get_webhook(webhook_uuid)
        print(f"Deleting webhook: {webhook['url']}")
        
        delete_webhook(webhook_uuid)
        print("Webhook deleted - notifications will stop")
        
        # Note: After deletion, you'll need polling or create a new webhook
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Token {token}",  # Use 'Token' format for API_TOKEN authentication
        "Content-Type": "application/json"
    }
    
    response = httpx.delete(
        f"{api_url}/api/v2/webhook/{uuid}/",
        headers=headers
    )
    response.raise_for_status()