import dagster as dg
from dagster_dbt import dbt_assets, DbtCliResource, DbtProject
from pathlib import Path



RELATIVE_PATH_TO_MY_DBT_PROJECT = "../de-zoomcamp-2025/dbt_clickhouse_taxy_rides"

dbt_project_directory = DbtProject(
    project_dir=Path(__file__)
    .parent
    .joinpath(RELATIVE_PATH_TO_MY_DBT_PROJECT)
    .resolve(),
)

# Initialize dbt project
dbt_project = DbtProject(project_dir=dbt_project_directory)
dbt_resource = DbtCliResource(project_dir=dbt_project)

# Prepare dbt project
dbt_project.prepare_if_dev()

# Asset definition remains the same
@dbt_assets(manifest=dbt_project.manifest_path)
def dbt_assets_models(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()