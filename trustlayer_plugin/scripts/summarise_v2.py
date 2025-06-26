"""
Backward-compatible wrapper for the TrustGraph pipeline.

This script provides a drop-in replacement for the existing summarise.py script,
using the new TrustGraph pipeline under the hood.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the parent directory to the path to import the trustgraph package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from trustgraph.pipeline import TrustGraphPipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_product_registry(output_path: str) -> str:
    """
    Create a basic product registry if it doesn't exist.
    
    Args:
        output_path: Path to save the registry
        
    Returns:
        Path to the registry file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Check if registry already exists
    if os.path.exists(output_path):
        logger.info(f"Product registry already exists at {output_path}")
        return output_path
    
    # Create a basic registry with common skincare products
    registry = {
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
        },
        "the_ordinary_niacinamide": {
            "product_id": "the_ordinary_niacinamide",
            "canonical_name": "The Ordinary Niacinamide 10% + Zinc 1%",
            "brand": "The Ordinary",
            "category": "skincare",
            "type": "serum",
            "aliases": [
                "the ordinary niacinamide",
                "niacinamide serum",
                "ordinary niacinamide zinc"
            ],
            "identifiers": {
                "asin": "B06VSX2B1S"
            }
        }
    }
    
    # Save the registry
    with open(output_path, "w") as f:
        json.dump(registry, f, indent=2)
    
    logger.info(f"Created basic product registry at {output_path}")
    return output_path


def summarize_reddit_data(input_path: str, output_path: str, max_comments: int = 10) -> None:
    """
    Backward-compatible function for summarizing Reddit data.
    
    Args:
        input_path: Path to input JSON file
        output_path: Path to output file
        max_comments: Maximum number of comments to process
    """
    logger.info(f"Summarizing Reddit data from {input_path} to {output_path}")
    
    # Create registry directory
    registry_dir = os.path.join("trustlayer_plugin", "data", "registry")
    os.makedirs(registry_dir, exist_ok=True)
    
    # Create or get product registry
    registry_path = os.path.join(registry_dir, "product_registry_detailed.json")
    registry_path = create_product_registry(registry_path)
    
    # Create pipeline
    pipeline = TrustGraphPipeline(
        product_registry_path=registry_path,
        base_storage_path=os.path.dirname(os.path.dirname(output_path))
    )
    
    # Process Reddit data
    trust_atoms = pipeline.process_reddit_data(
        input_path=input_path,
        output_path=output_path,
        max_items=max_comments
    )
    
    logger.info(f"[OK] Wrote {len(trust_atoms)} structured entries to {output_path}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Summarize Reddit data using TrustGraph pipeline")
    parser.add_argument("--input", "-i", default="data/reddit_sample.json", help="Input JSON file")
    parser.add_argument("--output", "-o", default="plugin/data/categories/skincare.json", help="Output JSON file")
    parser.add_argument("--max-comments", "-m", type=int, default=10, help="Maximum number of comments to process")
    
    args = parser.parse_args()
    
    summarize_reddit_data(args.input, args.output, args.max_comments)


if __name__ == "__main__":
    main()