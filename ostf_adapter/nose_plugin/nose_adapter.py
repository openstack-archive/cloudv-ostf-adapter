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

import fcntl
import logging
import os
import signal

from oslo.config import cfg

from ostf_adapter.logger import ResultsLogger
from ostf_adapter.nose_plugin import nose_storage_plugin
from ostf_adapter.nose_plugin import nose_test_runner
from ostf_adapter.nose_plugin import nose_utils
from ostf_adapter.storage import engine
from ostf_adapter.storage import models


LOG = logging.getLogger(__name__)


class InterruptTestRunException(KeyboardInterrupt):
    """Current class exception is used for cleanup action
    as KeyboardInterrupt is the only exception that is reraised by
    unittest (and nose correspondingly) into outside environment
    """


class NoseDriver(object):
    def __init__(self):
        LOG.warning('Initializing Nose Driver')

    def run(self, test_run, test_set, dbpath,
            ostf_os_access_creds=None,
            tests=None, token=None):

        if not ostf_os_access_creds:
            ostf_os_access_creds = dict()
        tests = tests or test_run.enabled_tests
        if tests:
            argv_add = [nose_utils.modify_test_name_for_nose(test)
                        for test in tests]
        else:
            argv_add = [test_set.test_path] + test_set.additional_arguments

        results_log = ResultsLogger(test_set.id)

        lock_path = cfg.CONF.adapter.lock_dir
        test_run.pid = nose_utils.run_proc(self._run_tests,
                                           lock_path,
                                           dbpath,
                                           test_run.id,
                                           ostf_os_access_creds,
                                           argv_add,
                                           token,
                                           results_log).pid

    def _run_tests(self, lock_path, dbpath, test_run_id, ostf_os_access_creds,
                   argv_add, token, results_log):
        cleanup_flag = False

        def raise_exception_handler(signum, stack_frame):
            raise InterruptTestRunException()
        signal.signal(signal.SIGUSR1, raise_exception_handler)

        with engine.contexted_session(dbpath) as session:
            try:
                if not os.path.exists(lock_path):
                    LOG.error('There is no directory to store locks')
                    raise Exception('There is no directory to store locks')

                aquired_locks = []

                nose_test_runner.SilentTestProgram(
                    addplugins=[nose_storage_plugin.StoragePlugin(
                        session, test_run_id, ostf_os_access_creds, token,
                        results_log
                    )],
                    exit=False,
                    argv=['ostf_tests'] + argv_add)

            except InterruptTestRunException:
                # (dshulyak) after process is interrupted we need to
                # disable existing handler
                signal.signal(signal.SIGUSR1, lambda *args: signal.SIG_DFL)

            except Exception:
                LOG.exception('Test run ID: %s', test_run_id)
            finally:
                updated_data = {'status': 'finished',
                                'pid': None}

                models.TestRun.update_test_run(
                    session, test_run_id, updated_data)

                for fd in aquired_locks:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                    fd.close()

                if cleanup_flag:
                    # TODO: add cleanup
                    pass

    def kill(self, test_run):
        try:
            if test_run.pid:
                os.kill(test_run.pid, signal.SIGUSR1)
                return True
        except OSError:
            return False
        return False
