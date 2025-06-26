"""
Product matching module for TrustGraph implementation.

This module contains classes and functions for matching product mentions
to canonical products in the product registry using a multi-stage approach.
"""

import os
import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional, Union
from difflib import SequenceMatcher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ProductMatcher:
    """Match product mentions to canonical products using a multi-stage approach."""
    
    def __init__(self, product_registry_path: str, embeddings_path: Optional[str] = None):
        """
        Initialize the ProductMatcher with a product registry.
        
        Args:
            product_registry_path: Path to the product registry JSON file
            embeddings_path: Optional path to pre-computed product embeddings
        """
        self.product_registry = self._load_product_registry(product_registry_path)
        self.embeddings = self._load_embeddings(embeddings_path) if embeddings_path else None
        self.unmatched_log_path = os.path.join(
            os.path.dirname(product_registry_path), 
            "registry_suggestions.json"
        )
    
    def _load_product_registry(self, path: str) -> Dict[str, Any]:
        """
        Load the product registry from a JSON file.
        
        Args:
            path: Path to the product registry JSON file
            
        Returns:
            Product registry as a dictionary
        """
        try:
            with open(path, "r") as f:
                registry = json.load(f)
            logger.info(f"Loaded product registry with {len(registry)} products")
            return registry
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading product registry: {e}")
            # Return an empty registry as fallback
            return {}
    
    def _load_embeddings(self, path: str) -> Dict[str, List[float]]:
        """
        Load pre-computed product embeddings.
        
        Args:
            path: Path to the embeddings JSON file
            
        Returns:
            Product embeddings as a dictionary
        """
        try:
            with open(path, "r") as f:
                embeddings = json.load(f)
            logger.info(f"Loaded embeddings for {len(embeddings)} products")
            return embeddings
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading embeddings: {e}")
            # Return empty embeddings as fallback
            return {}
    
    def match_product(self, text: str, context: Optional[Dict[str, Any]] = None) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Match a product mention using the multi-stage algorithm.
        
        Args:
            text: Text containing the product mention
            context: Optional additional context for the mention
            
        Returns:
            Tuple of (product_id, match_info) or (None, match_info) if no match
        """
        # Stage 1: Exact Alias Match (highest confidence)
        product_id, confidence = self.exact_alias_match(text)
        if product_id and confidence > 0.8:
            match_info = self._create_match_info("exact_alias", confidence, text, context)
            return product_id, match_info
        
        # Stage 2: Fuzzy Brand + Product Match
        product_id, confidence = self.fuzzy_brand_product_match(text)
        if product_id and confidence > 0.6:
            match_info = self._create_match_info("fuzzy_brand_product", confidence, text, context)
            return product_id, match_info
        
        # Stage 3: Semantic Similarity (if embeddings available)
        if self.embeddings:
            product_id, confidence = self.semantic_similarity_match(text)
            if product_id and confidence > 0.5:
                match_info = self._create_match_info("semantic_similarity", confidence, text, context)
                return product_id, match_info
        
        # No match found, log the unmatched mention
        self.log_unmatched(text)
        
        # Return a fallback with very low confidence
        match_info = {
            "match_method": "fallback",
            "match_score": 0.1,
            "alternative_matches": [],
            "context_factors": {
                "brand_mentioned": False,
                "product_type_mentioned": False,
                "identifier_mentioned": False
            }
        }
        return None, match_info
    
    def exact_alias_match(self, text: str) -> Tuple[Optional[str], float]:
        """
        Perform exact matching against product aliases.
        
        Args:
            text: Text to match
            
        Returns:
            Tuple of (product_id, confidence) or (None, 0) if no match
        """
        text_lower = text.lower()
        
        for product_id, product in self.product_registry.items():
            # Check canonical name
            canonical_name = product.get("canonical_name", "").lower()
            if canonical_name and canonical_name in text_lower:
                return product_id, 0.95
            
            # Check aliases
            for alias in product.get("aliases", []):
                if alias.lower() in text_lower:
                    return product_id, 0.9
        
        return None, 0
    
    def fuzzy_brand_product_match(self, text: str) -> Tuple[Optional[str], float]:
        """
        Perform fuzzy matching with brand detection.
        
        Args:
            text: Text to match
            
        Returns:
            Tuple of (product_id, confidence) or (None, 0) if no match
        """
        text_lower = text.lower()
        best_match = None
        best_score = 0
        
        # First detect if any brands are mentioned
        mentioned_brands = []
        for product_id, product in self.product_registry.items():
            brand = product.get("brand", "").lower()
            if brand and brand in text_lower:
                mentioned_brands.append(brand)
        
        # If brands found, prioritize products from those brands
        if mentioned_brands:
            for product_id, product in self.product_registry.items():
                if product.get("brand", "").lower() in mentioned_brands:
                    # Use fuzzy matching on product name
                    canonical = product.get("canonical_name", "").lower()
                    score = self._fuzzy_match_score(canonical, text_lower)
                    
                    # Boost score for brand match
                    score = score * 1.2
                    
                    if score > best_score:
                        best_score = score
                        best_match = product_id
        else:
            # No brand detected, try fuzzy matching on all products
            for product_id, product in self.product_registry.items():
                canonical = product.get("canonical_name", "").lower()
                score = self._fuzzy_match_score(canonical, text_lower)
                
                if score > best_score:
                    best_score = score
                    best_match = product_id
        
        # Normalize score to 0-1 range
        normalized_score = min(best_score, 1.0)
        
        return best_match, normalized_score
    
    def semantic_similarity_match(self, text: str) -> Tuple[Optional[str], float]:
        """
        Use vector embeddings to find semantically similar products.
        
        Args:
            text: Text to match
            
        Returns:
            Tuple of (product_id, confidence) or (None, 0) if no match
        """
        # This is a placeholder for semantic matching
        # In a real implementation, you would:
        # 1. Get embedding for the mention text using a model
        # 2. Compare with all product embeddings using cosine similarity
        # 3. Return the best match
        
        # For now, return None to fall back to other methods
        return None, 0
    
    def _fuzzy_match_score(self, str1: str, str2: str) -> float:
        """
        Calculate fuzzy match score between two strings.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Match score between 0 and 1
        """
        # Use SequenceMatcher for fuzzy matching
        matcher = SequenceMatcher(None, str1, str2)
        return matcher.ratio()
    
    def _create_match_info(self, method: str, score: float, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create match info dictionary.
        
        Args:
            method: Matching method used
            score: Match confidence score
            text: Original text
            context: Additional context
            
        Returns:
            Match info dictionary
        """
        # Determine context factors
        brand_mentioned = False
        product_type_mentioned = False
        identifier_mentioned = False
        
        # Check for brand mentions
        for product_id, product in self.product_registry.items():
            brand = product.get("brand", "").lower()
            if brand and brand in text.lower():
                brand_mentioned = True
                break
        
        # Check for product type mentions
        for product_id, product in self.product_registry.items():
            product_type = product.get("type", "").lower()
            if product_type and product_type in text.lower():
                product_type_mentioned = True
                break
        
        # Check for identifier mentions (UPC, ASIN, etc.)
        for product_id, product in self.product_registry.items():
            identifiers = product.get("identifiers", {})
            for id_type, id_value in identifiers.items():
                if id_value and id_value in text:
                    identifier_mentioned = True
                    break
            if identifier_mentioned:
                break
        
        # Get alternative matches
        alternative_matches = self._get_alternative_matches(text)
        
        return {
            "match_method": method,
            "match_score": score,
            "alternative_matches": alternative_matches,
            "context_factors": {
                "brand_mentioned": brand_mentioned,
                "product_type_mentioned": product_type_mentioned,
                "identifier_mentioned": identifier_mentioned
            }
        }
    
    def _get_alternative_matches(self, text: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get alternative product matches with lower confidence.
        
        Args:
            text: Text to match
            limit: Maximum number of alternatives to return
            
        Returns:
            List of alternative matches
        """
        alternatives = []
        text_lower = text.lower()
        
        # Get all products with their match scores
        all_matches = []
        for product_id, product in self.product_registry.items():
            canonical = product.get("canonical_name", "").lower()
            score = self._fuzzy_match_score(canonical, text_lower)
            all_matches.append((product_id, score))
        
        # Sort by score descending
        all_matches.sort(key=lambda x: x[1], reverse=True)
        
        # Take top matches (excluding the best match)
        for product_id, score in all_matches[1:limit+1]:
            alternatives.append({
                "product_id": product_id,
                "score": score
            })
        
        return alternatives
    
    def log_unmatched(self, text: str) -> None:
        """
        Log unmatched product mentions for future registry expansion.
        
        Args:
            text: Unmatched product mention
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.unmatched_log_path), exist_ok=True)
        
        # Load existing suggestions
        suggestions = []
        if os.path.exists(self.unmatched_log_path):
            try:
                with open(self.unmatched_log_path, "r") as f:
                    suggestions = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                suggestions = []
        
        # Add new suggestion
        suggestions.append({
            "mention_text": text,
            "timestamp": datetime.now().isoformat(),
            "status": "unprocessed"
        })
        
        # Save updated suggestions
        try:
            with open(self.unmatched_log_path, "w") as f:
                json.dump(suggestions, f, indent=2)
            logger.info(f"Logged unmatched mention: {text[:50]}...")
        except Exception as e:
            logger.error(f"Error logging unmatched mention: {e}")


