import datetime
from typing import Any, Dict, List, Optional, Union

import pendulum
from logzero import logger

from . import api, batch, constants


# pylint: disable=too-many-arguments,too-many-locals
async def get_workflows(
    cromwell: api.CromwellAPI,
    submission_time_hours_ago: Optional[int] = None,
    oliver_job_name: Optional[str] = None,
    oliver_job_group_name: Optional[str] = None,
    cromwell_workflow_uuid: Optional[str] = None,
    cromwell_workflow_name: Optional[str] = None,
    batches: Optional[Union[List[int], bool]] = None,
    batch_interval_mins: Optional[int] = 5,
    relative_batching: Optional[bool] = False,
    opt_into_reporting_running_jobs: bool = False,
    opt_into_reporting_aborted_jobs: bool = False,
    opt_into_reporting_failed_jobs: bool = False,
    opt_into_reporting_succeeded_jobs: bool = False,
) -> List[Dict[str, Any]]:
    """Retrieves a list of workflows and filter based on provided parameters.

    Re: `opt_into_reporting_XXXXXX_jobs`. Okay, so admittedly this is a weird
    way to structure these inputs, but I think it's a relatively straightforward
    implementation. The behavior we want is:

    (1) if the user doesn't specify any status on the command line, then default
    to posting `None` for the statuses parameter so we get everything (including
    statuses which may be added later in time and are not included here).
    (2) if the user _does_ specify any status on the command line, then we want
    to only show statuses they specify.

    Since these statuses are passed are arguments in argparse defaulting to
    False and set to True only when a user specifies the flag, we can achieve
    this by doing the following:

    - Pass in the True/False value for each flag denoting whether the user
      explicitly opted in for a given status.
    - If all of the statuses are `False`, then the user wants everything and
      `statuses` should be posted as None.
    - Otherwise, set `statuses` to a list of the statuses the user would like.

    Args:
        cromwell (api.CromwellAPI): cromwell api connected to the cromwell
        instance in question.

        submission_time_hours_ago (int, optional): if provided, will show jobs
        from a maximum of N hours ago.

        oliver_job_name (str, optional): filter by oliver job name of the
        workflow(s) in question.

        oliver_job_group_name (str, optional): filter by oliver group name of
        the workflow(s) in question.

        cromwell_workflow_uuid (str, optional): filter by Cromwell-assigned
        UUID of the workflow in question.

        cromwell_workflow_name (str, optional): filter by workflow (pipeline)
        name.

        batches(List[int], optional): split workflows into batches using
        and select only jobs in the specified batches. If `relative_batching`
        is True, this behavior changes to selecting "N batch ago".

        batch_interval_mins(int, optional): any two jobs separated by N
        minutes or more constitutes a new batch. Defaults to 5 minutes.

        relative_batching(bool): Calculate batches relative to the most recent
        batch (e.g. `0` is the most recent batch, `1` is the second most recent
        batch). Defaults to False.

        opt_into_reporting_running_jobs (bool, optional): Whether the user
        explicitly opted into seeing `Running` statuses. See the method's
        documentation for an explanation of how this works. Defaults to False.

        opt_into_reporting_aborted_jobs (bool, optional): Whether the user
        explicitly opted into seeing `Aborted` statuses. See the method's
        documentation for an explanation of how this works. Defaults to False.

        opt_into_reporting_failed_jobs (bool, optional): Whether the user
        explicitly opted into seeing `Failed` statuses. See the method's
        documentation for an explanation of how this works. Defaults to False.

        opt_into_reporting_succeeded_jobs (bool, optional): Whether the user
        explicitly opted into seeing `Succeeded` statuses. See the method's
        documentation for an explanation of how this works. Defaults to False.

    Returns:
        List[Dict]: a list of workflows returned from the api and filtered per
        the given parameters.
    """

    statuses = None  # none will show everything by default.

    if (
        opt_into_reporting_running_jobs
        or opt_into_reporting_aborted_jobs
        or opt_into_reporting_failed_jobs
        or opt_into_reporting_succeeded_jobs
    ):
        statuses = []
        if opt_into_reporting_running_jobs:
            statuses.append("Running")
        if opt_into_reporting_aborted_jobs:
            statuses.append("Aborted")
        if opt_into_reporting_failed_jobs:
            statuses.append("Failed")
        if opt_into_reporting_succeeded_jobs:
            statuses.append("Succeeded")

    labels = []
    if oliver_job_name:
        labels.append(f"{constants.OLIVER_JOB_NAME_KEY}:{oliver_job_name}")

    if oliver_job_group_name:
        labels.append(f"{constants.OLIVER_JOB_GROUP_KEY}:{oliver_job_group_name}")

    submission = None
    if isinstance(submission_time_hours_ago, int) and submission_time_hours_ago > 0:
        submission = (
            datetime.datetime.now()
            - datetime.timedelta(hours=submission_time_hours_ago)
        ).replace(microsecond=0).isoformat("T") + "Z"

    workflows = await cromwell.get_workflows_query(
        includeSubworkflows=False,
        labels=labels,
        ids=[cromwell_workflow_uuid] if cromwell_workflow_uuid else None,
        names=[cromwell_workflow_name] if cromwell_workflow_name else None,
        submission=submission,
    )

    workflows = sorted(
        workflows,
        key=lambda k: pendulum.parse(k.get("submission", "")).timestamp()
        if "submission" in k
        else 0,
    )

    if batches is not None:
        workflows = batch.get_workflow_batches(
            workflows,
            batches,
            batch_interval_mins=batch_interval_mins,
            relative=relative_batching,
        )

    if statuses:
        workflows = list(filter(lambda x: x["status"] in statuses, workflows))

    logger.info("Found %d eligible workflows given search criteria.", len(workflows))
    return workflows


async def get_outputs(
    cromwell: api.CromwellAPI, cromwell_workflow_uuid: str
) -> Dict[str, Any]:
    """Get the outputs from a workflow with the given uuid.

    Args:
        cromwell (api.CromwellAPI): cromwell api connected to the cromwell
        instance in question.

        cromwell_workflow_uuid (str, optional): Cromwell-assigned UUID
        of the workflow in question.
    """

    return await cromwell.get_workflows_outputs(cromwell_workflow_uuid)
