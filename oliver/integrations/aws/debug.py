import os

from typing import Any, cast, Dict, List, Optional, Tuple, Union
from functools import lru_cache
from logzero import logger

import pendulum
import boto3
from mypy_boto3_batch import BatchClient
from mypy_boto3_batch.type_defs import DescribeJobsResponseTypeDef
from mypy_boto3_logs import CloudWatchLogsClient

from ...lib import api, errors, reporting, workflows as _workflows


@lru_cache(maxsize=4096)
def describe_batch_job(
    batch_client: BatchClient, job_id: str
) -> DescribeJobsResponseTypeDef:
    return batch_client.describe_jobs(jobs=[job_id])


# pylint: disable=too-many-locals
def get_aws_batch_jobs(
    args: Dict[str, Any],
    batch_client: BatchClient,
    start_time_filter: Union[int, float],
    end_time_filter: Union[int, float],
) -> List[Dict[str, Any]]:
    paginator = batch_client.get_paginator("list_jobs")
    results = []

    for status in args.get("status", []):
        for item in paginator.paginate(
            jobQueue=args.get("queue", ""), jobStatus=status
        ):
            resp = item.get("jobSummaryList", [])
            if not resp:
                errors.report(
                    "Could not parse AWS API response for listing batch jobs!",
                    fatal=True,
                    exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
                )

            for job in resp:
                created = job.get("createdAt")
                start = job.get("startedAt")
                end = job.get("stoppedAt")

                new_job = {
                    "name": job.get("jobName", ""),
                    "id": job.get("jobId", ""),
                    "reason": job.get("statusReason", ""),
                    "containerExitCode": job.get("container", {}).get("exitCode", ""),
                    "created": round(created / 1000) if created else None,
                    "start": round(start / 1000) if start else None,
                    "end": round(end / 1000) if end else None,
                }

                new_job["createdReadable"] = (
                    reporting.localize_date_from_timestamp(
                        cast(int, new_job["created"])
                    )
                    if created and new_job.get("created") is not None
                    else None
                )
                new_job["startReadable"] = (
                    reporting.localize_date_from_timestamp(cast(int, new_job["start"]))
                    if start and new_job.get("start") is not None
                    else None
                )
                new_job["endReadable"] = (
                    reporting.localize_date_from_timestamp(cast(int, new_job["end"]))
                    if end and new_job.get("end") is not None
                    else None
                )

                this_jobs_start_time = cast(
                    int,
                    (
                        new_job["start"]
                        if new_job.get("start")
                        else new_job.get("created")
                    ),
                )
                this_jobs_end_time = cast(
                    int, (new_job["end"] if new_job.get("end") else pendulum.now())
                )

                # Successful jobs can exit container. We don't care about successful jobs
                # that don't fall into this category.
                if status == "SUCCEEDED" and "task exited" not in cast(
                    str, new_job.get("reason", "")
                ):
                    continue

                if start_time_filter > this_jobs_start_time:
                    logger.debug(
                        "Job disqualified because %s > %s.",
                        reporting.localize_date_from_timestamp(start_time_filter),
                        reporting.localize_date_from_timestamp(this_jobs_start_time),
                    )
                elif end_time_filter < this_jobs_end_time:
                    logger.debug(
                        "Job disqualified because %s < %s.",
                        reporting.localize_date_from_timestamp(end_time_filter),
                        reporting.localize_date_from_timestamp(this_jobs_end_time),
                    )
                else:
                    results.append(new_job)

    return list(sorted(results, key=lambda x: x["start"] if x.get("start") else 0))  # type: ignore


