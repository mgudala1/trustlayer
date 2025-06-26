"""
Trust Atom creation module for TrustGraph implementation.

This module contains classes and functions for creating Trust Atoms,
the fundamental building blocks of the TrustGraph.
"""

import os
import json
import uuid
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TrustAtomCreator:
    """Create Trust Atoms from processed data."""
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize the TrustAtomCreator.
        
        Args:
            schema_path: Optional path to the Trust Atom schema for validation
        """
        self.schema = self._load_schema(schema_path) if schema_path else None
    
    def _load_schema(self, path: str) -> Dict[str, Any]:
        """
        Load the Trust Atom schema from a JSON file.
        
        Args:
            path: Path to the schema JSON file
            
        Returns:
            Schema as a dictionary
        """
        try:
            with open(path, "r") as f:
                schema = json.load(f)
            logger.info(f"Loaded Trust Atom schema from {path}")
            return schema
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading schema: {e}")
            # Return an empty schema as fallback
            return {}
    
    def create_trust_atom(self, 
                         feedback: Dict[str, Any], 
                         product_match_result: Tuple[Optional[str], Dict[str, Any]],
                         sentiment_result: Tuple[str, float],
                         tags: List[str],
                         summary: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a Trust Atom from processed data.
        
        Args:
            feedback: Processed feedback data
            product_match_result: Tuple of (product_id, match_info)
            sentiment_result: Tuple of (sentiment_label, confidence)
            tags: Extracted tags
            summary: Optional summary text
            
        Returns:
            Trust Atom as a dictionary
        """
        product_id, match_info = product_match_result
        sentiment_label, sentiment_confidence = sentiment_result
        
        # If no product match, use a fallback ID
        if not product_id:
            product_id = "unknown_product"
        
        # Generate a unique atom ID
        atom_id = f"{feedback.get('source', 'unknown')}_{product_id}_{uuid.uuid4().hex[:8]}"
        
        # Use provided summary or feedback text if summary is None
        summary_text = summary if summary is not None else feedback.get('text', '')
        
        # Calculate overall confidence score
        # Weighted average of match confidence and sentiment confidence
        match_score = match_info.get("match_score", 0.1)
        overall_confidence = 0.7 * match_score + 0.3 * sentiment_confidence
        
        # Calculate authenticity score or use provided one
        authenticity_score = feedback.get('authenticity_score', 0.5)
        
        # Create the Trust Atom
        atom = {
            "atom_id": atom_id,
            "product_id": product_id,
            "source": feedback.get('source', 'unknown'),
            "timestamp": feedback.get('timestamp', datetime.now().isoformat()),
            "feedback_text": feedback.get('text', ''),
            "summary_text": summary_text,
            "sentiment_label": sentiment_label,
            "authenticity_score": authenticity_score,
            "confidence_score": overall_confidence,
            "tags": tags,
            "metadata": {
                "username_hash": self._anonymize_username(feedback.get('username')),
                "upvotes": feedback.get('score', 0),
                "permalink": feedback.get('permalink', '')
            },
            "product_match_info": match_info,
            "source_specific_data": {}
        }
        
        # Add source-specific data
        source = feedback.get('source', '').lower()
        if source == 'reddit':
            atom["source_specific_data"]["reddit_data"] = {
                "subreddit": feedback.get('subreddit', ''),
                "post_title": feedback.get('post_title', ''),
                "post_score": feedback.get('post_score', 0)
            }
        elif source == 'youtube':
            atom["source_specific_data"]["youtube_data"] = {
                "video_title": feedback.get('video_title', ''),
                "channel_name": feedback.get('channel_name', ''),
                "video_views": feedback.get('video_views', 0),
                "timestamp_in_video": feedback.get('timestamp_in_video', '')
            }
        elif source == 'amazon':
            atom["source_specific_data"]["amazon_data"] = {
                "product_title": feedback.get('product_title', ''),
                "star_rating": feedback.get('star_rating', 0),
                "review_title": feedback.get('review_title', '')
            }
        
        # Validate the Trust Atom if schema is available
        if self.schema:
            self._validate_trust_atom(atom)
        
        return atom
    
    def _anonymize_username(self, username: Optional[str]) -> str:
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
    
    def _validate_trust_atom(self, atom: Dict[str, Any]) -> bool:
        """
        Validate a Trust Atom against the schema.
        
        Args:
            atom: Trust Atom to validate
            
        Returns:
            True if valid, False otherwise
        """
        # This is a basic validation that checks required fields
        # For production, use a proper JSON Schema validator
        
        if not self.schema:
            return True
        
        required_fields = self.schema.get("required", [])
        for field in required_fields:
            if field not in atom:
                logger.warning(f"Trust Atom missing required field: {field}")
                return False
        
        return True
    
    def save_trust_atom(self, atom: Dict[str, Any], output_path: str) -> bool:
        """
        Save a Trust Atom to a JSON file.
        
        Args:
            atom: Trust Atom to save
            output_path: Path to save the Trust Atom
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Load existing data if file exists
            existing_data = []
            if os.path.exists(output_path):
                with open(output_path, "r") as f:
                    existing_data = json.load(f)
            
            # Add new Trust Atom
            existing_data.append(atom)
            
            # Save updated data
            with open(output_path, "w") as f:
                json.dump(existing_data, f, indent=2)
            
            logger.info(f"Saved Trust Atom {atom['atom_id']} to {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving Trust Atom: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Create a sample feedback
    sample_feedback = {
        "text": "I love the CeraVe cleanser! It works great on my oily skin.",
        "source": "reddit",
        "timestamp": "2025-06-26T15:30:00Z",
        "username": "user123",
        "score": 10,
        "permalink": "https://www.reddit.com/r/SkincareAddiction/comments/example/",
        "subreddit": "SkincareAddiction",
        "post_title": "Favorite Cleansers",
        "post_score": 100
    }
    
    # Create sample product match result
    product_match_result = (
        "cerave_foaming_cleanser_12oz",
        {
            "match_method": "exact_alias",
            "match_score": 0.9,
            "alternative_matches": [],
            "context_factors": {
                "brand_mentioned": True,
                "product_type_mentioned": True,
                "identifier_mentioned": False
            }
        }
    )
    
    # Create sample sentiment result
    sentiment_result = ("positive", 0.8)
    
    # Create sample tags
    tags = ["skincare", "cleanser", "oily"]
    
    # Create sample summary
    summary = "Works great on oily skin."
    
    # Create Trust Atom creator
    creator = TrustAtomCreator()
    
    # Create Trust Atom
    trust_atom = creator.create_trust_atom(
        sample_feedback,
        product_match_result,
        sentiment_result,
        tags,
        summary
    )
    
    # Print Trust Atom
    print(json.dumps(trust_atom, indent=2))
    
    # Save to a temporary file
    temp_output_path = "temp_trust_atom.json"
    creator.save_trust_atom(trust_atom, temp_output_path)
    
    # Clean up
    if os.path.exists(temp_output_path):
        os.remove(temp_output_path)