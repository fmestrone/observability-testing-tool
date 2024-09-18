from obs.cloud_logging import submit_log_entry_text, submit_log_entry_json
from obs.cloud_monitoring import submit_gauge_metric


def main():

    submit_log_entry_text("WARNING", "Hello World from new Text Logger App")
    submit_log_entry_json("INFO", {"text": "Hello World from new Json Logger App", "score": 0.73})
    submit_log_entry_json("INFO", {"hello": "world", "from": "Turin"})
    submit_log_entry_text("DEBUG", "Hello!",
                          resource_type="gce_instance",
                          resource_labels={
                              "instance_id": "123456789123456789",
                              "zone": "us-central1-f",
                          },
                          labels={
                              "foo": "bar",
                          },
                          other={
                              "trace": "T01234-YXZ",
                              "http_request": {
                                  "requestUrl": "localhost"
                              }
                          }
                          )

    submit_gauge_metric(12.3, "feds_metric",
                        resource_type="gce_instance",
                        resource_labels={
                            "instance_id": "1234567890123456789",
                            "zone": "us-central1-f"
                        },
                        metric_labels={
                            "store_id": "pittsburgh",
                        }
                        )


if __name__ == '__main__':
    main()
