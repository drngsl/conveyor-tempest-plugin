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

from oslo_serialization import jsonutils as json
import six
from six.moves.urllib import parse as urllib

from tempest.lib.common import rest_client

from tempest import config

CONF = config.CONF


class BaseConveyorClient(rest_client.RestClient):

    create_resp = 200

    def __init__(self, auth_provider, service, region, **kwargs):
        if 'build_timeout' not in kwargs:
            kwargs['build_timeout'] = CONF.conveyor.build_timeout
        if 'build_interval' not in kwargs:
            kwargs['build_interval'] = CONF.conveyor.build_interval
        super(BaseConveyorClient, self).__init__(
            auth_provider, service, region, **kwargs)

    def _prepare_params(self, params):
        """Prepares params for use in get or _ext_get methods.

        If params is a string it will be left as it is, but if it's not it will
        be urlencoded.
        """
        if isinstance(params, six.string_types):
            return params
        return urllib.urlencode(params)

    def list_plans(self, detail=False, params=None):
        """List all the plans created.

        Params can be a string (must be urlencoded) or a dictionary.
        """
        url = 'plans'
        if detail:
            url += '/detail'
        if params:
            url += '?%s' % self._prepare_params(params)

        resp, body = self.get(url)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return rest_client.ResponseBody(resp, body)

    def show_plan(self, plan_id):
        """Returns the details of a single plan."""
        url = "plans/%s" % str(plan_id)
        resp, body = self.get(url)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return rest_client.ResponseBody(resp, body)

    def create_plan(self, **kwargs):
        """Creates a new Plan.
        """
        post_body = json.dumps({'plan': kwargs})
        resp, body = self.post('plans', post_body)
        body = json.loads(body)
        self.expected_success(self.create_resp, resp.status)
        return rest_client.ResponseBody(resp, body)

    def update_plan(self, plan_id, **kwargs):
        """Updates the Specified Plan."""
        put_body = json.dumps({'plan': kwargs})
        resp, body = self.put('plans/%s' % plan_id, put_body)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return rest_client.ResponseBody(resp, body)

    def delete_plan(self, plan_id):
        """Deletes the Specified Plan."""
        resp, body = self.delete("plans/%s" % str(plan_id))
        self.expected_success(200, resp.status)
        return rest_client.ResponseBody(resp, body)

    def show_resource_types(self):
        url = 'resources/types'
        resp, body = self.get(url)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return rest_client.ResponseBody(resp, body)

    def list_resources(self, params=None):
        url = 'resources/detail'
        if params:
            url += '?%s' % self._prepare_params(params)

        resp, body = self.get(url)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return rest_client.ResponseBody(resp, body)

    def create_plan_by_template(self, template):
        post_body = json.dumps({"plan": {'template': template}})
        resp, body = self.post('plans/create_plan_by_template',
                               post_body)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def show_resource(self, res_id, **kwargs):
        post_body = json.dumps({'get_resource_detail': kwargs})
        resp, body = self.post('resources/%s/action' % res_id,
                               post_body)
        self.expected_success(202, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def export_clone_template(self, plan_id, **kwargs):
        """export a template of a Plan."""
        post_body = json.dumps({'export_clone_template': {
            'update_resources': kwargs.get('update_resources')}})
        resp, body = self.post('clones/%s/action' % plan_id,
                               post_body)
        return rest_client.ResponseBody(resp, body)

    def clone(self, plan_id, **kwargs):
        """clone a Plan."""
        post_body = json.dumps(
            {'clone': {'update_resources': kwargs.get('update_resources'),
                       'destination': kwargs.get('destination')}})
        resp, body = self.post('clones/%s/action' % plan_id,
                               post_body)
        return rest_client.ResponseBody(resp, body)

    def migrate(self, plan_id, **kwargs):
        """migrate a Plan."""
        post_body = json.dumps(
            {'migrate': {'destination': kwargs.get('destination')}})
        resp, body = self.post('migrates/%s/action' % plan_id,
                               post_body)
        return rest_client.ResponseBody(resp, body)
