"""
Content analysis module for TrustGraph implementation.

This module contains classes and functions for analyzing content,
including sentiment analysis, tag extraction, and summary generation.
"""

import re
import logging
from typing import Dict, List, Tuple, Any, Optional, Set

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import transformers for summarization
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers library not available. Summarization will use fallback method.")


class ContentAnalyzer:
    """Analyze content for sentiment, tags, and generate summaries."""
    
    def __init__(self, use_ml_models: bool = True):
        """
        Initialize the ContentAnalyzer.
        
        Args:
            use_ml_models: Whether to use ML models for analysis
        """
        self.use_ml_models = use_ml_models and TRANSFORMERS_AVAILABLE
        
        # Initialize summarization model if available
        self.summarizer = None
        if self.use_ml_models:
            try:
                self.summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")
                logger.info("Initialized summarization model")
            except Exception as e:
                logger.error(f"Error initializing summarization model: {e}")
                self.summarizer = None
        
        # Load category-specific tag dictionaries
        self.tag_dictionaries = self._load_tag_dictionaries()
    
    def _load_tag_dictionaries(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Load category-specific tag dictionaries.
        
        Returns:
            Dictionary of category-specific tag dictionaries
        """
        return {
            "skincare": {
                "skin_types": ["oily", "dry", "combination", "sensitive", "acne-prone"],
                "concerns": ["acne", "wrinkles", "redness", "dark spots", "blackheads", "pores"],
                "ingredients": ["retinol", "vitamin c", "hyaluronic acid", "niacinamide", "salicylic acid", 
                               "benzoyl peroxide", "ceramides", "peptides", "aha", "bha"]
            },
            "food": {
                "flavors": ["sweet", "savory", "spicy", "bitter", "sour", "umami"],
                "dietary": ["vegan", "gluten-free", "keto", "organic", "non-gmo", "paleo", "vegetarian"],
                "texture": ["crunchy", "smooth", "creamy", "crispy", "chewy", "soft"]
            },
            "household": {
                "features": ["eco-friendly", "biodegradable", "reusable", "disposable", "concentrated"],
                "concerns": ["stains", "odor", "germs", "bacteria", "allergens", "dust"],
                "surfaces": ["carpet", "wood", "glass", "tile", "fabric", "metal", "plastic"]
            }
        }
    
    def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """
        Analyze sentiment of text using a hybrid approach.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (sentiment_label, confidence)
        """
        # Rule-based approach for clear sentiment indicators
        positive_keywords = ["love", "great", "excellent", "amazing", "perfect", "recommend", 
                            "awesome", "fantastic", "wonderful", "best", "favorite", "worth"]
        negative_keywords = ["hate", "terrible", "awful", "disappointing", "waste", "avoid", 
                            "bad", "worst", "horrible", "useless", "regret", "return"]
        
        text_lower = text.lower()
        
        # Count sentiment keywords
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        
        # Rule-based decision with confidence
        if positive_count > 0 and negative_count == 0:
            confidence = min(0.5 + (positive_count * 0.1), 0.9)
            return "positive", confidence
        elif negative_count > 0 and positive_count == 0:
            confidence = min(0.5 + (negative_count * 0.1), 0.9)
            return "negative", confidence
        elif positive_count > 0 and negative_count > 0:
            # Mixed sentiment
            if positive_count > negative_count:
                return "mixed", 0.7
            elif negative_count > positive_count:
                return "mixed", 0.7
            else:
                return "mixed", 0.6
        
        # Check for neutral indicators
        neutral_keywords = ["okay", "ok", "fine", "average", "decent", "alright", "so-so"]
        neutral_count = sum(1 for word in neutral_keywords if word in text_lower)
        if neutral_count > 0:
            return "neutral", 0.7
        
        # Default to neutral with low confidence
        return "neutral", 0.5
    
    def extract_tags(self, text: str, category: str = "skincare") -> List[str]:
        """
        Extract relevant tags from text based on category.
        
        Args:
            text: Text to analyze
            category: Product category
            
        Returns:
            List of extracted tags
        """
        tags: Set[str] = set()
        text_lower = text.lower()
        
        # Get relevant dictionaries for the category
        category_dict = self.tag_dictionaries.get(category, {})
        
        # Check for matches in each tag type
        for tag_type, tag_list in category_dict.items():
            for tag in tag_list:
                # Check for exact word match with word boundaries
                pattern = r'\b' + re.escape(tag) + r'\b'
                if re.search(pattern, text_lower):
                    tags.add(tag)
        
        # Add category as a tag if not already included
        tags.add(category)
        
        return list(tags)
    
    def generate_summary(self, text: str, max_length: int = 30, min_length: int = 5) -> str:
        """
        Generate a summary of the text.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary in words
            min_length: Minimum length of summary in words
            
        Returns:
            Generated summary
        """
        # Check if text is too short to summarize
        if len(text.split()) <= max_length:
            return text
        
        # Use transformers if available
        if self.summarizer:
            try:
                summary = self.summarizer("summarize: " + text, max_length=max_length, 
                                         min_length=min_length, do_sample=False)[0]["summary_text"]
                return summary
            except Exception as e:
                logger.error(f"Error generating summary with model: {e}")
                # Fall back to rule-based method
        
        # Rule-based fallback method
        return self._rule_based_summary(text, max_length)
    
    def _rule_based_summary(self, text: str, max_length: int = 30) -> str:
        """
        Generate a summary using rule-based methods.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary in words
            
        Returns:
            Generated summary
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+\s+', text)
        
        # Remove very short sentences
        sentences = [s for s in sentences if len(s.split()) > 3]
        
        if not sentences:
            return text
        
        # Take the first sentence as the base summary
        summary = sentences[0]
        
        # If the first sentence is too short, add more sentences
        words = summary.split()
        sentence_index = 1
        
        while len(words) < max_length and sentence_index < len(sentences):
            next_sentence = sentences[sentence_index]
            next_words = next_sentence.split()
            
            # Check if adding the next sentence would exceed max_length
            if len(words) + len(next_words) <= max_length:
                summary += ". " + next_sentence
                words.extend(next_words)
            
            sentence_index += 1
        
        return summary
    
    def calculate_authenticity(self, feedback: Dict[str, Any]) -> float:
        """
        Calculate authenticity score for feedback.
        
        Args:
            feedback: Feedback data
            
        Returns:
            Authenticity score between 0 and 1
        """
        # Start with a base score
        score = 0.5
        
        # Adjust based on source
        source = feedback.get("source", "").lower()
        if source == "reddit":
            # Reddit comments with higher scores are more likely to be authentic
            upvotes = feedback.get("score", 0)
            if upvotes > 10:
                score += 0.1
            elif upvotes > 50:
                score += 0.2
            
            # Account for account age if available
            if feedback.get("account_age_days"):
                account_age = feedback.get("account_age_days", 0)
                if account_age > 365:  # Older than a year
                    score += 0.1
        
        elif source == "youtube":
            # Similar adjustments for YouTube
            likes = feedback.get("score", 0)
            if likes > 5:
                score += 0.1
            elif likes > 20:
                score += 0.2
        
        # Check for verified purchase if available
        if feedback.get("verified_purchase"):
            score += 0.2
        
        # Check text length - very short feedback might be less authentic
        text_length = len(feedback.get("text", "").split())
        if text_length < 5:
            score -= 0.1
        elif text_length > 30:
            score += 0.1
        
        # Cap the score between 0.1 and 1.0
        return max(0.1, min(score, 1.0))


# Example usage
if __name__ == "__main__":
    analyzer = ContentAnalyzer()
    
    # Test sentiment analysis
    text1 = "I absolutely love this cleanser! It works great on my oily skin and doesn't cause breakouts."
    sentiment1, confidence1 = analyzer.analyze_sentiment(text1)
    print(f"Sentiment 1: {sentiment1} with confidence {confidence1}")
    
    text2 = "This product was terrible. It dried out my skin and caused a rash."
    sentiment2, confidence2 = analyzer.analyze_sentiment(text2)
    print(f"Sentiment 2: {sentiment2} with confidence {confidence2}")
    
    text3 = "It's okay. Not great, not terrible. Does the job but I probably won't buy again."
    sentiment3, confidence3 = analyzer.analyze_sentiment(text3)
    print(f"Sentiment 3: {sentiment3} with confidence {confidence3}")
    
    # Test tag extraction
    tags1 = analyzer.extract_tags(text1, "skincare")
    print(f"Tags 1: {tags1}")
    
    # Test summary generation
    long_text = """
    I've been using this CeraVe Foaming Facial Cleanser for about three months now, and I'm really impressed with the results.
    My skin tends to be quite oily, especially in the T-zone, and I've struggled with finding a cleanser that effectively removes
    oil and dirt without stripping my skin completely. This cleanser strikes that perfect balance. It foams up nicely and a little
    goes a long way, so the bottle lasts quite a while. After washing, my skin feels clean but not tight or dry. I've noticed fewer
    breakouts since I started using it, and my skin tone seems more even. The formula contains ceramides and hyaluronic acid, which
    I think helps maintain my skin barrier. It's fragrance-free, which is great for sensitive skin. The price point is also reasonable
    compared to other skincare brands with similar quality. I use it twice daily, morning and night, as part of my skincare routine.
    Overall, I would definitely recommend this to anyone with combination to oily skin looking for an effective, gentle cleanser.
    """
    
    summary = analyzer.generate_summary(long_text)
    print(f"Summary: {summary}")