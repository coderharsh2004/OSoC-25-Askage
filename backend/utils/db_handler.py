import secrets
from pymongo import MongoClient
from bson import ObjectId


class MongoHandler:
    """
    Handles MongoDB operations.
    """
    
    _instance = None
    db = None


    def __new__(cls, uri):
        if cls._instance is None:
            cls._instance = super(MongoHandler, cls).__new__(cls)
            cls._client = MongoClient(uri)
            cls.db = cls._client["askage"]
            
        return cls._instance
    
    
    def generate_session_token(self) -> str:
        """
        Generates a unique session token.
        """
        return secrets.token_hex(16)
    
    
    def register_google_user(
        self,
        google_sub: str,
        email: str
    ) -> str:
        """
        Adds user details to registered users in Database.
        Returns: auth_token
        """

        if not google_sub or not email: raise Exception

        collection = self.db["users"]
        session_token = self.generate_session_token()

        existing_user = collection.find_one({"google_sub": google_sub})

        if existing_user:
            collection.update_one(
                {"_id": existing_user["_id"]},
                {"$set": {"session_token": session_token, "email": email}}
            )
            
            return f"{str(existing_user['_id'])}:{session_token}"
        
        else:
            result = collection.insert_one({
                "google_sub": google_sub,
                "session_token": session_token,
                "email": email
            })
            
            return f"{str(result.inserted_id)}:{session_token}"
        
        
    def new_conversation(
        self,
        user_id: str,
        suggestions: list[str]
    ) -> str:
        """
        Creates a new conversation in Database.
        Returns: conversation_id
        """
        
        try:
            collection = self.db["conversations"]
            
            result = collection.insert_one({
                "user_id": user_id,
                "history": [{
                    "role": "system",
                    "content": "You are Askage, a Chrome extension that answers user questions based on webpage content. Always be polite, but reply with only the necessary information. Use minimal words, avoid complete sentences unless required. No explanations unless asked. Use plain text, no markdown or formatting. Paragraph form only. No bullet points, no lists."
                }],
                "prompt_suggestions": suggestions
            })
            
            return str(result.inserted_id)
        
        except Exception as e:
            raise Exception(f"MongoDB error: {e}")
        
    def get_prompt_suggestions(
        self,
        user_id: str,
        conversation_id: str
    ) -> list[str]:
        """
        Fetches prompt suggestions for specified conversation.
        Returns: suggestions
        """
        
        try:
            collection = self.db["conversations"]
            
            result = collection.find_one({
                "_id": ObjectId(conversation_id),
                "user_id": user_id
            })
            
            return result["prompt_suggestions"]
        
        except Exception as e:
            raise Exception(f"MongoDB error: {e}")
        
    def get_chat_history(
        self,
        user_id: str,
        conversation_id: str
    ) -> list[dict]:
        """
        Fetches chat history of conversation.
        Returns: Chat history
        """
        
        try:
            collection = self.db["conversations"]
            
            result = collection.find_one({
                "_id": ObjectId(conversation_id),
                "user_id": user_id
            })
            
            return result["history"]
        
        except Exception as e:
            raise Exception(f"MongoDB error: {e}")
        
    def update_chat_history(
        self,
        user_id: str,
        conversation_id: str,
        history: list
    ) -> bool:
        """
        Updates chat history of conversation.
        Returns: Updated?
        """
        
        try:
            collection = self.db["conversations"]
            
            result = collection.update_one({
                "_id": ObjectId(conversation_id),
                "user_id": user_id
            }, {
                "$set": {"history": history}
            })
            
            return result.matched_count > 0
        
        except Exception as e:
            raise Exception(f"MongoDB error: {e}")
    
    
    def verify_auth_token(self, user_id: str, session_token: str) -> bool:
        """
        Verifies if the provided session token is valid for the given user.
        """
        
        collection = self.db["users"]
        user_doc = collection.find_one({"_id": ObjectId(user_id)})
        
        return ((user_doc is not None) and (user_doc.get("session_token", "") == session_token))
    
    
    def verify_conversation(self, user_id: str, conversation_id: str) -> bool:
        """
        Verifies if the given conversation exists for the given user.

        :param user_id: The ID of the user.
        :param conversation_id: The ID of the conversation to verify.

        :return: True if the conversation exists for the user, False otherwise.

        Raises:
            Exception: If any error occurs or the conversation_id is invalid.
        """
        
        try:
            collection = self.db["conversations"]
            
            result = collection.find_one({
                "_id": ObjectId(conversation_id),
                "user_id": user_id
            })
            
            return result is not None
        
        except Exception as e:
            raise Exception(f"Error: {e}")
