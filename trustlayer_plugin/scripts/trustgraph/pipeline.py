"""
Main pipeline module for TrustGraph implementation.

This module contains the main pipeline class that orchestrates
all the components of the TrustGraph implementation.
"""

import os
import json
import logging
from typing import Dict, List, Tuple, Any, Optional, Union

from .preprocessor import DataPreprocessor
from .product_matcher import ProductMatcher
from .content_analyzer import ContentAnalyzer
from .trust_atom_creator import TrustAtomCreator
from .storage import TrustAtomStorage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TrustGraphPipeline:
    """Main pipeline for processing data and creating Trust Atoms."""
    
    def __init__(self, 
                product_registry_path: str = "trustlayer_plugin/data/registry/product_registry_detailed.json",
                embeddings_path: Optional[str] = None,
                schema_path: Optional[str] = "trustlayer_plugin/data/trust_atom.schema.json",
                base_storage_path: str = "trustlayer_plugin/data"):
        """
        Initialize the TrustGraphPipeline.
        
        Args:
            product_registry_path: Path to the product registry JSON file
            embeddings_path: Optional path to pre-computed product embeddings
            schema_path: Optional path to the Trust Atom schema
            base_storage_path: Base path for storage
        """
        # Initialize components
        self.preprocessor = DataPreprocessor()
        self.product_matcher = ProductMatcher(product_registry_path, embeddings_path)
        self.content_analyzer = ContentAnalyzer()
        self.trust_atom_creator = TrustAtomCreator(schema_path)
        self.storage = TrustAtomStorage(base_storage_path)
        
        logger.info("Initialized TrustGraphPipeline")
    
    def process_reddit_data(self, 
                           input_path: str, 
                           output_path: Optional[str] = None, 
                           max_items: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Process Reddit data and create Trust Atoms.
        
        Args:
            input_path: Path to the input JSON file
            output_path: Optional path to the output file (for backward compatibility)
            max_items: Maximum number of items to process
            
        Returns:
            List of created Trust Atoms
        """
        logger.info(f"Processing Reddit data from {input_path}")
        
        # Load input data
        try:
            with open(input_path, "r") as f:
                raw_data = json.load(f)
            logger.info(f"Loaded {len(raw_data)} posts from {input_path}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading input data: {e}")
            return []
        
        trust_atoms = []
        count = 0
        
        for post in raw_data:
            post_data = {
                "permalink": post.get("permalink", "https://reddit.com"),
                "timestamp": post.get("created_utc"),
                "subreddit": post.get("subreddit"),
                "title": post.get("title"),
                "score": post.get("score", 0)
            }
            
            for comment in post.get("comments", []):
                if max_items and count >= max_items:
                    break
                
                # Skip empty comments
                if not comment.get("body", "").strip():
                    continue
                
                # Step 1: Preprocess data
                processed_data = self.preprocessor.process_reddit_comment(comment, post_data)
                
                # Step 2: Match product
                product_match_result = self.product_matcher.match_product(processed_data["text"])
                
                # Step 3: Analyze content
                sentiment_result = self.content_analyzer.analyze_sentiment(processed_data["text"])
                summary = self.content_analyzer.generate_summary(processed_data["text"])
                
                # Get product category for tag extraction
                product_id = product_match_result[0]
                if product_id:
                    # This is a simplified approach; in a real implementation,
                    # you would look up the category in the product registry
                    if "cleanser" in product_id or "moisturizer" in product_id:
                        category = "skincare"
                    elif "food" in product_id or "snack" in product_id:
                        category = "food"
                    else:
                        category = "unknown"
                else:
                    category = "unknown"
                
                tags = self.content_analyzer.extract_tags(processed_data["text"], category)
                
                # Step 4: Create Trust Atom
                trust_atom = self.trust_atom_creator.create_trust_atom(
                    processed_data,
                    product_match_result,
                    sentiment_result,
                    tags,
                    summary
                )
                
                # Step 5: Store Trust Atom
                if output_path:
                    # Store in specified output path (backward compatibility)
                    self.trust_atom_creator.save_trust_atom(trust_atom, output_path)
                else:
                    # Store in category-specific file and other locations
                    self.storage.store_all(trust_atom)
                
                trust_atoms.append(trust_atom)
                count += 1
                
                if count % 10 == 0:
                    logger.info(f"Processed {count} comments")
                
                if max_items and count >= max_items:
                    break
        
        logger.info(f"Processed {count} comments, created {len(trust_atoms)} Trust Atoms")
        return trust_atoms
    
    def process_youtube_data(self, 
                            input_path: str, 
                            output_path: Optional[str] = None, 
                            max_items: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Process YouTube data and create Trust Atoms.
        
        Args:
            input_path: Path to the input JSON file
            output_path: Optional path to the output file
            max_items: Maximum number of items to process
            
        Returns:
            List of created Trust Atoms
        """
        logger.info(f"Processing YouTube data from {input_path}")
        
        # Load input data
        try:
            with open(input_path, "r") as f:
                raw_data = json.load(f)
            logger.info(f"Loaded data from {input_path}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading input data: {e}")
            return []
        
        trust_atoms = []
        count = 0
        
        for video in raw_data:
            video_data = {
                "title": video.get("title"),
                "channel_name": video.get("channel_name"),
                "view_count": video.get("view_count", 0),
                "url": video.get("url")
            }
            
            for comment in video.get("comments", []):
                if max_items and count >= max_items:
                    break
                
                # Skip empty comments
                if not comment.get("text", "").strip():
                    continue
                
                # Step 1: Preprocess data
                processed_data = self.preprocessor.process_youtube_comment(comment, video_data)
                
                # Step 2: Match product
                product_match_result = self.product_matcher.match_product(processed_data["text"])
                
                # Step 3: Analyze content
                sentiment_result = self.content_analyzer.analyze_sentiment(processed_data["text"])
                summary = self.content_analyzer.generate_summary(processed_data["text"])
                
                # Get product category for tag extraction
                product_id = product_match_result[0]
                if product_id:
                    if "cleanser" in product_id or "moisturizer" in product_id:
                        category = "skincare"
                    elif "food" in product_id or "snack" in product_id:
                        category = "food"
                    else:
                        category = "unknown"
                else:
                    category = "unknown"
                
                tags = self.content_analyzer.extract_tags(processed_data["text"], category)
                
                # Step 4: Create Trust Atom
                trust_atom = self.trust_atom_creator.create_trust_atom(
                    processed_data,
                    product_match_result,
                    sentiment_result,
                    tags,
                    summary
                )
                
                # Step 5: Store Trust Atom
                if output_path:
                    # Store in specified output path
                    self.trust_atom_creator.save_trust_atom(trust_atom, output_path)
                else:
                    # Store in category-specific file and other locations
                    self.storage.store_all(trust_atom)
                
                trust_atoms.append(trust_atom)
                count += 1
                
                if count % 10 == 0:
                    logger.info(f"Processed {count} comments")
                
                if max_items and count >= max_items:
                    break
        
        logger.info(f"Processed {count} comments, created {len(trust_atoms)} Trust Atoms")
        return trust_atoms
    
    def process_single_comment(self, 
                              comment_text: str, 
                              source: str = "manual", 
                              metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a single comment and create a Trust Atom.
        
        Args:
            comment_text: Text of the comment
            source: Source of the comment
            metadata: Additional metadata
            
        Returns:
            Created Trust Atom
        """
        logger.info(f"Processing single comment from {source}")
        
        # Create basic feedback data
        feedback = {
            "text": comment_text,
            "source": source,
            "timestamp": metadata.get("timestamp") if metadata else None
        }
        
        # Add metadata if provided
        if metadata:
            feedback.update(metadata)
        
        # Step 1: Clean text
        feedback["text"] = self.preprocessor.clean_text(comment_text)
        
        # Step 2: Match product
        product_match_result = self.product_matcher.match_product(feedback["text"])
        
        # Step 3: Analyze content
        sentiment_result = self.content_analyzer.analyze_sentiment(feedback["text"])
        summary = self.content_analyzer.generate_summary(feedback["text"])
        
        # Get product category for tag extraction
        product_id = product_match_result[0]
        if product_id:
            if "cleanser" in product_id or "moisturizer" in product_id:
                category = "skincare"
            elif "food" in product_id or "snack" in product_id:
                category = "food"
            else:
                category = "unknown"
        else:
            category = "unknown"
        
        tags = self.content_analyzer.extract_tags(feedback["text"], category)
        
        # Step 4: Create Trust Atom
        trust_atom = self.trust_atom_creator.create_trust_atom(
            feedback,
            product_match_result,
            sentiment_result,
            tags,
            summary
        )
        
        # Step 5: Store Trust Atom
        self.storage.store_all(trust_atom)
        
        logger.info(f"Created Trust Atom {trust_atom['atom_id']}")
        return trust_atom


# Example usage
if __name__ == "__main__":
    import tempfile
    import shutil
    
    # Create temporary directories for testing
    temp_dir = tempfile.mkdtemp()
    registry_dir = os.path.join(temp_dir, "registry")
    os.makedirs(registry_dir, exist_ok=True)
    
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
        }
    }
    
    # Save sample registry
    registry_path = os.path.join(registry_dir, "product_registry_detailed.json")
    with open(registry_path, "w") as f:
        json.dump(sample_registry, f, indent=2)
    
    # Create a sample Reddit data file
    sample_reddit_data = [
        {
            "permalink": "https://www.reddit.com/r/SkincareAddiction/comments/example/",
            "created_utc": 1750346703.0,
            "subreddit": "SkincareAddiction",
            "title": "Favorite Cleansers",
            "score": 100,
            "comments": [
                {
                    "body": "I love the CeraVe cleanser! It works great on my oily skin.",
                    "author": "user123",
                    "created_utc": 1750347257.0,
                    "score": 10,
                    "id": "abc123"
                },
                {
                    "body": "Has anyone tried the Neutrogena face wash? Is it good for dry skin?",
                    "author": "user456",
                    "created_utc": 1750347300.0,
                    "score": 5,
                    "id": "def456"
                }
            ]
        }
    ]
    
    # Save sample Reddit data
    reddit_data_path = os.path.join(temp_dir, "sample_reddit_data.json")
    with open(reddit_data_path, "w") as f:
        json.dump(sample_reddit_data, f, indent=2)
    
    # Create pipeline
    pipeline = TrustGraphPipeline(
        product_registry_path=registry_path,
        base_storage_path=os.path.join(temp_dir, "data")
    )
    
    # Process Reddit data
    trust_atoms = pipeline.process_reddit_data(
        input_path=reddit_data_path,
        max_items=2
    )
    
    # Print results
    print(f"Created {len(trust_atoms)} Trust Atoms")
    for atom in trust_atoms:
        print(f"Atom ID: {atom['atom_id']}")
        print(f"Product ID: {atom['product_id']}")
        print(f"Sentiment: {atom['sentiment_label']} (confidence: {atom['confidence_score']})")
        print(f"Summary: {atom['summary_text']}")
        print(f"Tags: {atom['tags']}")
        print("---")
    
    # Process a single comment
    single_atom = pipeline.process_single_comment(
        comment_text="The CeraVe moisturizer is amazing for dry skin!",
        source="manual",
        metadata={
            "username": "test_user",
            "score": 1
        }
    )
    
    print(f"Single comment atom ID: {single_atom['atom_id']}")
    print(f"Product ID: {single_atom['product_id']}")
    print(f"Sentiment: {single_atom['sentiment_label']}")
    print(f"Summary: {single_atom['summary_text']}")
    
    # Clean up
    shutil.rmtree(temp_dir)