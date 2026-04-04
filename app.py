from utils.embeddings import create_vector_store

chunks = [
    "Artificial intelligence is transforming industries.",
    "Quantum computing uses qubits instead of classical bits.",
    "Machine learning models learn patterns from data."
]

vector_db = create_vector_store(chunks)

print("Vector database created successfully!")