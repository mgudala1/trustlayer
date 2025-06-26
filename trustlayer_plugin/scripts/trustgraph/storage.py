"""
Storage module for TrustGraph implementation.

This module contains classes and functions for storing Trust Atoms
in various formats and locations.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TrustAtomStorage:
    """Store Trust Atoms in various formats and locations."""
    
    def __init__(self, base_path: str = "trustlayer_plugin/data"):
        """
        Initialize the TrustAtomStorage.
        
        Args:
            base_path: Base path for storage
        """
        self.base_path = base_path
        self.category_path = os.path.join(base_path, "categories")
        self.trust_atoms_path = os.path.join(base_path, "trust_atoms")
        self.sources_path = os.path.join(base_path, "sources")
        
        # Create directories if they don't exist
        for path in [self.category_path, self.trust_atoms_path, self.sources_path]:
            os.makedirs(path, exist_ok=True)
    
    def store_by_category(self, trust_atom: Dict[str, Any]) -> bool:
        """
        Store a Trust Atom in a category-specific file.
        
        Args:
            trust_atom: Trust Atom to store
            
        Returns:
            True if successful, False otherwise
        """
        # Get category from product ID or fallback to "unknown"
        category = self._get_category(trust_atom.get("product_id", "unknown"))
        
        # Create path
        file_path = os.path.join(self.category_path, f"{category}.json")
        
        return self._store_in_file(trust_atom, file_path)
    
    def store_by_source(self, trust_atom: Dict[str, Any]) -> bool:
        """
        Store a Trust Atom in a source-specific file.
        
        Args:
            trust_atom: Trust Atom to store
            
        Returns:
            True if successful, False otherwise
        """
        # Get source or fallback to "unknown"
        source = trust_atom.get("source", "unknown")
        
        # Create path
        file_path = os.path.join(self.sources_path, f"{source}.json")
        
        return self._store_in_file(trust_atom, file_path)
    
    def store_as_trust_atom(self, trust_atom: Dict[str, Any]) -> bool:
        """
        Store a Trust Atom in the trust_atoms collection.
        
        Args:
            trust_atom: Trust Atom to store
            
        Returns:
            True if successful, False otherwise
        """
        # Get product ID or fallback to "unknown"
        product_id = trust_atom.get("product_id", "unknown")
        
        # Create path
        file_path = os.path.join(self.trust_atoms_path, f"{product_id}.json")
        
        return self._store_in_file(trust_atom, file_path)
    
    def store_all(self, trust_atom: Dict[str, Any]) -> Dict[str, bool]:
        """
        Store a Trust Atom in all storage locations.
        
        Args:
            trust_atom: Trust Atom to store
            
        Returns:
            Dictionary of storage results
        """
        results = {
            "category": self.store_by_category(trust_atom),
            "source": self.store_by_source(trust_atom),
            "trust_atom": self.store_as_trust_atom(trust_atom)
        }
        
        return results
    
    def _store_in_file(self, trust_atom: Dict[str, Any], file_path: str) -> bool:
        """
        Store a Trust Atom in a specific file.
        
        Args:
            trust_atom: Trust Atom to store
            file_path: Path to the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Load existing data
            existing_data = []
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    existing_data = json.load(f)
            
            # Add new Trust Atom
            existing_data.append(trust_atom)
            
            # Save updated data
            with open(file_path, "w") as f:
                json.dump(existing_data, f, indent=2)
            
            logger.info(f"Stored Trust Atom {trust_atom.get('atom_id')} in {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error storing Trust Atom in {file_path}: {e}")
            return False
    
    def _get_category(self, product_id: str) -> str:
        """
        Get category from product ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            Category name
        """
        # This is a simple implementation that extracts category from product ID
        # In a real implementation, this would use the product registry
        
        # Check for common categories in the product ID
        if "cleanser" in product_id or "moisturizer" in product_id or "serum" in product_id:
            return "skincare"
        elif "food" in product_id or "snack" in product_id or "drink" in product_id:
            return "food"
        elif "detergent" in product_id or "cleaner" in product_id:
            return "household"
        else:
            return "unknown"
    
    def get_trust_atoms_by_product(self, product_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all Trust Atoms for a specific product.
        
        Args:
            product_id: Product ID
            
        Returns:
            List of Trust Atoms for the product
        """
        atoms = []
        
        # Check if product-specific file exists
        product_file = os.path.join(self.trust_atoms_path, f"{product_id}.json")
        if os.path.exists(product_file):
            try:
                with open(product_file, "r") as f:
                    atoms = json.load(f)
                return atoms
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.error(f"Error reading {product_file}: {e}")
        
        # If not found or error, search all category files
        for category_file in os.listdir(self.category_path):
            if not category_file.endswith(".json"):
                continue
                
            try:
                with open(os.path.join(self.category_path, category_file), "r") as f:
                    category_atoms = json.load(f)
                
                # Filter by product_id
                product_atoms = [atom for atom in category_atoms if atom.get("product_id") == product_id]
                atoms.extend(product_atoms)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.error(f"Error reading {category_file}: {e}")
        
        return atoms
    
    def get_trust_atoms_by_source(self, source: str) -> List[Dict[str, Any]]:
        """
        Retrieve all Trust Atoms from a specific source.
        
        Args:
            source: Source name
            
        Returns:
            List of Trust Atoms from the source
        """
        source_file = os.path.join(self.sources_path, f"{source}.json")
        
        if not os.path.exists(source_file):
            logger.warning(f"Source file {source_file} not found")
            return []
        
        try:
            with open(source_file, "r") as f:
                atoms = json.load(f)
            return atoms
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error reading {source_file}: {e}")
            return []
    
    def get_trust_atoms_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Retrieve all Trust Atoms for a specific category.
        
        Args:
            category: Category name
            
        Returns:
            List of Trust Atoms for the category
        """
        category_file = os.path.join(self.category_path, f"{category}.json")
        
        if not os.path.exists(category_file):
            logger.warning(f"Category file {category_file} not found")
            return []
        
        try:
            with open(category_file, "r") as f:
                atoms = json.load(f)
            return atoms
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error reading {category_file}: {e}")
            return []


# Example usage
if __name__ == "__main__":
    # Create a sample Trust Atom
    sample_atom = {
        "atom_id": "reddit_cerave_foaming_cleanser_12345",
        "product_id": "cerave_foaming_cleanser_12oz",
        "source": "reddit",
        "timestamp": "2025-06-26T15:30:00Z",
        "feedback_text": "I love the CeraVe cleanser! It works great on my oily skin.",
        "summary_text": "Works great on oily skin.",
        "sentiment_label": "positive",
        "authenticity_score": 0.85,
        "confidence_score": 0.9,
        "tags": ["skincare", "cleanser", "oily"],
        "metadata": {
            "username_hash": "sha256:1234567890abcdef",
            "upvotes": 10,
            "permalink": "https://www.reddit.com/r/SkincareAddiction/comments/example/"
        },
        "product_match_info": {
            "match_method": "exact_alias",
            "match_score": 0.9,
            "alternative_matches": [],
            "context_factors": {
                "brand_mentioned": True,
                "product_type_mentioned": True,
                "identifier_mentioned": False
            }
        },
        "source_specific_data": {
            "reddit_data": {
                "subreddit": "SkincareAddiction",
                "post_title": "Favorite Cleansers",
                "post_score": 100
            }
        }
    }
    
    # Create storage with temporary path
    temp_base_path = "temp_storage"
    storage = TrustAtomStorage(temp_base_path)
    
    # Store the Trust Atom
    results = storage.store_all(sample_atom)
    print(f"Storage results: {results}")
    
    # Retrieve the Trust Atom
    atoms = storage.get_trust_atoms_by_product("cerave_foaming_cleanser_12oz")
    print(f"Retrieved {len(atoms)} Trust Atoms for product")
    
    # Clean up
    import shutil
    if os.path.exists(temp_base_path):
        shutil.rmtree(temp_base_path)