# Example usage
if __name__ == "__main__":
    # Create a sample product registry
    sample_registry = {
        "cerave_foaming_cleanser_12oz": {
            "product_id": "cerave_foaming_cleanser_12oz",
            "canonical_name": "CeraVe Foaming Facial Cleanser",
            "brand": "CeraVe",
            "category": "skincare",
            "type": "cleanser",
            "aliases": [
                "cerave foaming cleanser",
                "cerave face wash",
                "cerave foaming cleanser 12oz",
                "cerave cleanser"
            ],
            "identifiers": {
                "asin": "B01N1LL62W",
                "upc": "301871239012"
            }
        },
        "neutrogena_hydro_boost": {
            "product_id": "neutrogena_hydro_boost",
            "canonical_name": "Neutrogena Hydro Boost Water Gel",
            "brand": "Neutrogena",
            "category": "skincare",
            "type": "moisturizer",
            "aliases": [
                "neutrogena hydro boost",
                "hydro boost gel",
                "neutrogena water gel"
            ],
            "identifiers": {
                "asin": "B00AQ4ROX0"
            }
        }
    }
    
    # Save sample registry to a temporary file
    temp_registry_path = "temp_registry.json"
    with open(temp_registry_path, "w") as f:
        json.dump(sample_registry, f, indent=2)
    
    # Create matcher
    matcher = ProductMatcher(temp_registry_path)
    
    # Test exact match
    text1 = "I love the CeraVe Foaming Facial Cleanser for my oily skin"
    product_id1, match_info1 = matcher.match_product(text1)
    print(f"Match 1: {product_id1} with score {match_info1['match_score']}")
    
    # Test fuzzy match
    text2 = "The Neutrogena gel is great for hydration"
    product_id2, match_info2 = matcher.match_product(text2)
    print(f"Match 2: {product_id2} with score {match_info2['match_score']}")
    
    # Test no match
    text3 = "I prefer using natural oils for my skin"
    product_id3, match_info3 = matcher.match_product(text3)
    print(f"Match 3: {product_id3} with score {match_info3['match_score']}")
    
    # Clean up
    os.remove(temp_registry_path)
    if os.path.exists(os.path.join(os.path.dirname(temp_registry_path), "registry_suggestions.json")):
        os.remove(os.path.join(os.path.dirname(temp_registry_path), "registry_suggestions.json"))