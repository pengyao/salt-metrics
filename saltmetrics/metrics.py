# -*- coding: utf-8 -*-

# Import python libs
from __future__ import absolute_import
import logging
import json
import time
from Queue import Empty

# Import salt.libs
import salt.key
import salt.utils.minions

# Import saltmetrics libs
from .utils.event import EventConnoisseur


log = logging.getLogger(__name__)


class BaseMetrics(object):
    """
    Salt base metrics
    """
    def __init__(self, opts):
        self.opts = opts
        self.metric_opts = self.opts.get('metrics', dict())
        self.update_interval = self.metric_opts.get('update_interval', self.opts.get('loop_interval', 60))
        self.metric_saved_path = self.metric_opts.get('saved_path', '/tmp/salt_metrics.json')
        self.metrics = {
            'id': self.opts.get('id', ''),
            'role': self.role,
        }

    @property
    def role(self):
        return self.opts.get('__role', 'unknown')

    @property
    def is_running(self):
        return True

    def save_metrics(self):
        if self.metric_saved_path:
            self.metrics['saved_time'] = time.strftime('%Y%m%d%H%M%S', time.localtime())
            self.metrics['is_running'] = int(self.is_running)
            log.debug('Saving {0} metrics to {1}'.format(self.metrics['role'], self.metric_saved_path))
            with open(self.metric_saved_path, 'w') as fd:
                json.dump(self.metrics, fd)

    def start(self):
        last = time.time()
        while True:
            # Write to metric file
            if time.time() - last >= self.update_interval:
                self.save_metrics()
                last = time.time()
            time.sleep(1)


class MasterMetrics(BaseMetrics):
    """
    Salt master metrics
    """
    def __init__(self, opts):
        super(MasterMetrics, self).__init__(opts)
        if self.opts['transport'] in ('zeromq', 'tcp'):
            self.keys = salt.key.Key(self.opts)
        else:
            self.keys = salt.key.RaetKey(self.opts)
        self.ckminions = salt.utils.minions.CkMinions(self.opts)
        # Event and func metrics
        self.event_connoisseur = EventConnoisseur(
            self.opts,
            ext_fingers=self.metric_opts.get('ext_event_finger'))
        self.metrics['event'] = {}
        self.metrics['func'] = {}

    @property
    def is_running(self):
        return self.keys.check_master()

    @property
    def minions(self):
        _minions_keys = self.keys.list_keys()
        _connected_minions = self.ckminions._all_minions()
        return {
            'accepted': len(_minions_keys.get('minions', [])),
            'pending': len(_minions_keys.get('minions_pre', [])),
            'denied': len(_minions_keys.get('minions_denied', [])),
            'rejected': len(_minions_keys.get('minions_rejected', [])),
            'connected': len(_connected_minions)
        }

    def start(self):
        # Start event connoisseur

        self.event_connoisseur.start()
        last = time.time()
        while True:
            try:
                finger = self.event_connoisseur.queue.get_nowait()
            except Empty:
                finger = ()
            if finger and len(finger) >= 2:
                tag = finger[0]
                func = finger[1]
                if tag not in self.metrics['event']:
                    self.metrics['event'][tag] = 0
                self.metrics['event'][tag] += 1
                if func:
                    if func not in self.metrics['func']:
                        self.metrics['func'][func] = 0
                    self.metrics['func'][func] += 1
            # Write to metric file
            if time.time() - last >= self.update_interval:
                self.metrics.update(dict(minions=self.minions))
                self.save_metrics()
                last = time.time()


# TODO
class MinionMetrics(BaseMetrics):
    pass
