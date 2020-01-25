import boto3
import json
import os

from typing import Dict

from ... import errors


def write_log(batch_client, logs_client, job, output_directory):
    job_id = job.get("jobId")
    job_name = job.get("jobName")

    jobdir = os.path.join(output_directory, job_name, job_id)
    if not os.path.isdir(jobdir):
        os.makedirs(jobdir)

    resp = batch_client.describe_jobs(jobs=[job_id])
    jobs = resp.get("jobs")
    if not jobs:
        errors.report(
            "Could not parse AWS API response for describing a batch job!",
            fatal=True,
            exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
        )

    # status
    with open(os.path.join(jobdir, "summary.txt"), "w") as f:
        f.write(f"Started At: {jobs[0].get('startedAt')}")
        f.write(f"Stopped At: {jobs[0].get('stoppedAt')}")
        f.write(f"Status Reason: {jobs[0].get('statusReason')}")

    # logs
    logstream = jobs[0].get("container").get("logStreamName")

    try:
        logs = logs_client.get_log_events(
            logGroupName="/aws/batch/job", logStreamName=logstream
        )
        with open(os.path.join(jobdir, "cloudwatch-logs.txt"), "w") as f:
            for event in logs.get("events"):
                f.write(event.get("message") + "\n")
    except:
        errors.report(
            message=f"Could not find logstream reporting by describe-jobs: {logstream}! Skipping.",
            fatal=False,
        )


def failures(args: Dict):
    batch_client = boto3.client("batch")
    logs_client = boto3.client("logs")

    paginator = batch_client.get_paginator("list_jobs")
    for result in paginator.paginate(
        jobQueue=args.get("queue"), jobStatus=args.get("status")
    ):
        resp = result.get("jobSummaryList")
        if not resp:
            errors.report(
                "Could not parse AWS API response for listing batch jobs!",
                fatal=True,
                exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
            )

        for job in resp:
            write_log(batch_client, logs_client, job, args.get("output_folder"))
