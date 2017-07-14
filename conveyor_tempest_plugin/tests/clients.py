# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from tempest import clients
from tempest import config

from tempest.lib.services.compute.availability_zone_client import \
    AvailabilityZoneClient
from tempest.lib.services.compute.flavors_client import FlavorsClient
from tempest.lib.services.compute.keypairs_client import KeyPairsClient
from tempest.lib.services.compute.servers_client import ServersClient
from tempest.services.orchestration.json.orchestration_client import \
    OrchestrationClient
from tempest.services.volume.v1.json.volumes_client import VolumesClient
from tempest.services.volume.v2.json.volumes_client import \
    VolumesClient as VolumesV2Client

from conveyor_tempest_plugin.services import client

CONF = config.CONF


class Manager(clients.Manager):

    def __init__(self, credentials):
        super(Manager, self).__init__(credentials)

        params = {
            'service': CONF.conveyor.catalog_type,
            'region': CONF.conveyor.region or CONF.identity.region,
            'endpoint_type': CONF.conveyor.endpoint_type
        }
        params.update(self.default_params)

        self.conveyor_client = client.BaseConveyorClient(
            self.auth_provider, **params)

    def _set_compute_client(self):
        params = {
            'service': CONF.compute.catalog_type,
            'region': CONF.compute.region or CONF.identity.region,
            'endpoint_type': CONF.compute.endpoint_type,
            'build_interval': CONF.compute.build_interval,
            'build_timeout': CONF.compute.build_timeout
        }
        params.update(self.default_params)
        self.servers_client = ServersClient(
            self.auth_provider,
            enable_instance_password=CONF.compute_feature_enabled
                .enable_instance_password,
            **params)

        self.keypairs_client = KeyPairsClient(self.auth_provider, **params)
        self.flavors_client = FlavorsClient(self.auth_provider, **params)
        self.availability_zone_client = AvailabilityZoneClient(
            self.auth_provider, **params)

    def _set_volume_client(self):
        params = {
            'service': CONF.volume.catalog_type,
            'region': CONF.volume.region or CONF.identity.region,
            'endpoint_type': CONF.volume.endpoint_type,
            'build_interval': CONF.volume.build_interval,
            'build_timeout': CONF.volume.build_timeout
        }
        params.update(self.default_params)

        if CONF.volume_feature_enabled.api_v1:
            self.volumes_client = VolumesClient(
                self.auth_provider,
                default_volume_size=CONF.volume.volume_size,
                **params)
        else:
            self.volumes_client = VolumesV2Client(
                self.auth_provider,
                default_volume_size=CONF.volume.volume_size,
                **params)

    def _set_orchestration_client(self):
        self.orchestration_client = OrchestrationClient(
            self.auth_provider,
            CONF.orchestration.catalog_type,
            CONF.orchestration.region or CONF.identity.region,
            endpoint_type=CONF.orchestration.endpoint_type,
            build_interval=CONF.orchestration.build_interval,
            build_timeout=CONF.orchestration.build_timeout,
            **self.default_params)
