# Acceptance Criteria

## Task 1: Keyword Rule Matching Engine

### Acceptance Criteria
- [ ] build_search_text extracts and normalizes text from nested product/seller info dicts into lowercase searchable string
- [ ] evaluate_keyword_rules returns is_recommended=True when any keyword matches (OR logic)
- [ ] evaluate_keyword_rules counts and returns all matched keywords
- [ ] Case insensitive matching: "SONY" matches "sony a7m4"
- [ ] Pure alphanumeric keywords match as whole tokens only: "q1" does NOT match "q1r5"
- [ ] Pure alphanumeric keywords DO match when token boundaries exist: "q1r5" matches "q1r5"
- [ ] Returns is_recommended=False with reason when no keywords match
- [ ] Returns is_recommended=False when keywords list is empty
- [ ] Returns is_recommended=False when search text is empty
