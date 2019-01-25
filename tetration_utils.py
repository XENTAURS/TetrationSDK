'''
DESCRIPTION: A set of classes for working with the Tetration API
AUTHOR: Matt Mullen, Xentaurs
VERSION: 1.0

REQUIREMENTS:
    - Python requests module

'''

import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import sys

# Disable warnings due to self-signed cert
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class TetUtils(object):
    def _ResponseCheck(self,resp):
        self.last_status_code = resp.status_code
        if not resp.status_code == 200:
            print('ERROR: There was a problem submitting the request to {0}'.format(resp.url))
            print('HTTP Status Code: {0}'.format(str(resp.status_code)))
            print('Reason: {0}'.format(resp.reason))
            print('Content: {0}'.format(resp.content.decode('UTF-8')))
            sys.exit()

# Class to work with Scopes in Tetration
class Scope(TetUtils):
    '''
    Class to create/update/delete Tetration Scopes. Requires a tetpyclient.RestClient object
    '''
    def __init__(self,restclient):
        self.restclient = restclient
        self.scopes = self.restclient.get('/app_scopes')
        self._ResponseCheck(self.scopes)

    def ParentID_Lookup(self,parent_name):
        '''
        Look up the id of the parent Scope using short_name ex. "TAAS104"
        '''
        for payload in json.loads(self.scopes.content):
            if payload['short_name'] == parent_name:
                parent_id = payload['id']
        return parent_id

    def Create(self,name,type,field,value,parent_name):
        '''
        ex. Create('MyScope','eq','ip','10.0.0.0/8','TAAS104')
        '''
        self.scope_payload = {"short_name": name,
                     "short_query": {"type": type,
                                     "field": field,
                                     "value": value},
                     "parent_app_scope_id": self.ParentID_Lookup(parent_name)}
        self.scope_resp = self.restclient.post('/app_scopes', json_body=json.dumps(self.scope_payload))
        self._ResponseCheck(self.scope_resp)
        return self.scope_resp.status_code, self.scope_resp.reason

    def GetScopeByName(self,scope_name):
        '''
        Get a scope by full name including hierarchy (ex. default:TAAS104). Returns a tuple containing name,id
        '''
        found_scope = None
        for payload in json.loads(self.scopes.content):
            if payload['name'] == scope_name:
                found_scope = (payload['name'],payload['id'])

        return found_scope

    def GetScopeByShortName(self,scope_short_name):
        '''
        Get a scope by short_name (ex. "TAAS104"). Returns a tuple containing name,id
        '''
        found_scope = None
        for payload in json.loads(self.scopes.content):
            if payload['short_name'] == scope_short_name:
                found_scope = (payload['short_name'],payload['id'])
        return found_scope

    def GetScopeByID(self,id):
        '''
        Get a scope by its ID. Returns all details for the scope.
        '''
        found_scope = None
        for payload in json.loads(self.scopes.content):
            if payload['id'] == id:
                found_scope = payload
        return found_scope

    def GetScopeList(self):
        '''
        Return a list of scopes and their scope ids
        '''
        scope_list = []
        for scope in json.loads(self.scopes.content):
            scope_list.append((scope['name'],scope['id']))
        return scope_list

    def FindDirtyScopes(self):
        '''
        See what scope is reported as changed.
        '''
        dirty_scopes = []
        for payload in json.loads(self.scopes.content):
            if payload['dirty']:
                dirty_scopes.append(payload['name'])
        return dirty_scopes