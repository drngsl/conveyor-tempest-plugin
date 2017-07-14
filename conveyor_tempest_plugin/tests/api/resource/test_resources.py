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

import operator

from tempest.common.utils import data_utils
from tempest.common import waiters
from tempest import config
from tempest import test

from conveyor_tempest_plugin.tests import base

from oslo_log import log as logging

CONF = config.CONF
LOG = logging.getLogger(__name__)


class ResourcesV1TestJSON(base.BaseConveyorTest):
    def assertResourceIn(self, fetched_res, res_list, fields=None):

        if not fields:
            self.assertIn(fetched_res, res_list)

        res_list = map(operator.itemgetter(*fields), res_list)
        fetched_res = map(operator.itemgetter(*fields), [fetched_res])[0]

        self.assertIn(fetched_res, res_list)

    def assertListIn(self, expected_list, fetched_list):
        missing_items = [v for v in expected_list if v not in fetched_list]
        if len(missing_items) == 0:
            return
        raw_msg = "%s not in fetched_list %s" \
                  % (missing_items, fetched_list)
        self.fail(raw_msg)

    @classmethod
    def setup_clients(cls):
        super(ResourcesV1TestJSON, cls).setup_clients()

    @classmethod
    def resource_setup(cls):
        super(ResourcesV1TestJSON, cls).resource_setup()

        # cls.keypair_ref = CONF.conveyor.origin_keypair_ref
        cls.secgroup_ref = CONF.conveyor.origin_security_group_ref
        cls.net_ref = CONF.conveyor.origin_net_ref
        # cls.public_net_ref = CONF.conveyor.public_net_ref
        cls.floating_ip_pool_ref = CONF.conveyor.floating_ip_pool_ref
        # cls.subnet_ref = CONF.conveyor.origin_subnet_ref
        cls.image_ref = CONF.conveyor.image_ref
        cls.flavor_ref = CONF.conveyor.flavor_ref
        cls.availability_zone_ref = CONF.conveyor.availability_zone

        cls.volume_size = CONF.conveyor.volume_size
        cls.volume_type_ref = CONF.conveyor.volume_type

        cls.meta = {'hello': 'world'}
        cls.name = data_utils.rand_name('server')
        cls.password = data_utils.rand_password()
        networks = [{'uuid': cls.net_ref}]

        server_initial = cls.create_server(
            networks=networks,
            wait_until='ACTIVE',
            # name=cls.name,
            name="server_resource",
            metadata=cls.meta,
            adminPass=cls.password,
            # key_name=key_name,
            # security_groups=cls.secgroup_ref,
            availability_zone=cls.availability_zone_ref)

        cls.server = (
            cls.servers_client.show_server(server_initial['id'])['server'])
        cls.servers.append(cls.server)

        cls.volume = cls.volumes_client.create_volume(
            size=cls.volume_size,
            # display_name='volume01',
            display_name='volume_resource',
            availability_zone=cls.availability_zone_ref,
            volume_type=cls.volume_type_ref)['volume']

        cls.volumes.append(cls.volume)
        waiters.wait_for_volume_status(cls.volumes_client,
                                       cls.volume['id'], 'available')

        # Attach the volume to the server
        cls.servers_client.attach_volume(
            server_initial['id'],
            volumeId=cls.volume['id'])['volumeAttachment']
        waiters.wait_for_volume_status(cls.volumes_client,
                                       cls.volume['id'], 'in-use')

        cls.server = (
            cls.servers_client.show_server(server_initial['id'])['server'])

    @classmethod
    def resource_cleanup(cls):
        super(ResourcesV1TestJSON, cls).resource_cleanup()

    @test.attr(type='smoke')
    @test.idempotent_id('ee9aa589-d6f0-4365-aa66-613efd3c117f')
    def test_list_types(self):
        res_types = self.client.show_resource_types()['types']

        instance_type = {'type': 'OS::Nova::Server'}
        volume_type = {'type': 'OS::Cinder::Volume'}

        self.assertIn(instance_type, res_types)
        self.assertIn(volume_type, res_types)

    @test.attr(type='smoke')
    @test.idempotent_id('034e065b-8822-4017-9586-349ca735d06a')
    def test_list_resources(self):
        res = self.client.list_resources({'type': 'OS::Nova::Server',
                                          'all_tenants': 1})['resources']
        self.assertResourceIn(self.server, res, fields=['id'])

    @test.attr(type='smoke')
    @test.idempotent_id('186a8645-3a40-432b-8b78-e82e5e27aa49')
    def test_show_resource(self):
        res = self.client.show_resource(self.server['id'],
                                        type='OS::Nova::Server')['resource']
        fields = ['id', 'name']
        self.assertResourceIn(self.server, [res], fields=fields)
        for net, detail in self.server['addresses'].items():
            self.assertIn(net, res['addresses'].keys())
            self.assertEqual(detail, res['addresses'][net])
