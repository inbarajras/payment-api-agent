import argparse
import os
import sys
from scraper import scrape_documentation
from embedder import clean_and_structure_docs, create_embeddings

def main():
    parser = argparse.ArgumentParser(description="Populate Payment API Knowledge Base")
    parser.add_argument("--provider", choices=["stripe", "paypal", "all"], default="all",
                        help="Which API provider to scrape")
    args = parser.parse_args()

    providers = ["stripe", "paypal"] if args.provider == "all" else [args.provider]

    for provider in providers:
        print(f"Processing {provider.capitalize()} documentation...")

        # Step 1: Scrape documentation
        print("Scraping documentation...")
        base_url = "https://developer.paypal.com" if provider == "paypal" else "https://docs.stripe.com"
        output_dir = f"knowledge_base/{provider}"
        scrape_documentation(base_url, output_dir)

        # Step 2: Clean and structure documents
        print("Cleaning and structuring documents...")
        structured_output = f"structured_knowledge/{provider}.json"
        clean_and_structure_docs(output_dir, structured_output)

        # Step 3: Create embeddings
        print("Creating embeddings...")
        embeddings_dir = f"vector_db/{provider}"
        create_embeddings(structured_output, embeddings_dir)

        print(f"✅ Finished processing {provider.capitalize()} documentation!")

    print("\nKnowledge base population complete!")

if __name__ == "__main__":
    main()