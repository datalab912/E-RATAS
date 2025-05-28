import random
from redis import Redis
from requests import request
from rq import Queue, get_current_job

from log.log import Log

logger = Log("sample_job", "sample_job.log")


def sample_job_that_run_for_10_seconds(input_str: str):
    import time

    current_job = get_current_job()

    logger.info(f"Starting job with input: {input_str}, job_id: {current_job.id}")

    time.sleep(10)

    logger.info(f"Job completed with input: {input_str}, job_id: {current_job.id}")
    random_next_job_str = random.choice(["job1", "job2", "job3"])
    request(
        "POST",
        "http://127.0.0.1:6000/software/act_webhook",
        data={"input_str": random_next_job_str},
    )
    return "This is a sample job that runs for 10 seconds"


def enqueue_sample_job(input_str: str):
    redis_conn = Redis()
    q = Queue(connection=redis_conn)  # no args implies the default queue

    q.enqueue(
        sample_job_that_run_for_10_seconds,
        input_str,
    )
    logger.info(f"Sample job enqueued with input: {input_str}")
    return "Sample job enqueued"
