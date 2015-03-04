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


import argparse
import six


def args(*args, **kwargs):
    """
    Decorates commandline arguments for actions
    :param args: sub-category commandline arguments
    :param kwargs: sub-category commandline arguments
    :return: decorator: object attribute setter
    :rtype: callable
    """
    def _decorator(func):
        func.__dict__.setdefault('args', []).insert(0, (args, kwargs))
        return func
    return _decorator


def methods_of(obj):
    """
    Get all callable methods of an object that don't
    start with underscore (private attributes)
    returns
    :param obj: objects to get callable attributes from
    :type obj: object
    :return result: a list of tuples of the form (method_name, method)
    :rtype: list
    """
    result = []
    for i in dir(obj):
        if callable(getattr(obj, i)) and not i.startswith('_'):
            result.append((i, getattr(obj, i)))
    return result


def add_command_parsers(categories):
    """
    Parses actions commandline arguments from each category
    :param categories: commandline categories
    :type categories: dict
    :return: _subparser: commandline subparser
    """
    def _subparser(subparsers):
        """
        Iterates over categories and registers action
        commandline arguments for each category
        :param subparsers: commandline subparser
        :return: None
        :rtype: None
        """
        for category in categories:
            command_object = categories[category]()

            desc = getattr(command_object, 'description', None)
            parser = subparsers.add_parser(category, description=desc)
            parser.set_defaults(command_object=command_object)

            category_subparsers = parser.add_subparsers(dest='action')

            for (action, action_fn) in methods_of(command_object):
                parser = category_subparsers.add_parser(
                    action, description=desc)

                action_kwargs = []
                for args, kwargs in getattr(action_fn, 'args', []):
                    kwargs.setdefault('dest', args[0][2:])
                    if kwargs['dest'].startswith('action_kwarg_'):
                        action_kwargs.append(
                            kwargs['dest'][len('action_kwarg_'):])
                    else:
                        action_kwargs.append(kwargs['dest'])
                        kwargs['dest'] = 'action_kwarg_' + kwargs['dest']

                    parser.add_argument(*args, **kwargs)

                parser.set_defaults(action_fn=action_fn)
                parser.set_defaults(action_kwargs=action_kwargs)

                parser.add_argument('action_args', nargs='*',
                                    help=argparse.SUPPRESS)

    return _subparser


def _main(global_conf, local_conf, category_opt, cli_args):
    """

    :param global_conf: staged CONF
    :param local_conf: tool conf
    :param category_opt: subparser category options
    :param cli_args: tool CLI arguments
    :return:
    """
    global_conf.register_cli_opt(category_opt)
    local_conf.parse_args(cli_args)
    fn = global_conf.category.action_fn
    fn_args = [arg.decode('utf-8') for arg in global_conf.category.action_args]
    fn_kwargs = {}
    for k in global_conf.category.action_kwargs:
        v = getattr(global_conf.category, 'action_kwarg_' + k)
        if v is None:
            continue
        if isinstance(v, six.string_types):
            v = v.decode('utf-8')
        fn_kwargs[k] = v

    try:
        ret = fn(*fn_args, **fn_kwargs)
        return ret
    except Exception as e:
        print(str(e))
