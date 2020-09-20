# SPDX-FileCopyrightText: 2019 SAP SE or an SAP affiliate company and Gardener contributors
#
# SPDX-License-Identifier: Apache-2.0
from model.base import NamedModelElement


class Oauth2ProxyConfig(NamedModelElement):
    '''Not intended to be instantiated by users of this module
    '''

    def oauth2_proxy_chart_config(self):
        return Oauth2ProxyChartConfig(
            '',
            self.raw.get('oauth2_proxy_chart_config')
        )

    def github_oauth_config(self):
        return GithubOauthConfig(
            '',
            self.raw.get('github_oauth_config')
        )

    def external_url(self):
        return self.raw.get('external_url')

    def ingress_config(self):
        return self.raw.get('ingress_config')

    def ingress_host(self):
        return self.raw.get('ingress_host')

    def namespace(self):
        return self.raw.get('namespace')

    def _required_attributes(self):
        yield from super()._required_attributes()
        yield from [
            'external_url',
            'github_oauth_config',
            'ingress_config',
            'ingress_host',
            'namespace',
            'oauth2_proxy_chart_config',
        ]


class Oauth2ProxyChartConfig(NamedModelElement):
    def cookie_secret(self):
        return self.raw.get('cookie_secret')

    def cookie_name(self):
        return self.raw.get('cookie_name')

    def _required_attributes(self):
        yield from super()._required_attributes()
        yield from [
            'cookie_secret',
        ]

    def _optional_attributes(self):
        yield from super()._optional_attributes()
        yield from [
            'cookie_name',
        ]


class GithubOauthConfig(NamedModelElement):
    # Move to github.py?

    def client_id(self):
        return self.raw.get('client_id')

    def client_secret(self):
        return self.raw.get('client_secret')

    def github_cfg_name(self):
        return self.raw.get('github_cfg_name')

    def github_org(self):
        return self.raw.get('github_org')

    def github_team(self):
        return self.raw.get('github_team')

    def no_ssl_verify(self):
        return self.raw.get('no_ssl_verify', False)

    def _required_attributes(self):
        yield from super()._required_attributes()
        yield from [
            'client_id',
            'client_secret',
            'github_cfg_name',
            'github_org',
            'github_team',
        ]

    def _optional_attributes(self):
        yield from super()._optional_attributes()
        yield from [
            'no_ssl_verify',
        ]
