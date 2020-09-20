# SPDX-FileCopyrightText: 2020 SAP SE or an SAP affiliate company and Gardener contributors
#
# SPDX-License-Identifier: Apache-2.0

from model.base import (
    NamedModelElement,
)


class GcpServiceAccount(NamedModelElement):
    def service_account_key(self):
        '''
        service-account-key (credentials) as retrieved from GCP's IAM & Admin console
        '''
        return self.raw['service_account_key']

    def project(self):
        return self.raw['project']

    def _required_attributes(self):
        return ['service_account_key','project']
