# Nallo_CGU_configs
Configuration and parameters for running Nallo GMS pipeline at CGU on Miarka

## Validation and Compatibility
* [COMPATIBILITY.md](COMPATIBILITY.md): Specifies the version of the Nallo pipeline that the configs and parameters in this repository are designed for.
* A GitHub Actions workflow automatically validates the parameter files in `params/` against the official Nextflow schema of the version specified in `COMPATIBILITY.md`.
* **IMPORTANT:** You must update the version tag in `COMPATIBILITY.md` whenever configs and parameters are upgraded to be used with a new version of the Nallo pipeline.

## Config files

Config files are found under config:

* [nallo_CGU.config](config/nallo_CGU.config): config file with setttings specific to CGU revio WGS 


## Parameter files

* [nallo-cgu-params.revio_wgs.json](params/nallo-cgu-params.revio_wgs.json): parameters for running Nallo REVIO WGS at CGU

## Variant database files
[echtvar_dbs.csv](variant_dbs/echtvar_dbs.csv): file listing the echtvar databases used to annotate snv and indels with population allele frequencies

[svdb_dbs.csv](variant_dbs/svdb_dbs.csv): file listing the svdb databases to be queried with svdb query to annotate SVs with population allele frequencies

## scripts
[create_nallo_samplesheet.py](scripts/create_nallo_samplesheet.py): python script to create the Nallo samplesheet.csv file. See [README.md](scripts/README.md) for more information.


