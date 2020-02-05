import aiohttp
import datetime
import json
import sys

from logzero import logger
from typing import Dict, List
from requests import request
from urllib.parse import urljoin

from . import errors, reporting, utils


def remove_none_values(d: Dict):
    result = {}

    for key, item in d.items():
        if isinstance(item, dict):
            item = remove_none_values(item)

        if item:
            result[key] = item

    return result


class CromwellAPI:
    def __init__(
        self, server, version, headers={"Accept": "application/json"},
    ):
        self.server = server
        self.version = version
        self.headers = headers
        self.session = aiohttp.ClientSession()

    async def close(self):
        await self.session.close()

    async def _api_call(
        self, route, params={}, data={}, method="GET", url_override=None
    ):
        logger.debug(f"{method} {route}")
        url = urljoin(self.server, route).format(version=self.version)

        if isinstance(params, dict):
            params = remove_none_values(params)
        if isinstance(data, dict):
            data = remove_none_values(data)

        if url_override:
            url = url_override

        func = None
        if method == "GET":
            func = self.session.get
        elif method == "POST":
            func = self.session.post
        else:
            raise errors.report(
                "Unhandled API call type! This is an internal error with oliver.",
                fatal=True,
                exitcode=errors.ERROR_INTERNAL_ERROR,
                suggest_report=True,
            )

        kwargs = {"headers": self.headers}

        if params:
            kwargs["params"] = utils.dict_to_aiohttp_tuples(params)

        # format data as multipart-form
        if data:
            _data = aiohttp.FormData()
            for k, v in data.items():
                _data.add_field(k, v, filename=k, content_type="application/json")
            kwargs["data"] = _data

        try:
            response = await func(url, **kwargs)
        except aiohttp.client_exceptions.ClientConnectorError:
            await self.close()
            errors.report(
                message=f"Could not connect to {self.server}. Is the Cromwell server reachable?",
                fatal=True,
                exitcode=errors.ERROR_NO_RESPONSE,
            )
        status_code = response.status
        content = json.loads(await response.text())

        if not status_code // 200 == 1:
            message = f"Server returned status code {status_code}."
            fatal = content.get("status") == "fail"
            suggest = (
                not fatal
            )  # we have never experienced a case where the status wasn't "fail".
            # if such a case is encountered, we'd like to handle it here.
            if content.get("message"):
                message += f" Message: \"{content.get('message')}\""

            errors.report(
                message=message,
                fatal=fatal,
                exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
                suggest_report=suggest,
            )

        return status_code, content

    async def post_workflows(
        self,
        workflowSource=None,
        workflowUrl=None,
        workflowInputs={},
        workflowOptions={},
        labels={},
        url_override=None,
    ):
        "POST /api/workflows/{version}"

        if workflowSource is None and workflowUrl is None:
            errors.report(
                "Expected either 'workflowSource' or 'workflowUrl'!",
                fatal=True,
                exitcode=errors.ERROR_INVALID_INPUT,
            )

        data = {
            "workflowSource": workflowSource,
            "workflowUrl": workflowUrl,
            "workflowInputs": workflowInputs,
            "workflowOptions": workflowOptions,
            "labels": labels,
        }

        _, data = await self._api_call(
            "/api/workflows/{version}",
            method="POST",
            data=data,
            url_override=url_override,
        )
        return data

    async def post_workflows_batch(self):
        "POST /api/workflows/{version}/batch"
        raise NotImplementedError()

    async def get_workflows_labels(self):
        "GET /api/workflows/{version}/{id}/labels"
        raise NotImplementedError()

    async def patch_workflows_labels(self):
        "PATCH /api/workflows/{version}/{id}/labels"
        raise NotImplementedError()

    async def post_workflows_abort(self, workflow_id):
        "POST /api/workflows/{version}/{id}/abort"

        _, data = await self._api_call(
            f"/api/workflows/{{version}}/{workflow_id}/abort", method="POST"
        )
        return data

    async def post_workflows_release_hold(self):
        "POST /api/workflows/{version}/{id}/releaseHold"
        raise NotImplementedError()

    async def get_workflows_status(self):
        "GET /api/workflows/{version}/{id}/status"
        raise NotImplementedError()

    async def get_workflows_outputs(self, workflow_id):
        "GET /api/workflows/{version}/{id}/outputs"

        _, data = await self._api_call(
            f"/api/workflows/{{version}}/{workflow_id}/outputs"
        )
        return data

    async def get_workflows_logs(self, workflow_id):
        "POST /api/workflows/{version}/{id}/logs"

        _, data = await self._api_call(f"/api/workflows/{{version}}/{workflow_id}/logs")
        return data

    async def get_workflows_query(
        self,
        submission: datetime.datetime = None,
        start: datetime.datetime = None,
        end: datetime.datetime = None,
        statuses: List[str] = None,
        names: List[str] = None,
        ids: List[str] = None,
        labels: List[str] = None,
        labelors: List[str] = None,
        excludeLabelAnds: List[str] = None,
        excludeLabelOrs: List[str] = None,
        additionalQueryResultFields: List[str] = None,
        includeSubworkflows: bool = True,
    ) -> List:
        """GET /api/workflows/{version}/query
        
        Args:
            submission (datetime.datetime, optional): Returns only workflows with an equal or later submission time. Can be specified at most once. If both submission time and start date are specified, submission time should be before or equal to start date. Defaults to None.
            start (datetime.datetime, optional): Returns only workflows with an equal or later start datetime. Can be specified at most once. If both start and end date are specified, start date must be before or equal to end date. Defaults to None.
            end (datetime.datetime, optional): Returns only workflows with an equal or earlier end datetime. Can be specified at most once. If both start and end date are specified, start date must be before or equal to end date. Defaults to None.
            statuses (List[str], optional): Returns only workflows with the specified status. If specified multiple times, returns workflows in any of the specified statuses. Defaults to None.
            names (List[str], optional): Returns only workflows with the specified name. If specified multiple times, returns workflows with any of the specified names. Defaults to None.
            ids (List[str], optional): Returns only workflows with the specified workflow id. If specified multiple times, returns workflows with any of the specified workflow ids. Defaults to None.
            labels (List[str], optional): Returns workflows with the specified label keys. If specified multiple times, returns workflows with all of the specified label keys. Specify the label key and label value pair as separated with "label-key:label-value". Defaults to None.
            labelors (List[str], optional): Returns workflows with the specified label keys. If specified multiple times, returns workflows with any of the specified label keys. Specify the label key and label value pair as separated with "label-key:label-value". Defaults to None.
            excludeLabelAnd (List[str], optional): Excludes workflows with the specified label. If specified multiple times, excludes workflows with all of the specified label keys. Specify the label key and label value pair as separated with "label-key:label-value". Defaults to None.
            excludeLabelOr (List[str], optional): Excludes workflows with the specified label. If specified multiple times, excludes workflows with any of the specified label keys. Specify the label key and label value pair as separated with "label-key:label-value". Defaults to None.
            additionalQueryResultFields (List[str], optional): Currently only 'labels' is a valid value here. Use it to include a list of labels with each result. Defaults to None.
            includeSubworkflows (Boolean, optional): Include subworkflows in results. By default, it is taken as true. Defaults to True.
        
        Returns:
            List: All workflows that match the provided parameters.
        """

        params = {
            "submission": submission,
            "start": start,
            "end": end,
            "status": statuses,
            "name": names,
            "id": ids,
            "label": labels,
            "labelor": labelors,
            "excludeLabelAnd": excludeLabelAnds,
            "excludeLabelOr": excludeLabelOrs,
            "additionalQueryResultFields": additionalQueryResultFields,
            "includeSubworkflows": str(includeSubworkflows),
        }

        _, data = await self._api_call("/api/workflows/{version}/query", params=params)
        results = data.get("results")
        if not results:
            if not isinstance(results, list) or len(results) != 0:
                errors.report(
                    "Expected 'results' key in response!",
                    fatal=True,
                    exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
                )
            else:
                logger.warn("No results found in response!")

        return data["results"]

    async def post_workflows_query(self):
        "POST /api/workflows/{version}/query"
        raise NotImplementedError()

    async def get_workflows_timing(self):
        "GET /api/workflows/{version}/{id}/timing"
        raise NotImplementedError()

    async def get_workflows_metadata(
        self,
        id: str,
        includeKey: List[str] = None,
        excludeKey: List[str] = None,
        expandSubWorkflows: bool = False,
    ) -> Dict:
        """GET /api/workflows/{version}/{id}/metadata
        
        Args:
            id (str): Workflow ID to get metadata from.
            includeKey (List[str], optional): Keys to include in results. Defaults to None.
            excludeKey (List[str], optional): Keys to exclude in results. Defaults to None.
            expandSubWorkflows (bool, optional): Whether to expand subworkflows in results. Defaults to False.
        
        Returns:
            List: Metadata of specified workflow.
        """

        params = {
            "includeKey": includeKey,
            "excludeKey": excludeKey,
            "expandSubWorkflows": expandSubWorkflows,
        }

        _, data = await self._api_call(
            f"/api/workflows/{{version}}/{id}/metadata", params=params
        )
        return data

    async def get_workflows_call_caching_diff(self):
        "GET /api/workflows/{version}/callcaching/diff"
        raise NotImplementedError()

    async def get_workflows_backends(self):
        "GET /api/workflows/{version}/backends"
        raise NotImplementedError()
