import pandas as pd
import argparse
import sys

# Opt-in to future behavior for replace() to avoid FutureWarning
pd.set_option('future.no_silent_downcasting', True)

def validate_columns(df, required_columns, file_path):
    """
    Validate that a DataFrame contains all required columns.
    
    Args:
        df: pandas DataFrame to validate
        required_columns: list of column names that must be present
        file_path: path to the file (for error messages)
    
    Raises:
        SystemExit: if any required columns are missing
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: Missing required columns in {file_path}:", file=sys.stderr)
        print(f"  Missing: {', '.join(missing_columns)}", file=sys.stderr)
        print(f"  Available: {', '.join(df.columns.tolist())}", file=sys.stderr)
        sys.exit(1)

# Parse command-line arguments
def main():
    parser = argparse.ArgumentParser(description='Create Nallo samplesheet from units and sample info files')
    parser.add_argument('--units', required=True, help='Path to units TSV file')
    parser.add_argument('--samples-info', required=True, help='Path to samples info Excel file')
    parser.add_argument('--project-id', required=True, help='Project ID string')
    args = parser.parse_args()

    units = pd.read_csv(args.units, sep="\t")
    validate_columns(units, ["sample", "bam"], args.units)

    samples_info = pd.read_csv(args.samples_info)
    validate_columns(samples_info, ["Provnummer", "Sex"], args.samples_info)

    project_id = args.project_id


    samplesheet_df = pd.merge(units, samples_info, left_on="sample", right_on="Provnummer", how="inner")
    samplesheet_df["sex"] = samplesheet_df["Sex"].fillna("NA").replace({"Male": 1, "Female": 2, "NA": 0, "Unknown": 0})
    samplesheet_df["family_id"] = samplesheet_df["sample"]
    samplesheet_df["paternal_id"] = ["0"] * samplesheet_df.shape[0]
    samplesheet_df["maternal_id"] = ["0"] * samplesheet_df.shape[0]    
    samplesheet_df["phenotype"] = ["0"] * samplesheet_df.shape[0]
    samplesheet_df["project"] = [project_id] * samplesheet_df.shape[0]
    samplesheet_df.rename(columns={"bam": "file"}, inplace=True)

    nallo_samplesheet = samplesheet_df[["project","sample","file","family_id","paternal_id","maternal_id","sex","phenotype"]]
    nallo_samplesheet.to_csv("nallo_samplesheet.csv", index=False)

if __name__ == "__main__":
    main()
