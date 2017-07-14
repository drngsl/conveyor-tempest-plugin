# Copyright 2015
# All Rights Reserved.
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

service_option = [
    cfg.BoolOpt("conveyor_plugin",
                default=True,
                help="Whether or not conveyor is expected to be available"),
]

conveyor_group = cfg.OptGroup(name='conveyor',
                              title='Conveyor Service Options')

ConveyorGroup = [
    cfg.StrOpt('catalog_type',
               default='conveyor',
               help="Catalog type of the Alarming service."),
    cfg.StrOpt('endpoint_type',
               default='publicURL',
               choices=['public', 'admin', 'internal',
                        'publicURL', 'adminURL', 'internalURL'],
               help="The endpoint type to use for the alarming service."),
    cfg.StrOpt('region',
               default='RegionOne',
               help="The identity region name to use. Also used as the other "
                    "services' region name unless they are set explicitly. "
                    "If no such region is found in the service catalog, the "
                    "first found one is used."),
    cfg.IntOpt('build_timeout',
               default=300,
               help="Catalog type of the Alarming service."),
    cfg.IntOpt('build_interval',
               default=5,
               help="Catalog type of the Alarming service."),

    cfg.StrOpt('origin_keypair_ref',
               default='',
               help="The endpoint type to use for the alarming service."),
    cfg.StrOpt('update_keypair_ref',
               default='',
               help="The identity region name to use. Also used as the other "
                    "services' region name unless they are set explicitly. "
                    "If no such region is found in the service catalog, the "
                    "first found one is used."),
    cfg.StrOpt('origin_security_group_ref',
               default="",
               help="Catalog type of the Alarming service."),
    cfg.StrOpt('update_security_group_ref',
               default='',
               help="The endpoint type to use for the alarming service."),
    cfg.StrOpt('origin_net_ref',
               default='',
               help="The identity region name to use. Also used as the other "
                    "services' region name unless they are set explicitly. "
                    "If no such region is found in the service catalog, the "
                    "first found one is used."),

    cfg.StrOpt('update_net_ref',
               default="",
               help="Catalog type of the Alarming service."),
    cfg.StrOpt('origin_subnet_ref',
               default='',
               help="The endpoint type to use for the alarming service."),
    cfg.StrOpt('update_subnet_ref',
               default='',
               help="The identity region name to use. Also used as the other "
                    "services' region name unless they are set explicitly. "
                    "If no such region is found in the service catalog, the "
                    "first found one is used."),
    cfg.StrOpt('image_ref',
               default="",
               help="Catalog type of the Alarming service."),
    cfg.StrOpt('flavor_ref',
               default="",
               help="Catalog type of the Alarming service."),
    cfg.StrOpt('fix_ip',
               default="",
               help="Catalog type of the Alarming service."),
    cfg.StrOpt('availability_zone',
               default='',
               help="The endpoint type to use for the alarming service."),
    cfg.StrOpt('clone_availability_zone',
               default='',
               help="The identity region name to use. Also used as the other "
                    "services' region name unless they are set explicitly. "
                    "If no such region is found in the service catalog, the "
                    "first found one is used."),
    cfg.IntOpt('volume_size',
               default=1,
               help='Default size in GB for volumes created by volumes tests'),
    cfg.StrOpt('volume_type',
               default=None,
               help='volume type of volume'),
    cfg.StrOpt('floating_ip_pool_ref',
               default='',
               help="The ip pool to create floating ip."),
]
