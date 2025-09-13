#!/usr/bin/env python3
"""
JSON File Validator
Recursively searches directories for JSON files and validates their syntax.
"""

import os
import json
import sys
from pathlib import Path
from typing import List, Tuple, Dict

def find_json_files(directory: str) -> List[Path]:
    """
    Recursively find all JSON files in the given directory.
    
    Args:
        directory (str): Path to the directory to search
        
    Returns:
        List[Path]: List of Path objects for found JSON files
    """
    json_files = []
    directory_path = Path(directory)
    
    if not directory_path.exists():
        print(f"Error: Directory '{directory}' does not exist.")
        return json_files
    
    if not directory_path.is_dir():
        print(f"Error: '{directory}' is not a directory.")
        return json_files
    
    # Use rglob to recursively find all .json files
    for json_file in directory_path.rglob("*.json"):
        if json_file.is_file():
            json_files.append(json_file)
    
    return json_files

def validate_json_file(file_path: Path) -> Tuple[bool, str]:
    """
    Validate a single JSON file, handling both UTF-8 and UTF-8-BOM encodings.
    
    Args:
        file_path (Path): Path to the JSON file
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    encodings_to_try = ['utf-8-sig', 'utf-8', 'utf-16', 'latin-1']
    
    for encoding in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                json.load(f)
            return True, ""
        except UnicodeDecodeError:
            # Try next encoding
            continue
        except json.JSONDecodeError as e:
            return False, f"JSON decode error: {e}"
        except FileNotFoundError:
            return False, "File not found"
        except PermissionError:
            return False, "Permission denied"
        except Exception as e:
            return False, f"Unexpected error: {e}"
    
    # If all encodings failed
    return False, "Could not decode file with any supported encoding (UTF-8, UTF-8-BOM, UTF-16, Latin-1)"

def main():
    """
    Main function to run the JSON validator.
    """
    # Get the directory to search (default to current directory)
    if len(sys.argv) > 1:
        search_directory = sys.argv[1]
    else:
        search_directory = "."
    
    print(f"Searching for JSON files in: {os.path.abspath(search_directory)}")
    print("-" * 60)
    
    # Find all JSON files
    json_files = find_json_files(search_directory)
    
    if not json_files:
        print("No JSON files found.")
        return
    
    print(f"Found {len(json_files)} JSON file(s)")
    print("-" * 60)
    
    # Validate each JSON file
    valid_files = []
    invalid_files = []
    
    for json_file in json_files:
        is_valid, error_msg = validate_json_file(json_file)
        
        if is_valid:
            valid_files.append(json_file)
            print(f"✓ VALID:   {json_file}")
        else:
            invalid_files.append((json_file, error_msg))
            print(f"✗ INVALID: {json_file}")
            print(f"           Error: {error_msg}")
    
    # Summary
    print("-" * 60)
    print(f"SUMMARY:")
    print(f"  Total files checked: {len(json_files)}")
    print(f"  Valid JSON files:    {len(valid_files)}")
    print(f"  Invalid JSON files:  {len(invalid_files)}")
    
    if invalid_files:
        print(f"\nInvalid files:")
        for file_path, error in invalid_files:
            print(f"  - {file_path}: {error}")
    else:
        print(f"\n🎉 All JSON files are valid!")
    
    # Wait for user input before closing
    input("\nPress Enter to continue...")
    
    # Exit with appropriate code
    if invalid_files:
        sys.exit(1)  # Exit with error code if invalid files found
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()