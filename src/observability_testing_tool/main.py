import argparse
import sys
from observability_testing_tool.config.common import info_log, set_log_level, error_log
from observability_testing_tool.config.executor import prepare, run_logging_jobs, create_metrics_descriptors, run_monitoring_jobs


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
        action="version",
        version="observability-testing-tool 1.0.0"
    )

    args = parser.parse_args()

    # Set log level based on verbosity
    # 0: Errors only
    # 1: Info (-v)
    # 2: Debug (-vv or more)
    verbosity = min(args.verbose, 2)
    if verbosity >= 0:
        set_log_level(verbosity)

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
            
    except KeyboardInterrupt:
        info_log(">>> Obs Test Tool - Interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        error_log(">>> Obs Test Tool - An unexpected error occurred", exception=e)
        sys.exit(1)


if __name__ == '__main__':
    main()
