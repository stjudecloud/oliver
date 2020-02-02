import boto3
import datetime
import json
import os
import pendulum
import sys

from logzero import logger
from typing import Dict

from ...lib import api, errors, reporting, workflows as _workflows


def get_aws_batch_jobs(args, batch_client, start_time_filter, end_time_filter):
    paginator = batch_client.get_paginator("list_jobs")
    results = []

    for status in args.get("status"):
        for result in paginator.paginate(jobQueue=args.get("queue"), jobStatus=status):
            resp = result.get("jobSummaryList")
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
                    "name": job.get("jobName"),
                    "id": job.get("jobId"),
                    "reason": job.get("statusReason"),
                    "containerExitCode": job.get("container").get("exitCode"),
                    "created": round(created / 1000) if created else None,
                    "start": round(start / 1000) if start else None,
                    "end": round(end / 1000) if end else None,
                }

                new_job["createdReadable"] = (
                    reporting.localize_date_from_timestamp(new_job.get("created"))
                    if created
                    else None
                )
                new_job["startReadable"] = (
                    reporting.localize_date_from_timestamp(new_job.get("start"))
                    if start
                    else None
                )
                new_job["endReadable"] = (
                    reporting.localize_date_from_timestamp(new_job.get("end"))
                    if end
                    else None
                )

                this_jobs_start_time = (
                    new_job.get("start")
                    if new_job.get("start")
                    else new_job.get("created")
                )
                this_jobs_end_time = (
                    new_job.get("end") if new_job.get("end") else pendulum.now()
                )

                # Successful jobs can exit container. We don't care about successful jobs
                # that don't fall into this category.
                if status == "SUCCEEDED" and "task exited" not in new_job.get("reason"):
                    continue

                if start_time_filter > this_jobs_start_time:
                    logger.debug(
                        f"Job disqualified because {reporting.localize_date_from_timestamp(start_time_filter)} > {reporting.localize_date_from_timestamp(this_jobs_start_time)}."
                    )
                elif end_time_filter < this_jobs_end_time:
                    logger.debug(
                        f"Job disqualified because {reporting.localize_date_from_timestamp(end_time_filter)} < {reporting.localize_date_from_timestamp(this_jobs_end_time)}."
                    )
                else:
                    results.append(new_job)

        return list(sorted(results, key=lambda x: x["start"] if x.get("start") else 0))


async def get_calls_and_times_for_workflows(args, cromwell):
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
        for call_name, call in metadatas.get(w.get("id")).get("calls").items():
            for f in [f for f in call if f.get("executionStatus") == "Failed"]:
                failed_call = {
                    "id": f.get("jobId"),
                    "name": call_name.split(".")[-1],
                    "start": pendulum.parse(f.get("start")).timestamp(),
                    "end": pendulum.parse(f.get("end")).timestamp(),
                    "workflow_id": w.get("id"),
                }
                failed_call["startReadable"] = reporting.localize_date_from_timestamp(
                    failed_call.get("start")
                )
                failed_call["endReadable"] = reporting.localize_date_from_timestamp(
                    failed_call.get("end")
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

    return (
        failed_calls,
        start_time_to_filter_by.timestamp(),
        end_time_to_filter_by.timestamp(),
    )


def write_log(
    batch_client, logs_client, call, output_directory, candidate_batch_jobs=[]
):
    workflow_id = call.get("workflow_id")
    call_name = call.get("name")

    calldir = os.path.join(output_directory, workflow_id, call_name)
    if not os.path.isdir(calldir):
        os.makedirs(calldir)

    # summary
    with open(os.path.join(calldir, "summary.txt"), "w") as f:
        f.write("== Cromwell ==\n\n")
        f.write(f"Created at: {call.get('createdReadable')} ({call.get('created')}).\n")
        f.write(f"Started at: {call.get('startReadable')} ({call.get('start')}).\n")
        f.write(f"Stopped at: {call.get('stopReadable')} ({call.get('stop')}).\n")
        f.write(f"Workflow ID: {call.get('id')}.\n")

    for batch_job in candidate_batch_jobs:
        batchdir = os.path.join(calldir, "batch-job-" + batch_job.get("id"))
        if not os.path.isdir(batchdir):
            os.makedirs(batchdir)

        # summary
        with open(os.path.join(batchdir, "summary.txt"), "w") as f:
            f.write("== AWS batch ==\n\n")
            f.write(
                f"Created at: {batch_job.get('createdReadable')} ({batch_job.get('created')}).\n"
            )
            f.write(
                f"Started at: {batch_job.get('startReadable')} ({batch_job.get('start')}).\n"
            )
            f.write(
                f"Stopped at: {batch_job.get('stopReadable')} ({batch_job.get('stop')}).\n"
            )
            f.write(f"Status Reason: {batch_job.get('reason')}\n")

        # logs
        resp = batch_client.describe_jobs(jobs=[batch_job.get("id")])
        jobs = resp.get("jobs")
        if not jobs:
            errors.report(
                "Could not parse AWS API response for describing a batch job!",
                fatal=True,
                exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
            )
        logstream = jobs[0].get("container").get("logStreamName")

        with open(os.path.join(batchdir, "cloudwatch-logs.txt"), "w") as f:
            try:
                logs = logs_client.get_log_events(
                    logGroupName="/aws/batch/job", logStreamName=logstream
                )
                for event in logs.get("events"):
                    f.write(event.get("message") + "\n")
            except:
                f.write("Could not retrive logs!\n")
                errors.report(
                    message=f"Could not find logstream reporting by describe-jobs: {logstream}! Skipping.",
                    fatal=False,
                )


async def failures(args: Dict, cromwell: api.CromwellAPI):
    batch_client = boto3.client("batch")
    logs_client = boto3.client("logs")

    (
        failed_calls,
        start_time_filter,
        end_time_filter,
    ) = await get_calls_and_times_for_workflows(args, cromwell)
    logger.debug("")
    logger.debug("== Calls to match ==")
    for call in failed_calls:
        logger.debug(
            f"{call.get('name')}\t{call.get('startReadable')}\t{call.get('endReadable')}"
        )

    aws_batch_jobs = get_aws_batch_jobs(
        args, batch_client, start_time_filter, end_time_filter
    )
    logger.debug("")
    logger.debug("== Candidate AWS batch jobs ==")
    for job in aws_batch_jobs:
        logger.debug(
            f"{job.get('id')}\t{job.get('name')}\t{job.get('startReadable')}\t{job.get('endReadable')}"
        )

    for call in failed_calls:
        candidate_batch_jobs = []

        easy_call_identifier = (
            call.get("name").split("_")[0]
            if "_" in call.get("name")
            else call.get("name")
        )
        for batch_job in [
            j for j in aws_batch_jobs if easy_call_identifier in j.get("name")
        ]:
            # created at for the batch job is a better indicator than the start time because
            # once Cromwell submits the job (start time for Cromwell), the job may pend in AWS batch
            dist = abs(call.get("start") - batch_job.get("created"))
            if dist < 300:
                candidate_batch_jobs.append(batch_job)

        if candidate_batch_jobs:
            logger.debug(
                f"Found {len(candidate_batch_jobs)} candidate batch jobs for {call.get('workflow_id')}/{call.get('name')}."
            )

            write_log(
                batch_client,
                logs_client,
                call,
                args.get("output_folder"),
                candidate_batch_jobs=candidate_batch_jobs,
            )
