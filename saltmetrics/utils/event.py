# -*- coding: utf-8 -*-
"""
Utils for event
"""

# Import python libs
import re
import Queue
import threading
import logging

# Import salt libs
import salt.utils.event


log = logging.getLogger(__name__)


class EventConnoisseur(threading.Thread):
    """
    Event Connoisseur
    """
    def __init__(self, opts, ext_fingers=None):
        super(EventConnoisseur, self).__init__()
        self.opts = opts
        self.queue = Queue.Queue(0)
        self.event_fingers = dict()
        if isinstance(ext_fingers, list):
            for _each in ext_fingers:
                if isinstance(_each, dict):
                    self.event_fingers.update(_each)

    def setup_event_fingers(self, base='salt'):
        """
        Setup Event fingers
        """
        __jid = '\d{20}'
        __minion_id = '[\.\w-]+'
        __event_fingers = {
            'auth': r'^{0}/auth$'.format(base),
            'wheel_job': r'^{0}/wheel/{1}/new$'.format(base, __jid),
            'wheel_ret': r'^{0}/wheel/{1}/ret$'.format(base, __jid),
            'runner_job': r'^{0}/run/{1}/new$'.format(base, __jid),
            'runner_ret': r'^{0}/run/{1}/ret$'.format(base, __jid),
            'minion_job': r'^{0}/job/{1}/new$'.format(base, __jid),
            'minion_ret': r'^{0}/job/{1}/ret/{2}$'.format(base, __jid, __minion_id),
        }
        self.event_fingers.update(__event_fingers)
        for _key, _value in __event_fingers.iteritems():
            self.event_fingers[_key] = re.compile(_value)

    def get_finger(self, event=None):
        """
        Get finger from event
        """
        tag = 'other'
        func = ''
        if isinstance(event, dict):
            event_tag = event.get('tag', '')
            event_data = event.get('data', dict())
            for _tag, _rule in self.event_fingers.iteritems():
                if _rule.match(event_tag):
                    tag = _tag
                    if _tag.endswith('_job') and event_data:
                        func = event_data.get('fun', '')
                    break
        return tag, func

    def run(self):
        self.setup_event_fingers()
        event_bus = salt.utils.event.get_event(
            self.opts.get('__role', 'master'),
            transport=self.opts.get('transport', 'zeromq'),
            opts=self.opts,
            listen=True
        )
        for event in event_bus.iter_events(full=True):
            self.queue.put(self.get_finger(event))