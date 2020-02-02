#!/usr/bin/env bash


[[ $# -ne 2 ]] && >&2 echo "Usage: `basename $0` [CROMWELL_ENDPOINT] [WDL-WORKFLOW]" && exit 1

if ! which http &> /dev/null; then
  >&2 echo "httpie must be installed!"
  exit 1
fi

CROMWELL_ENDPOINT=$1; shift;
WDL_WORKFLOW=$1; shift;

for i in $(seq 1 5); do
    http -f POST \
      "${CROMWELL_ENDPOINT}/api/workflows/v1" \
      Accept:application/json \
      workflowSource@${WDL_WORKFLOW}
    echo ""
done