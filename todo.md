# Todo

## Plan
Implement the project bottom-up focusing on utility modules first, then core business logic, and finally integration services. Each task delivers a complete user-facing capability with tests.

## Tasks
- [x] Task 1: Implement keyword rule matching engine that filters products by keyword rules with OR-match logic, handling alphanumeric tokens as whole-word matches (keyword_rule_engine)
- [x] Task 2: Implement cron expression utilities that validate and normalize cron expressions including aliases like @daily and 5/6-field formats (cron_utils)
- [>] Task 3: Implement failure circuit breaker that pauses tasks after consecutive failures with daily notification rate limiting and auto-recovery when login state updates (failure_guard)
- [ ] Task 4: Implement utility functions including retry decorator, safe nested dict access, filename sanitization, link conversion, and date formatting (utils)
- [ ] Task 5: Implement account strategy resolver that determines runtime account selection based on strategy type, state files, and account pool availability (account_strategy)
- [ ] Task 6: Implement seller profile cache with TTL expiration and request coalescing for concurrent fetches (seller_cache)
- [ ] Task 7: Implement search pagination handler that advances through search result pages with retry logic and timeout handling (search_pagination)
- [ ] Task 8: Implement notification service with base client abstraction and webhook client that renders JSON templates with product data (notification_service)
- [ ] Task 9: Implement price history service for recording market snapshots, loading price data, computing market summaries and deal scores (price_history)
- [ ] Task 10: Implement task domain models with Pydantic validation for Task, TaskCreate, TaskUpdate, and TaskGenerateRequest including keyword rule normalization (task_models)
