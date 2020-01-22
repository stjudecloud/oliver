import pendulum

from typing import List, Dict

from . import errors


def batch_workflows(workflows: List[Dict], batch_interval_mins: int = 5) -> List[Dict]:
    """Batches workflows based on their `submission` key and a time interval.
    
    In short, this is a simple method of batching jobs. Here, we start with the
    first job and consider it batch 0. We then iterate through each element in
    the list of jobs and compute the delta between this job's submission time
    and the last job's submission time. If the difference is `batch_interval_mins`
    or more, we increase the batch count by 1.
    
    Args:
        workflows (List[Dict]): list of workflows returned from Cromwell. Must
                                contain the `submission` key.
        batch_interval_mins (int, optional): interval to constitute a new batch 
                                             in minutes. Defaults to 5.
    
    Returns:
        List[Dict]: the `workflows` list that was passed in, but with a new 
                    `batch` key added to each entry denoting the computed batch.
    """

    batch_num = 0
    last_submission_time = None
    for i in range(len(workflows)):
        w = workflows[i]
        if "submission" not in w:
            errors.report(
                f"`submission` not in workflow, so we cannot batch.\n{w}",
                fatal=True,
                exitcode=errors.ERROR_INTERNAL_ERROR,
                suggest_report=True,
            )

        w = workflows[i]
        t = pendulum.parse(w["submission"])
        if last_submission_time:
            delta = (t - last_submission_time).total_minutes()
            if delta > batch_interval_mins:
                batch_num += 1
        workflows[i]["batch"] = batch_num
        last_submission_time = t

    return workflows
