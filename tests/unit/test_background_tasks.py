import asyncio

import pytest
from homeykit.application.background_tasks import PeriodicTask, TaskSet, cancel_task
from homeykit.application.error_logging import run_logging_errors


class TestRunLoggingErrors:
    async def test_returns_the_result_of_the_action(self, log):
        async def action():
            return 42

        assert await run_logging_errors(log, "Failed", action) == 42
        assert log.messages == []

    async def test_logs_the_error_and_returns_none(self, log):
        async def action():
            raise ValueError("boom")

        assert await run_logging_errors(log, "Failed", action) is None
        assert log.messages == ["Failed: boom"]


class TestCancelTask:
    async def test_cancels_a_running_task_without_raising(self):
        task = asyncio.get_running_loop().create_task(asyncio.sleep(60))
        await cancel_task(task)
        assert task.cancelled()


class TestTaskSet:
    async def test_runs_and_forgets_finished_tasks(self):
        task_set = TaskSet()
        results = []

        async def work():
            results.append("done")

        await task_set.start(work())
        assert results == ["done"]

    async def test_cancel_all_stops_pending_tasks(self):
        task_set = TaskSet()
        tasks = [task_set.start(asyncio.sleep(60)) for _ in range(3)]
        await task_set.cancel_all()
        assert all(task.cancelled() for task in tasks)

    async def test_cancel_all_without_tasks_is_fine(self):
        await TaskSet().cancel_all()


class TestPeriodicTask:
    @pytest.fixture
    def calls(self):
        return []

    def build(self, calls, log, *, fail=False):
        async def action():
            calls.append("called")
            if fail:
                raise RuntimeError("boom")

        return PeriodicTask(
            interval_seconds=0.01,
            action=action,
            log=log,
            failure_message="Periodic action failed",
        )

    async def test_runs_the_action_repeatedly_until_stopped(self, calls, log):
        periodic_task = self.build(calls, log)
        periodic_task.start()
        periodic_task.start()
        assert periodic_task.is_running
        await asyncio.sleep(0.06)
        await periodic_task.stop()
        count_after_stop = len(calls)
        await asyncio.sleep(0.03)
        assert count_after_stop >= 2
        assert len(calls) == count_after_stop
        assert not periodic_task.is_running

    async def test_keeps_running_after_a_failure(self, calls, log):
        periodic_task = self.build(calls, log, fail=True)
        periodic_task.start()
        await asyncio.sleep(0.06)
        await periodic_task.stop()
        assert len(calls) >= 2
        assert log.contains("Periodic action failed: boom")

    async def test_stop_without_start_is_fine(self, calls, log):
        await self.build(calls, log).stop()
