"""
AI Tutor module for English conversation practice
Supports OpenAI GPT and Ollama
"""
import json
import logging
import time
from typing import List, Dict, Optional, Generator
from datetime import datetime
from pathlib import Path

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI library not available")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Requests library not available")

from config import Config

logger = logging.getLogger(__name__)

class ConversationHistory:
    """Manage conversation history with advanced tracking"""
    
    def __init__(self):
        self.messages: List[Dict[str, str]] = []
        self.session_start = datetime.now()
        self.total_tokens = 0
        self.conversation_id = None
        self.user_interests = set()  # Track user interests/topics
        self.recent_questions = []   # Track recent AI questions to avoid repetition
        self.conversation_topics = []  # Track conversation topics
        self.last_user_sentiment = "neutral"  # Track user sentiment
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation with advanced tracking"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.messages.append(message)
        
        # Track conversation elements
        if role == "user":
            self._extract_user_interests(content)
            self._detect_sentiment(content)
        elif role == "assistant":
            self._track_ai_questions(content)
            
        logger.info(f"Added {role} message: {content[:50]}...")
    
    def _extract_user_interests(self, content: str):
        """Extract and track user interests from their messages"""
        # Simple keyword extraction for interests
        interest_keywords = {
            'cooking': ['cook', 'recipe', 'food', 'kitchen', 'meal'],
            'travel': ['travel', 'trip', 'vacation', 'country', 'visit'],
            'sports': ['sport', 'exercise', 'gym', 'football', 'soccer', 'basketball'],
            'music': ['music', 'song', 'band', 'concert', 'guitar', 'piano'],
            'work': ['work', 'job', 'career', 'office', 'colleague', 'boss'],
            'family': ['family', 'parents', 'siblings', 'children', 'kids'],
            'movies': ['movie', 'film', 'cinema', 'actor', 'director'],
            'books': ['book', 'read', 'novel', 'author', 'library'],
            'technology': ['computer', 'phone', 'app', 'internet', 'software']
        }
        
        content_lower = content.lower()
        for interest, keywords in interest_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                self.user_interests.add(interest)
    
    def _detect_sentiment(self, content: str):
        """Simple sentiment detection"""
        positive_words = ['happy', 'great', 'good', 'love', 'amazing', 'wonderful', 'excited']
        negative_words = ['sad', 'bad', 'terrible', 'hate', 'awful', 'disappointed', 'worried']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            self.last_user_sentiment = "positive"
        elif negative_count > positive_count:
            self.last_user_sentiment = "negative"
        else:
            self.last_user_sentiment = "neutral"
    
    def _track_ai_questions(self, content: str):
        """Track AI questions to prevent repetition"""
        if '?' in content:
            # Extract the main question
            questions = [q.strip() + '?' for q in content.split('?') if q.strip()]
            for question in questions:
                self.recent_questions.append({
                    'question': question.lower(),
                    'timestamp': datetime.now()
                })
        
        # Keep only recent questions (last 10)
        self.recent_questions = self.recent_questions[-10:]
    
    def is_question_repetitive(self, new_question: str) -> bool:
        """Check if a question is repetitive"""
        new_q_lower = new_question.lower()
        
        # Check for exact or very similar questions
        for recent_q in self.recent_questions:
            similarity = self._calculate_similarity(new_q_lower, recent_q['question'])
            if similarity > 0.7:  # 70% similarity threshold
                return True
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Simple similarity calculation"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def get_personalization_context(self) -> str:
        """Get context for personalizing responses"""
        context_parts = []
        
        if self.user_interests:
            interests_str = ", ".join(self.user_interests)
            context_parts.append(f"User interests: {interests_str}")
        
        if self.last_user_sentiment != "neutral":
            context_parts.append(f"User mood: {self.last_user_sentiment}")
        
        recent_topics = self._get_recent_topics()
        if recent_topics:
            topics_str = ", ".join(recent_topics)
            context_parts.append(f"Recent topics discussed: {topics_str}")
        
        return " | ".join(context_parts)
    
    def _get_recent_topics(self) -> List[str]:
        """Extract recent conversation topics"""
        if len(self.messages) < 2:
            return []
        
        # Simple topic extraction from recent messages
        recent_messages = self.messages[-6:]  # Last 3 exchanges
        topics = []
        
        for msg in recent_messages:
            content = msg['content'].lower()
            # Extract potential topics (nouns and meaningful words)
            words = content.split()
            meaningful_words = [w for w in words if len(w) > 4 and w.isalpha()]
            topics.extend(meaningful_words[:2])  # Take first 2 meaningful words
        
        return list(set(topics))[-5:]  # Return unique recent topics
    
    def get_messages(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """Get recent messages for API calls"""
        messages = [{"role": msg["role"], "content": msg["content"]} 
                   for msg in self.messages]
        
        if limit:
            return messages[-limit:]
        return messages
    
    def save_to_file(self, filename: Optional[str] = None):
        """Save conversation to file"""
        if not filename:
            timestamp = self.session_start.strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
        
        filepath = Config.CONVERSATIONS_DIR / filename
        
        conversation_data = {
            "session_start": self.session_start.isoformat(),
            "session_end": datetime.now().isoformat(),
            "total_tokens": self.total_tokens,
            "message_count": len(self.messages),
            "messages": self.messages
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Conversation saved to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return None
    
    def load_from_file(self, filepath: str):
        """Load conversation from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.messages = data.get("messages", [])
            self.total_tokens = data.get("total_tokens", 0)
            if "session_start" in data:
                self.session_start = datetime.fromisoformat(data["session_start"])
            
            logger.info(f"Conversation loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to load conversation: {e}")
            return False
    
    def clear(self):
        """Clear conversation history"""
        self.messages.clear()
        self.session_start = datetime.now()
        self.total_tokens = 0
        self.user_interests.clear()
        self.recent_questions.clear()
        self.conversation_topics.clear()
        self.last_user_sentiment = "neutral"
        logger.info("Conversation history cleared")

class OpenAITutor:
    """OpenAI GPT-based conversation tutor"""
    
    def __init__(self, api_key: str):
        if not OPENAI_AVAILABLE:
            raise RuntimeError("OpenAI library not available")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = Config.OPENAI_MODEL
        self.system_prompt = self._get_system_prompt()
        self.conversation_history = ConversationHistory()
        
        # Add system prompt to conversation
        self.conversation_history.add_message("system", self.system_prompt)
        
        logger.info(f"OpenAI tutor initialized with model: {self.model}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI tutor"""
        return """You are a curious and engaging conversation partner who loves meeting new people and learning about their lives. 

Your personality:
- Friendly, enthusiastic, and genuinely interested in the person you're talking to
- You remember what people tell you and refer back to previous conversations
- You ask thoughtful follow-up questions based on what someone shares
- You share your own thoughts and reactions naturally, like a real friend would
- You're spontaneous and creative in your responses - avoid repetitive patterns
- You express emotions and empathy appropriately

Conversation style:
- Avoid repetitive questions like "How are you?" or "What did you do today?" if you've asked recently
- Remember topics discussed and build on them ("You mentioned you love cooking - have you tried any new recipes?")
- Ask specific, personalized questions based on what you know about the person
- Naturally transition between topics like a real conversation
- Show genuine interest and curiosity about their experiences, thoughts, and feelings
- Keep responses conversational and natural (1-3 sentences usually)
- Be encouraging but not overly formal or teacher-like

Remember: You're not just a language tutor - you're a conversation partner who wants to get to know this person better through meaningful dialogue."""
    
    def get_response(self, user_input: str) -> Optional[str]:
        """Get AI response to user input with advanced conversation logic"""
        try:
            # Add user message to history
            self.conversation_history.add_message("user", user_input)
            
            # Prepare messages for API - keep more context for better personalization
            messages = self.conversation_history.get_messages(limit=15)
            
            # Add personalization context to system message
            personalization = self.conversation_history.get_personalization_context()
            if personalization:
                enhanced_system_prompt = f"{self.system_prompt}\n\nPersonalization context: {personalization}"
                # Update the system message
                if messages and messages[0]['role'] == 'system':
                    messages[0]['content'] = enhanced_system_prompt
            
            # Add conversation guidance based on recent patterns
            guidance = self._get_conversation_guidance()
            if guidance:
                messages.append({
                    "role": "system", 
                    "content": f"Conversation guidance: {guidance}"
                })
            
            # Make API call with higher creativity settings
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=150,
                temperature=0.9,  # Increased for more creativity
                frequency_penalty=0.8,  # Higher to prevent repetition
                presence_penalty=0.6   # Higher to encourage topic diversity
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Check for repetitive questions and regenerate if needed
            if self._is_response_repetitive(ai_response):
                logger.info("Detected repetitive response, regenerating...")
                return self._generate_alternative_response(user_input, messages)
            
            # Add AI response to history
            self.conversation_history.add_message("assistant", ai_response)
            
            # Update token usage
            if hasattr(response, 'usage'):
                self.conversation_history.total_tokens += response.usage.total_tokens
            
            logger.info(f"OpenAI response: {ai_response[:50]}...")
            return ai_response
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._get_fallback_response(user_input)
    
    def _get_conversation_guidance(self) -> str:
        """Generate conversation guidance based on recent patterns"""
        guidance_parts = []
        
        # Check message length patterns
        recent_user_messages = [msg['content'] for msg in self.conversation_history.messages[-6:] 
                               if msg['role'] == 'user']
        
        if recent_user_messages:
            avg_length = sum(len(msg.split()) for msg in recent_user_messages) / len(recent_user_messages)
            
            if avg_length < 5:
                guidance_parts.append("User gives short responses - ask more specific, engaging questions to encourage longer answers")
            elif avg_length > 20:
                guidance_parts.append("User is sharing detailed responses - ask follow-up questions about specific details they mentioned")
        
        # Check for user interests
        if self.conversation_history.user_interests:
            interests = list(self.conversation_history.user_interests)[-3:]  # Latest interests
            guidance_parts.append(f"Focus on user's interests: {', '.join(interests)}")
        
        # Sentiment-based guidance
        if self.conversation_history.last_user_sentiment == "positive":
            guidance_parts.append("User seems positive - maintain the upbeat energy")
        elif self.conversation_history.last_user_sentiment == "negative":
            guidance_parts.append("User seems down - be empathetic and supportive")
        
        return " | ".join(guidance_parts)
    
    def _is_response_repetitive(self, response: str) -> bool:
        """Check if the AI response is repetitive"""
        # Check for repetitive questions
        if '?' in response:
            questions = [q.strip() + '?' for q in response.split('?') if q.strip()]
            for question in questions:
                if self.conversation_history.is_question_repetitive(question):
                    return True
        
        # Check for repetitive phrases in recent AI responses
        recent_ai_responses = [msg['content'] for msg in self.conversation_history.messages[-6:] 
                              if msg['role'] == 'assistant']
        
        if len(recent_ai_responses) >= 2:
            for prev_response in recent_ai_responses:
                similarity = self.conversation_history._calculate_similarity(
                    response.lower(), prev_response.lower()
                )
                if similarity > 0.6:  # 60% similarity threshold
                    return True
        
        return False
    
    def _generate_alternative_response(self, user_input: str, original_messages: List[Dict]) -> str:
        """Generate an alternative response when the first one is repetitive"""
        try:
            # Add explicit instruction to avoid repetition
            alternative_messages = original_messages.copy()
            alternative_messages.append({
                "role": "system",
                "content": "The previous response was repetitive. Generate a completely different, creative response. Ask a unique question or make an original comment that hasn't been made before in this conversation."
            })
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=alternative_messages,
                max_tokens=150,
                temperature=1.0,  # Even higher creativity for alternatives
                frequency_penalty=1.0,
                presence_penalty=0.8
            )
            
            alternative_response = response.choices[0].message.content.strip()
            
            # Add to history
            self.conversation_history.add_message("assistant", alternative_response)
            
            if hasattr(response, 'usage'):
                self.conversation_history.total_tokens += response.usage.total_tokens
            
            logger.info(f"Alternative response generated: {alternative_response[:50]}...")
            return alternative_response
            
        except Exception as e:
            logger.error(f"Failed to generate alternative response: {e}")
            return self._get_fallback_response(user_input)
    
    def _get_fallback_response(self, user_input: str) -> str:
        """Provide intelligent fallback response when API fails"""
        # Try to use user interests for personalized fallbacks
        if hasattr(self, 'conversation_history') and self.conversation_history.user_interests:
            interests = list(self.conversation_history.user_interests)
            if 'cooking' in interests:
                return "Speaking of cooking, have you discovered any interesting flavor combinations lately?"
            elif 'travel' in interests:
                return "Your travel experiences sound fascinating! What's been your most memorable journey so far?"
            elif 'music' in interests:
                return "I'm curious about your music taste. What genre speaks to your soul?"
        
        # Sentiment-aware fallbacks
        if hasattr(self, 'conversation_history'):
            if self.conversation_history.last_user_sentiment == "positive":
                fallbacks = [
                    "Your enthusiasm is contagious! What else brings you joy?",
                    "That sounds wonderful! I'd love to hear more about what makes it special.",
                    "You seem really passionate about this - what got you interested in it?"
                ]
            elif self.conversation_history.last_user_sentiment == "negative":
                fallbacks = [
                    "That sounds challenging. How are you dealing with it?",
                    "I can understand why that would be frustrating. What helps you cope?",
                    "That must be tough. Is there anything positive you can take from the experience?"
                ]
            else:
                fallbacks = [
                    "That's fascinating! What's the story behind that?",
                    "I'm intrigued - what's your perspective on this?",
                    "That's an interesting angle. What led you to that conclusion?",
                    "Tell me more about that - I'm genuinely curious."
                ]
        else:
            fallbacks = [
                "That's fascinating! What's the story behind that?",
                "I'm intrigued - what's your perspective on this?",
                "That's an interesting angle. What led you to that conclusion?"
            ]
        
        import random
        return random.choice(fallbacks)

class OllamaTutor:
    """Ollama-based conversation tutor for local AI"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        if not REQUESTS_AVAILABLE:
            raise RuntimeError("Requests library not available")
        
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.conversation_history = ConversationHistory()
        self.system_prompt = self._get_system_prompt()
        
        # Test connection
        if not self._test_connection():
            raise RuntimeError(f"Cannot connect to Ollama at {base_url}")
        
        logger.info(f"Ollama tutor initialized with model: {model}")
    
    def _test_connection(self) -> bool:
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI tutor"""
        return """You are a curious and engaging conversation partner. Avoid repetitive questions. Remember previous topics. Ask follow-up questions based on user's interests. Be creative and spontaneous in your responses. Show genuine interest in the person you're talking to."""
    
    def get_response(self, user_input: str) -> Optional[str]:
        """Get AI response using Ollama"""
        try:
            # Add user message to history
            self.conversation_history.add_message("user", user_input)
            
            # Prepare conversation context
            context = self.system_prompt + "\n\n"
            recent_messages = self.conversation_history.get_messages(limit=6)
            
            for msg in recent_messages:
                if msg["role"] == "user":
                    context += f"Student: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    context += f"Tutor: {msg['content']}\n"
            
            context += "Tutor:"
            
            # Make API call to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": context,
                    "stream": False,
                    "options": {
                        "temperature": 0.9,
                        "top_p": 0.9,
                        "max_tokens": 100
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "").strip()
                
                # Clean up response
                if ai_response.startswith("Tutor:"):
                    ai_response = ai_response[6:].strip()
                
                # Add AI response to history
                self.conversation_history.add_message("assistant", ai_response)
                
                logger.info(f"Ollama response: {ai_response[:50]}...")
                return ai_response
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return self._get_fallback_response()
                
        except Exception as e:
            logger.error(f"Ollama connection error: {e}")
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Provide creative fallback response when Ollama fails"""
        creative_fallbacks = [
            "That sparks my curiosity! What's the most surprising thing about that?",
            "Fascinating perspective! How did you come to that realization?",
            "That's genuinely intriguing - what's the story behind it?",
            "I'm drawn to that topic. What aspect excites you most?",
            "Your experience sounds unique. What made it stand out?",
            "That's thought-provoking. What unexpected lessons did you learn?"
        ]
        
        import random
        return random.choice(creative_fallbacks)

class AITutorService:
    """Unified AI tutor service"""
    
    def __init__(self):
        self.tutor = None
        self.provider = Config.AI_PROVIDER.lower()
        self.is_available = False
        
        self._initialize_tutor()
    
    def _initialize_tutor(self):
        """Initialize the appropriate AI tutor"""
        try:
            if self.provider == "openai" and Config.OPENAI_API_KEY:
                self.tutor = OpenAITutor(Config.OPENAI_API_KEY)
                self.is_available = True
                logger.info("OpenAI tutor initialized")
                
            elif self.provider == "ollama":
                self.tutor = OllamaTutor(Config.OLLAMA_BASE_URL, Config.OLLAMA_MODEL)
                self.is_available = True
                logger.info("Ollama tutor initialized")
                
            else:
                logger.warning(f"No valid AI provider configured: {self.provider}")
                self.is_available = False
                
        except Exception as e:
            logger.error(f"Failed to initialize AI tutor: {e}")
            self.is_available = False
    
    def get_response(self, user_input: str) -> str:
        """Get AI response to user input"""
        if not self.is_available or not self.tutor:
            return self._get_default_response()
        
        response = self.tutor.get_response(user_input)
        return response or self._get_default_response()
    
    def _get_default_response(self) -> str:
        """Default response when AI is not available"""
        return "I'm sorry, I'm having trouble connecting to the AI service right now. Could you try again?"
    
    def get_conversation_history(self) -> ConversationHistory:
        """Get current conversation history"""
        if self.tutor:
            return self.tutor.conversation_history
        return ConversationHistory()
    
    def save_conversation(self, filename: Optional[str] = None) -> Optional[str]:
        """Save current conversation"""
        if self.tutor:
            return self.tutor.conversation_history.save_to_file(filename)
        return None
    
    def load_conversation(self, filepath: str) -> bool:
        """Load conversation from file"""
        if self.tutor:
            return self.tutor.conversation_history.load_from_file(filepath)
        return False
    
    def clear_conversation(self):
        """Clear current conversation"""
        if self.tutor:
            self.tutor.conversation_history.clear()
    
    def get_stats(self) -> Dict[str, any]:
        """Get conversation statistics"""
        if not self.tutor:
            return {}
        
        history = self.tutor.conversation_history
        user_messages = [msg for msg in history.messages if msg["role"] == "user"]
        ai_messages = [msg for msg in history.messages if msg["role"] == "assistant"]
        
        return {
            "provider": self.provider,
            "is_available": self.is_available,
            "total_messages": len(history.messages),
            "user_messages": len(user_messages),
            "ai_messages": len(ai_messages),
            "total_tokens": history.total_tokens,
            "session_duration": (datetime.now() - history.session_start).total_seconds(),
            "session_start": history.session_start.isoformat()
        }

# Conversation topics and prompts
class ConversationTopics:
    """Pre-defined conversation topics and starter prompts"""
    
    TOPICS = {
        "daily_life": {
            "name": "Daily Life & Routines",
            "starters": [
                "Tell me about your typical morning routine.",
                "What did you do last weekend?",
                "How do you usually spend your free time?",
                "What's your favorite part of the day and why?"
            ]
        },
        "travel": {
            "name": "Travel & Places",
            "starters": [
                "Have you traveled anywhere interesting recently?",
                "If you could visit any country, where would you go?",
                "Tell me about your hometown.",
                "What's the most beautiful place you've ever seen?"
            ]
        },
        "food": {
            "name": "Food & Cooking",
            "starters": [
                "What's your favorite food and why?",
                "Can you cook? What's your specialty?",
                "Tell me about a traditional dish from your country.",
                "What did you have for lunch today?"
            ]
        },
        "hobbies": {
            "name": "Hobbies & Interests",
            "starters": [
                "What do you like to do in your free time?",
                "Have you picked up any new hobbies recently?",
                "What's something you're passionate about?",
                "Do you prefer indoor or outdoor activities?"
            ]
        },
        "work_study": {
            "name": "Work & Study",
            "starters": [
                "What do you do for work or study?",
                "What's the most challenging part of your job/studies?",
                "What are your career goals?",
                "How do you stay motivated at work or school?"
            ]
        },
        "future_goals": {
            "name": "Goals & Dreams",
            "starters": [
                "What are you hoping to achieve this year?",
                "If you could learn any new skill, what would it be?",
                "Where do you see yourself in five years?",
                "What's one goal you're working towards right now?"
            ]
        }
    }
    
    @classmethod
    def get_random_starter(cls, topic: Optional[str] = None) -> str:
        """Get a random conversation starter"""
        import random
        
        if topic and topic in cls.TOPICS:
            return random.choice(cls.TOPICS[topic]["starters"])
        else:
            # Random topic
            all_starters = []
            for topic_data in cls.TOPICS.values():
                all_starters.extend(topic_data["starters"])
            return random.choice(all_starters)
    
    @classmethod
    def get_topic_list(cls) -> List[str]:
        """Get list of available topics"""
        return list(cls.TOPICS.keys())

# Test function
def test_ai_tutor():
    """Test AI tutor functionality"""
    print("Testing AI Tutor...")
    
    service = AITutorService()
    
    if not service.is_available:
        print("AI tutor not available")
        return False
    
    print(f"AI tutor initialized ({service.provider})")
    
    # Test conversation
    test_inputs = [
        "Hello, I want to practice English conversation.",
        "I'm learning English to improve my career opportunities.",
        "What topics should we talk about?"
    ]
    
    for user_input in test_inputs:
        print(f"\nUser: {user_input}")
        response = service.get_response(user_input)
        print(f"AI: {response}")
    
    # Test stats
    stats = service.get_stats()
    print(f"\nConversation stats: {stats}")
    
    return True

if __name__ == "__main__":
    # Run tests
    test_ai_tutor()