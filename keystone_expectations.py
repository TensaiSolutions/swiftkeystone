"""Optional baseline contracts, evaluated without executing report contents."""
from keystone_common import ForgeError


def validate_expectations(value, checks=None):
    if not isinstance(value, dict) or not value or set(value) - {"required_test_targets", "minimum_executed_tests"}:
        raise ForgeError("baseline_expectations must contain required_test_targets and/or minimum_executed_tests.")
    if checks is not None and "test" not in checks:
        raise ForgeError("Baseline expectations require a configured test check.")
    targets = value.get("required_test_targets", [])
    if not isinstance(targets, list) or any(not isinstance(t, str) or not t.strip() or "\x00" in t for t in targets) or len(set(targets)) != len(targets):
        raise ForgeError("required_test_targets must be unique nonempty target names.")
    if "required_test_targets" in value and not targets:
        raise ForgeError("required_test_targets must not be empty.")
    minimum = value.get("minimum_executed_tests")
    if "minimum_executed_tests" in value and (type(minimum) is not int or minimum < 1):
        raise ForgeError("minimum_executed_tests must be a positive integer.")
    return value


def target_counts(data):
    """Count executed leaf cases by Xcode bundle name; refuse unsupported case evidence."""
    result = {}
    if not isinstance(data, dict) or not isinstance(data.get("testNodes"), list):
        raise ValueError("Missing Xcode test nodes")
    def visit(node, owner=None, depth=0):
        if depth > 128 or not isinstance(node, dict):
            raise ValueError("Invalid Xcode test tree")
        kind = node.get("nodeType")
        if kind in ("Unit test bundle", "UI test bundle"):
            owner = node.get("name")
            if not isinstance(owner, str) or not owner.strip():
                raise ValueError("Missing test bundle name")
            result.setdefault(owner, 0)
        if kind == "Test Case":
            outcome = node.get("result")
            if outcome not in ("Passed", "Failed", "Skipped", "Expected Failure") or owner is None:
                raise ValueError("Unsupported test case evidence")
            if outcome != "Skipped":
                result[owner] += 1
            return  # Parameterized child iterations are not additional test cases.
        children = node.get("children", [])
        if not isinstance(children, list):
            raise ValueError("Invalid test children")
        for child in children:
            visit(child, owner, depth + 1)
    for node in data["testNodes"]:
        visit(node)
    return result


def assess(expectations, summary, targets=None):
    validate_expectations(expectations)
    counts = (summary.get("passedTests"), summary.get("failedTests")) if isinstance(summary, dict) else (None, None)
    executed = sum(counts) if all(type(n) is int and n >= 0 for n in counts) and "error" not in summary else None
    findings = []
    if executed is None:
        findings.append("executed_count_unavailable")
    elif executed < expectations.get("minimum_executed_tests", 1):
        findings.append("minimum_executed_tests_not_met")
    required = expectations.get("required_test_targets", [])
    if required and isinstance(targets, dict) and executed is not None:
        if any(type(n) is not int or n < 0 for n in targets.values()) or sum(targets.values()) != executed:
            findings.append("target_counts_do_not_match_summary")
    missing = [t for t in required if not isinstance(targets, dict) or type(targets.get(t)) is not int or targets[t] < 1]
    if missing:
        findings.append("required_test_targets_not_executed")
    return {"status": "failed" if findings else "passed", "executed_tests": executed,
            "minimum_executed_tests": expectations.get("minimum_executed_tests"),
            "missing_test_targets": missing, "findings": findings}
