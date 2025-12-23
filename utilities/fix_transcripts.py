#!/usr/bin/env python3
"""
Fix transcript CSV files to conform to CollectionBuilder format.
Converts various formats to: timestamp,speaker,words
"""

import csv
import sys
from pathlib import Path

def fix_transcript_file(filepath):
    """Fix a single transcript CSV file."""
    print(f"Processing {filepath.name}...")
    
    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.strip():
        print(f"  Warning: {filepath.name} is empty")
        return
    
    lines = content.strip().split('\n')
    header = lines[0]
    
    # Detect delimiter from header
    delimiter = ';' if header.count(';') > header.count(',') else ','
    
    # Parse the CSV
    import io
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
    
    # Prepare output rows
    output_rows = []
    
    for row in reader:
        # Handle empty column name (leading comma/semicolon)
        if '' in row and not row[''].strip():
            del row['']
        
        # Map various column names to the standard format
        # Priority: exact match, then case-insensitive
        timestamp = ''
        speaker = ''
        words = ''
        
        # Find timestamp (prefer Start Timestamp over End Timestamp)
        for key in ['timestamp', 'Timestamp', 'Start Timestamp', 'start timestamp']:
            if key in row and row[key]:
                timestamp = row[key].strip()
                break
        
        # Find speaker
        for key in ['speaker', 'Speaker']:
            if key in row and row[key]:
                speaker = row[key].strip()
                break
        
        # Find words/transcript
        for key in ['words', 'Transcript', 'transcript']:
            if key in row and row[key]:
                words = row[key].strip()
                break
        
        # Skip completely empty rows
        if not timestamp and not speaker and not words:
            continue
            
        output_rows.append({
            'timestamp': timestamp,
            'speaker': speaker,
            'words': words
        })
    
    # Write back to file with comma delimiter
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'speaker', 'words'])
        writer.writeheader()
        writer.writerows(output_rows)
    
    print(f"  ✓ Fixed {filepath.name} ({len(output_rows)} rows)")

def main():
    # Files that need fixing based on our analysis
    transcript_dir = Path(__file__).parent.parent / '_data' / 'transcripts'
    
    files_to_fix = [
        'dg_1752254667.csv',
        'dg_1763646599.csv', 
        'dg_1752254652.csv',
        'dg_1752254537.csv',
    ]
    
    for filename in files_to_fix:
        filepath = transcript_dir / filename
        if filepath.exists():
            try:
                fix_transcript_file(filepath)
            except Exception as e:
                print(f"  ✗ Error processing {filename}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"  Warning: {filename} not found")
    
    print("\nDone!")

if __name__ == '__main__':
    main()
