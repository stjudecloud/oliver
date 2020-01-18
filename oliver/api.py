import json
import sys

from requests import request
from urllib.parse import urljoin

from . import errors, reporting


class CromwellAPI:
    def __init__(
        self,
        server="http://localhost:8000",
        version="v1",
        headers={"Accept": "application/json"},
    ):
        self.server = server
        self.version = version
        self.headers = headers

    def _api_call(self, route, params={}, data=None, files=None, method="GET"):
        url = urljoin(self.server, route).format(version=self.version)

        response = request(
            method, url, headers=self.headers, params=params, data=data, files=files
        )

        status_code = response.status_code
        content = json.loads(response.content)

        if not str(status_code).startswith("2"):
            if "status" in content and content["status"] == "fail":
                reporting.print_error_as_table(
                    content["status"].capitalize(), content["message"].capitalize()
                )
                sys.exit(errors.ERROR_UNEXPECTED_RESPONSE)

        return status_code, content

    def post_workflows(
        self,
        workflowSource=None,
        workflowUrl=None,
        workflowInputs={},
        workflowOptions={},
        labels={},
    ):
        "POST /api/workflows/{version}"

        if workflowSource is None and workflowUrl is None:
            errors.report(
                "Expected either 'workflowSource' or 'workflowUrl'!",
                fatal=True,
                exitcode=errors.ERROR_INVALID_INPUT,
            )

        files = {
            "workflowSource": workflowSource,
            "workflowUrl": workflowUrl,
            "workflowInputs": workflowInputs,
            "workflowOptions": workflowOptions,
            "labels": labels,
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

        _, data = self._api_call(
            f"/api/workflows/{{version}}/{workflow_id}/abort", method="POST"
        )
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

    def get_workflows_query(self, includeSubworkflows=True, statuses=None, labels=None):
        "GET /api/workflows/{version}/query"
        params = {"includeSubworkflows": includeSubworkflows}

        if statuses:
            params["status"] = statuses

        if labels:
            params["label"] = labels

        _, data = self._api_call("/api/workflows/{version}/query", params=params)
        if not "results" in data:
            errors.report(
                "Expected 'results' key in response!",
                fatal=True,
                exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
            )

        return data["results"]

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