# pylint: disable=too-many-branches
async def get_calls_and_times_for_workflows(
    args: Dict[str, Any], cromwell: api.CromwellAPI
) -> Tuple[List[Dict[str, Any]], Union[int, float], Union[int, float]]:
    batches = None
    relative = None

    if args.get("batches_relative"):
        batches = args.get("batches_relative")
        relative = True
    elif args.get("batches_absolute"):
        batches = args.get("batches_absolute")
        relative = False
    else:
        errors.report(
            "Neither relative nor absolute batches was given!",
            fatal=True,
            exitcode=errors.ERROR_INVALID_INPUT,
        )

    workflows = await _workflows.get_workflows(
        cromwell,
        submission_time_hours_ago=args.get("submission_time"),
        batches=batches,
        relative_batching=relative,
        opt_into_reporting_aborted_jobs=True,
        opt_into_reporting_failed_jobs=True,
    )

    start_time_to_filter_by = None
    end_time_to_filter_by = None
    metadatas = {
        w["id"]: await cromwell.get_workflows_metadata(w["id"]) for w in workflows
    }

    failed_calls = []

    for w in workflows:
        # (1) aggregate all individual failed calls into `failed_calls`.
        for call_name, cur_call in (
            metadatas.get(w.get("id", ""), {}).get("calls", []).items()
        ):
            for cur_file in [
                cur_file
                for cur_file in cur_call
                if cur_file.get("executionStatus") == "Failed"
            ]:
                failed_call = {
                    "id": cur_file.get("jobId"),
                    "name": call_name.split(".")[-1],
                    "start": pendulum.parse(cur_file.get("start")).timestamp(),
                    "end": pendulum.parse(cur_file.get("end")).timestamp(),
                    "workflow_id": w.get("id"),
                }
                if failed_call.get("start") is not None:
                    failed_call[
                        "startReadable"
                    ] = reporting.localize_date_from_timestamp(
                        cast(int, failed_call.get("start"))
                    )
                if failed_call.get("end") is not None:
                    failed_call["endReadable"] = reporting.localize_date_from_timestamp(
                        cast(int, failed_call.get("end"))
                    )
                failed_calls.append(failed_call)

        # (2) compute earliest start time and latest end time to know what time ranges
        #     to query AWS batch for.
        workflows_start_time = w.get("start")
        workflows_end_time = w.get("end")

        if workflows_start_time:
            workflows_start_time = pendulum.parse(workflows_start_time)
            if (
                not start_time_to_filter_by
                or workflows_start_time < start_time_to_filter_by
            ):
                start_time_to_filter_by = workflows_start_time

        if workflows_end_time:
            workflows_end_time = pendulum.parse(workflows_end_time)
            if not workflows_end_time:
                # if 'end' doesn't exist, the job is still running, so the
                # end time should be considered up until the present.
                end_time_to_filter_by = pendulum.now()
            elif (
                not end_time_to_filter_by or workflows_end_time > end_time_to_filter_by
            ):
                end_time_to_filter_by = workflows_end_time

    if start_time_to_filter_by is None or end_time_to_filter_by is None:
        errors.report(
            "Unexpected values for workflow start or end time!",
            fatal=True,
            exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
        )

    assert start_time_to_filter_by is not None and end_time_to_filter_by is not None

    return (
        failed_calls,
        start_time_to_filter_by.timestamp(),
        end_time_to_filter_by.timestamp(),
    )


