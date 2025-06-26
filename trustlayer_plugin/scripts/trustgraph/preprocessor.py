"""
Data preprocessing module for TrustGraph implementation.

This module contains classes and functions for preprocessing raw data
from various sources before further processing.
"""

import re
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional


class DataPreprocessor:
    """Preprocess raw data for further processing in the TrustGraph pipeline."""
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text for further processing.
        
        Args:
            text: Raw text from comment or post
            
        Returns:
            Preprocessed text with URLs and special characters removed
        """
        if not text:
            return ""
            
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove special characters but keep apostrophes for contractions
        text = re.sub(r'[^\w\s\']', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def process_reddit_comment(self, comment: Dict[str, Any], post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a Reddit comment into a standardized format.
        
        Args:
            comment: Raw Reddit comment data
            post_data: Data about the parent post
            
        Returns:
            Processed comment data in a standardized format
        """
        # Extract the comment body
        body = comment.get("body", "")
        
        # Clean the text
        cleaned_text = self.clean_text(body)
        
        # Convert timestamp to ISO format if it's a numeric timestamp
        timestamp = comment.get("created_utc")
        if isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp).isoformat()
        
        return {
            "text": cleaned_text,
            "source": "reddit",
            "timestamp": timestamp,
            "username": comment.get("author"),
            "score": comment.get("score", 0),
            "permalink": post_data.get("permalink"),
            "subreddit": post_data.get("subreddit"),
            "post_title": post_data.get("title"),
            "post_score": post_data.get("score", 0),
            "comment_id": comment.get("id")
        }
    
    def process_youtube_comment(self, comment: Dict[str, Any], video_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a YouTube comment into a standardized format.
        
        Args:
            comment: Raw YouTube comment data
            video_data: Data about the parent video
            
        Returns:
            Processed comment data in a standardized format
        """
        # Extract the comment text
        text = comment.get("text", "")
        
        # Clean the text
        cleaned_text = self.clean_text(text)
        
        # Convert timestamp to ISO format if needed
        timestamp = comment.get("published_at")
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        return {
            "text": cleaned_text,
            "source": "youtube",
            "timestamp": timestamp,
            "username": comment.get("author"),
            "score": comment.get("like_count", 0),
            "permalink": comment.get("url"),
            "video_title": video_data.get("title"),
            "channel_name": video_data.get("channel_name"),
            "video_views": video_data.get("view_count", 0),
            "timestamp_in_video": comment.get("timestamp_in_video"),
            "comment_id": comment.get("id")
        }
    
    def segment_text(self, text: str) -> Dict[str, Any]:
        """
        Segment text into sentences and paragraphs.
        
        Args:
            text: Preprocessed text
            
        Returns:
            Dictionary with full text, paragraphs, and sentences
        """
        # Simple paragraph splitting by newlines
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        # Simple sentence splitting by periods, question marks, and exclamation points
        # This is a basic implementation; for production, use a proper NLP library like nltk
        sentence_pattern = r'[.!?]+\s+'
        sentences = [s.strip() for s in re.split(sentence_pattern, text) if s.strip()]
        
        return {
            "full_text": text,
            "paragraphs": paragraphs,
            "sentences": sentences
        }
    
    def anonymize_username(self, username: Optional[str]) -> str:
        """
        Anonymize a username using SHA-256 hashing.
        
        Args:
            username: Username to anonymize
            
        Returns:
            Anonymized username hash
        """
        if not username:
            return "sha256:anonymous"
        
        # Create a SHA-256 hash of the username
        hash_obj = hashlib.sha256(username.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Return a truncated hash with prefix
        return f"sha256:{hash_hex[:16]}"


# Example usage
if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    
    # Example Reddit comment
    sample_comment = {
        "body": "This CeraVe cleanser worked great on my oily skin. https://example.com",
        "author": "user123",
        "created_utc": 1750346703.0,
        "score": 5,
        "id": "abc123"
    }
    
    sample_post = {
        "permalink": "https://www.reddit.com/r/SkincareAddiction/comments/example/",
        "subreddit": "SkincareAddiction",
        "title": "Product Recommendations",
        "score": 100
    }
    
    processed = preprocessor.process_reddit_comment(sample_comment, sample_post)
    print(f"Processed comment: {processed}")
    
    # Test text cleaning
    dirty_text = "Check out this product: https://example.com/product?id=123 It's amazing!!!"
    clean_text = preprocessor.clean_text(dirty_text)
    print(f"Clean text: {clean_text}")