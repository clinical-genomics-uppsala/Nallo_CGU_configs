#!/usr/bin/env python3
import json
import jsonschema
import sys
import glob
import argparse
import urllib.request
import urllib.error
import os

def download_schema(version="0.11.0", output_path="nallo_schema.json"):
    # Try the v-prefixed tag first, then without, or the direct link
    url = f"https://raw.githubusercontent.com/genomic-medicine-sweden/nallo/v{version.lstrip('v')}/nextflow_schema.json"
    print(f"Downloading schema from {url} ...")
    try:
        with urllib.request.urlopen(url, timeout=30) as response, open(output_path, 'wb') as f:
            f.write(response.read())
        print("Download successful.")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f"Failed to download schema: {e}")
        # fallback without 'v'
        fallback_url = f"https://raw.githubusercontent.com/genomic-medicine-sweden/nallo/{version.lstrip('v')}/nextflow_schema.json"
        print(f"Trying fallback url: {fallback_url} ...")
        try:
            with urllib.request.urlopen(fallback_url, timeout=30) as fallback_response, open(output_path, 'wb') as f:
                f.write(fallback_response.read())
            print("Download successful.")
        except (urllib.error.URLError, TimeoutError, OSError) as fallback_e:
            print(f"Failed to download schema: {fallback_e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Validate param files against Nallo schema")
    parser.add_argument("--schema-version", default="0.11.0", help="Nallo version tag to fetch schema for (e.g. 0.11.0)")
    parser.add_argument("--schema-file", default="nallo_schema.json", help="Local path to store or read the schema")
    parser.add_argument("--params-dir", default="params", help="Directory containing JSON parameter files")
    parser.add_argument("--force-download", action="store_true", help="Force redownload of the schema")
    args = parser.parse_args()

    if args.force_download or not os.path.exists(args.schema_file):
        download_schema(args.schema_version, args.schema_file)

    with open(args.schema_file) as f:
        schema = json.load(f)
        
    validator = jsonschema.Draft7Validator(schema)
    success = True
    
    param_files = glob.glob(os.path.join(args.params_dir, "*.json"))
    if not param_files:
        print(f"No JSON files found in {args.params_dir}/")
        sys.exit(1)

    for param_file in param_files:
        print(f"\nChecking {param_file} ...")
        try:
            with open(param_file) as f:
                instance = json.load(f)
        except Exception as e:
            print(f"  ❌ Failed to read JSON: {e}")
            success = False
            continue
            
        errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
        
        # We expect input and outdir to be missing since they are CLI arguments
        ignored_root_required = {"input", "outdir"}

        def is_ignored_required(err):
            if err.validator != "required":
                return False
            if len(err.path) != 0:  # only suppress root-level required errors
                return False
            return err.message in {f"'{k}' is a required property" for k in ignored_root_required}

        actual_errors = [e for e in errors if not is_ignored_required(e)]
        
        if actual_errors:
            success = False
            for e in actual_errors:
                print(f"  ❌ Error: {e.message}")
        else:
            print("  ✅ Validation passed")

    if not success:
        print("\nValidation failed for one or more files.")
        sys.exit(1)
    else:
        print("\nAll parameter files passed validation!")

if __name__ == "__main__":
    main()
