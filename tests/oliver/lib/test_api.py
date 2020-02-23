import pytest

from oliver.lib import api


def test_none_values_with_dict():
    d = api.remove_none_values({"foo": "bar", "baz": {}})

    assert d == {"foo": "bar"}


@pytest.mark.asyncio
async def test_get_workflows():
    cromwell = api.CromwellAPI(server="http://cromwell:8000", version="v1")
    results = await cromwell.get_workflows_query()

    assert len(results) == 5
    for result in results:
        assert result.get("status") == "Succeeded"

    await cromwell.close()


@pytest.mark.asyncio
async def test_api_get():
    cromwell = api.CromwellAPI(server="http://httpbin:80", version="v1")

    # pylint: disable=W0212
    (code, response) = await cromwell._api_call(
        "/get", params={"includeSubworkflows": "true"}
    )

    assert code == 200
    assert response.get("args", {}).get("includeSubworkflows") == "true"

    await cromwell.close()


@pytest.mark.asyncio
async def test_api_post():
    cromwell = api.CromwellAPI(server="http://httpbin:80", version="v1")

    data = {
        "workflowSource": None,
        "workflowUrl": "http://my-test-url/hello.wdl",
        "workflowInputs": "{'hello.text': 'Hello, world!'}",
        "workflowOptions": "{}",
        "labels": "{}",
    }

    # pylint: disable=W0212
    (code, response) = await cromwell._api_call("/post", data=data, method="POST")

    assert code == 200
    assert response.get("files", {}).get("labels") == "{}"
    assert (
        response.get("files", {}).get("workflowInputs")
        == "{'hello.text': 'Hello, world!'}"
    )
    assert (
        response.get("files", {}).get("workflowUrl") == "http://my-test-url/hello.wdl"
    )
    assert response.get("files", {}).get("workflowOptions") == "{}"
    assert "workflowSource" not in response.get("files", {})

    await cromwell.close()


@pytest.mark.asyncio
async def test_errors_on_unknown_http_method():
    cromwell = api.CromwellAPI(server="http://httpbin:80", version="v1")

    # pylint: disable=W0212
    with pytest.raises(SystemExit):
        await cromwell._api_call("/bar", method="BAZ")

    await cromwell.close()


@pytest.mark.asyncio
async def test_errors_on_unreachable_host():
    cromwell = api.CromwellAPI(server="http://foo", version="v1")

    # pylint: disable=W0212
    with pytest.raises(SystemExit):
        await cromwell._api_call("/bar")

    await cromwell.close()


@pytest.mark.asyncio
async def test_errors_on_bad_response():
    cromwell = api.CromwellAPI(server="http://httpbin", version="v1")

    # pylint: disable=W0212
    with pytest.raises(SystemExit):
        await cromwell._api_call("/status/404")

    await cromwell.close()


@pytest.mark.asyncio
async def test_post_workflows_empty_params():
    cromwell = api.CromwellAPI(
        server="http://httpbin:80", version="v1", route_override="/post"
    )

    await cromwell.post_workflows(workflowUrl="https://foo/bar")
    await cromwell.close()


@pytest.mark.asyncio
async def test_errors_on_post_workflows_no_workflow_source():
    cromwell = api.CromwellAPI(server="http://httpbin", version="v1")

    with pytest.raises(SystemExit):
        await cromwell.post_workflows(workflowUrl=None, workflowSource=None)

    await cromwell.close()


@pytest.mark.asyncio
async def test_post_workflows_batch_not_implemented():
    with pytest.raises(NotImplementedError):
        cromwell = api.CromwellAPI(server="http://cromwell:8000", version="v1")
        await cromwell.post_workflows_batch()


@pytest.mark.asyncio
async def test_get_workflows_labels_not_implemented():
    with pytest.raises(NotImplementedError):
        cromwell = api.CromwellAPI(server="http://cromwell:8000", version="v1")
        await cromwell.get_workflows_labels()


@pytest.mark.asyncio
async def test_patch_workflows_labels_not_implemented():
    with pytest.raises(NotImplementedError):
        cromwell = api.CromwellAPI(server="http://cromwell:8000", version="v1")
        await cromwell.patch_workflows_labels()


@pytest.mark.asyncio
async def test_post_workflows_release_hold_not_implemented():
    with pytest.raises(NotImplementedError):
        cromwell = api.CromwellAPI(server="http://cromwell:8000", version="v1")
        await cromwell.post_workflows_release_hold()


@pytest.mark.asyncio
async def test_get_workflows_status_not_implemented():
    with pytest.raises(NotImplementedError):
        cromwell = api.CromwellAPI(server="http://cromwell:8000", version="v1")
        await cromwell.get_workflows_status()


@pytest.mark.asyncio
async def test_post_workflows_query_not_implemented():
    with pytest.raises(NotImplementedError):
        cromwell = api.CromwellAPI(server="http://cromwell:8000", version="v1")
        await cromwell.post_workflows_query()


@pytest.mark.asyncio
async def test_get_workflows_timing_not_implemented():
    with pytest.raises(NotImplementedError):
        cromwell = api.CromwellAPI(server="http://cromwell:8000", version="v1")
        await cromwell.get_workflows_timing()


@pytest.mark.asyncio
async def test_get_workflows_call_caching_diff_not_implemented():
    with pytest.raises(NotImplementedError):
        cromwell = api.CromwellAPI(server="http://cromwell:8000", version="v1")
        await cromwell.get_workflows_call_caching_diff()


@pytest.mark.asyncio
async def test_get_workflows_backends_not_implemented():
    with pytest.raises(NotImplementedError):
        cromwell = api.CromwellAPI(server="http://cromwell:8000", version="v1")
        await cromwell.get_workflows_backends()
