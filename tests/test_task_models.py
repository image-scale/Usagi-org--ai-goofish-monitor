"""Tests for task domain models."""
import pytest

from src.task_models import Task, TaskCreate, TaskUpdate, TaskGenerateRequest


def test_task_can_start_and_stop():
    task = Task(
        id=1,
        task_name="Sony A7M4",
        enabled=True,
        keyword="sony a7m4",
        description="body",
        max_pages=2,
        personal_only=True,
        ai_prompt_base_file="prompts/base_prompt.txt",
        ai_prompt_criteria_file="prompts/sony_a7m4_criteria.txt",
        is_running=False,
    )

    assert task.can_start() is True
    assert task.can_stop() is False

    running = task.model_copy(update={"is_running": True})
    assert running.can_start() is False
    assert running.can_stop() is True


def test_task_apply_update():
    task = Task(
        id=1,
        task_name="Sony A7M4",
        enabled=True,
        keyword="sony a7m4",
        description="body",
        max_pages=2,
        personal_only=True,
        ai_prompt_base_file="prompts/base_prompt.txt",
        ai_prompt_criteria_file="prompts/sony_a7m4_criteria.txt",
        is_running=False,
    )

    update = TaskUpdate(enabled=False, max_pages=5)
    updated = task.apply_update(update)

    assert updated.enabled is False
    assert updated.max_pages == 5
    assert updated.task_name == task.task_name


def test_legacy_keyword_groups_are_flattened():
    task = Task(
        id=1,
        task_name="Sony A7M4",
        enabled=True,
        keyword="sony a7m4",
        description="body",
        max_pages=2,
        personal_only=True,
        ai_prompt_base_file="prompts/base_prompt.txt",
        ai_prompt_criteria_file="prompts/sony_a7m4_criteria.txt",
        decision_mode="keyword",
        keyword_rule_groups=[
            {"name": "G1", "include_keywords": ["a7m4", "verified"], "exclude_keywords": ["flaw"]},
            {"name": "G2", "include_keywords": ["full frame", "a7m4"], "exclude_keywords": ["repair"]},
        ],
        is_running=False,
    )

    assert task.keyword_rules == ["a7m4", "verified", "full frame"]


def test_generate_request_accepts_legacy_group_payload():
    req = TaskGenerateRequest(
        task_name="legacy",
        keyword="sony a7m4",
        description="",
        decision_mode="keyword",
        keyword_rule_groups=[{"include_keywords": ["a7m4", "verified"], "exclude_keywords": ["flaw"]}],
    )
    assert req.keyword_rules == ["a7m4", "verified"]


def test_generate_request_enables_image_analysis_by_default():
    req = TaskGenerateRequest(
        task_name="Sony A7M4",
        keyword="sony a7m4",
        description="Looking for good condition body.",
        decision_mode="ai",
    )
    assert req.analyze_images is True


def test_generate_request_infers_fixed_from_state_file():
    req = TaskGenerateRequest(
        task_name="Sony A7M4",
        keyword="sony a7m4",
        description="Looking for good condition.",
        decision_mode="ai",
        account_state_file="state/acc_1.json",
    )
    assert req.account_strategy == "fixed"


def test_generate_request_requires_state_file_for_fixed():
    with pytest.raises(ValueError) as exc_info:
        TaskGenerateRequest(
            task_name="Sony A7M4",
            keyword="sony a7m4",
            description="Looking for good condition.",
            decision_mode="ai",
            account_strategy="fixed",
        )
    assert "account_state_file" in str(exc_info.value)


def test_task_create_validates_ai_mode_requires_description():
    with pytest.raises(ValueError) as exc_info:
        TaskCreate(
            task_name="Sony A7M4",
            keyword="sony a7m4",
            description="",
            decision_mode="ai",
        )
    assert "description" in str(exc_info.value).lower()


def test_task_create_validates_keyword_mode_requires_keywords():
    with pytest.raises(ValueError) as exc_info:
        TaskCreate(
            task_name="Sony A7M4",
            keyword="sony a7m4",
            description="test",
            decision_mode="keyword",
            keyword_rules=[],
        )
    assert "keyword" in str(exc_info.value).lower()


def test_task_create_normalizes_price_values():
    task = TaskCreate(
        task_name="Sony A7M4",
        keyword="sony a7m4",
        description="test description",
        decision_mode="ai",
        min_price=8000,
        max_price=16000.99,
    )
    assert task.min_price == "8000"
    assert task.max_price == "16000.99"


def test_task_create_validates_cron():
    task = TaskCreate(
        task_name="Sony A7M4",
        keyword="sony a7m4",
        description="test description",
        decision_mode="ai",
        cron="@daily",
    )
    assert task.cron == "0 0 * * *"


def test_task_create_rejects_invalid_cron():
    with pytest.raises(ValueError):
        TaskCreate(
            task_name="Sony A7M4",
            keyword="sony a7m4",
            description="test description",
            decision_mode="ai",
            cron="not-valid-cron",
        )
