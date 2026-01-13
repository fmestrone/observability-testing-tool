import argparse
import sys
from importlib.metadata import version, PackageNotFoundError
from observability_testing_tool.config.common import info_log, set_log_level, error_log, set_dry_run, set_not_gce, set_skip_schema
from observability_testing_tool.config.executor import prepare, run_logging_jobs, create_metrics_descriptors, run_monitoring_jobs


class VersionAction(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        try:
            pkg_version = version("observability-testing-tool")
        except PackageNotFoundError:
            pkg_version = "unknown"
        print(f"observability-testing-tool {pkg_version}")
        parser.exit()


def main():
    parser = argparse.ArgumentParser(
        description="🛠️ Obs Test Tool - Bulk generate logs and metrics in Google Cloud."
    )
    parser.add_argument(
        "config",
        nargs="?",
        default="config.obs.yaml",
        help="Path to the configuration YAML file. If not provided, it looks for config.obs.yaml in the current directory."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase output verbosity (e.g., -v for info, -vv for debug)."
    )
    parser.add_argument(
        "--version",
        action=VersionAction,
        help="Show the tool's version and exit."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making any changes."
    )
    parser.add_argument(
        "--no-gce",
        action="store_true",
        help="Run without requesting GCE metadata."
    )
    parser.add_argument(
        "--skip-schema-validation",
        action="store_true",
        help="Do not run schema validation against the configuration file. Do not use unless you know fully well why you're doing it."
    )

    args = parser.parse_args()

    # Set log level based on verbosity
    # 0: Errors only
    # 1: Info (-v)
    # 2: Debug (-vv or more)
    verbosity = min(args.verbose, 2)
    # If param not set, let the environment variable determine behaviour
    if verbosity > 0:
        set_log_level(verbosity)

    # If param not set, let the environment variable determine behaviour
    if args.dry_run:
        set_dry_run(True)

    # If param not set, let the environment variable determine behaviour
    if args.no_gce:
        set_not_gce(True)

    # If param not set, let the environment variable determine behaviour
    if args.skip_schema_validation:
        set_skip_schema(True)

    try:
        info_log(">>> Obs Test Tool - Getting things going...")
        prepare(args.config)
        
        info_log(">>> Obs Test Tool - Done with preparation. Now proceeding with logging tasks...")
        p1 = run_logging_jobs()
        
        info_log(">>> Obs Test Tool - Done with logging tasks. Now proceeding with monitoring tasks...")
        create_metrics_descriptors()
        p2 = run_monitoring_jobs()
        
        info_log(">>> Obs Test Tool - Done with monitoring tasks. Now waiting for live jobs to terminate...")
        if p1 is not None:
            p1.join()
        if p2 is not None:
            p2.join()

        info_log(">>> Obs Test Tool - All done!")

    except KeyboardInterrupt:
        info_log(">>> Obs Test Tool - Interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        error_log(">>> Obs Test Tool - An unexpected error occurred", ex=e)
        sys.exit(1)


if __name__ == '__main__':

    # Check Python version before doing anything else
    if sys.version_info < (3, 12):
        error_log("Error: This tool requires Python 3.12 or higher.")
        error_log(f"Current version: {sys.version.split()[0]}")
        sys.exit(1)

    main()
