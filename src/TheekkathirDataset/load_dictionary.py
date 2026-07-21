# Step 1: Load the Tamil dictionary from the two files

def load_words(filepath):
    words = set()
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()  # splits by whitespace
            word = parts[0]       # take just the word, ignore the count
            words.add(word)
    return words
# Load both word lists
freq_words = load_words("frequent_tamil_words.txt")
manual_words = load_words("manually_collected_words.txt")

# Combine them into one big dictionary
tamil_dict = freq_words.union(manual_words)

print(f"Loaded {len(freq_words)} frequent words")
print(f"Loaded {len(manual_words)} manually collected words")
print(f"Total unique words in dictionary: {len(tamil_dict)}")

# Quick test — check if a word exists
test_word = "வணக்கம்"  # means "hello" in Tamil
if test_word in tamil_dict:
    print(f"'{test_word}' found in dictionary ✅")
else:
    print(f"'{test_word}' NOT found in dictionary ❌")

# Debug: print a few words from the dictionary to inspect them
print("\n--- Sample words from dictionary ---")
sample = list(tamil_dict)[:10]
for word in sample:

    print(repr(word))
# Test: can we detect and fix a broken word?
broken_parts = ["குறிப்பி", "டத்தக்க"]
merged = "".join(broken_parts)

print("\n--- Testing word merge ---")
print(f"Part 1: {broken_parts[0]}")
print(f"Part 2: {broken_parts[1]}")
print(f"Merged: {merged}")

if merged in tamil_dict:
    print(f"'{merged}' found in dictionary ✅ — this IS the correct merge!")
else:
    print(f"'{merged}' NOT found in dictionary ❌")
import re

TAMIL_RANGE = re.compile(r'[\u0B80-\u0BFF]')

def is_tamil_word(token):
    """Check if a token contains Tamil characters"""
    return bool(TAMIL_RANGE.search(token))

# Common short words that should NOT be merged with neighbors
DO_NOT_MERGE = {"ஆம்", "போல", "கொண்டு", "என", "என்று", "ஒரு", "இந்த", "அந்த", "என்ற"}

def fix_broken_words(text, dictionary):
    tokens = text.split()
    result = []
    i = 0
    while i < len(tokens):
        word = tokens[i]

        if not is_tamil_word(word) or word in DO_NOT_MERGE:
            result.append(word)
            i += 1
            continue

        merged = False
        if i + 1 < len(tokens) and tokens[i + 1] not in DO_NOT_MERGE:
            candidate = word + tokens[i + 1]
            if candidate in dictionary:
                result.append(candidate)
                i += 2
                merged = True

        if not merged and i + 2 < len(tokens):
            candidate = word + tokens[i + 1] + tokens[i + 2]
            if candidate in dictionary:
                result.append(candidate)
                i += 3
                merged = True

        if not merged:
            result.append(word)
            i += 1

    return " ".join(result)

# --- Test it on a full sentence ---
test_sentence = "இது ஒரு குறிப்பி டத்தக்க நிகழ்வு ஆகும்"
print("\n--- Testing full sentence fix ---")
print("BEFORE:", test_sentence)
print("AFTER :", fix_broken_words(test_sentence, tamil_dict))

# --- Stress test with more examples ---
test_cases = [
    "அவர் குறிப் பிடத்தக்க சாதனை படைத்தார்",   # split differently
    "இது ஒரு சாதாரண வாக்கியம்",                # nothing broken, should stay same
    "மக்கள் இந்த முடிவை வரவேற் றனர்",           # another broken word
]

print("\n--- Stress test ---")
for sentence in test_cases:
    fixed = fix_broken_words(sentence, tamil_dict)
    print(f"BEFORE: {sentence}")
    print(f"AFTER : {fixed}")
    print()

# Debug: check if the expected merged word exists in the dictionary
check_word = "வரவேற்றனர்"
print(f"\nIs '{check_word}' in dictionary? {check_word in tamil_dict}")

# Debug: manually test this exact merge
part1 = "வரவேற்"
part2 = "றனர்"
manual_merge = part1 + part2

