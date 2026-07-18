from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import allure


def read_json_report(path: Path, builder: Callable[[], Any] | None = None) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))

    if builder is None:
        raise FileNotFoundError(path)

    report = builder()
    if hasattr(report, "to_dict"):
        payload = report.to_dict()
    elif isinstance(report, dict):
        payload = report
    else:
        raise TypeError(f"Unsupported report payload type: {type(report).__name__}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return payload


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, indent=2, ensure_ascii=False, default=str)


def attach_case(
    *,
    parent_suite: str,
    suite: str,
    title: str,
    expected_output: Any,
    actual_output: Any,
    score: float | None,
    passed: bool,
    sub_suite: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    allure.dynamic.parent_suite(parent_suite)
    allure.dynamic.suite(suite)
    if sub_suite:
        allure.dynamic.sub_suite(sub_suite)
    allure.dynamic.title(title)

    payload: dict[str, Any] = {
        "title": title,
        "expected_output": expected_output,
        "actual_output": actual_output,
        "score": score,
        "passed": passed,
    }
    if details:
        payload["details"] = details

    allure.attach(
        _stringify(payload),
        name="case-details",
        attachment_type=allure.attachment_type.JSON,
    )
