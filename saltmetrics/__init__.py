# -*- coding: utf-8 -*-
"""
Salt-metrics package
"""

# Import Python libs
import logging
import multiprocessing

# Import salt libs
import salt.utils

# Import salt metrics libs
from .metrics import MasterMetrics, MinionMetrics

log = logging.getLogger(__name__)

class MetricsCollector(multiprocessing.Process):
    """
    Metrics Collector
    """
    def __init__(self, opts=None):
        super(MetricsCollector, self).__init__()
        if opts.get('__role') == 'master':
            self._collector = MasterMetrics(opts)
        else:
            self._collector = MinionMetrics(opts)

    def run(self):
        """
        Fire up collector
        """
        salt.utils.appendproctitle('MetricsCollector')
        self._collector.start()


collector = MetricsCollector