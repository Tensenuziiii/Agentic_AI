"""Small standalone Sentence Transformers similarity demo retained from the workspace."""
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")
sentences = ["I love cats.", "I like kittens.", "The car is very fast."]
embeddings = model.encode(sentences)
for sentence, embedding in zip(sentences, embeddings):
    print("\nSentence:", sentence)
    print("Number of dimensions:", len(embedding))
    print("First 10 values:", embedding[:10])
print("\nSIMILARITY")
print("Cats vs Kittens:", util.cos_sim(embeddings[0], embeddings[1]).item())
print("Cats vs Car:", util.cos_sim(embeddings[0], embeddings[2]).item())
