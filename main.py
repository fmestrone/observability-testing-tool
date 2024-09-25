from config.common import debug_log

from config.executor import run_logging_jobs, create_metrics_descriptors, run_monitoring_jobs, prepare


def main():
    prepare()
    p1 = run_logging_jobs()
    debug_log("Done with logging tasks. Now proceeding with monitoring tasks...")
    create_metrics_descriptors()
    p2 = run_monitoring_jobs()
    debug_log("Done with monitoring tasks. Now waiting for live jobs to terminate...")
    if p1 is not None: p1.join()
    if p2 is not None: p2.join()


if __name__ == '__main__':
    main()
