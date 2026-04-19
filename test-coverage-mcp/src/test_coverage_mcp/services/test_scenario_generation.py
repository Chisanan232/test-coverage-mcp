"""Test scenario generation logic."""

from typing import Any, Dict, List, Optional


class TestScenarioGenerator:
    """Generator for test scenarios based on code analysis."""

    @staticmethod
    def generate_unit_test_scenarios(
        function_name: str, parameters: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """Generate unit test scenarios for a function.

        Args:
            function_name: Name of the function
            parameters: List of function parameters with types

        Returns:
            List of test scenarios
        """
        scenarios = []

        # Happy path scenario
        scenarios.append(
            {
                "name": f"test_{function_name}_happy_path",
                "description": "Test with valid inputs",
                "type": "happy_path",
                "inputs": {param["name"]: f"valid_{param['name']}" for param in parameters},
                "expected": "Success",
            }
        )

        # Edge case scenarios
        for param in parameters:
            if param["type"] in ["int", "float"]:
                scenarios.append(
                    {
                        "name": f"test_{function_name}_zero_{param['name']}",
                        "description": f"Test with zero {param['name']}",
                        "type": "edge_case",
                        "inputs": {p["name"]: 0 if p["name"] == param["name"] else f"valid_{p['name']}" for p in parameters},
                        "expected": "Handles zero correctly",
                    }
                )
                scenarios.append(
                    {
                        "name": f"test_{function_name}_negative_{param['name']}",
                        "description": f"Test with negative {param['name']}",
                        "type": "edge_case",
                        "inputs": {p["name"]: -1 if p["name"] == param["name"] else f"valid_{p['name']}" for p in parameters},
                        "expected": "Handles negative values correctly",
                    }
                )
            elif param["type"] == "str":
                scenarios.append(
                    {
                        "name": f"test_{function_name}_empty_{param['name']}",
                        "description": f"Test with empty {param['name']}",
                        "type": "edge_case",
                        "inputs": {p["name"]: "" if p["name"] == param["name"] else f"valid_{p['name']}" for p in parameters},
                        "expected": "Handles empty string correctly",
                    }
                )

        # Error handling scenarios
        scenarios.append(
            {
                "name": f"test_{function_name}_invalid_input",
                "description": "Test with invalid input",
                "type": "error_handling",
                "inputs": {param["name"]: "invalid" for param in parameters},
                "expected": "Raises appropriate exception",
            }
        )

        return scenarios

    @staticmethod
    def generate_integration_test_scenarios(
        component_name: str, dependencies: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate integration test scenarios for a component.

        Args:
            component_name: Name of the component
            dependencies: List of dependencies

        Returns:
            List of integration test scenarios
        """
        scenarios = []

        # Normal operation scenario
        scenarios.append(
            {
                "name": f"test_{component_name}_normal_operation",
                "description": "Test normal component operation",
                "type": "normal_operation",
                "setup": "Initialize component with valid dependencies",
                "execution": "Execute component operations",
                "expected": "Component operates correctly",
            }
        )

        # Dependency failure scenarios
        for dep in dependencies:
            scenarios.append(
                {
                    "name": f"test_{component_name}_{dep}_failure",
                    "description": f"Test component when {dep} fails",
                    "type": "dependency_failure",
                    "setup": f"Mock {dep} to fail",
                    "execution": "Execute component operations",
                    "expected": "Component handles failure gracefully",
                }
            )

        # State transition scenarios
        scenarios.append(
            {
                "name": f"test_{component_name}_state_transitions",
                "description": "Test component state transitions",
                "type": "state_transition",
                "setup": "Initialize component",
                "execution": "Trigger state transitions",
                "expected": "Component transitions correctly",
            }
        )

        return scenarios

    @staticmethod
    def generate_branch_coverage_scenarios(
        condition: str, true_branch: str, false_branch: str
    ) -> List[Dict[str, Any]]:
        """Generate scenarios for branch coverage.

        Args:
            condition: The condition being tested
            true_branch: Code executed when condition is true
            false_branch: Code executed when condition is false

        Returns:
            List of branch coverage scenarios
        """
        scenarios = []

        # True branch scenario
        scenarios.append(
            {
                "name": f"test_{condition}_true",
                "description": f"Test when {condition} is true",
                "type": "branch_coverage",
                "condition": condition,
                "condition_value": True,
                "expected_branch": true_branch,
            }
        )

        # False branch scenario
        scenarios.append(
            {
                "name": f"test_{condition}_false",
                "description": f"Test when {condition} is false",
                "type": "branch_coverage",
                "condition": condition,
                "condition_value": False,
                "expected_branch": false_branch,
            }
        )

        return scenarios

    @staticmethod
    def generate_exception_scenarios(
        function_name: str, exceptions: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate exception handling test scenarios.

        Args:
            function_name: Name of the function
            exceptions: List of exceptions that can be raised

        Returns:
            List of exception test scenarios
        """
        scenarios = []

        for exception in exceptions:
            scenarios.append(
                {
                    "name": f"test_{function_name}_raises_{exception.lower()}",
                    "description": f"Test that {function_name} raises {exception}",
                    "type": "exception_handling",
                    "exception": exception,
                    "expected": f"Raises {exception} with appropriate message",
                }
            )

        return scenarios

    @staticmethod
    def generate_performance_scenarios(
        function_name: str, complexity: str
    ) -> List[Dict[str, Any]]:
        """Generate performance test scenarios.

        Args:
            function_name: Name of the function
            complexity: Estimated complexity (O(n), O(n²), etc.)

        Returns:
            List of performance test scenarios
        """
        scenarios = []

        # Small input scenario
        scenarios.append(
            {
                "name": f"test_{function_name}_small_input",
                "description": f"Test {function_name} with small input",
                "type": "performance",
                "input_size": "small",
                "expected": "Completes quickly",
            }
        )

        # Medium input scenario
        scenarios.append(
            {
                "name": f"test_{function_name}_medium_input",
                "description": f"Test {function_name} with medium input",
                "type": "performance",
                "input_size": "medium",
                "expected": "Completes in reasonable time",
            }
        )

        # Large input scenario (if complexity allows)
        if complexity not in ["O(n²)", "O(n³)"]:
            scenarios.append(
                {
                    "name": f"test_{function_name}_large_input",
                    "description": f"Test {function_name} with large input",
                    "type": "performance",
                    "input_size": "large",
                    "expected": "Completes within performance budget",
                }
            )

        return scenarios

    @staticmethod
    def generate_comprehensive_scenarios(
        code_element: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate comprehensive test scenarios for a code element.

        Args:
            code_element: Dictionary with code element information:
                - name: Element name
                - type: Element type (function, class, method)
                - parameters: List of parameters
                - exceptions: List of exceptions
                - complexity: Time complexity

        Returns:
            List of comprehensive test scenarios
        """
        scenarios = []
        element_type = code_element.get("type", "function")
        name = code_element.get("name", "element")

        if element_type == "function":
            parameters = code_element.get("parameters", [])
            scenarios.extend(
                TestScenarioGenerator.generate_unit_test_scenarios(name, parameters)
            )

            exceptions = code_element.get("exceptions", [])
            if exceptions:
                scenarios.extend(
                    TestScenarioGenerator.generate_exception_scenarios(name, exceptions)
                )

            complexity = code_element.get("complexity", "O(n)")
            scenarios.extend(
                TestScenarioGenerator.generate_performance_scenarios(name, complexity)
            )

        elif element_type == "class":
            dependencies = code_element.get("dependencies", [])
            scenarios.extend(
                TestScenarioGenerator.generate_integration_test_scenarios(
                    name, dependencies
                )
            )

        return scenarios
