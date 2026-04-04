from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_text(documents: list[dict]) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    
    chunks = []
    for doc in documents:
        if not doc["content"]:
            continue
            
        splits = splitter.split_text(doc["content"])
        
        for split in splits:
            chunks.append({
                "text": split,
                "source": doc["url"],
                "title": doc["title"]
            })
    
    return chunks


if __name__ == "__main__":
    sample = [{
        "title": "Test Article",
        "url": "https://example.com",
        "content": "Artificial intelligence is transforming the world. " * 50
    }]
    
    chunks = chunk_text(sample)
    print(f"Total chunks created: {len(chunks)}")
    print(f"\nFirst chunk preview:")
    print(chunks[0]["text"])
    print(f"\nSource: {chunks[0]['source']}")