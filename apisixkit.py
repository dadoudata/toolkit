# -*- coding:utf-8 -*-
#
#------------------------------------+
# Simple Apisix Gateway Admin API SDK
# License: MIT
# Deps: python3, requests
#------------------------------------+
#
# 
import requests
from urllib.parse import urljoin
import os
import logging

logger = logging.getLogger(__name__)


class APISIXHandler(object):
    def __init__(self):
        self.apisix_host = os.environ.get('APISIX_HOST', settings.APISIX_HOST)
        self.apisix_key = os.environ.get('APISIX_KEY', settings.APISIX_KEY)
        self.base_uri = urljoin(self.apisix_host, '/apisix/admin/')
        self.timeout = 30

    def do(self, method, path, body=None):
        logger.debug("request body => {}".format(body))
        resp = requests.request(
            method,
            urljoin(self.base_uri, path),
            json=body,
            headers={'X-API-KEY': self.apisix_key},
            timeout=self.timeout
        )
        response = resp.json()
        if resp.status_code >= 300:
            error_msg = response.get('error_msg', '') or response.get('message', '')
            logger.warn('{} {} failed, status: {} => {}'.format(method, path, resp.status_code, error_msg))
            return None
        return response['node']

    def add_consumer(self, **kwargs):
        if not kwargs['username']:
            raise Exception('no username specified')
        http_verb = 'PUT'
        url = 'consumers'
        resp = self.do(http_verb, url, kwargs)
        consumer_username = resp['key'].split('/')[-1]
        logger.debug("add consumer username => {}".format(consumer_username))
        return consumer_username

    def get_consumer(self, consumer_username):
        if not consumer_username:
            raise Exception('no consumer_username specified')
        return self.do('GET', 'consumers/' + str(consumer_username))

    def get_consumer_list(self):
        return self.do('GET', 'consumers')

    def del_consumer(self, consumer_username):
        if not consumer_username:
            raise Exception('no consumer_username specified')
        logger.warn("delete consumer username => {}".format(consumer_username))
        return self.do('DELETE', 'consumers/' + str(consumer_username))

    def add_route(self, **kwargs):
        if not kwargs['uris']:
            raise Exception('no uris specified')
        http_verb = 'POST'
        url = 'routes/'
        route_id = kwargs['route_id']
        del kwargs['route_id']
        if route_id:
            http_verb = 'PUT'
            url = url + str(route_id)
        resp = self.do(http_verb, url, kwargs)
        route_id = resp['key'].split('/')[-1]
        logger.debug("add route id => {}".format(route_id))
        return int(route_id)

    def get_route(self, route_id):
        if not route_id:
            raise Exception('no route_id specified')
        return self.do('GET', 'routes/' + str(route_id))

    def get_route_list(self):
        return self.do('GET', 'routes')

    def del_route(self, route_id):
        if not route_id:
            raise Exception('no route_id specified')
        logger.warn("delete route id => {}".format(route_id))
        return self.do('DELETE', 'routes/' + str(route_id))


if __name__ == '__main__':
    ah = APISIXHandler()
    # route_id = "351396369996449157"
    # ah.get_route(route_id)

    
    # plugins = {
    #     "key-auth": {
    #         "disable": False,
    #         "key": "123u12"
    #     },
    #     "limit-count": {
    #         "count": 10,
    #         "disable": False,
    #         "key": "consumer_name",
    #         "rejected_code": 429,
    #         "time_window": 60,
    #         "policy": "redis",
    #         "redis_host": "127.0.0.1",
    #         "redis_port": 6379,
    #         "redis_database": 2,
    #         "redis_timeout": 1000
    #     },
    #     "limit-conn": {
    #         "conn": 1,
    #         "burst": 2,
    #         "default_conn_delay": 0.1,
    #         "rejected_code": 429,
    #         "key": "remote_addr"
    #     }
    # }
    # ah.add_consumer(
    #     username="emailservice_user12",
    #     desc="email user 12",
    #     plugins=plugins
    # )

    plugins = {
        "key-auth": {
            "disable": False
        },
        "request-id": {
            "include_in_response": True
        },
        "ip-restriction": {
            "whitelist": ["127.0.0.1", "20.74.26.106/24"]
        }
    }
    upstream = {
        "nodes": [
            {
                "host": "127.0.0.1",
                "port": 9002,
                "weight": 1
            }
        ],
        "timeout": {
            "connect": 6,
            "read": 6,
            "send": 6
        },
        "type": "roundrobin",
        "pass_host": "pass"
    }
    labels = {"API_VERSION": "1.0", "api": "demo-api"}
    ah.add_route(
        route_id="123123",
        name="api_route_1",
        uris=["/v2/*"],
        methods=["GET", "POST"],
        hosts=["api.example.com"],
        plugins=plugins,
        upstream=upstream,
        labels=labels,
        status=1
    )
