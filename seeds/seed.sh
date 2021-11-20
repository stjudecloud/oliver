#!/usr/bin/env bash
set -x

[[ $# -ne 2 ]] && echo "Usage: $(basename "$0") [CROMWELL_ENDPOINT] [WDL-WORKFLOW]" >&2 && exit 1

if ! which http &> /dev/null; then
    echo "httpie must be installed!" >&2
    exit 1
fi

CROMWELL_ENDPOINT=$1; shift;
WDL_WORKFLOW=$1; shift;

for _ in $(seq 1 5); do
    http -f POST \
        "${CROMWELL_ENDPOINT}/api/workflows/v1" \
        Accept:application/json \
        workflowSource@"${WDL_WORKFLOW}"
    echo ""
done
