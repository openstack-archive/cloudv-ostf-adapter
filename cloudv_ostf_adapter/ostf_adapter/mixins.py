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

import logging

from oslo.config import cfg
from sqlalchemy.orm import joinedload

from cloudv_ostf_adapter.ostf_adapter.storage import models

cfg.CONF.register_opts([cfg.ListOpt('deployment_tags',
                                    default=['ha'],
                                    help="Types of tests to be run")])
LOG = logging.getLogger(__name__)


TEST_REPOSITORY = []


def clean_db(session):
    LOG.info('Starting clean db action.')
    session.query(models.TestSet).delete()

    session.commit()


def cache_test_repository(session):
    test_repository = session.query(models.TestSet)\
        .options(joinedload('tests'))\
        .all()

    crucial_tests_attrs = ['name', 'deployment_tags']
    for test_set in test_repository:
        data_elem = dict()

        data_elem['test_set_id'] = test_set.id
        data_elem['deployment_tags'] = test_set.deployment_tags
        data_elem['tests'] = []

        for test in test_set.tests:
            test_dict = dict([(attr_name, getattr(test, attr_name))
                              for attr_name in crucial_tests_attrs])
            data_elem['tests'].append(test_dict)

        TEST_REPOSITORY.append(data_elem)


def discovery_check(session, token=None):
    cluster_deployment_args = _get_cluster_depl_tags(token=token)

    cluster_data = {
        'deployment_tags': cluster_deployment_args
    }

    _add_cluster_testing_pattern(session, cluster_data)


def _get_cluster_depl_tags(token=None):
    """
    Read deployment tags from config instead of Nailgun
    """
    return cfg.CONF.deployment_tags


def _add_cluster_testing_pattern(session, cluster_data):
    pass
    # to_database = []
    #
    # global TEST_REPOSITORY
    #
    # # populate cache if it's empty
    # if not TEST_REPOSITORY:
    #     cache_test_repository(session)
    #
    # for test_set in TEST_REPOSITORY:
    #     if nose_utils.process_deployment_tags(
    #         cluster_data['deployment_tags'],
    #         test_set['deployment_tags']
    #     ):
    #
    #         testing_pattern = dict()
    #         testing_pattern['test_set_id'] = test_set['test_set_id']
    #         testing_pattern['tests'] = []
    #
    #         for test in test_set['tests']:
    #             if nose_utils.process_deployment_tags(
    #                 cluster_data['deployment_tags'],
    #                 test['deployment_tags']
    #             ):
    #
    #                 testing_pattern['tests'].append(test['name'])
    #         pattern = models.ClusterTestingPattern
    #         query = session.query(pattern).filter(
    #             pattern.test_set_id == testing_pattern['test_set_id'])
    #         already_exists = query.count() > 0
    #         if not already_exists:
    #             to_database.append(
    #                 pattern(**testing_pattern)
    #             )
    #
    # session.add_all(to_database)
