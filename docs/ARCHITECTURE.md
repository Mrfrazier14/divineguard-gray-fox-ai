# Boundaries

- GovCon Pulse owns opportunity records and evidence links.
- Gray Fox owns outbound model calls. It does not submit bids or certify claims.
- SaaS Platform owns proposed shared cloud identity, storage and health runtime.

These repositories are independent starters. No network connection between them is implemented yet. No existing desktop app, hosted pilot, credentials, customer records or billing configuration has been migrated.

A future web/desktop client should call an authenticated backend. That backend must derive tenant identity from verified tokens, enforce authorization on every record, call Gray Fox server-side, and store only authorized records. Never expose provider keys in a frontend bundle.