print(f"\npart1: {repr(part1)}")
print(f"part2: {repr(part2)}")
print(f"manual_merge: {repr(manual_merge)}")
print(f"manual_merge in dictionary? {manual_merge in tamil_dict}")
print(f"part2 in dictionary? {part2 in tamil_dict}")

import pandas as pd

# Load the real dataset
df = pd.read_parquet("january_2025.parquet")

print("\n--- Dataset Info ---")
print(f"Number of rows: {len(df)}")
print(f"Columns: {list(df.columns)}")

# Show the first row's content to see what it looks like
print("\n--- Sample content (first row) ---")
print(df.iloc[0])

# --- Run your cleaning function on real dataset content ---
print("\n--- Testing on REAL dataset rows ---")

for i in range(5):  # test first 5 articles
    original = df.iloc[i]['உள்ளடக்கம்']
    cleaned = fix_broken_words(original, tamil_dict)
    
    print(f"\n===== Article {i+1} =====")
    print("ORIGINAL (first 300 chars):")
    print(original[:300])
    print("\nCLEANED (first 300 chars):")
    print(cleaned[:300])
    
    if original != cleaned:
        print("\n✅ Changes were made to this article")
    else:
        print("\n(No changes needed)")

CONTROL_CHAR_RE = re.compile(r'[\x00-\x1f\x7f-\x9f]')
ENGLISH_RE = re.compile(r'\b[a-zA-Z]+\b')

def clean_text(text, dictionary):
    if not isinstance(text, str):
        return text
    text = CONTROL_CHAR_RE.sub('', text)      # remove binary/control chars
    text = ENGLISH_RE.sub('', text)           # remove stray English words
    text = fix_broken_words(text, dictionary) # fix broken Tamil words
    text = re.sub(r'\s+', ' ', text).strip()  # clean up extra spaces
    return text

print("\n--- Cleaning full dataset ---")
df['உள்ளடக்கம்'] = df['உள்ளடக்கம்'].apply(lambda t: clean_text(t, tamil_dict))
df['தலைப்பு'] = df['தலைப்பு'].apply(lambda t: clean_text(t, tamil_dict))

df.to_parquet("january_2025_cleaned.parquet")
print("✅ Saved cleaned dataset as january_2025_cleaned.parquet")

import glob
import os

print("\n" + "="*50)
print("BATCH PROCESSING ALL MONTHLY FILES")
print("="*50)

# Find all raw parquet files (skip already-cleaned ones)
all_parquet_files = glob.glob("*.parquet")
raw_files = [f for f in all_parquet_files if "_cleaned" not in f]

print(f"Found {len(raw_files)} raw parquet files to process\n")

os.makedirs("cleaned_dataset", exist_ok=True)

all_cleaned_dfs = []

for filename in raw_files:
    try:
        df = pd.read_parquet(filename)
        df['உள்ளடக்கம்'] = df['உள்ளடக்கம்'].apply(lambda t: clean_text(t, tamil_dict))
        df['தலைப்பு'] = df['தலைப்பு'].apply(lambda t: clean_text(t, tamil_dict))

        output_path = os.path.join("cleaned_dataset", filename.replace(".parquet", "_cleaned.parquet"))
        df.to_parquet(output_path)
        
        all_cleaned_dfs.append(df)
        print(f"✅ {filename} → {output_path} ({len(df)} rows)")
    except Exception as e:
        print(f"❌ FAILED on {filename}: {e}")

# Combine everything into one master file
if all_cleaned_dfs:
    combined = pd.concat(all_cleaned_dfs, ignore_index=True)
    combined_path = os.path.join("cleaned_dataset", "theekkathir_full_cleaned.parquet")
    combined.to_parquet(combined_path)
    print(f"\n✅ Combined dataset saved: {combined_path} ({len(combined)} total rows)")

print("\n--- Checking the 2 failed files ---")
for f in ["june_2026.parquet", "may_2026.parquet"]:
    try:
        df_check = pd.read_parquet(f)
        print(f"{f}: {len(df_check)} rows, columns: {list(df_check.columns)}")
    except Exception as e:
        print(f"{f}: ERROR reading file — {e}")