import dagster as dg
from dagster_dbt import dbt_assets, DbtCliResource, DbtProject
from pathlib import Path
import subprocess
import tempfile
import logging

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clone_repo(repo_url: str, tmp_dir: str) -> Path:
    """Clones the repository to a temporary directory."""
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, tmp_dir],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info("The repository has been successfully cloned.")
        return Path(tmp_dir)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error cloning repository: {e.stderr}")
        raise

def run_dbt_command(command: list[str], cwd: Path) -> None:
    """Executes dbt command."""
    try:
        subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
        logger.info(f"Command {' '.join(command)} completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при выполнении команды {' '.join(command)}: {e.stderr}")
        raise

def main():
    """The main function for initializing a dbt project and creating assets."""
    repo_url = "https://github.com/AIZharau/de-zoomcamp-2025.git"
    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            # Clone repository to temporary directory
            dbt_project_directory = clone_repo(repo_url, tmp_dir) / "dbt_clickhouse_taxi_rides"

            # Installing dependencies dbt
            run_dbt_command(["dbt", "deps"], dbt_project_directory)

            # Compiling dbt-project
            run_dbt_command(["dbt", "compile"], dbt_project_directory)

            
            # Initialize dbt project
            dbt_project = DbtProject(project_dir=dbt_project_directory)
            dbt_resource = DbtCliResource(project_dir=dbt_project)

            # Prepare dbt project
            dbt_project.prepare_if_dev()

            # Asset definition remains the same
            @dbt_assets(manifest=dbt_project.manifest_path)
            def dbt_assets_models(context: dg.AssetExecutionContext, dbt: DbtCliResource):
                yield from dbt.cli(["build"], context=context).stream()

        except Exception as e:
            logger.error(f"Error initializing dbt-project: {e}")
            raise

if __name__ == "__main__":
    main()