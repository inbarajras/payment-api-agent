
import os
import json
import re
from nltk.tokenize import sent_tokenize
import numpy as np
from sentence_transformers import SentenceTransformer

def clean_and_structure_docs(input_dir, output_file):
    """Clean and structure scraped documentation"""
    print(f"Cleaning and structuring documents from {input_dir}...")

    structured_docs = []

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Process each file in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(input_dir, filename)

            try:
                with open(filepath, 'r') as f:
                    doc = json.load(f)

                # Skip empty documents
                if not doc.get('content'):
                    continue

                # Clean content
                content = doc['content']
                content = re.sub(r'\s+', ' ', content).strip()  # Remove extra whitespace

                # Break into chunks (paragraphs or sections)
                # This is a simple approach - in practice you might use more sophisticated chunking
                chunks = []
                paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

                for paragraph in paragraphs:
                    # If paragraph is very long, split into sentences
                    if len(paragraph) > 1000:
                        sentences = sent_tokenize(paragraph)
                        current_chunk = ""

                        for sentence in sentences:
                            if len(current_chunk) + len(sentence) < 1000:
                                current_chunk += " " + sentence
                            else:
                                if current_chunk:
                                    chunks.append(current_chunk.strip())
                                current_chunk = sentence

                        if current_chunk:
                            chunks.append(current_chunk.strip())
                    else:
                        chunks.append(paragraph)

                # Extract code examples and their context
                code_examples = []
                for code in doc.get('code_examples', []):
                    if code.strip():
                        # Detect language (simplified)
                        language = "unknown"
                        if "function" in code and "{" in code:
                            language = "javascript"
                        elif "def " in code and ":" in code:
                            language = "python"
                        elif "<?php" in code:
                            language = "php"

                        code_examples.append({
                            'code': code.strip(),
                            'language': language
                        })

                # Create structured document
                structured_doc = {
                    'title': doc['title'],
                    'url': doc['url'],
                    'chunks': chunks,
                    'code_examples': code_examples,
                    'category': categorize_document(doc['title'], content)
                }

                structured_docs.append(structured_doc)

            except Exception as e:
                print(f"Error processing {filename}: {e}")

    # Save structured documents
    with open(output_file, 'w') as f:
        json.dump(structured_docs, f, indent=2)

    print(f"Structured {len(structured_docs)} documents to {output_file}")
    return structured_docs

def categorize_document(title, content):
    """Categorize document based on content"""
    categories = {
        'authentication': ['auth', 'token', 'key', 'credential', 'connect', 'setup'],
        'payment_processing': ['payment', 'charge', 'transaction', 'checkout'],
        'subscription': ['subscription', 'recurring', 'billing'],
        'refund': ['refund', 'return', 'cancel', 'void'],
        'webhook': ['webhook', 'event', 'notification', 'callback'],
        'error_handling': ['error', 'exception', 'troubleshoot', 'debug']
    }

    title_content = (title + " " + content).lower()

    for category, keywords in categories.items():
        if any(keyword in title_content for keyword in keywords):
            return category

    return 'general'

def create_embeddings(input_file, output_dir):
    """Create embeddings for structured documentation"""
    print(f"Creating embeddings from {input_file}...")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Load documents
        with open(input_file, 'r') as f:
            documents = json.load(f)

        # Initialize embedding model
        print("Loading embedding model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # Process each document
        embeddings_data = []

        print(f"Processing {len(documents)} documents...")
        for doc_idx, doc in enumerate(documents):
            print(f"Processing document {doc_idx + 1}/{len(documents)}: {doc['title']}")

            # Create embeddings for each chunk
            for chunk_idx, chunk in enumerate(doc['chunks']):
                embedding = model.encode(chunk)

                embeddings_data.append({
                    'document_id': doc['url'],
                    'chunk_id': chunk_idx,
                    'title': doc['title'],
                    'text': chunk,
                    'category': doc['category'],
                    'embedding': embedding.tolist()
                })

            # Also create embeddings for code examples
            for code_idx, example in enumerate(doc['code_examples']):
                # Add a context prefix for better search
                context = f"Code example ({example['language']}): {example['code']}"
                embedding = model.encode(context)

                embeddings_data.append({
                    'document_id': doc['url'],
                    'chunk_id': f"code_{code_idx}",
                    'title': doc['title'],
                    'text': context,
                    'category': doc['category'],
                    'code': example['code'],
                    'language': example['language'],
                    'embedding': embedding.tolist()
                })

        # Save embeddings
        output_file = os.path.join(output_dir, 'embeddings.json')
        with open(output_file, 'w') as f:
            json.dump(embeddings_data, f)

        print(f"Created {len(embeddings_data)} embeddings saved to {output_file}")
        return len(embeddings_data)

    except Exception as e:
        print(f"Error creating embeddings: {e}")
        return 0