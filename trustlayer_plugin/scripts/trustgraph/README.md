# TrustGraph Implementation for TrustLayer 2.0

This directory contains the implementation of the TrustGraph-based architecture for TrustLayer 2.0, focusing on Trust Atoms as the fundamental building blocks of the TrustGraph.

## Overview

The TrustGraph implementation provides a robust solution for processing unstructured data from various sources (Reddit, YouTube, etc.), matching product mentions to canonical products, analyzing sentiment and content, and creating structured Trust Atoms that can be used to build a knowledge graph.

### Key Features

- **Enhanced Product Matching**: Multi-stage matching algorithm with confidence scoring
- **Rich Metadata Capture**: Detailed information about product matches, sentiment, and context
- **Flexible Storage Options**: Store Trust Atoms by category, source, or product
- **Backward Compatibility**: Drop-in replacement for the existing summarization pipeline

## Directory Structure

```
trustlayer_plugin/
├── data/
│   ├── trust_atom.schema.json       # JSON Schema for Trust Atoms
│   ├── registry/                    # Product registry
│   │   ├── product_registry_detailed.json
│   │   └── registry_suggestions.json
│   ├── categories/                  # Category-specific Trust Atoms
│   │   ├── skincare.json
│   │   └── food.json
│   └── trust_atoms/                 # Product-specific Trust Atoms
│       ├── cerave_foaming_cleanser_12oz.json
│       └── neutrogena_hydro_boost.json
├── scripts/
│   ├── summarise.py                 # Original summarization script
│   ├── summarise_v2.py              # Backward-compatible wrapper
│   └── trustgraph/                  # TrustGraph implementation
│       ├── __init__.py
│       ├── preprocessor.py          # Data preprocessing
│       ├── product_matcher.py       # Product matching
│       ├── content_analyzer.py      # Sentiment and tag analysis
│       ├── trust_atom_creator.py    # Trust Atom creation
│       ├── storage.py               # Storage options
│       └── pipeline.py              # Main pipeline
```

## Components

### 1. DataPreprocessor

Handles cleaning and normalization of raw data from various sources.

```python
from trustgraph.preprocessor import DataPreprocessor

preprocessor = DataPreprocessor()
processed_data = preprocessor.process_reddit_comment(comment, post_data)
```

### 2. ProductMatcher

Implements the multi-stage product matching algorithm with confidence scoring.

```python
from trustgraph.product_matcher import ProductMatcher

matcher = ProductMatcher("path/to/registry.json")
product_id, match_info = matcher.match_product("I love the CeraVe cleanser!")
```

### 3. ContentAnalyzer

Analyzes content for sentiment, extracts tags, and generates summaries.

```python
from trustgraph.content_analyzer import ContentAnalyzer

analyzer = ContentAnalyzer()
sentiment, confidence = analyzer.analyze_sentiment(text)
tags = analyzer.extract_tags(text, "skincare")
summary = analyzer.generate_summary(text)
```

### 4. TrustAtomCreator

Creates Trust Atoms from processed data.

```python
from trustgraph.trust_atom_creator import TrustAtomCreator

creator = TrustAtomCreator("path/to/schema.json")
trust_atom = creator.create_trust_atom(
    feedback,
    product_match_result,
    sentiment_result,
    tags,
    summary
)
```

### 5. TrustAtomStorage

Stores Trust Atoms in various formats and locations.

```python
from trustgraph.storage import TrustAtomStorage

storage = TrustAtomStorage("path/to/base/dir")
storage.store_by_category(trust_atom)
storage.store_by_source(trust_atom)
storage.store_as_trust_atom(trust_atom)
```

### 6. TrustGraphPipeline

Orchestrates all the components to process data and create Trust Atoms.

```python
from trustgraph.pipeline import TrustGraphPipeline

pipeline = TrustGraphPipeline(
    product_registry_path="path/to/registry.json",
    base_storage_path="path/to/base/dir"
)
trust_atoms = pipeline.process_reddit_data("path/to/input.json")
```

## Usage

### Backward-Compatible Usage

To use the new implementation as a drop-in replacement for the existing summarization pipeline:

```bash
python trustlayer_plugin/scripts/summarise_v2.py --input data/reddit_sample.json --output plugin/data/categories/skincare.json
```

### Advanced Usage

For more control over the pipeline:

```python
from trustgraph.pipeline import TrustGraphPipeline

# Initialize the pipeline
pipeline = TrustGraphPipeline(
    product_registry_path="trustlayer_plugin/data/registry/product_registry_detailed.json",
    base_storage_path="trustlayer_plugin/data"
)

# Process Reddit data
trust_atoms = pipeline.process_reddit_data(
    input_path="data/reddit_sample.json",
    max_items=10
)

# Process YouTube data
trust_atoms = pipeline.process_youtube_data(
    input_path="data/youtube_sample.json",
    max_items=10
)

# Process a single comment
trust_atom = pipeline.process_single_comment(
    comment_text="I love the CeraVe cleanser!",
    source="manual",
    metadata={
        "username": "user123",
        "score": 5
    }
)
```

## Product Registry

The product registry is a key component of the TrustGraph implementation. It contains canonical product information, including aliases and identifiers, which are used for product matching.

Example registry entry:

```json
{
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
```

## Trust Atom Schema

Trust Atoms are the fundamental building blocks of the TrustGraph. They represent atomic units of structured user trust evidence.

Example Trust Atom:

```json
{
  "atom_id": "reddit_cerave_foaming_cleanser_12oz_1234abcd",
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
      "brand_mentioned": true,
      "product_type_mentioned": true,
      "identifier_mentioned": false
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
```

## Future Enhancements

1. **Semantic Similarity Matching**: Implement embedding-based matching for better product identification
2. **Advanced Sentiment Analysis**: Integrate more sophisticated sentiment analysis models
3. **Graph Database Integration**: Connect to a proper graph database for more efficient storage and querying
4. **Feedback Loop**: Implement a learning loop to improve matching based on user feedback
5. **Distributed Processing**: Scale the pipeline for processing large volumes of data

## Requirements

- Python 3.8+
- Required packages:
  - transformers (for summarization)
  - nltk (for text processing)
  - json (for data handling)
  - hashlib (for anonymization)
  - uuid (for unique IDs)
  - logging (for logging)
  - typing (for type hints)