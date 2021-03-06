#! -*-coding:utf-8-*-

from __future__ import unicode_literals
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

import logging
import requests

from marshmallow.schema import Schema
from marshmallow import fields

HOST = "192.168.1.99"
PORT = 11100
BASE_URL = "http://{host}:{port}".format(host=HOST, port=PORT)


class TestCaseFailure(Exception):
    pass


class FindHostSchema(Schema):

    class HostSchema(Schema):
        connected = fields.Boolean(required=True, validate=lambda value: value is True)
        host_name = fields.String(required=True)
        oracle_listener_port = fields.Integer(required=True)
        vip = fields.String(required=True)
        ip = fields.String(required=True)

    class ScanSchema(Schema):
        scan_name = fields.String(required=True)
        scan_ip = fields.String(required=True)
        scan_port = fields.Integer(required=True)

    cluster_name = fields.String(required=True)
    cluster_scan_ip = fields.Nested(ScanSchema, required=True, many=True)
    hosts = fields.Nested(HostSchema, required=True, many=True)


class FindResourceDatabasePoolSchema(Schema):
    active_hosts = fields.Function(
        deserialize=lambda value: value, validate=lambda value: isinstance(value, list),
        required=True
    )
    importance = fields.String(required=True)
    max = fields.String(required=True)
    min = fields.String(required=True)
    pool_name = fields.String(required=True)


class FindDatabaseSchema(Schema):

    class InstanceSchema(Schema):
        host_name = fields.String(required=True)
        inst_name = fields.String(required=True)
        inst_stat = fields.String(required=True)

    config = fields.Function(
        deserialize=lambda v: v,
        validate=lambda value: isinstance(value, dict),
        required=True
    )
    db_name = fields.String(required=True)
    hosts = fields.Function(
        deserialize=lambda v: v,
        validate=lambda value: isinstance(value, list),
        required=True
    )
    instances = fields.Nested(InstanceSchema, many=True, required=True)


class DatabaseConnectionSchema(Schema):
    class Instance(Schema):
        connected = fields.Boolean(required=True)
        inst_name = fields.String(required=True)

    db_name = fields.String(required=True)
    instances = fields.Nested(Instance, many=True)


class DatabaseServiceNameSchema(Schema):
    db_name = fields.String(required=True)
    service_name = fields.Function(
        deserialize=lambda value: value, validate=lambda value: isinstance(value, list),
        required=True
    )


class HttpJSONClient:
    def __init__(self, username, password, auth_url):
        self.auth_url = auth_url
        self.username = username
        self.password = password
        self.session = requests.session()
        self.session.headers.update({'x-access-token': self.__token})

    def get(self, *args, **kwargs):
        return self.session.get(*args, **kwargs).json()

    def post(self, *args, **kwargs):
        response = self.session.post(*args, **kwargs)
        return response.json()

    def put(self, *args, **kwargs):
        return self.session.put(*args, **kwargs).json()

    def delete(self, *args, **kwargs):
        return self.session.delete(*args, **kwargs).json()

    def __del__(self):
        self.session.close()
        del self

    @property
    def __token(self):
        response = requests.post(self.auth_url, json={'name': self.username, 'password': self.password})
        return response.json()['data']['token']


