import os
import json
import shutil
from typing import Dict, List, Tuple, Optional

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


# Label definitions with detailed descriptions
LABEL_DESCRIPTIONS = {
    "dynamic": "This text contains temporal information such as events, deadlines, admissions, scholarships, announcements, exam dates, registration periods, or time-sensitive information that changes frequently.",
    "static": "This text contains permanent information such as FAQs, department details, policies, general information, infrastructure, faculty profiles, course descriptions, or information that rarely changes.",
}


def load_model(model_name: str = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"):
    """
    Load the multilingual zero-shot classification model.
    This model supports multiple Indian languages including Hindi, English, and others.
    """
    print(f"Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    # Move to GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.eval()

    print(f"Model loaded on device: {device}")
    return model, tokenizer, device


def classify_text(text: str, model, tokenizer, device, max_length: int = 512) -> Tuple[str, float, Dict[str, float]]:
    """
    Classify text as 'static' or 'dynamic' using zero-shot classification.

    Returns:
        - label: 'static' or 'dynamic'
        - confidence: confidence score for the predicted label
        - all_scores: dictionary with scores for both labels
    """
    # Truncate text if too long (use first part which often contains key info)
    if len(text) > 2000:
        text = text[:2000]

    # Prepare hypothesis for each label
    premise = text
    labels = list(LABEL_DESCRIPTIONS.keys())

    results = {}

    with torch.no_grad():
        for label in labels:
            hypothesis = LABEL_DESCRIPTIONS[label]

            # Encode premise and hypothesis (NLI format)
            inputs = tokenizer(
                premise, hypothesis, truncation=True, max_length=max_length, padding=True, return_tensors="pt"
            )

            # Move to device
            inputs = {k: v.to(device) for k, v in inputs.items()}

            # Get prediction
            outputs = model(**inputs)
            logits = outputs.logits

            # Get entailment probability (index 2 is entailment in XNLI)
            probs = torch.softmax(logits, dim=1)
            entailment_score = probs[0][2].item()  # Entailment class

            results[label] = entailment_score

    # Determine final label
    predicted_label = max(results, key=results.get)
    confidence = results[predicted_label]

    return predicted_label, confidence, results


def classify_file(file_path: str, model, tokenizer, device) -> Optional[Dict]:
    """
    Classify a single text file.

    Returns:
        Dictionary with classification results or None on error.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        if not text.strip():
            print(f"⚠️  Empty file: {os.path.basename(file_path)}")
            return None

        label, confidence, scores = classify_text(text, model, tokenizer, device)

        return {
            "file": os.path.basename(file_path),
            "path": file_path,
            "category": label,
            "confidence": round(confidence, 4),
            "scores": {k: round(v, 4) for k, v in scores.items()},
        }

    except Exception as e:
        print(f"❌ Error classifying {os.path.basename(file_path)}: {e}")
        return None


def process_directory(
    input_base_dir: str = "./processed_data",
    output_json: str = "./classified_data.json",
    organize_files: bool = True,
    output_organized_dir: str = "./classified_data",
) -> List[Dict]:
    """
    Process all text files in processed_data directory and classify them.

    Args:
        input_base_dir: Base directory containing processed text files
        output_json: Path to save classification results JSON
        organize_files: Whether to copy files to organized folders
        output_organized_dir: Base directory for organized classified files

    Returns:
        List of classification results
    """
    # Load model
    model, tokenizer, device = load_model()

    categories = ["pdf", "docs", "html"]
    all_results = []

    print(f"\n{'='*60}")
    print(f"Starting classification...")
    print(f"{'='*60}\n")

    for category in categories:
        input_dir = os.path.join(input_base_dir, category)

        if not os.path.isdir(input_dir):
            print(f"⚠️  Directory not found: {input_dir}, skipping...")
            continue

        print(f"\nProcessing {category.upper()} files from: {input_dir}")
        print("-" * 60)

        files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]

        for filename in files:
            file_path = os.path.join(input_dir, filename)

            result = classify_file(file_path, model, tokenizer, device)

            if result:
                all_results.append(result)

                # Print result
                label_emoji = "📅" if result["category"] == "dynamic" else "📚"
                print(f"{label_emoji} {filename[:50]:50} → {result['category']:8} (conf: {result['confidence']:.2f})")

                # Organize files if requested
                if organize_files:
                    dest_dir = os.path.join(output_organized_dir, result["category"], category)
                    os.makedirs(dest_dir, exist_ok=True)
                    dest_path = os.path.join(dest_dir, filename)
                    shutil.copy2(file_path, dest_path)

    # Save results to JSON
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"\n{'='*60}")
    print(f"Classification completed!")
    print(f"{'='*60}")
    print(f"Total files classified: {len(all_results)}")

    static_count = sum(1 for r in all_results if r["category"] == "static")
    dynamic_count = sum(1 for r in all_results if r["category"] == "dynamic")

    print(f"📚 Static documents: {static_count}")
    print(f"📅 Dynamic documents: {dynamic_count}")
    print(f"\nResults saved to: {output_json}")

    if organize_files:
        print(f"Organized files saved to: {output_organized_dir}/")

    print(f"{'='*60}\n")

    return all_results


def main():
    """
    Main function to run classification on all processed text files.
    """
    results = process_directory(
        input_base_dir="./processed_data",
        output_json="./classified_data.json",
        organize_files=True,
        output_organized_dir="./classified_data",
    )

    return results


if __name__ == "__main__":
    main()
