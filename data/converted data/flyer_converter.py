import pandas as pd
import json
import os

def convert_flyer_csv_to_json():
    """
    Convert flyer_gap-fill.csv to JSON format
    Input: data/raw data/flyer_gap-fill.csv
    Output: data/converted data/flyer_gap-fill.json
    """
    
    # Define paths
    input_path = os.path.join("data", "raw data", "flyer_gap-fill.csv")
    output_path = os.path.join("data", "converted data", "flyer_gap-fill.json")

    print(f"--- Starting Conversion ---")
    
    try:
        # Read CSV with UTF-8 encoding
        df = pd.read_csv(input_path, encoding='utf-8-sig')
        
        questions = []
        for _, row in df.iterrows():
            # Collect all options into a list
            options = [
                str(row['Option A']), 
                str(row['Option B']), 
                str(row['Option C']), 
                str(row['Option D'])
            ]
            
            # Determine correct answer based on letter (A, B, C, or D)
            correct_letter = str(row['Correct Answer']).strip().upper()
            letter_to_index = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
            
            # Get the correct option text
            correct_option_index = letter_to_index.get(correct_letter, 0)
            correct_option_text = options[correct_option_index]
            
            # Create mapping for error analysis on distractors
            error_analysis = {}
            for letter, index in letter_to_index.items():
                opt_text = options[index]
                if letter != correct_letter:
                    error_analysis[opt_text] = {
                        "error_type": row['Error Type']
                    }

            # Build question data structure
            question_data = {
                "id": str(row['ID']),
                "topic": row['Topic'],
                "question_text": row['Question'],
                "options": options,
                "correct_answer": correct_option_text,
                "correct_letter": correct_letter,
                "error_type": row['Error Type'],
                "error_analysis": error_analysis
            }
            questions.append(question_data)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Export to JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=4)
        
        print(f"✅ Success! {len(questions)} questions converted.")
        print(f"📁 File saved to: {output_path}")

    except FileNotFoundError:
        print(f"❌ Error: Could not find file at {input_path}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    convert_flyer_csv_to_json()
