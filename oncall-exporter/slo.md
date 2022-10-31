# SLO

## Business

* `oncall_teams_with_less_than_two_members / ONCALL_TEAMS_TOTAL` < 1%
* * Rationale: Team with 1 or 0 people can't do proper shifts, therefore this can only be allowed for a few teams that are new and hiring. 
* `oncall_shifts_without_partner` < 5%
* * Rationale: Shifts without backup pose a risk in case primary becomes unavailable for any reason, so these are only allowed for the fartherst-planned shifts that do not have a secondary yet, or the planned secondary became unavailable. 

## System
* `oncall_api_requests_failed_total / oncall_api_requests_total` < 95%
* * Oncall is a critical piece of software for company's mode of operation, so high guarantees should be provided for its availability. Due to the fact that Oncall is still in development, 5% is provided for possible downtime-caused errors + 5xx errors.
* `avg_over_time(oncall_health_status[1d])` >= 99%
* * As noted earlier, Oncall availability is critical, this metric disregards 5xx errors and only measures service's health over time, therefore 99% uptime is guaranteed.