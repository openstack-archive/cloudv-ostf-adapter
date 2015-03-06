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


from oslo_config import cfg


from cloudv_ostf_adapter import version


common_opts = [
    cfg.StrOpt("health_check_config_path",
               default='etc/cloudv_ostf_adapter/health_check.conf'),
    cfg.StrOpt("enabled_validation_plugins", default=['fuel_health']),
    cfg.StrOpt("nose_verbosity", default="-v")
]

sanity_group = cfg.OptGroup("sanity", "Sanity configuration group.")
smoke_group = cfg.OptGroup("smoke", "Smoke configuration group.")
platform_group = cfg.OptGroup("platform",
                              "Platform functional configuration group.")
ha_group = cfg.OptGroup("high_availability", "HA configuration group.")


sanity_opts = [
    cfg.MultiStrOpt("enabled_tests", default=[
        'fuel_health.tests.sanity.test_sanity_identity.SanityIdentityTest',
        'fuel_health.tests.sanity.test_sanity_compute.SanityComputeTest',
        'fuel_health.tests.sanity.test_sanity_heat.SanityHeatTest',
        'fuel_health.tests.sanity.test_sanity_networking.NetworksTest:'
        'test_list_networks_nova_network',
        'fuel_health.tests.sanity.test_sanity_ceilometer.CeilometerApiTests',
    ]),
]
smoke_opts = [
    cfg.MultiStrOpt("enabled_tests", default=[
        'fuel_health.tests.smoke.test_create_flavor.FlavorsAdminTest',
        'fuel_health.tests.smoke.test_create_volume.VolumesTest',
        'fuel_health.tests.smoke.test_neutron_actions.TestNeutron',
        'fuel_health.tests.smoke.test_nova_create_instance_with_connectivity.'
        'TestNovaNetwork',
        'fuel_health.tests.smoke.test_nova_image_actions.TestImageAction',
        'fuel_health.tests.smoke.test_user_create.TestUserTenantRole',
    ]),
]
platform_opts = [
    cfg.MultiStrOpt("enabled_tests", default=[]),
]
ha_opts = [
    cfg.MultiStrOpt("enabled_tests", default=[]),
]

CONF = cfg.CONF
CONF.register_opts(common_opts)

CONF.register_group(sanity_group)
CONF.register_group(smoke_group)
CONF.register_group(platform_group)
CONF.register_group(ha_group)

CONF.register_opts(sanity_opts, sanity_group)
CONF.register_opts(smoke_opts, smoke_group)
CONF.register_opts(platform_opts, platform_group)
CONF.register_opts(ha_opts, ha_group)


def parse_args(argv, default_config_files=None):
    cfg.CONF(args=argv[1:],
             project='cloudv_ostf_adapter',
             version=version.version,
             default_config_files=default_config_files)
