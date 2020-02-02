from oliver.lib import api, config


def test_get_workflows():
    c = config.read_config()
    cromwell = api.CromwellAPI(
        server=c.get("cromwell_server"), version=c.get("cromwell_api_version")
    )
    results = cromwell.get_workflows_query()

    assert len(results) == 5
    for result in results:
        assert result.get("status") == "Succeeded"
