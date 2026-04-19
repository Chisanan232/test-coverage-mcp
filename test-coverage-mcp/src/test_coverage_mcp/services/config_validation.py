"""Configuration validation logic for coverage settings."""

from typing import Any, Dict, List, Optional


class ConfigValidator:
    """Validator for coverage configuration."""

    @staticmethod
    def validate_include_paths(paths: List[str]) -> Dict[str, Any]:
        """Validate include paths configuration.

        Args:
            paths: List of include paths

        Returns:
            Validation result with errors and warnings
        """
        errors = []
        warnings = []

        if not paths:
            warnings.append("No include paths specified")

        for path in paths:
            if not path:
                errors.append("Empty path in include_paths")
            elif path.startswith("!"):
                errors.append(f"Invalid path syntax: {path} (use exclude_paths instead)")
            elif "*" in path and "**" not in path:
                warnings.append(f"Path '{path}' uses single wildcard (consider using **)")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    @staticmethod
    def validate_exclude_paths(paths: List[str]) -> Dict[str, Any]:
        """Validate exclude paths configuration.

        Args:
            paths: List of exclude paths

        Returns:
            Validation result with errors and warnings
        """
        errors = []
        warnings = []

        if not paths:
            warnings.append("No exclude paths specified")

        for path in paths:
            if not path:
                errors.append("Empty path in exclude_paths")
            elif path.startswith("!"):
                errors.append(f"Invalid path syntax: {path}")
            elif path == "*" or path == "**":
                errors.append(f"Path '{path}' excludes everything")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    @staticmethod
    def validate_thresholds(thresholds: Dict[str, float]) -> Dict[str, Any]:
        """Validate coverage thresholds.

        Args:
            thresholds: Dictionary of threshold values

        Returns:
            Validation result with errors and warnings
        """
        errors = []
        warnings = []

        for threshold_name, threshold_value in thresholds.items():
            if not isinstance(threshold_value, (int, float)):
                errors.append(f"Threshold '{threshold_name}' must be numeric")
            elif threshold_value < 0 or threshold_value > 100:
                errors.append(f"Threshold '{threshold_name}' must be between 0 and 100")
            elif threshold_value > 95:
                warnings.append(
                    f"Threshold '{threshold_name}' is very high ({threshold_value}%)"
                )
            elif threshold_value < 50:
                warnings.append(
                    f"Threshold '{threshold_name}' is very low ({threshold_value}%)"
                )

        # Check threshold relationships
        if "minimum" in thresholds and "target" in thresholds:
            if thresholds["minimum"] > thresholds["target"]:
                errors.append("Minimum threshold cannot be greater than target threshold")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    @staticmethod
    def validate_components(components: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Validate component configuration.

        Args:
            components: Dictionary of component definitions

        Returns:
            Validation result with errors and warnings
        """
        errors = []
        warnings = []

        for component_name, component_config in components.items():
            if not isinstance(component_config, dict):
                errors.append(f"Component '{component_name}' must be a dictionary")
                continue

            # Check required fields
            if "paths" not in component_config:
                errors.append(f"Component '{component_name}' missing 'paths' field")
            else:
                paths = component_config["paths"]
                if not isinstance(paths, list):
                    errors.append(f"Component '{component_name}' paths must be a list")
                elif not paths:
                    warnings.append(f"Component '{component_name}' has no paths")

            # Check optional fields
            if "threshold" in component_config:
                threshold = component_config["threshold"]
                if not isinstance(threshold, (int, float)):
                    errors.append(
                        f"Component '{component_name}' threshold must be numeric"
                    )
                elif threshold < 0 or threshold > 100:
                    errors.append(
                        f"Component '{component_name}' threshold must be between 0 and 100"
                    )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    @staticmethod
    def validate_flags(flags: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Validate feature flag configuration.

        Args:
            flags: Dictionary of feature flag definitions

        Returns:
            Validation result with errors and warnings
        """
        errors = []
        warnings = []

        for flag_name, flag_config in flags.items():
            if not isinstance(flag_config, dict):
                errors.append(f"Flag '{flag_name}' must be a dictionary")
                continue

            # Check required fields
            if "paths" not in flag_config:
                errors.append(f"Flag '{flag_name}' missing 'paths' field")
            else:
                paths = flag_config["paths"]
                if not isinstance(paths, list):
                    errors.append(f"Flag '{flag_name}' paths must be a list")
                elif not paths:
                    warnings.append(f"Flag '{flag_name}' has no paths")

            # Check optional fields
            if "carryforward" in flag_config:
                carryforward = flag_config["carryforward"]
                if not isinstance(carryforward, bool):
                    errors.append(f"Flag '{flag_name}' carryforward must be boolean")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    @staticmethod
    def validate_full_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate complete configuration.

        Args:
            config: Full configuration dictionary

        Returns:
            Comprehensive validation result
        """
        all_errors = []
        all_warnings = []

        # Validate each section
        if "include_paths" in config:
            result = ConfigValidator.validate_include_paths(config["include_paths"])
            all_errors.extend(result["errors"])
            all_warnings.extend(result["warnings"])

        if "exclude_paths" in config:
            result = ConfigValidator.validate_exclude_paths(config["exclude_paths"])
            all_errors.extend(result["errors"])
            all_warnings.extend(result["warnings"])

        if "thresholds" in config:
            result = ConfigValidator.validate_thresholds(config["thresholds"])
            all_errors.extend(result["errors"])
            all_warnings.extend(result["warnings"])

        if "components" in config:
            result = ConfigValidator.validate_components(config["components"])
            all_errors.extend(result["errors"])
            all_warnings.extend(result["warnings"])

        if "flags" in config:
            result = ConfigValidator.validate_flags(config["flags"])
            all_errors.extend(result["errors"])
            all_warnings.extend(result["warnings"])

        return {
            "valid": len(all_errors) == 0,
            "errors": all_errors,
            "warnings": all_warnings,
            "error_count": len(all_errors),
            "warning_count": len(all_warnings),
        }
