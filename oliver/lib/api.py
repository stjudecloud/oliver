import datetime
import json
import os

from typing import Any, cast, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin
from logzero import logger

import aiohttp
from . import errors, utils

FILE_PARAMS = ["workflowSource", "workflowDependencies"]


def remove_none_values(d: Dict[str, Any]) -> Dict[str, Any]:
    result = {}

    for key, item in d.items():
        if isinstance(item, dict):
            item = remove_none_values(item)

        if item:
            result[key] = item

    return result


class CromwellAPI:
    def __init__(
        self,
        server: str,
        version: str,
        headers: Optional[Dict[str, str]] = None,
        route_override: Optional[str] = None,
    ):
        self.server = server
        self.version = version
        self.headers = headers or {"Accept": "application/json"}
        self.session = aiohttp.ClientSession()
        self.route_override = route_override

    async def close(self) -> None:
        await self.session.close()

    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    async def _api_call(
        self,
        route: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        method: str = "GET",
    ) -> Tuple[int, Dict[str, Any]]:
        # only used when testing
        if self.route_override:
            route = self.route_override

        logger.debug("%s %s", method, route)
        url = urljoin(self.server, route).format(version=self.version)

        if params is None:
            params = {}
        if data is None:
            data = {}

        if isinstance(params, dict):
            params = remove_none_values(params)
        if isinstance(data, dict):
            data = remove_none_values(data)

        params = remove_none_values(params)
        data = remove_none_values(data)

        func = None
        if method == "GET":
            func = self.session.get
        elif method == "POST":
            func = self.session.post
        else:
            errors.report(
                "Unhandled API call type! This is an internal error with oliver.",
                fatal=True,
                exitcode=errors.ERROR_INTERNAL_ERROR,
                suggest_report=True,
            )

        kwargs: Dict[str, Any] = {"headers": self.headers}

        if params:
            kwargs["params"] = utils.dict_to_aiohttp_tuples(params)

        # format data as multipart-form
        if data:
            _data = aiohttp.FormData()
            for k, v in data.items():
                if k in FILE_PARAMS:
                    filename = os.path.basename(v)
                    # pylint: disable=R1732
                    _data.add_field(k, open(v, "rb"), filename=filename)
                else:
                    _data.add_field(k, v, filename=k, content_type="application/json")
            kwargs["data"] = _data

        try:
            assert func is not None
            response = await func(url, **kwargs)
        except aiohttp.client_exceptions.ClientConnectorError:
            await self.close()
            errors.report(
                message=f"Could not connect to {self.server}. Is the Cromwell server reachable?",
                fatal=True,
                exitcode=errors.ERROR_NO_RESPONSE,
            )
        except aiohttp.client_exceptions.InvalidURL:
            await self.close()
            errors.report(
                message=f"Could not connect to {self.server}. Is the address correct?",
                fatal=True,
                exitcode=errors.ERROR_INVALID_INPUT,
            )
        status_code = response.status
        response_text = await response.text()
        content: Dict[str, Any] = {}
        try:
            if response_text:
                content = json.loads(response_text)
        # pylint: disable=broad-exception-caught
        except Exception:
            pass
        # pylint: enable=broad-exception-caught

        if not status_code // 200 == 1:
            message = f"Server returned status code {status_code}."
            if content:
                fatal = content.get("status") == "fail"
            else:
                fatal = True
            suggest = (
                not fatal
            )  # we have never experienced a case where the status wasn't "fail".
            # if such a case is encountered, we'd like to handle it here.
            if content and content.get("message"):
                message += f" Message: \"{content.get('message')}\""

            errors.report(
                message=message,
                fatal=fatal,
                exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
                suggest_report=suggest,
            )

        return status_code, content

    # pylint: disable=too-many-arguments
    async def post_workflows(
        self,
        workflowSource: Optional[str] = None,
        workflowUrl: Optional[str] = None,
        workflowInputs: Optional[Dict[str, str]] = None,
        workflowOptions: Optional[Dict[str, str]] = None,
        labels: Optional[Dict[str, str]] = None,
        workflowDependencies: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        "POST /api/workflows/{version}"

        if workflowInputs is None:
            workflowInputs = {}
        if workflowOptions is None:
            workflowOptions = {}
        if labels is None:
            labels = {}

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
            "workflowDependencies": workflowDependencies,
        }

        logger.debug("workflowSource: %s", workflowSource)
        logger.debug("workflowUrl: %s", workflowUrl)
        logger.debug("workflowInputs: %s", workflowInputs)
        logger.debug("workflowOptions: %s", workflowOptions)
        logger.debug("labels: %s", labels)
        logger.debug("workflowDependencies: %s", workflowDependencies)

        _, data = await self._api_call(
            "api/workflows/{version}",
            method="POST",
            data=data,
        )
        return data

    async def post_workflows_batch(self) -> None:
        "POST /api/workflows/{version}/batch"
        raise NotImplementedError()

    async def get_workflows_labels(self) -> None:
        "GET /api/workflows/{version}/{id}/labels"
        raise NotImplementedError()

    async def patch_workflows_labels(self) -> None:
        "PATCH /api/workflows/{version}/{id}/labels"
        raise NotImplementedError()

    async def post_workflows_abort(self, workflow_id: str) -> Dict[str, Any]:
        "POST /api/workflows/{version}/{id}/abort"

        _, data = await self._api_call(
            f"api/workflows/{{version}}/{workflow_id}/abort", method="POST"
        )
        return data

    async def post_workflows_release_hold(self) -> None:
        "POST /api/workflows/{version}/{id}/releaseHold"
        raise NotImplementedError()

    async def get_workflows_status(self) -> None:
        "GET /api/workflows/{version}/{id}/status"
        raise NotImplementedError()

    async def get_workflows_outputs(self, workflow_id: str) -> Dict[str, Any]:
        "GET /api/workflows/{version}/{id}/outputs"

        _, data = await self._api_call(
            f"api/workflows/{{version}}/{workflow_id}/outputs"
        )
        return data

    async def get_workflows_logs(self, workflow_id: str) -> Dict[str, Any]:
        "POST /api/workflows/{version}/{id}/logs"

        _, data = await self._api_call(f"api/workflows/{{version}}/{workflow_id}/logs")
        return data

    async def get_workflows_query(
        self,
        submission: Optional[Union[datetime.datetime, str]] = None,
        start: Optional[datetime.datetime] = None,
        end: Optional[datetime.datetime] = None,
        statuses: Optional[List[str]] = None,
        names: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        labelors: Optional[List[str]] = None,
        excludeLabelAnds: Optional[List[str]] = None,
        excludeLabelOrs: Optional[List[str]] = None,
        additionalQueryResultFields: Optional[List[str]] = None,
        includeSubworkflows: Optional[bool] = True,
    ) -> List[Dict[str, Any]]:
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

        _, data = await self._api_call("api/workflows/{version}/query", params=params)
        results = cast(List[Dict[str, Any]], data.get("results"))
        if not results:
            if not isinstance(results, list):
                errors.report(
                    "Expected 'results' key in response!",
                    fatal=True,
                    exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
                )
            else:
                errors.report(
                    "No results found in response!",
                    fatal=True,
                    exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
                )

        return results

    async def post_workflows_query(self) -> None:
        "POST /api/workflows/{version}/query"
        raise NotImplementedError()

    async def get_workflows_timing(self) -> None:
        "GET /api/workflows/{version}/{id}/timing"
        raise NotImplementedError()

    async def get_workflows_metadata(
        self,
        # pylint: disable=redefined-builtin
        id: str,
        includeKey: Optional[List[str]] = None,
        excludeKey: Optional[List[str]] = None,
        expandSubWorkflows: Optional[bool] = False,
    ) -> Dict[str, Any]:
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
            f"api/workflows/{{version}}/{id}/metadata", params=params
        )
        return data

    async def get_workflows_call_caching_diff(self) -> None:
        "GET /api/workflows/{version}/callcaching/diff"
        raise NotImplementedError()

    async def get_workflows_backends(self) -> None:
        "GET /api/workflows/{version}/backends"
        raise NotImplementedError()
