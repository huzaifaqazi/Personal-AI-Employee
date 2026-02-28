# Skill: Extract Action Items

## Purpose
Identify and list actionable tasks from meetings, emails, or documents.

## When to Use
- Processing meeting notes
- Reviewing email threads
- Analyzing project discussions
- Creating task lists from conversations

## Process
1. Read through the source material
2. Identify commitments and decisions
3. Extract specific action items
4. Assign owners (if mentioned)
5. Note deadlines (if specified)
6. Prioritize by urgency

## Output Format
```markdown
# Action Items

**Source:** [meeting/email/document]
**Date:** [YYYY-MM-DD]
**Extracted:** [timestamp]

## High Priority
- [ ] **[Owner]** - Action item description (Due: YYYY-MM-DD)
- [ ] **[Owner]** - Action item description (Due: YYYY-MM-DD)

## Medium Priority
- [ ] **[Owner]** - Action item description
- [ ] **[Owner]** - Action item description

## Low Priority / FYI
- [ ] **[Owner]** - Action item description

## Follow-up Required
- Item requiring clarification
- Item needing more information

## Notes
- Additional context
- Dependencies
```

## Usage
Reference in task: `@skill:extract_action_items`
