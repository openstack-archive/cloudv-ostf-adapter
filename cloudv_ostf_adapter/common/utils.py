#    Copyright 2015 Mirantis, Inc
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import sys
import prettytable
import six

from cloudv_ostf_adapter.common import cfg
from oslo.utils import encodeutils

CONF = cfg.CONF


def _print(pt, order):
    if sys.version_info >= (3, 0):
        print(pt.get_string(sortby=order))
    else:
        print(encodeutils.safe_encode(pt.get_string(sortby=order)))


def print_dict(d, property="Property"):
    pt = prettytable.PrettyTable([property, 'Value'], caching=False)
    pt.align = 'l'
    [pt.add_row(list(r)) for r in six.iteritems(d)]
    _print(pt, property)


def print_list(objs, fields, formatters={}, order_by=None, obj_is_dict=False,
               labels={}):
    if not labels:
        labels = {}
    for field in fields:
        if field not in labels:
            # No underscores (use spaces instead) and uppercase any ID's
            label = field.replace("_", " ").replace("id", "ID")
            # Uppercase anything else that's less than 3 chars
            if len(label) < 3:
                label = label.upper()
            # Capitalize each word otherwise
            else:
                label = ' '.join(word[0].upper() + word[1:]
                                 for word in label.split())
            labels[field] = label

    pt = prettytable.PrettyTable(
        [labels[field] for field in fields], caching=False)
    # set the default alignment to left-aligned
    align = dict((labels[field], 'l') for field in fields)
    set_align = True
    for obj in objs:
        row = []
        for field in fields:
            if formatters and field in formatters:
                row.append(formatters[field](obj))
            elif obj_is_dict:
                data = obj.get(field, '')
            else:
                data = getattr(obj, field, '')
            row.append(data)
            # set the alignment to right-aligned if it's a numeric
            if set_align and hasattr(data, '__int__'):
                align[labels[field]] = 'r'
        set_align = False
        pt.add_row(row)
    pt._align = align

    if not order_by:
        order_by = fields[0]
    order_by = labels[order_by]
    _print(pt, order_by)


def poll_until(pollster, expected_result=None, sleep_time=5):
    import time
    if not callable(pollster):
        raise Exception("%s is not callable" % pollster.__name__)
    while pollster() != expected_result:
        time.sleep(sleep_time)
