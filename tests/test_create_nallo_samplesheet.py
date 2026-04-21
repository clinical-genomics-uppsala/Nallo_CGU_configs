import os
import sys
import pandas as pd
import subprocess

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
    assert row2["family_id"] == "sample2"
    assert row2["paternal_id"] == 0
    assert row2["maternal_id"] == 0
    assert row2["phenotype"] == 0

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

def test_missing_column_in_units(tmp_path):
    """Test that the script fails with clear error when required column is missing in units file."""
    # Missing 'bam' column
    units_data = {
        "sample": ["sample1", "sample2"],
        "file_path": ["/path/to/sample1.bam", "/path/to/sample2.bam"]  # Wrong column name
    }
    units_file = tmp_path / "units.tsv"
    pd.DataFrame(units_data).to_csv(units_file, sep="\t", index=False)

    samples_info_data = {
        "Provnummer": ["sample1", "sample2"],
        "Sex": ["Male", "Female"]
    }
    samples_info_file = tmp_path / "samples_info.csv"
    pd.DataFrame(samples_info_data).to_csv(samples_info_file, index=False)

    cmd = [
        sys.executable,
        SCRIPT_PATH,
        "--units", str(units_file),
        "--samples-info", str(samples_info_file),
        "--project-id", "TEST_PROJECT"
    ]

    result = subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 1
    assert "Missing required columns" in result.stderr
    assert "bam" in result.stderr

def test_missing_column_in_samples_info(tmp_path):
    """Test that the script fails with clear error when required column is missing in samples info file."""
    units_data = {
        "sample": ["sample1", "sample2"],
        "bam": ["/path/to/sample1.bam", "/path/to/sample2.bam"]
    }
    units_file = tmp_path / "units.tsv"
    pd.DataFrame(units_data).to_csv(units_file, sep="\t", index=False)

    # Missing 'Sex' column
    samples_info_data = {
        "Provnummer": ["sample1", "sample2"],
        "Gender": ["Male", "Female"]  # Wrong column name
    }
    samples_info_file = tmp_path / "samples_info.csv"
    pd.DataFrame(samples_info_data).to_csv(samples_info_file, index=False)

    cmd = [
        sys.executable,
        SCRIPT_PATH,
        "--units", str(units_file),
        "--samples-info", str(samples_info_file),
        "--project-id", "TEST_PROJECT"
    ]

    result = subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 1
    assert "Missing required columns" in result.stderr
    assert "Sex" in result.stderr

def test_missing_multiple_columns(tmp_path):
    """Test that the script fails with clear error when multiple columns are missing."""
    # Missing 'sample' column
    units_data = {
        "sample_id": ["sample1", "sample2"],  # Wrong column name
        "file": ["/path/to/sample1.bam", "/path/to/sample2.bam"]  # Wrong column name
    }
    units_file = tmp_path / "units.tsv"
    pd.DataFrame(units_data).to_csv(units_file, sep="\t", index=False)

    samples_info_data = {
        "Provnummer": ["sample1", "sample2"],
        "Sex": ["Male", "Female"]
    }
    samples_info_file = tmp_path / "samples_info.csv"
    pd.DataFrame(samples_info_data).to_csv(samples_info_file, index=False)

    cmd = [
        sys.executable,
        SCRIPT_PATH,
        "--units", str(units_file),
        "--samples-info", str(samples_info_file),
        "--project-id", "TEST_PROJECT"
    ]

    result = subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 1
    assert "Missing required columns" in result.stderr
    assert "sample" in result.stderr
    assert "bam" in result.stderr

def test_custom_output_path(tmp_path):
    """Test that the --output argument allows specifying a custom output path."""
    # Create dummy units.tsv
    units_data = {
        "sample": ["sample1"],
        "bam": ["/path/to/sample1.bam"]
    }
    units_file = tmp_path / "units.tsv"
    pd.DataFrame(units_data).to_csv(units_file, sep="\t", index=False)

    # Create dummy samples_info.csv
    samples_info_data = {
        "Provnummer": ["sample1"],
        "Sex": ["Male"]
    }
    samples_info_file = tmp_path / "samples_info.csv"
    pd.DataFrame(samples_info_data).to_csv(samples_info_file, index=False)

    # Specify a custom output path
    custom_output = tmp_path / "custom_output.csv"
    
    cmd = [
        sys.executable,
        SCRIPT_PATH,
        "--units", str(units_file),
        "--samples-info", str(samples_info_file),
        "--project-id", "TEST_PROJECT",
        "--output", str(custom_output)
    ]

    result = subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, f"Script failed with stderr: {result.stderr}"

    # Check if custom output file was created
    assert custom_output.exists(), f"Custom output file {custom_output} not created"
    
    # Verify the default output was NOT created
    default_output = tmp_path / "nallo_samplesheet.csv"
    assert not default_output.exists(), "Default output file should not be created when --output is specified"

    # Verify content is correct
    result_df = pd.read_csv(custom_output)
    assert len(result_df) == 1
    assert result_df.iloc[0]["sample"] == "sample1"


