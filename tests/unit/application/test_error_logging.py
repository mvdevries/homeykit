from homeykit.application.error_logging import run_logging_errors


class TestRunLoggingErrors:
    async def test_given_a_working_action_when_run_then_its_result_is_returned(
        self, log
    ):
        async def action():
            return 42

        result = await run_logging_errors(log, "Failed", action)

        assert result == 42
        assert log.messages == []

    async def test_given_a_failing_action_when_run_then_the_error_is_logged(self, log):
        async def action():
            raise ValueError("boom")

        result = await run_logging_errors(log, "Failed", action)

        assert result is None
        assert log.messages == ["Failed: boom"]
