import json
import pickle
from pathlib import Path
from fastembed import TextEmbedding
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load model
print("Loading embedding model...")
model = TextEmbedding(model="text2vec-base")

embeddings_folder = Path("embeddings")
pdf_folder = Path("Original_Documents")


def load_all_embeddings():
    """Load all embeddings into memory"""
    print("Loading all embeddings...")
    pdf_files = list(pdf_folder.glob("*.pdf"))
    all_rich_data = []
    for pdf_file in pdf_files:
        embedding_file = embeddings_folder / f"{pdf_file.stem}_embeddings.pkl"
        if embedding_file.exists():
            with open(embedding_file, "rb") as f:
                embeddings = pickle.load(f)
                all_rich_data.extend(embeddings)
    print(f"Loaded {len(all_rich_data)} total chunks from {len(pdf_files)} papers")
    return all_rich_data


def retrieve_chunks(query, all_rich_data, top_n=5):
    """Retrieve top N chunks for a query"""
    # Extract embeddings into matrix
    vector_matrix = np.array([item["embedding"] for item in all_rich_data])
    
    # Embed query
    query_embedding = list(model.embed([query]))
    query_embedding = np.array(query_embedding).reshape(1, -1)
    
    # Compute similarities
    similarities = cosine_similarity(query_embedding, vector_matrix)[0]
    
    # Get top results
    top_indices = np.argsort(similarities)[::-1][:top_n]
    
    top_results = []
    for idx in top_indices:
        result = {
            "score": float(similarities[idx]),
            "pdf_file": all_rich_data[idx]["pdf_file"],
            "chunk_num": all_rich_data[idx]["chunk_num"],
            "text": all_rich_data[idx]["text"]
        }
        top_results.append(result)
    
    return top_results


def check_if_correct_paper_retrieved(retrieved_chunks, expected_papers):
    """
    Check if any of the expected papers are in the retrieved chunks
    """
    retrieved_papers = set([chunk["pdf_file"] for chunk in retrieved_chunks])
    expected_set = set(expected_papers)
    
    found = retrieved_papers.intersection(expected_set)
    return len(found) > 0, found, retrieved_papers


def check_answer_contains_key_terms(answer, ground_truth):
    """
    Simple keyword matching - does the answer contain key terms from ground truth?
    """
    # Extract potential key terms (very naive approach)
    # Numbers, capitalized terms, etc.
    answer_lower = answer.lower()
    ground_truth_lower = ground_truth.lower()
    
    # Check for some key numbers/terms
    key_terms = []
    
    # Look for numbers
    import re
    numbers = re.findall(r'\d+\.?\d*', ground_truth)
    for num in numbers:
        if num in answer:
            key_terms.append(num)
    
    # Check if ground truth concepts appear in answer
    # This is crude but gives you a signal
    overlap_score = 0
    gt_words = set(ground_truth_lower.split())
    answer_words = set(answer_lower.split())
    
    # Remove common words
    common = {'the', 'a', 'an', 'in', 'of', 'to', 'and', 'is', 'was', 'were', 'are', 'for', 'with'}
    gt_words = gt_words - common
    answer_words = answer_words - common
    
    overlap = gt_words.intersection(answer_words)
    if len(gt_words) > 0:
        overlap_score = len(overlap) / len(gt_words)
    
    return overlap_score, list(overlap)


def run_evaluation():
    """Run evaluation on all questions"""
    
    # Load questions
    questions_file = Path("evaluation_questions.json")
    with open(questions_file, "r") as f:
        questions = json.load(f)
    
    print(f"\nLoaded {len(questions)} questions\n")
    print("="*100)
    
    # Load all embeddings
    all_rich_data = load_all_embeddings()
    
    print("\n" + "="*100)
    print("STARTING EVALUATION")
    print("="*100)
    
    results = []
    correct_paper_retrieved = 0
    
    for i, q_data in enumerate(questions):
        question = q_data["question"]
        ground_truth = q_data["ground_truth"]
        expected_papers = q_data["papers_containing_answer"]
        
        print(f"\n{'='*100}")
        print(f"QUESTION {i+1}/{len(questions)}")
        print(f"{'='*100}")
        print(f"Q: {question}\n")
        print(f"Expected paper(s): {', '.join(expected_papers)}")
        print(f"Ground truth: {ground_truth}\n")
        
        # Retrieve chunks
        retrieved = retrieve_chunks(question, all_rich_data, top_n=5)
        
        # Check if correct paper retrieved
        paper_found, found_papers, all_retrieved_papers = check_if_correct_paper_retrieved(
            retrieved, expected_papers
        )
        
        if paper_found:
            correct_paper_retrieved += 1
            print(f"✓ CORRECT PAPER RETRIEVED: {found_papers}")
        else:
            print(f"✗ WRONG PAPERS RETRIEVED")
        
        print(f"\nTop 5 retrieved chunks:")
        for j, chunk in enumerate(retrieved):
            print(f"  {j+1}. {chunk['pdf_file']} (score: {chunk['score']:.3f})")
            print(f"     Preview: {chunk['text'][:150]}...")
        
        # Generate "answer" by concatenating chunks
        answer = "\n\n".join([chunk["text"] for chunk in retrieved])
        
        # Check keyword overlap
        overlap_score, overlapping_terms = check_answer_contains_key_terms(answer, ground_truth)
        
        print(f"\nKeyword overlap with ground truth: {overlap_score:.2%}")
        if overlapping_terms:
            print(f"Overlapping terms: {', '.join(overlapping_terms[:10])}")
        
        # Store result
        result = {
            "question": question,
            "correct_paper_retrieved": paper_found,
            "retrieved_papers": list(all_retrieved_papers),
            "expected_papers": expected_papers,
            "top_chunk_score": retrieved[0]["score"],
            "keyword_overlap": overlap_score
        }
        results.append(result)
    
    # Print summary
    print("\n" + "="*100)
    print("EVALUATION SUMMARY")
    print("="*100)
    print(f"Questions evaluated: {len(questions)}")
    print(f"Correct papers retrieved: {correct_paper_retrieved}/{len(questions)} ({correct_paper_retrieved/len(questions)*100:.1f}%)")
    
    avg_overlap = sum(r["keyword_overlap"] for r in results) / len(results)
    print(f"Average keyword overlap: {avg_overlap:.2%}")
    
    avg_top_score = sum(r["top_chunk_score"] for r in results) / len(results)
    print(f"Average top chunk similarity score: {avg_top_score:.3f}")
    
    # Save results
    output_file = Path("evaluation_results.json")
    with open(output_file, "w") as f:
        json.dump({
            "summary": {
                "total_questions": len(questions),
                "correct_papers_retrieved": correct_paper_retrieved,
                "accuracy": correct_paper_retrieved / len(questions),
                "avg_keyword_overlap": avg_overlap,
                "avg_top_chunk_score": avg_top_score
            },
            "results": results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to {output_file}")


if __name__ == "__main__":
    run_evaluation()