class ClusterManager:
    def __init__(self, username, password):
        self.client = HttpJSONClient(username, password, urljoin(BASE_URL, "/users/auth"))

    def create_cluster(self, **kwargs):
        cluster_creation_url = urljoin(BASE_URL, "/cloud/cluster")
        return self.client.post(cluster_creation_url, json=kwargs)

    def remove_cluster(self, cluster_id):
        return self.client.delete(urljoin(BASE_URL, "/cloud/cluster/{cluster_id}".format(cluster_id=cluster_id)))

    def find_host(self, **kwargs):
        find_host_url = urljoin(BASE_URL, "/cloud/cluster/node/find")
        return self.client.post(find_host_url, json=kwargs)

    def find_resource_database_pool(self, **kwargs):
        find_resource_database_pool_url = urljoin(BASE_URL, "/cloud/cluster/dbpool/find")
        return self.client.post(find_resource_database_pool_url, json=kwargs)

    def find_database(self, **kwargs):
        find_database_url = urljoin(BASE_URL, "/cloud/cluster/db/find")
        return self.client.post(find_database_url, json=kwargs)

    def get_database_connection(self, **kwargs):
        database_connection_url = urljoin(BASE_URL, "/cloud/cluster/databases/connection")
        return self.client.post(database_connection_url, json=kwargs)

    def get_database_service_name(self, **kwargs):
        service_name_url = urljoin(BASE_URL, "/cloud/cluster/databases/servicename")
        return self.client.post(service_name_url, json=kwargs)

    def get_clusters(self):
        url = urljoin(BASE_URL, "/cloud/cluster/general")
        return self.client.get(url)

    def create_cluster_with_validation(self, **kwargs):
        response = self.create_cluster(**kwargs)
        assert response['error_code'] == 0
        return response

    def remove_cluster_with_validation(self, cluster_id):
        response = self.remove_cluster(cluster_id)
        assert response['error_code'] == 0
        return response

    def find_host_with_validation(self, **kwargs):
        logging.info(kwargs)
        response = self.find_host(**kwargs)
        return self._validation_with_schema(response, FindHostSchema, strict=True)

    def find_resource_database_pool_with_validation(self, **kwargs):
        response = self.find_resource_database_pool(**kwargs)
        return self._validation_with_schema(
            response, FindResourceDatabasePoolSchema, strict=True, many=True
        )

    def find_database_with_validation(self, **kwargs):
        response = self.find_database(**kwargs)
        return self._validation_with_schema(response, FindDatabaseSchema, strict=True, many=True)

    def get_database_connection_with_validation(self, **kwargs):
        response = self.get_database_connection(**kwargs)
        return self._validation_with_schema(response, DatabaseConnectionSchema, strict=True, many=True)

    def get_database_service_name_with_validation(self, **kwargs):
        response = self.get_database_service_name(**kwargs)
        return self._validation_with_schema(response, DatabaseServiceNameSchema, strict=True, many=True)

    def get_cluster_with_validation(self, cluster_alias_name):
        try:
            cluster_info = self.get_clusters()['data']['clusters']
        except LookupError:
            raise TestCaseFailure("集群信息为空")

        try:
            cluster = [cluster for cluster in cluster_info if cluster['alias_name'] == cluster_alias_name][0]
        except IndexError:
            raise TestCaseFailure("没有找到该集群的信息")

        return cluster

    def _validation_with_schema(self, response, schema, *args, **kwargs):
        assert response['error_code'] == 0, "response:{}".format(response)
        data = response['data']
        validation_schema = schema(*args, **kwargs)
        return validation_schema.load(data).data


