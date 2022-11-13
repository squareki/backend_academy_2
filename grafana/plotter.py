from prometheus_api_client import PrometheusConnect, MetricsList, Metric

import matplotlib.pyplot as plt
import datetime as dt

prom = PrometheusConnect()
label_config = {"instance": "localhost:9090", "job": "prometheus"}


def plot() -> None:
    metric_data = prom.get_metric_range_data(
        metric_name="prometheus_tsdb_head_series",
        label_config=label_config,
        start_time=dt.datetime.now() - dt.timedelta(hours=2),
        end_time=dt.datetime.now()
    )

    metrics_object_list = MetricsList(metric_data)
    # print(metrics_object_list)
    tsdb_metric: Metric = metrics_object_list[0]
    # print(tsdb_metric)
    tsdb_metric.plot()

    plt.show()

if __name__ == "__main__":
    plot()