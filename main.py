import config.executor # keep this import! it loads the configuration

from config.executor import run_logging_jobs, create_metrics_descriptors, run_monitoring_jobs


def main():
    # https://docs.python.org/3/library/multiprocessing.html
    run_logging_jobs()
    create_metrics_descriptors()
    run_monitoring_jobs()


if __name__ == '__main__':
    main()