def write_log(
    batch_client: BatchClient,
    logs_client: CloudWatchLogsClient,
    cur_call: Dict[str, Any],
    output_directory: str,
    candidate_batch_jobs: Optional[List[Dict[str, Any]]] = None,
) -> None:
    if candidate_batch_jobs is None:
        candidate_batch_jobs = []

    workflow_id = cur_call.get("workflow_id", "")
    call_name = cur_call.get("name", "")

    calldir = os.path.join(output_directory, workflow_id, call_name)
    if not os.path.isdir(calldir):
        os.makedirs(calldir)

    # summary
    with open(
        os.path.join(calldir, "summary.txt"), mode="w", encoding="utf-8"
    ) as cur_file:
        cur_file.write("== Cromwell ==\n\n")
        for k, v in cur_call.items():
            cur_file.write(f"{k.capitalize()}: {v}\n")

    for batch_job in candidate_batch_jobs:
        logger.info("Writing info for %s.", batch_job.get("id"))
        batchdir = os.path.join(calldir, "batch-job-" + batch_job.get("id", ""))
        if not os.path.isdir(batchdir):
            os.makedirs(batchdir)

        # summary
        with open(
            os.path.join(batchdir, "summary.txt"), mode="w", encoding="utf-8"
        ) as cur_file:
            cur_file.write("== AWS batch ==\n\n")
            for k, v in batch_job.items():
                cur_file.write(f"{k.capitalize()}: {v}\n")

        # logs
        resp = describe_batch_job(batch_client, batch_job.get("id"))
        jobs = resp.get("jobs", [])
        if not jobs:
            errors.report(
                "Could not parse AWS API response for describing a batch job!",
                fatal=True,
                exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
            )
        assert len(jobs) == 1
        logstream = jobs[0].get("container", {}).get("logStreamName", "")

        with open(
            os.path.join(batchdir, "cloudwatch-logs.txt"), mode="w", encoding="utf-8"
        ) as cur_file:
            success = False

            for logstream_name in [logstream, logstream + "-proxy"]:
                if success:
                    break

                try:
                    logs = logs_client.get_log_events(
                        logGroupName="/aws/batch/job", logStreamName=logstream_name
                    )
                    for event in logs.get("events", []):
                        cur_file.write(event.get("message", "") + "\n")
                    success = True
                # pylint: disable=broad-exception-caught
                except Exception:
                    pass
                # pylint: enable=broad-exception-caught

            if not success:
                cur_file.write("Could not retrive logs!\n")
                errors.report(
                    message=f"Could not find logstream reporting by describe-jobs: {logstream}! Skipping.",
                    fatal=False,
                )


async def call(args: Dict[str, Any], cromwell: api.CromwellAPI) -> None:
    batch_client: BatchClient = boto3.client("batch")
    logs_client: CloudWatchLogsClient = boto3.client("logs")

    (
        failed_calls,
        start_time_filter,
        end_time_filter,
    ) = await get_calls_and_times_for_workflows(args, cromwell)

    logger.info(
        "Attempting to match up %s failed calls with associated AWS logs.",
        len(failed_calls),
    )
    for cur_call in failed_calls:
        logger.debug(
            "  [*] %s (%s -> %s)",
            cur_call.get("name"),
            cur_call.get("startReadable"),
            cur_call.get("endReadable"),
        )
    logger.info(
        "Searching from %s -> %s.",
        reporting.localize_date_from_timestamp(start_time_filter),
        reporting.localize_date_from_timestamp(end_time_filter),
    )
    aws_batch_jobs = get_aws_batch_jobs(
        args, batch_client, start_time_filter, end_time_filter
    )

    logger.info("Found %s matching AWS batch jobs.", len(aws_batch_jobs))

    for job in aws_batch_jobs:
        logger.debug(
            "  [*] %s-%s (%s -> %s)",
            job.get("name"),
            job.get("id"),
            job.get("startReadable"),
            job.get("endReadable"),
        )

    for cur_call in failed_calls:
        candidate_batch_jobs = []

        call_name = cur_call.get("name", "")
        easy_call_identifier = (
            call_name.split("_")[0] if "_" in call_name else call_name
        )
        for batch_job in [
            j for j in aws_batch_jobs if easy_call_identifier in j.get("name", "")
        ]:
            # created at for the batch job is a better indicator than the start time because
            # once Cromwell submits the job (start time for Cromwell), the job may pend in AWS batch
            dist = abs(cur_call.get("start", 0) - batch_job.get("created", 0))
            if dist < 300:
                candidate_batch_jobs.append(batch_job)

        if candidate_batch_jobs:
            logger.debug(
                "Found %s candidate batch jobs for %s/%s.",
                len(candidate_batch_jobs),
                cur_call.get("workflow_id"),
                cur_call.get("name"),
            )

            write_log(
                batch_client,
                logs_client,
                cur_call,
                args.get("output_folder", ""),
                candidate_batch_jobs=candidate_batch_jobs,
            )
