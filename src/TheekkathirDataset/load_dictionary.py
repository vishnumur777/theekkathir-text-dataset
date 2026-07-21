"""
Cleans the theekkathir-text-dataset by:
1. Removing binary/control characters from content and title
2. Removing stray English words mixed into Tamil text
3. Reconstructing Tamil words that were incorrectly split during the
   original newspaper-to-website data conversion (e.g. "குறிப்பி டத்தக்க"
   -> "குறிப்பிடத்தக்க")

Word reconstruction works by checking a dictionary of valid Tamil words:
if two (or three) adjacent word fragments don't form valid words on their
own, but their concatenation does, they are merged back together.

Corpus / dictionary source:
    Kaniyam Foundation's iyal-tamil-spellchecker project
    https://github.com/KaniyamFoundation/iyal-tamil-spellchecker
    Files used: collect_words/frequent_tamil_words.txt (155,966 words)
                collect_words/manually_collected_words.txt

Usage:
    python clean_pipeline.py
    (processes every *.parquet file in the current folder except files
    already ending in "_cleaned.parquet", and writes output into
    cleaned_dataset/)

Author: ARULSELVI72 ( TossHack26)
"""

import os
import re
import glob
import pandas as pd

# Configuration


FREQUENT_WORDS_FILE = "frequent_tamil_words.txt"
MANUAL_WORDS_FILE = "manually_collected_words.txt"
OUTPUT_DIR = "cleaned_dataset"

CONTENT_COLUMN = "உள்ளடக்கம்"
TITLE_COLUMN = "தலைப்பு"

# Tamil unicode block: used to detect whether a token contains Tamil text
TAMIL_RANGE = re.compile(r"[\u0B80-\u0BFF]")

# Control/binary characters left over from the original data conversion
CONTROL_CHAR_RE = re.compile(r"[\x00-\x1f\x7f-\x9f]")

# Matches standalone English words (used to strip stray English text)
ENGLISH_WORD_RE = re.compile(r"\b[a-zA-Z]+\b")

# Short, common Tamil grammar words that should never be merged with a
# neighboring word, even if the combined string happens to also be a
# valid dictionary word (e.g. "ஆம் ஆண்டு" = "the year", must NOT become
# "ஆம்ஆண்டு").
DO_NOT_MERGE = {
    "ஆம்", "போல", "கொண்டு", "என", "என்று", "ஒரு", "இந்த", "அந்த", "என்ற",
}


# Dictionary loading


def load_words(filepath):
    """
    Load a word list file into a set for fast lookup.

    Each line in the source file is formatted as "<word> <frequency_count>".
    Only the word itself (first whitespace-separated token) is kept.

    Args:
        filepath: path to a text file, one word (+ optional count) per line.

    Returns:
        A set of unique words found in the file.
    """
    words = set()
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            word = line.split()[0]
            words.add(word)
    return words


def build_dictionary():
    """
    Build the combined Tamil word dictionary used for word reconstruction.

    Combines the frequent-word list and the manually-collected word list
    from the Kaniyam Foundation spellchecker project into a single set.

    Returns:
        A set of ~156,000 valid Tamil words.
    """
    frequent_words = load_words(FREQUENT_WORDS_FILE)
    manual_words = load_words(MANUAL_WORDS_FILE)
    return frequent_words.union(manual_words)


# Word reconstruction


def is_tamil_word(token):
    """Return True if the token contains at least one Tamil character."""
    return bool(TAMIL_RANGE.search(token))


