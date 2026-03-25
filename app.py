from flask import Flask, request, jsonify
import os
import json
from datetime import datetime
from groq_ai import GroqAI
from whatsapp import WhatsAppClient

app = Flask(__name__)

# Initialize clients
groq_client = GroqAI()
whatsapp_client = WhatsAppClient()

# In-memory conversation storage (use Redis/DB for production)
conversations = {}

def get_conversation(phone_number):
    """Get conversation history for a user."""
    if phone_number not in conversations:
        conversations[phone_number] = {
            "messages": [],
            "state": "greeting",
            "order_data": {},
            "last_active": datetime.now()
        }
    return conversations[phone_number]

def update_conversation(phone_number, role, message):
    """Add message to conversation history."""
    conv = get_conversation(phone_number)
    conv["messages"].append({"role": role, "content": message, "timestamp": datetime.now().isoformat()})
    conv["last_active"] = datetime.now()
    # Keep only last 20 messages
    if len(conv["messages"]) > 20:
        conv["messages"] = conv["messages"][-20:]

def detect_intent(message):
    """Detect user intent from message."""
    msg_lower = message.lower()
    
    greetings = ['hello', 'hi', 'hey', 'salam', 'aslam', 'assalam', 'salam']
    price_keywords = ['price', 'rate', 'cost', 'kitna', 'price list', 'rates', 'kimat', 'qimat']
    order_keywords = ['order', 'buy', 'purchase', 'mangwana', 'book', 'order karna', 'buy karna']
    
    for g in greetings:
        if g in msg_lower:
            return "greeting"
    
    for p in price_keywords:
        if p in msg_lower:
            return "price"
    
    for o in order_keywords:
        if o in msg_lower:
            return "order"
    
    return "general"

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "service": "WhatsApp AI Bot",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Handle WhatsApp webhook verification and messages."""
    
    # GET request: Webhook verification from Meta
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        verify_token = os.environ.get('VERIFY_TOKEN', 'your_verify_token')
        
        if mode == 'subscribe' and token == verify_token:
            print(f"Webhook verified successfully!")
            return challenge, 200
        else:
            return "Verification failed", 403
    
    # POST request: Incoming messages from WhatsApp
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(f"Received webhook data: {json.dumps(data, indent=2)}")
            
            # Extract message data
            entry = data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            
            # Check for messages
            messages = value.get('messages', [])
            
            if messages:
                message = messages[0]
                from_number = message.get('from')
                msg_body = message.get('text', {}).get('body', '')
                
                print(f"Message from {from_number}: {msg_body}")
                
                # Update conversation
                update_conversation(from_number, "user", msg_body)
                conv = get_conversation(from_number)
                
                # Get AI response
                ai_response = groq_client.get_response(
                    user_message=msg_body,
                    conversation_history=conv["messages"],
                    intent=detect_intent(msg_body),
                    state=conv["state"]
                )
                
                # Update conversation state based on intent
                intent = detect_intent(msg_body)
                if intent == "order":
                    conv["state"] = "collecting_order"
                
                # Send reply
                success = whatsapp_client.send_message(from_number, ai_response)
                
                if success:
                    update_conversation(from_number, "assistant", ai_response)
                    print(f"Reply sent successfully: {ai_response}")
                else:
                    print("Failed to send reply")
            
            # Check for status updates
            statuses = value.get('statuses', [])
            for status in statuses:
                print(f"Message status update: {status.get('id')} - {status.get('status')}")
            
            return jsonify({"success": True}), 200
            
        except Exception as e:
            print(f"Error processing webhook: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "error": str(e)}), 500

@app.route('/send-message', methods=['POST'])
def send_message():
    """Endpoint to manually send a message."""
    data = request.get_json()
    phone_number = data.get('phone_number')
    message = data.get('message')
    
    if not phone_number or not message:
        return jsonify({"error": "phone_number and message required"}), 400
    
    success = whatsapp_client.send_message(phone_number, message)
    
    if success:
        return jsonify({"success": True, "message": "Message sent"}), 200
    else:
        return jsonify({"error": "Failed to send message"}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "active_conversations": len(conversations),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
