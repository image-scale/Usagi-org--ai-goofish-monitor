# Acceptance Criteria

## Task 1: Keyword Rule Matching Engine

### Acceptance Criteria
- [x] build_search_text extracts and normalizes text from nested product/seller info dicts into lowercase searchable string
- [x] evaluate_keyword_rules returns is_recommended=True when any keyword matches (OR logic)
- [x] evaluate_keyword_rules counts and returns all matched keywords
- [x] Case insensitive matching: "SONY" matches "sony a7m4"
- [x] Pure alphanumeric keywords match as whole tokens only: "q1" does NOT match "q1r5"
- [x] Pure alphanumeric keywords DO match when token boundaries exist: "q1r5" matches "q1r5"
- [x] Returns is_recommended=False with reason when no keywords match
- [x] Returns is_recommended=False when keywords list is empty
- [x] Returns is_recommended=False when search text is empty

## Task 2: Cron Expression Utilities

### Acceptance Criteria
- [x] normalize_cron_expression expands aliases: "@daily" -> "0 0 * * *"
- [x] normalize_cron_expression returns None for empty/None input
- [x] build_cron_trigger accepts 5-field cron expressions (minute hour day month weekday)
- [x] build_cron_trigger accepts 6-field cron expressions (second minute hour day month weekday)
- [x] build_cron_trigger accepts cron aliases like @hourly, @daily, @weekly, @monthly, @yearly
- [x] build_cron_trigger supports timezone parameter
- [x] validate_cron_expression returns normalized expression for valid input
- [x] validate_cron_expression raises ValueError with helpful message for invalid input

## Task 3: Failure Circuit Breaker

### Acceptance Criteria
- [x] record_failure tracks consecutive failures per task
- [x] Circuit opens (pauses task) after threshold consecutive failures
- [x] should_skip_start returns skip=True when task is paused
- [x] should_notify=True once per day when task is in paused state
- [x] record_success resets the failure counter and clears pause
- [x] Auto-recovery: when cookie file modification time changes, pause is lifted
- [x] State is persisted to JSON file for durability across restarts

## Task 4: Utility Functions

### Acceptance Criteria
- [ ] safe_get retrieves nested dict/list values safely, returning default on missing keys
- [ ] sanitize_filename removes/replaces unsafe characters for filenames
- [ ] get_link_unique_key extracts unique portion of product link (before first &)
- [ ] convert_goofish_link transforms desktop item URLs to mobile format with encoded parameters
- [ ] format_registration_days converts total days to "X years Y months" display format
- [ ] retry_on_failure decorator retries async functions on HTTP errors with configurable retries/delay
