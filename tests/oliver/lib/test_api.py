import pytest

from oliver.lib import api, config


@pytest.mark.asyncio
async def test_get_workflows():
    c = config.read_config()
    cromwell = api.CromwellAPI(
        server="http://cromwell:8000", version="v1"
    )
    results = await cromwell.get_workflows_query()

    assert len(results) == 5
    for result in results:
        assert result.get("status") == "Succeeded"

    await cromwell.close()


@pytest.mark.asyncio
async def test_api_get():
    c = config.read_config()
    cromwell = api.CromwellAPI(
        server="http://httpbin:80", version="v1"
    )

    (code, response) = await cromwell._api_call(
        "/get", params={"includeSubworkflows": "true"}
    )

    assert code == 200
    assert response.get("args", {}).get("includeSubworkflows") == "true"

    await cromwell.close()


@pytest.mark.asyncio
async def test_api_post():
    c = config.read_config()
    cromwell = api.CromwellAPI(
        server="http://httpbin:80", version="v1"
    )

    data = {
        "workflowSource": None,
        "workflowUrl": "http://my-test-url/hello.wdl",
        "workflowInputs": "{'hello.text': 'Hello, world!'}",
        "workflowOptions": "{}",
        "labels": "{}",
    }

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
