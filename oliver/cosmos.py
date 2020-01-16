import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
import azure.cosmos.http_constants as http_constants

import json 
import os

class CosmosAPI:
    def __init__(self, cosmos_name = "", resource_group=""):
        stream = os.popen('az cosmosdb show --name '+cosmos_name+' --resource-group '+resource_group)
        server = stream.read()
        server = json.loads(server)
        self.server = server['documentEndpoint']
        stream = os.popen('az cosmosdb keys list --name '+cosmos_name+' --resource-group '+resource_group)
        key = stream.read()
        key = json.loads(key)
        self.key = key['primaryMasterKey']
        self.client = cosmos_client.CosmosClient(self.server, {'masterKey': self.key})

    def _api_call(self, route, params = {}, data = None, files = None, method="GET"):
        url = urljoin(self.server, route).format(
            version = self.version
        )
        
        response = request(method, url, headers=self.headers, params=params, data=data, files=files)
        return response.status_code, json.loads(response.content)

    def query(self, database_id = "TES", container_id = "Tasks", where=""):
        return self.client.QueryItems("dbs/" + database_id + "/colls/" + container_id,
                              'SELECT * FROM ' + container_id + ' r ' + where,
                              {'enableCrossPartitionQuery': True})
