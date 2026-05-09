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
- [ ] normalize_cron_expression expands aliases: "@daily" -> "0 0 * * *"
- [ ] normalize_cron_expression returns None for empty/None input
- [ ] build_cron_trigger accepts 5-field cron expressions (minute hour day month weekday)
- [ ] build_cron_trigger accepts 6-field cron expressions (second minute hour day month weekday)
- [ ] build_cron_trigger accepts cron aliases like @hourly, @daily, @weekly, @monthly, @yearly
- [ ] build_cron_trigger supports timezone parameter
- [ ] validate_cron_expression returns normalized expression for valid input
- [ ] validate_cron_expression raises ValueError with helpful message for invalid input
