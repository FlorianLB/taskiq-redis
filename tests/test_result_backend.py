import asyncio
import uuid

import pytest
from taskiq import TaskiqResult

from taskiq_redis import RedisAsyncClusterResultBackend, RedisAsyncResultBackend
from taskiq_redis.exceptions import ResultIsMissingError


@pytest.mark.anyio
async def test_set_result_success(redis_url: str) -> None:
    """
    Tests that results can be set without errors.

    :param redis_url: redis URL.
    """
    result_backend = RedisAsyncResultBackend(  # type: ignore
        redis_url=redis_url,
    )
    task_id = uuid.uuid4().hex
    result: "TaskiqResult[int]" = TaskiqResult(
        is_err=True,
        log="My Log",
        return_value=11,
        execution_time=112.2,
    )
    await result_backend.set_result(
        task_id=task_id,
        result=result,
    )

    fetched_result = await result_backend.get_result(
        task_id=task_id,
        with_logs=True,
    )
    assert fetched_result.log == "My Log"
    assert fetched_result.return_value == 11
    assert fetched_result.execution_time == 112.2
    assert fetched_result.is_err
    await result_backend.shutdown()


@pytest.mark.anyio
async def test_fetch_without_logs(redis_url: str) -> None:
    """
    Check if fetching value without logs works fine.

    :param redis_url: redis URL.
    """
    result_backend = RedisAsyncResultBackend(  # type: ignore
        redis_url=redis_url,
    )
    task_id = uuid.uuid4().hex
    result: "TaskiqResult[int]" = TaskiqResult(
        is_err=True,
        log="My Log",
        return_value=11,
        execution_time=112.2,
    )
    await result_backend.set_result(
        task_id=task_id,
        result=result,
    )

    fetched_result = await result_backend.get_result(
        task_id=task_id,
        with_logs=False,
    )
    assert fetched_result.log is None
    assert fetched_result.return_value == 11
    assert fetched_result.execution_time == 112.2
    assert fetched_result.is_err
    await result_backend.shutdown()


@pytest.mark.anyio
async def test_remove_results_after_reading(redis_url: str) -> None:
    """
    Check if removing results after reading works fine.

    :param redis_url: redis URL.
    """
    result_backend = RedisAsyncResultBackend(  # type: ignore
        redis_url=redis_url,
        keep_results=False,
    )
    task_id = uuid.uuid4().hex
    result: "TaskiqResult[int]" = TaskiqResult(
        is_err=True,
        log="My Log",
        return_value=11,
        execution_time=112.2,
    )
    await result_backend.set_result(
        task_id=task_id,
        result=result,
    )

    await result_backend.get_result(task_id=task_id)
    with pytest.raises(ResultIsMissingError):
        await result_backend.get_result(task_id=task_id)

    await result_backend.shutdown()


@pytest.mark.anyio
async def test_keep_results_after_reading(redis_url: str) -> None:
    """
    Check if keeping results after reading works fine.

    :param redis_url: redis URL.
    """
    result_backend = RedisAsyncResultBackend(  # type: ignore
        redis_url=redis_url,
        keep_results=True,
    )
    task_id = uuid.uuid4().hex
    result: "TaskiqResult[int]" = TaskiqResult(
        is_err=True,
        log="My Log",
        return_value=11,
        execution_time=112.2,
    )
    await result_backend.set_result(
        task_id=task_id,
        result=result,
    )

    res1 = await result_backend.get_result(task_id=task_id)
    res2 = await result_backend.get_result(task_id=task_id)
    assert res1 == res2
    await result_backend.shutdown()


