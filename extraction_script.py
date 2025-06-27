import os
import pandas as pd
import re

# Folder path where the text files are stored
FOLDER_PATH = './corpus'  
OUTPUT_CSV = 'positive_keyword_contexts_new.csv'

# Define your positive keywords
positive_keywords = [
    "simple", "simplicity", "simply", "simplify", "simplifies", "simpler", "simplest", "simpleâ€”", "simple'",
    "well", "better", "best", "benefits", "benefit", "beneficial", "success", "successful", "successfully",
    "ease", "easy", "easier", "easiest", "trivial", "positives", "positive", "positively", "advantage", 
    "advantages", "improved", "improvement", "improvements", "effective", "efficiency", "efficient",
    "achievement", "achievements", "achieve", "accomplished", "accomplishment", "solution", "solutions",
    "solved", "resolution", "resolutions", "enhance", "enhanced", "enhancement", "progress", "value", 
    "valuable", "helpful"
]

'''
negative_keywords = [
    "problem", "problems", "difficult", "difficulty", "difficulties", "challenge", "challenges", 
    "challenging", "constraint", "constraints", "negative", "issue", "issues", "obstacles", 
    "problematic", "hard", "harder", "hardest", "hardly", "failure", "failures", "fault", "faults", 
    "error", "errors", "bug", "bugs", "flaw", "flaws", "mistake", "mistakes", "struggle", "struggling",
    "limitation", "limitations", "drawback", "drawbacks", "barrier", "barriers", "risk", "risks", 
    "risky", "hurdle", "hurdles", "bottleneck", "bottlenecks", "poor", "insufficient", "inadequate", 
    "incomplete", "weak", "weakness", "weaknesses", "restriction", "restrictions", "obstacle", 
    "impediment", "impediments", "unsuccessful", "problematic", "crisis", "crises", "unfeasible", 
    "unsolved", "complicated", "complexity", "worse", "worsening", "deteriorate", "degraded"
]'''


# Compile regex pattern for fast searching (word boundary-based)
keyword_pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in positive_keywords) + r')\b', re.IGNORECASE)

def clean_word(word):
    # Remove punctuation and make lowercase for matching
    return re.sub(r'[^\w]', '', word).lower()

# Regex to extract a 4-digit year (between 1900-2099) from filename
year_pattern = re.compile(r'(19|20)\d{2}')

if not os.path.exists(OUTPUT_CSV):
    pd.DataFrame(columns=['File', 'Left Context', 'Hit', 'Right Context', 'Full Passage', 'Year']).to_csv(OUTPUT_CSV, index=False, encoding='utf-8')


# Loop through each file in the folder
for filename in os.listdir(FOLDER_PATH):
    if filename.endswith('.txt'):
        file_path = os.path.join(FOLDER_PATH, filename)
        
        # Extract year from filename
        year_match = year_pattern.search(filename)
        year = year_match.group(0) if year_match else 'Unknown'
        print(f"Processing file: {filename} (Year: {year})")
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            text = file.read()
            
            # Clean non-ASCII characters (remove weird encoding symbols)
            text = re.sub(r'[^\x00-\x7F]+', ' ', text)

            # Tokenize the text into words
            words = re.findall(r'\b\w+\b', text)
            
            results = []
            i = 0
            while i < len(words):
                current_word = clean_word(words[i])
                if current_word.lower() in [k.lower() for k in positive_keywords]:
                    # Get 25 words before and after
                    left_start = max(0, i - 25)
                    right_end = min(len(words), i + 26)  # +1 for the hit word, +25 after
                    
                    left_context = ' '.join(words[left_start:i])
                    hit = current_word
                    right_context = ' '.join(words[i+1:right_end])
                    full_passage = f"{left_context} {hit} {right_context}".strip()
                    
                    results.append({
                        'File': filename,
                        'Left Context': left_context,
                        'Hit': hit,
                        'Right Context': right_context,
                        'Full Passage': full_passage,
                        'Year': year
                    })
                    
                    # Skip next 25 words after the hit
                    i += 26
                else:
                    i += 1

            # After each file: append results to CSV
            if results:
                pd.DataFrame(results).to_csv(OUTPUT_CSV, mode='a', header=False, index=False, encoding='utf-8')
                print(f"Appended {len(results)} rows from {filename} to CSV.")