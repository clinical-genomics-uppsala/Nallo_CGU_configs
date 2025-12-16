import json
import subprocess
import pytest
from pathlib import Path

# Path to params file
PARAMS_FILE = Path(__file__).parent.parent / "params" / "nallo-cgu-params.revio_wgs.json"
NALLO_VERSION = "0.8.1"


def test_params_file_exists():
    """Test that the params file exists and is valid JSON."""
    assert PARAMS_FILE.exists(), f"Params file not found: {PARAMS_FILE}"
    
    with open(PARAMS_FILE) as f:
        params = json.load(f)
    
    assert isinstance(params, dict), "Params file should contain a JSON object"
    assert len(params) > 0, "Params file should not be empty"


def test_params_json_syntax():
    """Test that params file has valid JSON syntax."""
    with open(PARAMS_FILE) as f:
        try:
            json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON syntax: {e}")


def test_params_nextflow_config_parsing():
    """Test that Nextflow can parse the params file.
    
    This requires Nextflow to be installed and available in PATH.
    The test will be skipped if Nextflow is not available.
    """
    # Check if nextflow is available
    try:
        result = subprocess.run(
            ["nextflow", "-version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            pytest.skip("Nextflow not available")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pytest.skip("Nextflow not available")
    
    # Test config parsing with the params file
    # We use a minimal config that just loads the params
    result = subprocess.run([
        "nextflow", "config",
        "-params-file", str(PARAMS_FILE),
        "-"
    ], 
    input="params { }",  # Minimal config
    capture_output=True, 
    text=True,
    timeout=30)
    
    assert result.returncode == 0, f"Nextflow config parsing failed: {result.stderr}"


def test_params_required_fields():
    """Test that required parameters are present."""
    with open(PARAMS_FILE) as f:
        params = json.load(f)
    
    # Define required parameters for Nallo
    required_params = [
        "fasta",
        "preset"
    ]
    
    missing_params = [p for p in required_params if p not in params]
    assert not missing_params, f"Missing required parameters: {missing_params}"


def test_params_file_paths_format():
    """Test that file path parameters have valid format."""
    with open(PARAMS_FILE) as f:
        params = json.load(f)
    
    # Parameters that should be file paths
    file_path_params = [
        "fasta", "target_regions", "par_regions", "tandem_repeats",
        "str_bed", "echtvar_snv_databases", "svdb_sv_databases",
        "stranger_repeat_catalog", "variant_consequences_snvs",
        "variant_consequences_svs", "vep_cache", "vep_plugin_files",
        "cnv_expected_xx_cn", "cnv_expected_xy_cn", "cnv_excluded_regions",
        "somalier_sites"
    ]
    
    for param in file_path_params:
        if param in params:
            value = params[param]
            assert isinstance(value, str), f"{param} should be a string path"
            assert len(value) > 0, f"{param} should not be empty"


def test_params_boolean_values():
    """Test that boolean parameters have valid values."""
    with open(PARAMS_FILE) as f:
        params = json.load(f)
    
    boolean_params = [
        "publish_unannotated_family_svs",
        "skip_rank_variants",
        "skip_genome_assembly"
    ]
    
    for param in boolean_params:
        if param in params:
            value = params[param]
            assert isinstance(value, bool), f"{param} should be a boolean, got {type(value)}"


def test_params_preset_value():
    """Test that preset parameter has a valid value."""
    with open(PARAMS_FILE) as f:
        params = json.load(f)
    
    if "preset" in params:
        valid_presets = ["revio", "pacbio", "ONT_R10"]
        assert params["preset"] in valid_presets, \
            f"preset should be one of {valid_presets}, got {params['preset']}"