@pytest.mark.anyio
async def test_set_result_max_connections(redis_url: str) -> None:
    """
    Tests that asynchronous backend works with connection limit.

    :param redis_url: redis URL.
    """
    result_backend = RedisAsyncResultBackend(  # type: ignore
        redis_url=redis_url,
        max_connection_pool_size=1,
        timeout=3,
    )

    task_id = uuid.uuid4().hex
    result: "TaskiqResult[int]" = TaskiqResult(
        is_err=True,
        log="My Log",
        return_value=11,
        execution_time=112.2,
    )
    await result_backend.set_result(
        task_id=task_id,
        result=result,
    )

    async def get_result() -> None:
        await result_backend.get_result(task_id=task_id, with_logs=True)

    await asyncio.gather(*[get_result() for _ in range(10)])
    await result_backend.shutdown()


@pytest.mark.anyio
async def test_set_result_success_cluster(redis_cluster_url: str) -> None:
    """
    Tests that results can be set without errors in cluster mode.

    :param redis_url: redis URL.
    """
    result_backend = RedisAsyncClusterResultBackend(  # type: ignore
        redis_url=redis_cluster_url,
    )
    task_id = uuid.uuid4().hex
    result: "TaskiqResult[int]" = TaskiqResult(
        is_err=True,
        log="My Log",
        return_value=11,
        execution_time=112.2,
    )
    await result_backend.set_result(
        task_id=task_id,
        result=result,
    )

    fetched_result = await result_backend.get_result(
        task_id=task_id,
        with_logs=True,
    )
    assert fetched_result.log == "My Log"
    assert fetched_result.return_value == 11
    assert fetched_result.execution_time == 112.2
    assert fetched_result.is_err
    await result_backend.shutdown()


@pytest.mark.anyio
async def test_fetch_without_logs_cluster(redis_cluster_url: str) -> None:
    """
    Check if fetching value without logs works fine.

    :param redis_url: redis URL.
    """
    result_backend = RedisAsyncClusterResultBackend(  # type: ignore
        redis_url=redis_cluster_url,
    )
    task_id = uuid.uuid4().hex
    result: "TaskiqResult[int]" = TaskiqResult(
        is_err=True,
        log="My Log",
        return_value=11,
        execution_time=112.2,
    )
    await result_backend.set_result(
        task_id=task_id,
        result=result,
    )

    fetched_result = await result_backend.get_result(
        task_id=task_id,
        with_logs=False,
    )
    assert fetched_result.log is None
    assert fetched_result.return_value == 11
    assert fetched_result.execution_time == 112.2
    assert fetched_result.is_err
    await result_backend.shutdown()


@pytest.mark.anyio
async def test_remove_results_after_reading_cluster(redis_cluster_url: str) -> None:
    """
    Check if removing results after reading works fine.

    :param redis_url: redis URL.
    """
    result_backend = RedisAsyncClusterResultBackend(  # type: ignore
        redis_url=redis_cluster_url,
        keep_results=False,
    )
    task_id = uuid.uuid4().hex
    result: "TaskiqResult[int]" = TaskiqResult(
        is_err=True,
        log="My Log",
        return_value=11,
        execution_time=112.2,
    )
    await result_backend.set_result(
        task_id=task_id,
        result=result,
    )

    await result_backend.get_result(task_id=task_id)
    with pytest.raises(ResultIsMissingError):
        await result_backend.get_result(task_id=task_id)

    await result_backend.shutdown()


@pytest.mark.anyio
async def test_keep_results_after_reading_cluster(redis_cluster_url: str) -> None:
    """
    Check if keeping results after reading works fine.

    :param redis_url: redis URL.
    """
    result_backend = RedisAsyncClusterResultBackend(  # type: ignore
        redis_url=redis_cluster_url,
        keep_results=True,
    )
    task_id = uuid.uuid4().hex
    result: "TaskiqResult[int]" = TaskiqResult(
        is_err=True,
        log="My Log",
        return_value=11,
        execution_time=112.2,
    )
    await result_backend.set_result(
        task_id=task_id,
        result=result,
    )

    res1 = await result_backend.get_result(task_id=task_id)
    res2 = await result_backend.get_result(task_id=task_id)
    assert res1 == res2
    await result_backend.shutdown()
