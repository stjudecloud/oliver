import json

from requests import request
from urllib.parse import urljoin

class CromwellAPI:

    def __init__(self, server = "http://localhost:8000", version = "v1", 
                headers = { 'Accept' : 'application/json'}):
        self.server = server
        self.version = version
        self.headers = headers

    def _api_call(self, route, params = {}, data = None, files = None, method="GET"):
        url = urljoin(self.server, route).format(
            version = self.version
        )
        
        response = request(method, url, headers=self.headers, params=params, data=data, files=files)
        return response.status_code, json.loads(response.content)

    def post_workflows(self, workflowUrl, workflowInputs, workflowOptions):
        "POST /api/workflows/{version}"

        workflowInputs_file = open(workflowInputs, "rb")
        workflowInputs_text = workflowInputs_file.read()

        files = {
            "workflowUrl": workflowUrl,
            "workflowInputs": workflowInputs_text
        }

        _, data = self._api_call("/api/workflows/{version}", method="POST", files=files)
        return data

    def post_workflows_batch(self):
        "POST /api/workflows/{version}/batch"
        raise NotImplementedError()

    def get_workflows_labels(self):
        "GET /api/workflows/{version}/{id}/labels"
        raise NotImplementedError()

    def patch_workflows_labels(self):
        "PATCH /api/workflows/{version}/{id}/labels"
        raise NotImplementedError()

    def post_workflows_abort(self, workflow_id):
        "POST /api/workflows/{version}/{id}/abort"

        _, data = self._api_call(f"/api/workflows/{{version}}/{workflow_id}/abort", method="POST")
        return data

    def post_workflows_release_hold(self):
        "POST /api/workflows/{version}/{id}/releaseHold"
        raise NotImplementedError()

    def get_workflows_status(self):
        "GET /api/workflows/{version}/{id}/status"
        raise NotImplementedError()

    def get_workflows_outputs(self, workflow_id):
        "GET /api/workflows/{version}/{id}/outputs"

        _, data = self._api_call(f"/api/workflows/{{version}}/{workflow_id}/outputs")
        return data

    def get_workflows_logs(self, workflow_id):
        "POST /api/workflows/{version}/{id}/logs"

        _, data = self._api_call(f"/api/workflows/{{version}}/{workflow_id}/logs")
        return data

    def get_workflows_query(self, includeSubworkflows=True, statuses=None):
        "GET /api/workflows/{version}/query"
        params = { "includeSubworkflows": includeSubworkflows }

        if statuses:
            params["status"] = statuses

        _, data = self._api_call("/api/workflows/{version}/query", params=params)
        if not 'results' in data:
            raise RuntimeError("Expected 'results' key in response!")

        return data['results']

    def post_workflows_query(self):
        "POST /api/workflows/{version}/query"
        raise NotImplementedError()

    def get_workflows_timing(self):
        "GET /api/workflows/{version}/{id}/timing"
        raise NotImplementedError()


    def get_workflows_metadata(self, workflow_id):
        "GET /api/workflows/{version}/{id}/metadata"

        _, data = self._api_call(f"/api/workflows/{{version}}/{workflow_id}/metadata")
        return data


    def get_workflows_call_caching_diff(self):
        "GET /api/workflows/{version}/callcaching/diff"
        raise NotImplementedError()

    def get_workflows_backends(self):
        "GET /api/workflows/{version}/backends"
        raise NotImplementedError()