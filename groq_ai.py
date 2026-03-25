import os
import json
from groq import Groq

class GroqAI:
    """Groq AI client for generating responses."""
    
    def __init__(self):
        self.api_key = os.environ.get('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama3-8b-8192"  # LLaMA 3 8B model
        
        # Price list in Urdu
        self.price_list = """
        ہمارے پروڈکٹ کی قیمتیں:
        
        • Product A: Rs. 500
        • Product B: Rs. 1,000  
        • Product C: Rs. 1,500
        • Product D: Rs. 2,000
        
        ڈلیوری فری ہے!
        """
        
        # System prompt
        self.system_prompt = """آپ ایک کاروباری اسسٹنٹ ہیں جو اردو میں گاہکوں کی مدد کرتے ہیں۔

اہم ہدایات:
1. ہمیشہ اردو میں مختصر اور واضح جواب دیں
2. زیادہ سے زیادہ 2-3 جملوں میں جواب دیں
3. مہذب اور پیشہ ورانہ لہجہ استعمال کریں
4. کاروباری مدد کے لیے تیار رہیں

امکانی صورت حال:
- اگر صارف سلام کرے → "والیکم السلام! میں آپ کا کاروباری اسسٹنٹ ہوں۔ میں آپ کی کیا مدد کر سکتا ہوں؟"
- اگر صارف قیمت پوچھے → مکمل پرائس لسٹ بھیجیں
- اگر صارف آرڈر دینا چاہے → نام، پتہ، اور فون نمبر مانگیں
- عام سوالات کے لیے → مددگار جواب دیں

پرائس لسٹ:
"""
    
    def get_response(self, user_message, conversation_history=None, intent="general", state="greeting"):
        """Generate AI response using Groq API."""
        
        try:
            # Prepare messages
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt + self.price_list
                }
            ]
            
            # Add conversation history (last 5 messages)
            if conversation_history:
                for msg in conversation_history[-5:]:
                    role = "user" if msg["role"] == "user" else "assistant"
                    messages.append({
                        "role": role,
                        "content": msg["content"]
                    })
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Handle specific intents
            if intent == "greeting":
                return "والیکم السلام! میں آپ کا کاروباری اسسٹنٹ ہوں۔ میں آپ کی کیا مدد کر سکتا ہوں؟"
            
            elif intent == "price":
                return """ہمارے پروڈکٹ کی قیمتیں:

• Product A: Rs. 500
• Product B: Rs. 1,000  
• Product C: Rs. 1,500
• Product D: Rs. 2,000

ڈلیوری فری ہے! آرڈر دینے کے لیے "آرڈر" لکھیں۔"""
            
            elif intent == "order":
                return "آرڈر دینے کے لیے براہ کرم اپنا نام، مکمل پتہ، اور فون نمبر بھیجیں۔"
            
            # For other intents, use AI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=150,
                top_p=1,
                stream=False
            )
            
            ai_reply = response.choices[0].message.content.strip()
            
            # Ensure Urdu response is short
            if len(ai_reply) > 200:
                ai_reply = ai_reply[:197] + "..."
            
            return ai_reply
            
        except Exception as e:
            print(f"Error calling Groq API: {str(e)}")
            # Fallback responses in Urdu
            fallback_responses = [
                "معاف کیجئے، میں آپ کی درخواست سمجھ نہیں پایا۔ دوبارہ کوشش کریں۔",
                "براہ کرم اپنا سوال دوبارہ پوچھیں۔",
                "میں آپ کی مدد کے لیے تیار ہوں۔ کیا پوچھنا چاہتے ہیں؟"
            ]
            import random
            return random.choice(fallback_responses)
    
    def generate_custom_response(self, prompt):
        """Generate custom response for specific prompts."""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "آپ ایک مددگار کاروباری اسسٹنٹ ہیں جو اردو میں جواب دیتا ہے۔"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error in custom response: {str(e)}")
            return "معاف کیجئے، ایک نقص پیش آگیا۔"
