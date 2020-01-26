import pendulum

from logzero import logger
from typing import Dict, List, Union

from . import errors


def get_workflow_batches(
    workflows: List[dict],
    batches: Union[int, List[int]],
    batch_interval_mins: int = 5,
    relative: bool = False,
):
    """Returns all workflows where the derived batch number is included in `batches`.
    
    args:
        workflows (List[dict]): list of workflows returned from cromwell. must
                                contain the `submission` key.
        batches(Union[bool, int, List[int]]): batches to be returned. if `True`, returns all batches. 
                                        if a single integer, returns a single batch. if a list of integers,
                                        batches that match the specified numbers. 
        batch_interval_mins (int, optional): interval to constitute a new batch 
                                             in minutes. defaults to 5.
        relative(bool): if True, batches will be considered as "N batches ago" (e.g.
                        `0` will return the most recent batch, `1` will return the second
                        most recent batch).
    returns:
        List[dict]: the `workflows` filtered by batch number.
    """

    if not isinstance(batches, bool) and isinstance(batches, int):
        batches = [batches]

    _workflows, _max_batch_num = batch_workflows(
        workflows, batch_interval_mins=batch_interval_mins
    )
    _batches = batches

    if relative:
        _batches = [_max_batch_num - b for b in _batches]
        if any([b < 0 for b in _batches]):
            errors.report(
                message="One of the batch numbers given was higher than the largest batch number, so it does not exist!",
                fatal=True,
                exitcode=errors.ERROR_INVALID_INPUT,
            )

    if isinstance(batches, bool) and batches == True:
        logger.info("Targetting all batches.")
        return _workflows
    else:
        logger.info(
            f"Targetting all jobs in batch(es): {', '.join([str(b) for b in _batches])} (original={', '.join([str(b) for b in batches])}, relative={relative})."
        )
        return list(filter(lambda w: w.get("batch") in _batches, _workflows))


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
        List[Dict], int: The first returned value is the `workflows` list that was 
                         passed in, but with a new `batch` key added to each entry 
                         denoting the computed batch. The second returned value is the
                         maximum batch number.
    """

    batch_num = 0
    last_submission_time = None
    for i in range(len(workflows)):
        w = workflows[i]
        submission = w.get("submission")
        if not submission:
            errors.report(
                f"`submission` not in workflow, so we cannot batch.\n{w}",
                fatal=True,
                exitcode=errors.ERROR_INTERNAL_ERROR,
                suggest_report=True,
            )

        t = pendulum.parse(submission)
        if last_submission_time:
            delta = (t - last_submission_time).total_minutes()
            if delta > batch_interval_mins:
                batch_num += 1
        workflows[i]["batch"] = batch_num
        last_submission_time = t

    return workflows, batch_num