def fix_broken_words(text, dictionary):
    """
    Detect and merge Tamil words that were incorrectly split into two or
    three fragments, using dictionary lookup.

    Algorithm:
        Scan the text token by token. For each Tamil token, check whether
        joining it with the next 1 or 2 tokens produces a string that
        exists in the dictionary. If so, merge them into a single word.
        Tokens in DO_NOT_MERGE are never merged with their neighbor, to
        avoid corrupting short grammar words (e.g. "ஆம் ஆண்டு").

    Args:
        text: raw sentence/paragraph of Tamil text.
        dictionary: set of valid Tamil words (see build_dictionary()).

    Returns:
        The text with broken words rejoined where possible. Non-Tamil
        tokens (numbers, punctuation, already-removed English words) are
        left untouched.
    """
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

        # Try merging with the next word (2-way split)
        if i + 1 < len(tokens) and tokens[i + 1] not in DO_NOT_MERGE:
            candidate = word + tokens[i + 1]
            if candidate in dictionary:
                result.append(candidate)
                i += 2
                merged = True

        # Try merging with the next two words (3-way split)
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


# Full cleaning pipeline


def clean_text(text, dictionary):
    """
    Run the full cleaning pipeline on a single piece of text:
        1. Strip control/binary characters
        2. Strip stray English words
        3. Reconstruct broken Tamil words
        4. Normalize whitespace

    Args:
        text: raw text from the content or title column. Non-string
            values (e.g. NaN) are returned unchanged.
        dictionary: set of valid Tamil words.

    Returns:
        The cleaned text.
    """
    if not isinstance(text, str):
        return text

    text = CONTROL_CHAR_RE.sub("", text)
    text = ENGLISH_WORD_RE.sub("", text)
    text = fix_broken_words(text, dictionary)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_dataframe(df, dictionary):
    """
    Apply clean_text() to the content and title columns of a dataframe.

    Args:
        df: dataframe loaded from one monthly parquet file.
        dictionary: set of valid Tamil words.

    Returns:
        The same dataframe with CONTENT_COLUMN and TITLE_COLUMN cleaned
        in place.
    """
    df[CONTENT_COLUMN] = df[CONTENT_COLUMN].apply(lambda t: clean_text(t, dictionary))
    df[TITLE_COLUMN] = df[TITLE_COLUMN].apply(lambda t: clean_text(t, dictionary))
    return df


# Batch processing (monthly pipeline entry point)


def process_all_files(input_dir=".", output_dir=OUTPUT_DIR):
    """
    Clean every raw monthly parquet file in input_dir and write:
      - one cleaned parquet per month, to output_dir
      - one combined parquet containing all months, to output_dir

    Files already ending in "_cleaned.parquet" are skipped as input, so
    this function is safe to re-run without double-cleaning output files.
    Empty parquet files (0 rows) are skipped automatically.

    Args:
        input_dir: folder containing raw monthly *.parquet files.
        output_dir: folder to write cleaned files into.

    Returns:
        Number of files successfully processed.
    """
    dictionary = build_dictionary()
    os.makedirs(output_dir, exist_ok=True)

    all_files = glob.glob(os.path.join(input_dir, "*.parquet"))
    raw_files = [f for f in all_files if "_cleaned" not in f]

    cleaned_frames = []
    processed_count = 0

    for filepath in raw_files:
        filename = os.path.basename(filepath)
        try:
            df = pd.read_parquet(filepath)

            if df.empty:
                print(f"Skipping {filename} (0 rows)")
                continue

            df = clean_dataframe(df, dictionary)

            output_name = filename.replace(".parquet", "_cleaned.parquet")
            output_path = os.path.join(output_dir, output_name)
            df.to_parquet(output_path)

            cleaned_frames.append(df)
            processed_count += 1
            print(f"Cleaned {filename} -> {output_path} ({len(df)} rows)")

        except Exception as e:
            print(f"FAILED on {filename}: {e}")

    if cleaned_frames:
        combined = pd.concat(cleaned_frames, ignore_index=True)
        combined_path = os.path.join(output_dir, "theekkathir_full_cleaned.parquet")
        combined.to_parquet(combined_path)
        print(f"Combined dataset saved: {combined_path} ({len(combined)} rows)")

    return processed_count



# Entry point

if __name__ == "__main__":
    process_all_files()
