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

import os.path
import time
import yaml

from tempest.common import compute
from tempest.common import credentials_factory as common_creds
from tempest.common import waiters
from tempest import config
from tempest import exceptions
from tempest.lib import exceptions as lib_exc
from tempest import test

from oslo_log import log as logging

from conveyor_tempest_plugin.tests import clients
from conveyor_tempest_plugin.tests import exceptions as conveyor_exceptions

CONF = config.CONF

LOG = logging.getLogger(__name__)


class BaseConveyorTest(test.BaseTestCase):
    """Base test case class for all Conveyor API tests."""

    _api_version = 2
    credentials = ['primary']

    @classmethod
    def skip_checks(cls):
        super(BaseConveyorTest, cls).skip_checks()

        if not CONF.service_available.conveyor:
            skip_msg = (
                "%s skipped as Conveyor is not available" % cls.__name__)
            raise cls.skipException(skip_msg)

    @classmethod
    def setup_credentials(cls):
        cls.set_network_resources()
        super(BaseConveyorTest, cls).setup_credentials()

    @classmethod
    def get_client_manager(cls, credential_type=None, roles=None,
                           force_new=None):
        manager = super(BaseConveyorTest, cls).get_client_manager(
            credential_type=credential_type,
            roles=roles,
            force_new=force_new
        )
        return clients.Manager(manager.credentials)

    @classmethod
    def setup_clients(cls):
        super(BaseConveyorTest, cls).setup_clients()
        cls.client = cls.os_primary.conveyor_client
        cls.servers_client = cls.os_primary.servers_client
        cls.keypairs_client = cls.os_primary.keypairs_client
        cls.volumes_client = cls.os_primary.volumes_client

    @classmethod
    def resource_setup(cls):
        super(BaseConveyorTest, cls).resource_setup()
        cls.servers = []

        cls.volumes = []
        cls.clone_servers = []
        cls.clone_volumes = []
        cls.keypairs = []

    @classmethod
    def resource_cleanup(cls):
        super(BaseConveyorTest, cls).resource_cleanup()
        cls.clear_servers()
        cls.clear_volumes()
        cls.clear_keypairs()

    @classmethod
    def load_template(cls, name, ext='yaml'):
        loc = ["templates", "%s.%s" % (name, ext)]
        fullpath = os.path.join(os.path.dirname(__file__), *loc)

        with open(fullpath, "r") as f:
            return yaml.safe_load(f)

    @classmethod
    def read_template(cls, name, ext='yaml'):
        loc = ["templates", "%s.%s" % (name, ext)]
        fullpath = os.path.join(os.path.dirname(__file__), *loc)

        with open(fullpath, "r") as f:
            content = f.read()
            return content

    @classmethod
    def clear_volumes(cls):
        volumes = []
        volumes.extend(cls.volumes)
        volumes.extend(cls.clone_volumes)
        for volume in volumes:
            try:
                cls.volumes_client.delete_volume(volume['id'])
            except Exception:
                pass

        for volume in volumes:
            try:
                cls.volumes_client.wait_for_resource_deletion(volume['id'])
            except Exception:
                pass

    @classmethod
    def clear_keypairs(cls):
        for keypair in cls.keypairs:
            try:
                cls.keypairs_client.delete_keypair(keypair)
            except Exception:
                pass

    @classmethod
    def clear_servers(cls):
        servers = []
        servers.extend(cls.servers)
        servers.extend(cls.clone_servers)
        LOG.debug('Clearing servers: %s', ','.join(
            server['id'] for server in servers))
        for server in servers:
            try:
                cls.servers_client.delete_server(server['id'])
            except lib_exc.NotFound:
                # Something else already cleaned up the server, nothing to be
                # worried about
                pass
            except Exception:
                LOG.exception('Deleting server %s failed' % server['id'])

        for server in cls.servers:
            try:
                waiters.wait_for_server_termination(cls.servers_client,
                                                    server['id'])
            except Exception:
                LOG.exception('Waiting for deletion of server %s failed'
                              % server['id'])

    @classmethod
    def create_server(cls, validatable=False, volume_backed=False, **kwargs):
        tenant_network = cls.get_tenant_network()
        body, servers = compute.create_test_server(
            cls.os,
            validatable,
            validation_resources=cls.validation_resources,
            tenant_network=tenant_network,
            **kwargs)
        return body

    @classmethod
    def wait_for_plan_status(self, client, plan_id, status):
        """Waits for a plan to reach a given status."""
        body = client.show_plan(plan_id)['plan']
        plan_status = body['plan_status']
        start = int(time.time())

        while plan_status != status:
            time.sleep(client.build_interval)
            body = client.show_plan(plan_id)['plan']
            plan_status = body['plan_status']
            if plan_status == 'error':
                raise conveyor_exceptions.PlanBuildErrorException(
                    plan_id=plan_id)
            if int(time.time()) - start >= client.build_timeout:
                message = ('Plan %s failed to reach %s status (current %s) '
                           'within the required time (%s s).' %
                           (plan_id, status, plan_status,
                            client.build_timeout))
                raise exceptions.TimeoutException(message)

    @classmethod
    def wait_for_server_deletion(cls, client, plan_id):
        """Waits for plan to reach deletion."""
        start_time = int(time.time())
        while True:
            try:
                client.show_plan(plan_id)['plan']
            except Exception:
                return

            if int(time.time()) - start_time >= client.build_timeout:
                raise exceptions.TimeoutException

            time.sleep(client.build_interval)
