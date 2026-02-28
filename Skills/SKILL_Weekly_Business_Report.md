# Weekly Business Report

## Purpose
Generate comprehensive weekly business summary and performance analysis

## Instructions
1. Review all Done/ tasks from past 7 days
2. Check Logs/ for activity patterns and metrics
3. Analyze productivity and completion rates
4. Identify blockers and issues
5. Create report in Plans/Weekly_Report_[date].md
6. Generate actionable recommendations

## Report Template
```markdown
# Weekly Business Report
**Week Ending:** [date]
**Generated:** [timestamp]

## Executive Summary
[2-3 paragraph overview of the week's key activities and outcomes]

## Tasks Completed
**Total:** [number] tasks

### By Category
- **Emails:** [count] processed, [count] sent
- **LinkedIn:** [count] posts published
- **WhatsApp:** [count] alerts handled
- **Projects:** [count] completed
- **Administrative:** [count] completed

### By Priority
- **High Priority:** [count] ([percentage]%)
- **Medium Priority:** [count] ([percentage]%)
- **Low Priority:** [count] ([percentage]%)

## Tasks Pending
**Total:** [number] tasks

### Age Analysis
- **< 24 hours:** [count]
- **1-3 days:** [count]
- **3-7 days:** [count]
- **> 7 days:** [count] ⚠️

### By Priority
- **High Priority:** [count]
- **Medium Priority:** [count]
- **Low Priority:** [count]

## Blockers and Issues

### Critical Issues
[List any critical blockers or system failures]

### Warnings
[List any warnings or potential issues]

### Resolved Issues
[List issues that were resolved this week]

## Performance Metrics

### Completion Rate
- **Overall:** [percentage]%
- **High Priority:** [percentage]%
- **Target:** 90%+

### Average Task Time
- **Email responses:** [hours/days]
- **LinkedIn posts:** [hours/days]
- **Project tasks:** [hours/days]

### Response Times
- **Email:** Average [hours] (Target: < 24h)
- **WhatsApp alerts:** Average [minutes] (Target: < 1h)
- **Approvals:** Average [hours] (Target: < 4h)

### System Uptime
- **Orchestrator:** [percentage]%
- **Watchers:** [percentage]%
- **Downtime incidents:** [count]

## Activity Highlights

### Top Accomplishments
1. [Major achievement 1]
2. [Major achievement 2]
3. [Major achievement 3]

### Key Communications
- **Emails sent:** [count] to [number] recipients
- **LinkedIn engagement:** [likes/comments/shares]
- **WhatsApp responses:** [count] urgent alerts handled

### Automation Wins
[List tasks that were successfully automated or streamlined]

## Next Week Priorities

### High Priority
1. [Priority task 1]
2. [Priority task 2]
3. [Priority task 3]

### Medium Priority
1. [Task 1]
2. [Task 2]
3. [Task 3]

### Carry-Over Tasks
[List tasks from this week that need to continue]

## Recommendations

### Process Improvements
1. [Improvement suggestion 1]
2. [Improvement suggestion 2]
3. [Improvement suggestion 3]

### System Optimizations
1. [Optimization 1]
2. [Optimization 2]

### New Automations
1. [Automation opportunity 1]
2. [Automation opportunity 2]

## Appendix

### Detailed Task List
[Link to detailed task breakdown if needed]

### Log Files
- Orchestrator: `Logs/orchestrator_[dates].md`
- Gmail: `Logs/gmail_[dates].md`
- LinkedIn: `Logs/linkedin_[dates].md`
- WhatsApp: `Logs/whatsapp_[dates].md`

---
*Report generated automatically by AI Employee*
*Review and adjust recommendations as needed*
```

## Data Collection

### Sources
1. **Done/ folder:** Completed tasks with timestamps
2. **Needs_Action/ folder:** Pending tasks with age
3. **Logs/ folder:** Activity logs and metrics
4. **Approved/ folder:** Items awaiting execution
5. **Rejected/ folder:** Declined items

### Metrics to Calculate

**Completion Rate:**
```
(Tasks Completed / Total Tasks) × 100
```

**Average Task Time:**
```
Sum(Task Completion Times) / Number of Tasks
```

**Response Time:**
```
Time between task creation and completion
```

**Priority Distribution:**
```
(High Priority Tasks / Total Tasks) × 100
```

## Analysis Guidelines

### Identify Patterns
- Which days have highest activity?
- What types of tasks take longest?
- Are there recurring blockers?
- Which automations are most effective?

### Spot Trends
- Is completion rate improving?
- Are response times decreasing?
- Is task backlog growing?
- Are priorities being handled appropriately?

### Flag Concerns
- Tasks pending > 7 days
- Completion rate < 80%
- System downtime > 5%
- High priority tasks delayed

## Recommendations Framework

### Process Improvements
- Streamline approval workflows
- Adjust check intervals
- Refine priority rules
- Update automation triggers

### System Optimizations
- Increase watcher frequency for critical items
- Adjust rate limits
- Optimize resource usage
- Improve error handling

### New Automations
- Identify repetitive manual tasks
- Suggest new integrations
- Propose workflow enhancements
- Recommend tool additions

## Quality Checklist

Before finalizing report:
- [ ] All data sources reviewed
- [ ] Metrics calculated accurately
- [ ] Trends identified and explained
- [ ] Blockers clearly documented
- [ ] Recommendations are actionable
- [ ] Executive summary is concise
- [ ] Report is well-formatted
- [ ] Links to source data included

## Scheduling

**Trigger:** Every Sunday at 8:00 PM
**Delivery:** Save to Plans/Weekly_Report_[date].md
**Notification:** Create reminder in Needs_Action/

## Integration

This skill integrates with:
- Scheduler (weekly trigger)
- All log files (data source)
- Done/ folder (completed tasks)
- Needs_Action/ folder (pending tasks)
- Dashboard.md (current status)

## Example Insights

### Good Week Example
```
Executive Summary:
Strong performance this week with 95% completion rate on high-priority tasks.
Email response time averaged 4 hours, well below our 24-hour target. LinkedIn
engagement increased 40% with 3 posts generating significant discussion. System
uptime was 99.8% with only one minor watcher restart.
```

### Needs Improvement Example
```
Executive Summary:
Completion rate dropped to 78% this week due to increased task volume and two
system outages. Email backlog grew to 12 pending items, with 3 high-priority
emails pending > 48 hours. Recommend increasing Gmail watcher frequency and
addressing recurring authentication issues.
```

## Follow-Up Actions

After generating report:
1. Review with human for accuracy
2. Discuss recommendations
3. Implement approved improvements
4. Track metrics for next week
5. Archive report in Plans/
