import os
import json
import requests

class WhatsAppClient:
    """WhatsApp Cloud API client for sending messages."""
    
    def __init__(self):
        self.api_token = os.environ.get('WHATSAPP_API_TOKEN')
        self.phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
        
        if not self.api_token:
            raise ValueError("WHATSAPP_API_TOKEN environment variable is required")
        if not self.phone_number_id:
            raise ValueError("WHATSAPP_PHONE_NUMBER_ID environment variable is required")
        
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def send_message(self, to_phone_number, message_text):
        """Send text message to WhatsApp user."""
        
        url = f"{self.base_url}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone_number,
            "type": "text",
            "text": {
                "body": message_text,
                "preview_url": False
            }
        }
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Message sent successfully: {result}")
                return True
            else:
                print(f"Failed to send message. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("Request timed out while sending message")
            return False
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            return False
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False
    
    def send_template_message(self, to_phone_number, template_name, language_code="en_US", components=None):
        """Send template message (for notifications)."""
        
        url = f"{self.base_url}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        if components:
            payload["template"]["components"] = components
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Template message sent: {result}")
                return True
            else:
                print(f"Failed to send template. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending template: {str(e)}")
            return False
    
    def send_media_message(self, to_phone_number, media_type, media_id_or_url, caption=None):
        """Send media message (image, document, video, audio)."""
        
        url = f"{self.base_url}/messages"
        
        # media_type can be: image, document, video, audio
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone_number,
            "type": media_type,
            media_type: {}
        }
        
        # Check if it's a URL or media ID
        if media_id_or_url.startswith("http"):
            payload[media_type]["link"] = media_id_or_url
        else:
            payload[media_type]["id"] = media_id_or_url
        
        if caption and media_type in ["image", "document", "video"]:
            payload[media_type]["caption"] = caption
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Media message sent: {result}")
                return True
            else:
                print(f"Failed to send media. Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error sending media: {str(e)}")
            return False
    
    def mark_message_as_read(self, message_id):
        """Mark a message as read."""
        
        url = f"{self.base_url}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error marking as read: {str(e)}")
            return False
    
    def get_message_status(self, message_id):
        """Get status of a sent message."""
        
        # This would require webhook status tracking
        # Messages statuses come through webhooks
        pass
    
    def verify_webhook_setup(self):
        """Verify webhook is properly configured."""
        
        url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/subscribed_apps"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"Webhook subscription data: {data}")
                return True
            else:
                print(f"Failed to verify webhook: {response.text}")
                return False
        except Exception as e:
            print(f"Error verifying webhook: {str(e)}")
            return False
