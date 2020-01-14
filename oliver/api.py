def post_workflow():
    "POST /api/workflows/{version}"
    raise NotImplementedError()

def post_workflow_batch():
    "POST /api/workflows/{version}/batch"
    raise NotImplementedError()

def get_workflow_labels():
    "GET /api/workflows/{version}/{id}/labels"
    raise NotImplementedError()

def patch_workflow_labels():
    "PATCH /api/workflows/{version}/{id}/labels"
    raise NotImplementedError()

def post_workflow_abort():
    "POST /api/workflows/{version}/{id}/abort"
    raise NotImplementedError()

def post_workflow_release_hold():
    "POST /api/workflows/{version}/{id}/releaseHold"
    raise NotImplementedError()

def get_workflow_status():
    "GET /api/workflows/{version}/{id}/status"
    raise NotImplementedError()

def get_workflow_outputs():
    "GET /api/workflows/{version}/{id}/outputs"
    raise NotImplementedError()

def get_workflow_logs():
    "POST /api/workflows/{version}/{id}/logs"
    raise NotImplementedError()

def get_workflow_query():
    "GET /api/workflows/{version}/query"
    raise NotImplementedError()

def post_workflow_query():
    "POST /api/workflows/{version}/query"
    raise NotImplementedError()

def get_workflow_timing():
    "GET /api/workflows/{version}/{id}/timing"
    raise NotImplementedError()

def get_workflow_metadata():
    "GET /api/workflows/{version}/{id}/metadata"
    raise NotImplementedError()

def get_workflow_call_caching_diff():
    "GET /api/workflows/{version}/callcaching/diff"
    raise NotImplementedError()

def get_workflow_backends():
    "GET /api/workflows/{version}/backends"
    raise NotImplementedError()