=================================
Cloud Validation adapter for OSTF
=================================

** WARNING
** This repository is deprecated. All sources are available at
gerrit.mirantis.com

Overview
--------

Existing [OSTF](http://docs.mirantis.com/fuel-dev/develop/ostf_contributors_guide.html)
code provides a number of tests which cover a number of cases needed for cloud
validation. The downside of existing OSTF is that it is tightly coupled with
FUEL's nailgun. Given project aims to create standalone adapter for OSTF which
is independent of FUEL thus making it possible to run OSTF tests on any random
cloud (in theory).

High-level design
-----------------

CLI tool that works with health check plugins
Supported plugins::

  - fuel health check


Usage
-----

Please note that if you're using Fuel OSTF plugin, you have to install it manually.

.. code-block:: bash

  $ cloudvalidation cloud-health-check {argument} [argument_parameters]

Arguments::

    list_plugins - Lists plugins
    list_plugin_suites - Lists plugin test suites
    list_plugin_tests - Lists plugin tests from all available suites
    run_suites - Runs all tests from all suites
    run_suite - Runs certain test suite
    run_test - Runs certain test


Examples
--------

.. code-block:: bash

  $ cloudvalidation-cli cloud-health-check list_plugins

+----------+------------------------------------------------------------------+
| Property | Value                                                            |
+----------+------------------------------------------------------------------+
| name     | fuel_health                                                      |
| suites   | fuel_health.tests.sanity.test_sanity_identity.SanityIdentityTest |
|          | fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest   |
|          | fuel_health.tests.sanity.test_sanity_heat.SanityHeatTest         |
|          | fuel_health.tests.smoke.test_create_flavor.FlavorsAdminTest      |
+----------+------------------------------------------------------------------+

.. code-block:: bash

  $ cloudvalidation-cli cloud-health-check list_plugin_suites --validation-plugin fuel_health

+----------+------------------------------------------------------------------+
| Property | Value                                                            |
+----------+------------------------------------------------------------------+
| suites   | fuel_health.tests.sanity.test_sanity_identity.SanityIdentityTest |
|          | fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest   |
|          | fuel_health.tests.sanity.test_sanity_heat.SanityHeatTest         |
|          | fuel_health.tests.smoke.test_create_flavor.FlavorsAdminTest      |
+----------+------------------------------------------------------------------+

.. code-block:: bash

  $ cloudvalidation-cli cloud-health-check list_plugin_tests --validation-plugin fuel_health

+----------+--------------------------------------------------------------------------------------+
| Property | Value                                                                                |
+----------+--------------------------------------------------------------------------------------+
| tests    | fuel_health.tests.sanity.test_sanity_identity.SanityIdentityTest:test_list_services  |
|          | fuel_health.tests.sanity.test_sanity_identity.SanityIdentityTest:test_list_users     |
|          | fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest:test_list_flavors     |
|          | fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest:test_list_images      |
|          | fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest:test_list_instances   |
|          | fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest:test_list_rate_limits |
|          | fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest:test_list_snapshots   |
|          | fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest:test_list_volumes     |
|          | fuel_health.tests.sanity.test_sanity_heat.SanityHeatTest:test_list_stacks            |
|          | fuel_health.tests.smoke.test_create_flavor.FlavorsAdminTest:test_create_flavor       |
+----------+--------------------------------------------------------------------------------------+

.. code-block:: bash

 $ cloudvalidation-cli --config-dir=/etc/cloudv_ostf_adapter cloud-health-check run_suites --validation-plugin-name fuel_health


Request user list ... ok
Request flavor list ... ok
Request image list ... ok
Request instance list ... ok
Request absolute limits list ... ok
Request snapshot list ... ok
Request volume list ... ok
Request stack list ... ok
Create instance flavor ... ok

----------------------------------------------------------------------
Ran 9 tests in 5.310s

OK

.. code-block::

 $ cloudvalidation-cli --config-dir=/etc/cloudv_ostf_adapter cloud-health-check run_suite --validation-plugin-name fuel_health --suite fuel_health.tests.sanity.test_sanity_identity.SanityIdentityTest

Running test suite: fuel_health.tests.sanity.test_sanity_identity.SanityIdentityTest ...
Request user list ... ok

----------------------------------------------------------------------
Ran 1 test in 0.938s

OK

Links
-----

 * OSTF contributor's guide - http://docs.mirantis.com/fuel-dev/develop/ostf_contributors_guide.html)
 * OSTF source code - https://github.com/stackforge/fuel-ostf

========
REST API
========


Run server
----------

.. code-block:: bash

 $ cloudvalidation-server --config-file=path_to_config
 * Running on http://127.0.0.1:8777/ (Press CTRL+C to quit)

Example of config
-----------------

 [rest]
 server_host=127.0.0.1
 server_port=8777
 log_file=/var/log/ostf.log
 jobs_dir=/var/log/ostf
 debug=False

List of supported operations
----------------------------
 - get list of supported plugins
   GET /v1/plugins?load_tests=True/False
   In load_tests=True case tests for plugin will be shown.

 - get suites in plugin
   GET /v1/plugins/<plugin_name>/suites

 - get tests for all suites in plugin
   GET /v1/plugins/<plugin_name>/suites/tests

 - get tests per suite in plugin
   GET /v1/plugins/<plugin_name>/suites/<suite>/tests

 - run suites for plugin
   POST /v1/plugins/<plugin_name>/suites

 - run suite for plugin
   POST /v1/plugins/<plugin_name>/suites/<suite>

 - run test for plugin
   POST /v1/plugins/<plugin_name>/suites/tests/<test>

 - create job with user's tests set
   POST /v1/jobs/create
   Example of JSON:


.. code-block:: bash

    {
      "job": {
        "name": "fake",
        "description": "description",
        "tests": [
              "fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest:test_list_flavors"] 
       }
    }

- list of all jobs
  GET /v1/jobs

- execute job
  GET /v1/jobs/execute/<job_id>

- get status with report for executed job
  GET /v1/jobs/<job_id>

- delete job
  DELETE /v1/jobs/<job_id>


=====================
REST API Client usage
=====================

.. code-block:: python

    from cloudv_ostf_adapter.cloudv_client import client

    cloudvclient = client.Client(CONF.host, CONF.port, CONF.api_version)

    plugins = cloudvclient.plugins.list()
    plugin_one = plugins[0]['name']

    suites = cloudvalidation.suites.list_suites(plugin_one)

=========================
REST API Client CLI usage
=========================

To connect cloudvalidation client to ReST service you need to do next::

    # create configuration file, that contains
          [DEFAULT]
          host = localhost
          port = 8777
          api_version = v1

    or

    # export next operating system variables:
        export MCLOUDV_HOST=localhost
        export MCLOUDV_PORT=8777
        export MCLOUDV_API=v1


Usage examples::
.. code-block:: bash

    cloudvalidation cloud-health-check list_plugins

+----------+----------------------------------------------------------------------------------------------+
| Property | Value                                                                                        |
+----------+----------------------------------------------------------------------------------------------+
| name     | fuel_health                                                                                  |
| suites   | fuel_health.tests.sanity.test_sanity_identity.SanityIdentityTest                             |
|          | fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest                               |
|          | fuel_health.tests.sanity.test_sanity_heat.SanityHeatTest                                     |
|          | fuel_health.tests.sanity.test_sanity_networking.NetworksTest:test_list_networks_nova_network |
|          | fuel_health.tests.sanity.test_sanity_ceilometer.CeilometerApiTests                           |
|          | fuel_health.tests.smoke.test_create_flavor.FlavorsAdminTest                                  |
|          | fuel_health.tests.smoke.test_create_volume.VolumesTest                                       |
|          | fuel_health.tests.smoke.test_neutron_actions.TestNeutron                                     |
|          | fuel_health.tests.smoke.test_nova_create_instance_with_connectivity.TestNovaNetwork          |
|          | fuel_health.tests.smoke.test_nova_image_actions.TestImageAction                              |
|          | fuel_health.tests.smoke.test_user_create.TestUserTenantRole                                  |
+----------+----------------------------------------------------------------------------------------------+


    cloudvalidation cloud-health-check list_plugin_suites --validation-plugin-name fuel_health

+----------+----------------------------------------------------------------------------------------------+
| Property | Value                                                                                        |
+----------+----------------------------------------------------------------------------------------------+
| suites   | fuel_health.tests.sanity.test_sanity_identity.SanityIdentityTest                             |
|          | fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest                               |
|          | fuel_health.tests.sanity.test_sanity_heat.SanityHeatTest                                     |
|          | fuel_health.tests.sanity.test_sanity_networking.NetworksTest:test_list_networks_nova_network |
|          | fuel_health.tests.sanity.test_sanity_ceilometer.CeilometerApiTests                           |
|          | fuel_health.tests.smoke.test_create_flavor.FlavorsAdminTest                                  |
|          | fuel_health.tests.smoke.test_create_volume.VolumesTest                                       |
|          | fuel_health.tests.smoke.test_neutron_actions.TestNeutron                                     |
|          | fuel_health.tests.smoke.test_nova_create_instance_with_connectivity.TestNovaNetwork          |
|          | fuel_health.tests.smoke.test_nova_image_actions.TestImageAction                              |
|          | fuel_health.tests.smoke.test_user_create.TestUserTenantRole                                  |
+----------+----------------------------------------------------------------------------------------------+


    cloudvalidation cloud-health-check list_plugin_tests --validation-plugin-name fuel_health

+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| Property | Value                                                                                                                                                |
+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| tests    | fuel_health.tests.sanity.test_sanity_identity.SanityIdentityTest:test_list_services                                                                  |
|          | fuel_health.tests.sanity.test_sanity_identity.SanityIdentityTest:test_list_users                                                                     |
|          | fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest:test_list_flavors                                                                     |
|          | fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest:test_list_images                                                                      |
|          | fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest:test_list_instances                                                                   |
|          | fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest:test_list_rate_limits                                                                 |
|          | fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest:test_list_snapshots                                                                   |
|          | fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest:test_list_volumes                                                                     |
|          | fuel_health.tests.sanity.test_sanity_heat.SanityHeatTest:test_list_stacks                                                                            |
|          | fuel_health.tests.sanity.test_sanity_ceilometer.CeilometerApiTests:test_list_meters                                                                  |
|          | fuel_health.tests.smoke.test_create_flavor.FlavorsAdminTest:test_create_flavor                                                                       |
|          | fuel_health.tests.smoke.test_create_volume.VolumesTest:test_create_boot_volume                                                                       |
|          | fuel_health.tests.smoke.test_create_volume.VolumesTest:test_volume_create                                                                            |
|          | fuel_health.tests.smoke.test_neutron_actions.TestNeutron:test_check_neutron_objects_creation                                                         |
|          | fuel_health.tests.smoke.test_nova_create_instance_with_connectivity.TestNovaNetwork:test_001_create_keypairs                                         |
|          | fuel_health.tests.smoke.test_nova_create_instance_with_connectivity.TestNovaNetwork:test_002_create_security_groups                                  |
|          | fuel_health.tests.smoke.test_nova_create_instance_with_connectivity.TestNovaNetwork:test_003_check_networks                                          |
|          | fuel_health.tests.smoke.test_nova_create_instance_with_connectivity.TestNovaNetwork:test_004_create_servers                                          |
|          | fuel_health.tests.smoke.test_nova_create_instance_with_connectivity.TestNovaNetwork:test_006_check_internet_connectivity_instance_without_floatingIP |
|          | fuel_health.tests.smoke.test_nova_create_instance_with_connectivity.TestNovaNetwork:test_008_check_public_instance_connectivity_from_instance        |
|          | fuel_health.tests.smoke.test_nova_image_actions.TestImageAction:test_snapshot                                                                        |
|          | fuel_health.tests.smoke.test_user_create.TestUserTenantRole:test_create_user                                                                         |
+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+


    cloudvalidation cloud-health-check run_suites --validation-plugin-name fuel_health

Note this command will generate big report, so it might be useful to save it into a file.


    cloudvalidation cloud-health-check run_suite --validation-plugin-name fuel_health --suite fuel_health.tests.sanity.test_sanity_identity.SanityIdentityTest

Note this command will generate big report, so it might be useful to save it into a file.


    cloudvalidation cloud-health-check run_test --validation-plugin-name fuel_health --test fuel_health.tests.sanity.test_sanity_identity.SanityIdentityTest:test_list_services

+-------------------------------------------------------------------------------------+----------+--------+------------------------------------------------------------------------+
| Test                                                                                | Duration | Result | Report                                                                 |
+-------------------------------------------------------------------------------------+----------+--------+------------------------------------------------------------------------+
| fuel_health.tests.sanity.test_sanity_identity.SanityIdentityTest:test_list_services | 1.184s   | Passed | Request active services list ... ok                                    |
|                                                                                     |          |        |                                                                        |
|                                                                                     |          |        | ---------------------------------------------------------------------- |
|                                                                                     |          |        | Ran 1 test in 1.184s                                                   |
|                                                                                     |          |        |                                                                        |
|                                                                                     |          |        | OK                                                                     |
|                                                                                     |          |        |                                                                        |
+-------------------------------------------------------------------------------------+----------+--------+------------------------------------------------------------------------+

