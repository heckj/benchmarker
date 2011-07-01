# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 Fourth Paradigm Development
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

"""ExampleService is responsible for doing nothing other than returning a
response quickly. It's used to benchmark message queue mechanisms.

"""

from nova import context
from nova import flags
from nova import log as logging
from nova import manager

LOG = logging.getLogger("benchmark.examplemanager")

FLAGS = flags.FLAGS

class ExampleManager(manager.Manager):
    """Implements a basic dummy manager that responds to queue mechanisms.

    """

    def __init__(self, *args, **kwargs):
        self.context = context.get_admin_context()

    def respond_to_message(self, context):
        LOG.debug(_('responding to queue message'), context=context)
        return "hello!"

