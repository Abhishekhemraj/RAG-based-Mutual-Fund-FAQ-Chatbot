import os
import json
import re

def clean_text(text):
    """Basic text cleaning."""
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def split_into_chunks(text, chunk_size=800, overlap=80):
    """Splits text into overlapping chunks."""
    # A very simple chunking strategy for demonstration
    # In a real RAG system, we'd use LangChain's RecursiveCharacterTextSplitter
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunks.append(" ".join(chunk_words))
        i += (chunk_size - overlap)
        if i >= len(words):
            break
    return chunks

def process_file(file_path, output_dir):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract source URL from the first few lines if present
    source_url = "Unknown"
    fund_name = "Unknown"
    
    lines = content.split('\n')
    for line in lines[:5]:
        if line.startswith("Source:"):
            source_url = line.replace("Source:", "").strip()
        if line.startswith("# "):
            fund_name = line.replace("# ", "").strip()

    cleaned_content = clean_text(content)
    # For now, we'll split by major sections to keep semantics better than random words
    sections = re.split(r'\n## ', cleaned_content)
    
    chunks = []
    for section in sections:
        if not section.strip():
            continue
        
        # Determine section title for metadata
        section_lines = section.strip().split('\n')
        section_title = section_lines[0] if section_lines else "General"
        
        chunk_data = {
            "fund_name": fund_name,
            "source_url": source_url,
            "section": section_title,
            "content": f"Fund: {fund_name}\nSection: {section_title}\n\n{section.strip()}"
        }
        chunks.append(chunk_data)

    base_name = os.path.basename(file_path).replace('.md', '.json')
    output_path = os.path.join(output_dir, base_name)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=4)
    
    print(f"Processed {file_path} -> {output_path} ({len(chunks)} chunks)")

def main():
    raw_dir = 'data/raw'
    cleaned_dir = 'data/cleaned'
    
    if not os.path.exists(cleaned_dir):
        os.makedirs(cleaned_dir)
        
    if not os.path.exists(raw_dir):
        print(f"Raw directory {raw_dir} does not exist. Skipping processing.")
        os.makedirs(raw_dir, exist_ok=True)
        return
        
    for filename in os.listdir(raw_dir):
        if filename.endswith('.md'):
            process_file(os.path.join(raw_dir, filename), cleaned_dir)

if __name__ == "__main__":
    main()
