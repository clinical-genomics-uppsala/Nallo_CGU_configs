import os
import sys
import pandas as pd
import subprocess
import shutil

# Path to the script under test
SCRIPT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/create_nallo_samplesheet.py'))

def test_create_nallo_samplesheet(tmp_path):
    """
    Test that the script properly merges units and samples info and generates the expected CSV.
    """
    # Create dummy units.tsv
    units_data = {
        "sample": ["sample1", "sample2"],
        "bam": ["/path/to/sample1.bam", "/path/to/sample2.bam"]
    }
    units_file = tmp_path / "units.tsv"
    pd.DataFrame(units_data).to_csv(units_file, sep="\t", index=False)

    # Create dummy samples_info.csv
    # Note: The script treats "Sex" keys: "Male": 1, "Female": 2, "NA": 0, "Unknown": 0
    samples_info_data = {
        "Provnummer": ["sample1", "sample2"],
        "Sex": ["Male", "Female"]
    }
    samples_info_file = tmp_path / "samples_info.csv"
    pd.DataFrame(samples_info_data).to_csv(samples_info_file, index=False)

    project_id = "TEST_PROJECT"
    output_file = tmp_path / "nallo_samplesheet.csv"

    # Use python to run the script
    cmd = [
        sys.executable,
        SCRIPT_PATH,
        "--units", str(units_file),
        "--samples-info", str(samples_info_file),
        "--project-id", project_id
    ]

    # Run the script inside the temporary directory so the output file is created there
    result = subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True)
    
    # Check if the command ran successfully
    assert result.returncode == 0, f"Script failed with stderr: {result.stderr}"

    # Check if output file was created
    assert output_file.exists(), "Output file nallo_samplesheet.csv not created"

    # Read result and verify contents
    result_df = pd.read_csv(output_file)
    
    expected_columns = ["project", "sample", "file", "family_id", "paternal_id", "maternal_id", "sex", "phenotype"]
    assert list(result_df.columns) == expected_columns

    # Verify rows
    assert len(result_df) == 2
    
    # Row 1 (sample1)
    row1 = result_df[result_df["sample"] == "sample1"].iloc[0]
    assert row1["project"] == project_id
    assert row1["file"] == "/path/to/sample1.bam"
    assert row1["sex"] == 1  # Male -> 1
    assert row1["family_id"] == "sample1"
    assert row1["paternal_id"] == 0
    assert row1["maternal_id"] == 0
    assert row1["phenotype"] == 0

    # Row 2 (sample2)
    row2 = result_df[result_df["sample"] == "sample2"].iloc[0]
    assert row2["project"] == project_id
    assert row2["file"] == "/path/to/sample2.bam"
    assert row2["sex"] == 2  # Female -> 2

def test_create_nallo_samplesheet_missing_args(tmp_path):
    """Test that the script fails when required arguments are missing."""
    cmd = [sys.executable, SCRIPT_PATH]
    result = subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode != 0
    assert "the following arguments are required" in result.stderr

def test_missing_common_samples(tmp_path):
    """Test behavior when no samples match between units and info."""
    units_file = tmp_path / "units.tsv"
    pd.DataFrame({"sample": ["A"], "bam": ["path/A"]}).to_csv(units_file, sep="\t", index=False)
    
    samples_info_file = tmp_path / "samples_info.csv"
    pd.DataFrame({"Provnummer": ["B"], "Sex": ["Male"]}).to_csv(samples_info_file, index=False)

    cmd = [
        sys.executable,
        SCRIPT_PATH,
        "--units", str(units_file),
        "--samples-info", str(samples_info_file),
        "--project-id", "PROJ"
    ]
    
    result = subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0
    
    output_file = tmp_path / "nallo_samplesheet.csv"
    assert output_file.exists()
    
    # Should be empty since inner join finds no matches
    df = pd.read_csv(output_file)
    assert len(df) == 0

def test_sex_conversion_na_unknown(tmp_path):
    """Test that NA and Unknown in Sex column are converted to 0."""
    units_data = {
        "sample": ["sample3", "sample4"],
        "bam": ["/path/to/sample3.bam", "/path/to/sample4.bam"]
    }
    units_file = tmp_path / "units.tsv"
    pd.DataFrame(units_data).to_csv(units_file, sep="\t", index=False)

    samples_info_data = {
        "Provnummer": ["sample3", "sample4"],
        "Sex": ["NA", "Unknown"]
    }
    samples_info_file = tmp_path / "samples_info.csv"
    pd.DataFrame(samples_info_data).to_csv(samples_info_file, index=False)

    project_id = "TEST_PROJECT"
    output_file = tmp_path / "nallo_samplesheet.csv"

    cmd = [
        sys.executable,
        SCRIPT_PATH,
        "--units", str(units_file),
        "--samples-info", str(samples_info_file),
        "--project-id", project_id
    ]

    result = subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0
    
    result_df = pd.read_csv(output_file)
    assert len(result_df) == 2
    
    # Both should have sex = 0
    assert result_df.loc[result_df["sample"] == "sample3", "sex"].values[0] == 0
    assert result_df.loc[result_df["sample"] == "sample4", "sex"].values[0] == 0
