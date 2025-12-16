## Usage

usage: create_nallo_samplesheet.py [-h] --units UNITS --samples-info SAMPLES_INFO --project-id PROJECT_ID [--output OUTPUT]

Create Nallo samplesheet from units and sample info files

options:
  -h, --help            show this help message and exit
  --units UNITS         Path to units TSV file
  --samples-info SAMPLES_INFO
                        Path to samples info CSV file
  --project-id PROJECT_ID
                        Project ID string
  --output OUTPUT       Output CSV file path (default: nallo_samplesheet.csv)

## Where it is used

This script is executed in the Nallo start script, see https://github.com/clinical-genomics-uppsala/pipeline_start_scripts/blob/develop/miarka/start_wp3_hifi_wgs.sh
