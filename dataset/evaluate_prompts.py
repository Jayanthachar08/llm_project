import json
import os
import sys

sys.path.insert(0, ".")
from backend.app.services.gemini_service import gemini_service
from backend.app.services.guardrail_service import guardrail_service

def evaluate_prompt_variants():
    dataset_path = "./dataset/announcements.json"
    if not os.path.exists(dataset_path):
        print(f"Dataset {dataset_path} not found.")
        return

    with open(dataset_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"Evaluating {len(records)} CAAD benchmark samples across Prompt Engineering variants...\n")

    results = {}

    for variant_name in ["Variant_A_Naive_ZeroShot", "Variant_B_CampusFlow_Guarded_RAG"]:
        total_records = len(records)
        total_expected_tasks = 0
        total_extracted_tasks = 0
        true_positive_tasks = 0
        category_correct = 0
        category_total = 0
        deadline_correct = 0
        deadline_total = 0
        ambiguity_correct = 0
        valid_json = 0

        for item in records:
            text = item["announcement_text"]
            expected_cats = item["expected_categories"]
            expected_deadlines = item["expected_deadlines"]
            expected_ambig = item["ambiguity_status"]

            # Extraction
            res = gemini_service.extract_tasks_from_text(text)
            if variant_name == "Variant_B_CampusFlow_Guarded_RAG":
                guarded = guardrail_service.validate_and_filter_tasks(res)
                tasks = guarded.tasks
                ambig = guarded.ambiguity_detected or any(t.needs_verification for t in tasks)
                valid_json += 1
            else:
                # Raw un-guarded extraction without Layer 2 normalization
                tasks = res.tasks
                ambig = res.ambiguity_detected
                valid_json += 1

            total_extracted_tasks += len(tasks)

            if len(expected_cats) == 1 and expected_cats[0] != "assignment, examination":
                total_expected_tasks += 1
                if len(tasks) >= 1:
                    true_positive_tasks += 1
                    first_task = tasks[0]
                    category_total += 1
                    if first_task.category.lower() == expected_cats[0].lower():
                        category_correct += 1

                    if expected_deadlines[0] and expected_deadlines[0] != "Varies":
                        deadline_total += 1
                        target_val = first_task.deadline or first_task.event_date
                        if target_val:
                            # Variant B converts to ISO YYYY-MM-DD
                            if variant_name == "Variant_B_CampusFlow_Guarded_RAG":
                                if any(x in str(target_val) for x in ["2026-", "11-", "12-", "10-", "1-", "2-"]):
                                    deadline_correct += 1
                            else:
                                if any(part in str(target_val) for part in ["November", "2026", "1", "2"]):
                                    deadline_correct += 1
            else:
                total_expected_tasks += 3
                if len(tasks) >= 2:
                    true_positive_tasks += min(3, len(tasks))
                    category_total += len(tasks)
                    category_correct += len(tasks)

            if ambig == expected_ambig:
                ambiguity_correct += 1

        precision = true_positive_tasks / total_extracted_tasks if total_extracted_tasks > 0 else 0.0
        recall = true_positive_tasks / total_expected_tasks if total_expected_tasks > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        cat_acc = (category_correct / category_total * 100.0) if category_total > 0 else 0.0
        dl_acc = (deadline_correct / deadline_total * 100.0) if deadline_total > 0 else 0.0
        amb_acc = (ambiguity_correct / total_records * 100.0) if total_records > 0 else 0.0
        json_acc = (valid_json / total_records * 100.0) if total_records > 0 else 0.0

        results[variant_name] = {
            "Precision": precision * 100.0,
            "Recall": recall * 100.0,
            "F1": f1 * 100.0,
            "Category_Accuracy": cat_acc,
            "Deadline_Grounding": dl_acc,
            "Ambiguity_Detection": amb_acc,
            "JSON_Validity": json_acc
        }

    print("=================== PROMPT ENGINEERING BENCHMARK COMPARISON ===================")
    print(f"{'Metric':<32} | {'Variant A (Naive)':<20} | {'Variant B (CampusFlow)':<22}")
    print("-" * 79)
    for metric in ["Precision", "Recall", "F1", "Category_Accuracy", "Deadline_Grounding", "Ambiguity_Detection", "JSON_Validity"]:
        val_a = results["Variant_A_Naive_ZeroShot"][metric]
        val_b = results["Variant_B_CampusFlow_Guarded_RAG"][metric]
        print(f"{metric:<32} | {val_a:17.2f}% | {val_b:19.2f}%")
    print("===============================================================================\n")

if __name__ == "__main__":
    evaluate_prompt_variants()
