# TASK CONTROL SKILLS

## Task Command Execution Skill

**Skill Name:** task-command-execution
**Description:** Safely call Task APIs
**Function:** Execute task management operations through secure API calls while ensuring proper validation and error handling
**Input:** Task operation request with parameters
**Output:** API response with success/error status

## Task Search Skill

**Skill Name:** task-search
**Description:** Search by title or description keywords
**Function:** Find specific tasks based on keyword matching in title or description fields
**Input:** Search query string
**Output:** List of matching tasks with relevance scores

## Task Filter Skill

**Skill Name:** task-filter
**Description:** Filter by completed / incomplete / date
**Function:** Apply filters to task lists based on status or date criteria
**Filters Available:**
- Completed (show only finished tasks)
- Incomplete (show only unfinished tasks)
- Date (filter by due date, creation date, etc.)
**Input:** Filter criteria
**Output:** Filtered list of tasks matching criteria

## Task Sort Skill

**Skill Name:** task-sort
**Description:** Sort by title, date, or status
**Function:** Order task lists based on specified criteria
**Sort Options:**
- Title (alphabetical ordering)
- Date (chronological ordering)
- Status (by task completion state)
**Input:** Sort criteria and direction (ascending/descending)
**Output:** Sorted list of tasks