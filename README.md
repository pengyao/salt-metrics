# salt-metrics

Salt Metrics for master

# How to use it?

## Install salt-metrics

```bash
pip install salt-metrics
```

## Config salt-metrics

* /etc/salt/master

```
......
ext_processes:
  - saltmetrics.collector
```

* /etc/salt/master.d/metrics.conf

```yaml
metrics:
  update_interval: 30
  saved_path: /tmp/salt_metrics.json
```

* Restart salt master
