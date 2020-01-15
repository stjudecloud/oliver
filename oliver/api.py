def post_workflows():
    "POST /api/workflows/{version}"
    raise NotImplementedError()

def post_workflows_batch():
    "POST /api/workflows/{version}/batch"
    raise NotImplementedError()

def get_workflows_labels():
    "GET /api/workflows/{version}/{id}/labels"
    raise NotImplementedError()

def patch_workflows_labels():
    "PATCH /api/workflows/{version}/{id}/labels"
    raise NotImplementedError()

def post_workflows_abort():
    "POST /api/workflows/{version}/{id}/abort"
    raise NotImplementedError()

def post_workflows_release_hold():
    "POST /api/workflows/{version}/{id}/releaseHold"
    raise NotImplementedError()

def get_workflows_status():
    "GET /api/workflows/{version}/{id}/status"
    raise NotImplementedError()

def get_workflows_outputs():
    "GET /api/workflows/{version}/{id}/outputs"
    raise NotImplementedError()

def get_workflows_logs():
    "POST /api/workflows/{version}/{id}/logs"
    raise NotImplementedError()

def get_workflows_query():
    "GET /api/workflows/{version}/query"
    raise NotImplementedError()

def post_workflows_query():
    "POST /api/workflows/{version}/query"
    raise NotImplementedError()

def get_workflows_timing():
    "GET /api/workflows/{version}/{id}/timing"
    raise NotImplementedError()

def get_workflows_metadata():
    "GET /api/workflows/{version}/{id}/metadata"
    raise NotImplementedError()

def get_workflows_call_caching_diff():
    "GET /api/workflows/{version}/callcaching/diff"
    raise NotImplementedError()

def get_workflows_backends():
    "GET /api/workflows/{version}/backends"
    raise NotImplementedError()