def test_numeric_sample_prefixing(tmp_path):
    """Test that numeric sample IDs are prefixed with 'D-'."""
    # Numeric samples: 52662
    units_data = {
        "sample": [52662],
        "bam": ["/path/to/52662.bam"]
    }
    units_file = tmp_path / "units.tsv"
    pd.DataFrame(units_data).to_csv(units_file, sep="\t", index=False)

    # Info also has numeric provnummer
    samples_info_data = {
        "Provnummer": [52662],
        "Sex": ["Male"]
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
    assert len(result_df) == 1
    # Check that sample was renamed D-52662
    assert result_df.iloc[0]["sample"] == "D-52662"
    # Check that merge worked (which implies Provnummer was matched correctly)
    assert result_df.iloc[0]["sex"] == 1


def test_mixed_numeric_and_alphanumeric_samples(tmp_path):
    """Test that only numeric sample IDs are prefixed with 'D-' in mixed datasets."""
    # Mixed samples: one numeric (52662) and one alphanumeric (D99-07356)
    units_data = {
        "sample": [52662, "D99-07356"],
        "bam": ["/path/to/52662.bam", "/path/to/D99-07356.bam"]
    }
    units_file = tmp_path / "units.tsv"
    pd.DataFrame(units_data).to_csv(units_file, sep="\t", index=False)

    # Info also has mixed provnummer
    samples_info_data = {
        "Provnummer": [52662, "D99-07356"],
        "Sex": ["Male", "Female"]
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
    assert result.returncode == 0, f"Script failed with stderr: {result.stderr}"
    
    result_df = pd.read_csv(output_file)
    assert len(result_df) == 2
    
    # Check that numeric sample was prefixed
    assert "D-52662" in result_df["sample"].values
    # Check that alphanumeric sample was NOT modified
    assert "D99-07356" in result_df["sample"].values
    
    # Verify both merges worked correctly
    row1 = result_df[result_df["sample"] == "D-52662"].iloc[0]
    assert row1["sex"] == 1  # Male
    
    row2 = result_df[result_df["sample"] == "D99-07356"].iloc[0]
    assert row2["sex"] == 2  # Female

def test_rename_samples(tmp_path):
    # Create dummy units.tsv
    units_data = {
        "sample": ["sample1", "sample2"],
        "bam": ["/path/to/sample1.bam", "/path/to/sample2.bam"]
    }
    units_file = tmp_path / "units.tsv"
    pd.DataFrame(units_data).to_csv(units_file, sep="\t", index=False)

    # Create dummy samples_info.csv
    samples_info_data = {
        "Provnummer": ["sample1", "sample2"],
        "Sex": ["Male", "Female"]
    }
    samples_info_file = tmp_path / "samples_info.csv"
    pd.DataFrame(samples_info_data).to_csv(samples_info_file, index=False)

    # Create dummy rename_map.tsv
    rename_map_data = {
        "old_name": ["sample1"],
        "new_name": ["sample1_renamed"]
    }
    rename_map_file = tmp_path / "rename_map.tsv"
    pd.DataFrame(rename_map_data).to_csv(rename_map_file, sep="\t", index=False)

    project_id = "TEST_PROJECT"
    output_file = tmp_path / "nallo_samplesheet.csv"

    cmd = [
        sys.executable,
        SCRIPT_PATH,
        "--units", str(units_file),
        "--samples-info", str(samples_info_file),
        "--project-id", project_id,
        "--rename-map", str(rename_map_file)
    ]

    result = subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, f"Script failed with stderr: {result.stderr}"
    
    result_df = pd.read_csv(output_file)
    assert len(result_df) == 2
    
    # Check that sample was renamed
    assert "sample1_renamed" in result_df["sample"].values
    # Check that the other sample was not renamed
    assert "sample2" in result_df["sample"].values
    
    # Verify the merge worked correctly
    row1 = result_df[result_df["sample"] == "sample1_renamed"].iloc[0]
    assert row1["sex"] == 1  # Male
    
    row2 = result_df[result_df["sample"] == "sample2"].iloc[0]
    assert row2["sex"] == 2  # Female

    