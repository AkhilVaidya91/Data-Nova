import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from tabulate import tabulate

# Initialize the all-MiniLM-L6-v2 embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define anchor sentences
anchor_sentences = [
    "Undertaking environmental impact studies & monitoring programs",
    "Utilizing waste materials for energy production",
    "Training & Development of employees and providing career opportunities",
    "Improved recycling of products",
    "Sponsoring community projects, public health projects, medical research, or scholarships"
]

# Define example sentences
example_sentences = [
    "Our team conducts comprehensive environmental assessments before new facility construction to minimize ecological disruption.",
    "We've implemented a program to convert factory waste byproducts into supplemental power for our manufacturing operations.",
    "The company offers extensive professional development workshops and clear advancement pathways for all employees.",
    "Our redesigned packaging now contains 85% post-consumer materials and is fully recyclable.",
    "Through our foundation, we've funded three new medical research initiatives focused on childhood diseases.",
    "The environmental monitoring equipment was purchased from Impact Studies Inc., a leading provider in the industry.",
    "Our waste management team ensures proper disposal of all materials according to regulatory requirements.",
    "Employees participated in training exercises to improve workplace safety protocols last quarter.",
    "We've launched a product recycling incentive program that rewards customers for returning used items.",
    "The marketing department sponsored several community sporting events to increase brand visibility.",
    r"Impact studies show our solar panel installation has reduced carbon emissions by 30% compared to previous energy sources.",
    "Our new waste reduction initiative aims to minimize materials sent to landfills rather than using them for energy recovery.",
    "The development of new talent remains a priority, with mentorship opportunities available across departments.",
    "We've improved our manufacturing process to reduce waste rather than focusing solely on recycling finished products.",
    "Our sponsorship of the local arts festival brought together community members from diverse backgrounds.",
    "Environmental consultants conducted impact assessments and established ongoing ecological monitoring systems at all operational sites.",
    r"The biomass facility converts agricultural waste into energy that powers 40% of our production line.",
    r"Our leadership development program has helped 78% of participants advance to higher positions within two years.",
    "The product design team has improved recyclability by eliminating composite materials that are difficult to separate.",
    "We've established a scholarship fund that has supported 50 students from underserved communities in pursuing STEM education."
]

# Generate embeddings for anchor and example sentences
anchor_embeddings = model.encode(anchor_sentences)
example_embeddings = model.encode(example_sentences)

# Calculate cosine similarity between anchor and example sentences
similarity_scores = {}

for i, anchor in enumerate(anchor_sentences):
    # Calculate cosine similarity between current anchor and all example sentences
    scores = cosine_similarity([anchor_embeddings[i]], example_embeddings)[0]
    
    # Create a list of (example_idx, score) tuples
    scored_examples = [(idx, score) for idx, score in enumerate(scores)]
    
    # Sort by score in descending order
    scored_examples.sort(key=lambda x: x[1], reverse=True)
    
    # Store the results
    similarity_scores[anchor] = scored_examples

# Define the threshold for matching
threshold = 0.5

# Process and display results for each anchor sentence
print("\n" + "="*100)
print("CSR SEMANTIC SIMILARITY ANALYSIS RESULTS")
print("="*100)

for i, anchor in enumerate(anchor_sentences):
    print(f"\nAnchor {i+1}: \"{anchor}\"")
    print("-" * 80)
    
    # Get the scored examples for this anchor
    scored_examples = similarity_scores[anchor]
    
    # Top 3 matching examples (above threshold if possible)
    matching = [(idx, score) for idx, score in scored_examples if score >= threshold]
    if not matching:
        # If no examples above threshold, just take the top 3
        matching = scored_examples[:3]
    else:
        # Take up to 3 from those that match
        matching = matching[:3]
    
    # Bottom 3 non-matching examples
    non_matching = [(idx, score) for idx, score in scored_examples if score < threshold]
    if len(non_matching) < 3:
        # If fewer than 3 examples below threshold, take the lowest 3 regardless
        non_matching = scored_examples[-3:]
    else:
        # Take the 3 lowest scores
        non_matching = sorted(non_matching, key=lambda x: x[1])[:3]
    
    # Display top matching examples
    print("TOP 3 MATCHING SENTENCES:")
    table_data = []
    for idx, score in matching:
        match_status = "✓ Match" if score >= threshold else "✗ No Match"
        table_data.append([score, match_status, example_sentences[idx]])
    
    print(tabulate(table_data, headers=["Similarity", "Status", "Sentence"], tablefmt="grid", floatfmt=".4f"))
    print()
    
    # Display bottom non-matching examples
    print("BOTTOM 3 NON-MATCHING SENTENCES:")
    table_data = []
    for idx, score in non_matching:
        match_status = "✓ Match" if score >= threshold else "✗ No Match"
        table_data.append([score, match_status, example_sentences[idx]])
    
    print(tabulate(table_data, headers=["Similarity", "Status", "Sentence"], tablefmt="grid", floatfmt=".4f"))

# Calculate overall statistics
total_matches = 0
matches_per_anchor = []

for anchor in anchor_sentences:
    scored_examples = similarity_scores[anchor]
    matches = sum(1 for _, score in scored_examples if score >= threshold)
    total_matches += matches
    matches_per_anchor.append(matches)

print("\n" + "="*100)
print("SUMMARY STATISTICS")
print("="*100)
print(f"Total number of example sentences: {len(example_sentences)}")
print(f"Total number of matches (similarity ≥ {threshold}): {total_matches}")
print(f"Percentage of sentences that match with at least one anchor: {total_matches/len(example_sentences)*100:.2f}%")

print("\nMatches per anchor:")
for i, anchor in enumerate(anchor_sentences):
    print(f"Anchor {i+1}: {matches_per_anchor[i]} matching sentences")

print("\nNote: A sentence can match with multiple anchors, so the sum of matches per anchor may exceed")
print("the total number of unique matching sentences.")