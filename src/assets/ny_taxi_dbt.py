import dagster as dg
from dagster_dbt import dbt_assets, DbtCliResource, DbtProject
from pathlib import Path
import subprocess
import tempfile

# Clone repository to temporary directory
with tempfile.TemporaryDirectory() as tmp_dir:
    repo_url = "https://github.com/AIZharau/de-zoomcamp-2025.git"
    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, tmp_dir],
        check=True
    )
    
    # Path to dbt project inside cloned repository
    dbt_project_directory = Path(tmp_dir) / "dbt_clickhouse_taxi_rides"
    
    # Install dbt dependencies
    subprocess.run(["dbt", "deps"], cwd=dbt_project_directory, check=True)

    # Make manifest
    subprocess.run(["dbt", "compile"], cwd=dbt_project_directory, check=True)

    # Initialize dbt project
    dbt_project = DbtProject(project_dir=dbt_project_directory)
    dbt_resource = DbtCliResource(project_dir=dbt_project)
    
    # Prepare dbt project
    dbt_project.prepare_if_dev()

# Asset definition remains the same
@dbt_assets(manifest=dbt_project.manifest_path)
def dbt_assets_models(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()