import unittest

from agents.intent_agent import Intent, IntentResult
from context_flow import get_context_types, load_context


class ContextSelectionTests(unittest.TestCase):
    def test_goal_task_query_loads_only_goal_and_task_memory(self):
        context_types = get_context_types(
            IntentResult(intent=Intent.GOAL_TASK_QUERY),
            "what are my goals?",
        )

        self.assertEqual(context_types, {"goal_tasks"})

    def test_motivation_loads_goal_and_task_memory(self):
        context_types = get_context_types(
            IntentResult(intent=Intent.MOTIVATION),
            "motivate me",
        )

        self.assertEqual(context_types, {"goal_tasks"})

    def test_approval_response_loads_operational_state_and_recent_turns(self):
        context_types = get_context_types(
            IntentResult(intent=Intent.APPROVAL_RESPONSE),
            "yes",
        )

        self.assertEqual(context_types, {"operational", "recent_turns"})


class ContextLoadingTests(unittest.TestCase):
    def test_load_context_loads_only_requested_stores(self):
        calls = []

        def loader(name, value):
            def _load():
                calls.append(name)
                return value

            return _load

        context = load_context(
            get_context_types(
                IntentResult(intent=Intent.ADD_TASK),
                "add a task to forecasting",
            ),
            loaders={
                "goal_tasks": loader("goal_tasks", {"goals": [], "standalone_tasks": []}),
                "recent_turns": loader("recent", []),
                "operational": loader("operational", {}),
            },
        )

        self.assertEqual(calls, ["goal_tasks"])
        self.assertEqual(context["goal_tasks"], {"goals": [], "standalone_tasks": []})
        self.assertNotIn("recent_turns", context)


if __name__ == "__main__":
    unittest.main()
