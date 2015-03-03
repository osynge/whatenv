#!/usr/bin/env python
import os

username = os.environ.get('OS_USERNAME')
password = os.environ.get('OS_PASSWORD')
authurl = os.environ.get('OS_AUTH_URL')
tenant_name = os.environ.get('OS_TENANT_NAME')

def get_keystone_creds():
    d = {}
    d['username'] = username
    d['password'] = password
    d['auth_url'] = authurl
    d['tenant_name'] = tenant_name
    return d

def get_nova_creds():
    d = {}
    d['username'] = username
    d['api_key'] = password
    d['auth_url'] = authurl
    d['project_id'] = tenant_name
    return d
