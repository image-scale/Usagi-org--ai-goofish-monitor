# Goal

## Project
ai-goofish-monitor — a python project.

## Description
A Playwright and AI-powered multi-task real-time monitoring tool for Goofish (Xianyu), featuring web management interface. The tool enables:
- Keyword and AI-based product filtering/recommendation
- Cron-scheduled task execution
- Multi-channel notifications (ntfy, Bark, Telegram, WeChat, Webhook)
- Price history tracking and market analysis
- Account/proxy rotation with failure circuit breaker
- Task management via FastAPI backend with SQLite persistence

## Scope
- Core domain models for tasks and configuration
- Keyword matching engine for product filtering
- Cron expression validation and scheduling utilities
- Failure guard / circuit breaker for task reliability
- Notification service with multiple client implementations
- Price history service with market analytics
- Seller profile caching
- Search pagination handling
- Account strategy resolution
- Utility functions for text processing and link conversion
- Full test coverage for all modules