class ClusterCreationManager:

    def __init__(
            self,
            login_username=None,
            login_password=None,
            cluster_ip=None,
            oracle_home=None,
            oracle_user=None,
            grid_home=None,
            grid_user=None,
            cluster_name=None,
            cluster_ssh_password=None,
            cluster_ssh_public_key=None,
            cluster_ssh_username=None,
            cluster_ssh_port=None,
    ):

        self.login_username = login_username
        self.login_password = login_password
        self._cluster_manager = ClusterManager(login_username, login_password)

        self.oracle_home = oracle_home
        self.oracle_user = oracle_user
        self.grid_home = grid_home
        self.grid_user = grid_user
        self.cluster_name = cluster_name
        self.cluster_ssh_password = cluster_ssh_password
        self.cluster_ssh_public_key = cluster_ssh_public_key
        self.cluster_ssh_username = cluster_ssh_username
        self.cluster_ssh_port = cluster_ssh_port
        self.cluster_ip = cluster_ip

    def create_cluster_with_password(self, monitor_user, monitor_password):

        hosts = self._cluster_manager.find_host_with_validation(
            host_ip=self.cluster_ip,
            username=self.cluster_ssh_username,
            gi_home=self.grid_home,
            grid_user=self.grid_user,
            oracle_user=self.oracle_user,
            oracle_home=self.oracle_home,
            ssh_port=self.cluster_ssh_port,
            password=self.cluster_ssh_password
        )

        resource_pool_hosts = [
            {
                "ip": host['ip'],
                "username": self.cluster_ssh_username,
                "password": self.cluster_ssh_password,
                "ssh_port": self.cluster_ssh_port
            }
            for host in hosts['hosts']
            ]
        resource_pool = self._cluster_manager.find_resource_database_pool_with_validation(
            hosts=resource_pool_hosts, oracle_home=self.oracle_home, oracle_user=self.oracle_user
        )

        database_host = [
            {
                'ip': host['ip'],
                'username': self.cluster_ssh_username,
                'password': self.cluster_ssh_password,
                "ssh_port": self.cluster_ssh_port,
                "vip": host['vip'],
                "host_name": host['host_name']
            }
            for host in hosts['hosts']
            ]

        databases = self._cluster_manager.find_database_with_validation(
            username=self.cluster_ssh_username,
            oracle_home=self.oracle_home,
            oracle_user=self.oracle_user,
            gi_home=self.grid_home,
            grid_user=self.grid_user,
            hosts=database_host
        )

        databases_connection = self._cluster_manager.get_database_connection_with_validation(
            cluster_scan_ip=hosts['cluster_scan_ip'],
            o_user=monitor_user,
            o_pass=monitor_password,
            databases=databases
        )
        # 获取连接正常的数据库
        connection_health_databases = [
            item for item in databases_connection
            if False not in [inst['connected'] for inst in item['instances']]
            ]
        service_name_list = self._cluster_manager.get_database_service_name_with_validation(
            cluster_scan_ip=hosts['cluster_scan_ip'],
            o_user=monitor_user,
            o_pass=monitor_password,
            databases=connection_health_databases
        )

        service_name_hash = {service['db_name']: service['service_name'] for service in service_name_list}
        healthy_database_name_list = [db['db_name'] for db in connection_health_databases]

        healthy_databases = [item for item in databases if item['db_name'] in healthy_database_name_list]
        for db in healthy_databases:
            db['service_name'] = service_name_hash[db['db_name']]

        create_cluster_hosts = [
            {
                'ip': host['ip'],
                'username': self.cluster_ssh_username,
                'password': self.cluster_ssh_password,
                "ssh_port": self.cluster_ssh_port,
                "vip": host['vip'],
                "host_name": host['host_name'],
                "connected": True,
                "oracle_listener_port": host['oracle_listener_port'],
                "pub_key": ""
            }
            for host in hosts['hosts']
            ]
        response = self._cluster_manager.create_cluster_with_validation(
            cluster_name=hosts['cluster_name'],
            cluster_alias_name=self.cluster_name,
            oracle_home=self.oracle_home,
            oracle_user=self.oracle_user,
            o_user=monitor_user,
            o_pass=monitor_password,
            grid_user=self.grid_user,
            gi_home=self.grid_home,
            cluster_scan_ip=hosts['cluster_scan_ip'],
            cluster_ssh_port=self.cluster_ssh_port,
            cluster_ssh_password=self.cluster_ssh_password,
            cluster_ssh_pub_key="",
            cluster_ssh_user=self.cluster_ssh_username,
            databases=healthy_databases,
            pools=resource_pool,
            hosts=create_cluster_hosts
        )

        return response

    def get_cluster(self):
        return self._cluster_manager.get_cluster_with_validation(self.cluster_name)

    def remove_cluster(self):
        cluster = self.get_cluster()
        return self._cluster_manager.remove_cluster_with_validation(cluster['cluster_id'])
