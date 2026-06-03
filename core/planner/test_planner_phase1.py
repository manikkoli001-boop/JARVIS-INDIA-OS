import unittest

from core.agent import AgentPlan, AgentStep
from core.memory.memory_manager import MemoryManager
from core.planner.checkpoint_engine import CheckpointStep
from core.planner.planner import Planner
from core.tool_manager import ToolManager


class PlannerPhase1Test(unittest.TestCase):

    def setUp(self):
        self.tool_manager = ToolManager()
        self.memory = MemoryManager()

    def test_optimizer_enriches_normalizes_and_deduplicates_steps(self):
        planner = Planner(tool_manager=self.tool_manager, memory_manager=self.memory)
        plan = AgentPlan(
            goal="  Calculate value  ",
            steps=[
                AgentStep(
                    name="  Compute  ",
                    description="",
                    tool=" calculator ",
                    parameters={"expression": 2, "unused": "drop-me"},
                ),
                AgentStep(
                    name="Compute",
                    description="Calculate a simple arithmetic expression.",
                    tool="calculator",
                    parameters={"expression": "2"},
                ),
            ],
        )

        optimized = planner.optimize(plan)

        self.assertEqual(optimized.goal, "Calculate value")
        self.assertEqual(len(optimized.steps), 1)
        self.assertEqual(optimized.steps[0].name, "Compute")
        self.assertEqual(optimized.steps[0].description, "Calculate a simple arithmetic expression.")
        self.assertEqual(optimized.steps[0].tool, "calculator")
        self.assertEqual(optimized.steps[0].parameters, {"expression": "2"})

    def test_optimizer_expands_structured_compound_steps(self):
        planner = Planner(tool_manager=self.tool_manager, memory_manager=self.memory)
        plan = AgentPlan(
            goal="Run compound work",
            steps=[
                AgentStep(
                    name="Compound",
                    description="Run two calculations",
                    parameters={
                        "__steps__": [
                            {
                                "name": "First",
                                "description": "Compute 1+1",
                                "tool": "calculator",
                                "parameters": {"expression": "1+1"},
                            },
                            {
                                "name": "Second",
                                "description": "Compute 2+2",
                                "tool": "calculator",
                                "parameters": {"expression": "2+2"},
                            },
                        ]
                    },
                )
            ],
        )

        optimized = planner.optimize(plan)

        self.assertEqual([step.name for step in optimized.steps], ["First", "Second"])
        self.assertEqual([step.tool for step in optimized.steps], ["calculator", "calculator"])

    def test_optimizer_can_insert_checkpoints_when_enabled(self):
        planner = Planner(tool_manager=self.tool_manager, memory_manager=self.memory, insert_checkpoints=True)
        plan = AgentPlan(
            goal="Shutdown system",
            steps=[
                AgentStep(
                    name="Shutdown",
                    description="Shutdown the machine",
                    tool="system_shutdown",
                    parameters={"confirm": "false"},
                )
            ],
        )

        optimized = planner.optimize(plan)

        self.assertEqual(len(optimized.steps), 2)
        self.assertIsInstance(optimized.steps[0], CheckpointStep)
        self.assertEqual(optimized.steps[1].parameters, {"confirm": False})

    def test_invalid_plan_returns_raw_plan(self):
        planner = Planner(tool_manager=self.tool_manager, memory_manager=self.memory)
        plan = AgentPlan(goal="", steps=[AgentStep(name="Compute", description="", tool="calculator")])

        optimized = planner.optimize(plan)

        self.assertIs(optimized, plan)


if __name__ == "__main__":
    unittest.main()
