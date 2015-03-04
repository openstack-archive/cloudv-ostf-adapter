=================================
Cloud Validation adapter for OSTF
=================================

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

  $ cloudvalidation cloud-health-check list_plugins

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

  $ cloudvalidation cloud-health-check list_plugin_suites --validation-plugin fuel_health

+----------+------------------------------------------------------------------+
| Property | Value                                                            |
+----------+------------------------------------------------------------------+
| suites   | fuel_health.tests.sanity.test_sanity_identity.SanityIdentityTest |
|          | fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest   |
|          | fuel_health.tests.sanity.test_sanity_heat.SanityHeatTest         |
|          | fuel_health.tests.smoke.test_create_flavor.FlavorsAdminTest      |
+----------+------------------------------------------------------------------+

.. code-block:: bash

  $ cloudvalidation cloud-health-check list_plugin_tests --validation-plugin fuel_health

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

 $ cloudvalidation --config-dir=/etc/cloudv_ostf_adapter cloud-health-check run_suites --validation-plugin-name fuel_health


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

 $ cloudvalidation --config-dir=/etc/cloudv_ostf_adapter cloud-health-check run_suite --validation-plugin-name fuel_health --suite fuel_health.tests.sanity.test_sanity_identity.SanityIdentityTest

Running test suite: fuel_health.tests.sanity.test_sanity_identity.SanityIdentityTest ...
Request user list ... ok

----------------------------------------------------------------------
Ran 1 test in 0.938s

OK

Links
-----

 * OSTF contributor's guide - http://docs.mirantis.com/fuel-dev/develop/ostf_contributors_guide.html)
 * OSTF source code - https://github.com/stackforge/fuel-ostf
