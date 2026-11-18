import asyncio

import pytest
from homeykit.application.background_tasks import PeriodicTask, TaskSet, cancel_task


class TestCancelTask:
    async def test_given_a_running_task_when_cancelled_then_nothing_is_raised(self):
        task = asyncio.get_running_loop().create_task(asyncio.sleep(60))

        await cancel_task(task)

        assert task.cancelled()


class TestTaskSet:
    async def test_given_a_short_task_when_started_then_it_runs_to_the_end(self):
        task_set = TaskSet()
        results = []

        async def work():
            results.append("done")

        await task_set.start(work())

        assert results == ["done"]

    async def test_given_pending_tasks_when_cancelled_then_all_of_them_stop(self):
        task_set = TaskSet()
        tasks = [task_set.start(asyncio.sleep(60)) for _ in range(3)]

        await task_set.cancel_all()

        assert all(task.cancelled() for task in tasks)

    async def test_given_no_tasks_when_cancelled_then_nothing_happens(self):
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

    async def test_given_a_started_task_when_stopped_then_it_stops_calling_the_action(
        self, calls, log
    ):
        periodic_task = self.build(calls, log)

        periodic_task.start()
        periodic_task.start()
        running = periodic_task.is_running
        await asyncio.sleep(0.06)
        await periodic_task.stop()
        count_after_stop = len(calls)
        await asyncio.sleep(0.03)

        assert running
        assert count_after_stop >= 2
        assert len(calls) == count_after_stop
        assert not periodic_task.is_running

    async def test_given_a_failing_action_when_running_then_it_keeps_going_and_logs(
        self, calls, log
    ):
        periodic_task = self.build(calls, log, fail=True)

        periodic_task.start()
        await asyncio.sleep(0.06)
        await periodic_task.stop()

        assert len(calls) >= 2
        assert log.contains("Periodic action failed: boom")

    async def test_given_a_task_that_never_started_when_stopped_then_nothing_happens(
        self, calls, log
    ):
        await self.build(calls, log).stop()
