# CORE AI SKILLS

## Natural Language Understanding Skill

**Skill Name:** natural-language-understanding
**Description:** Understand user free-text commands
**Function:** Parse and comprehend natural language input from users to extract meaning and intent
**Input:** Raw user text/command
**Output:** Structured understanding of user request

## Intent Classification Skill

**Skill Name:** intent-classification
**Description:** Classify user commands into specific action categories
**Function:** Identify the user's intention from predefined categories
**Categories:**
- Add (create new todo items)
- Delete (remove todo items)
- Edit (modify existing todo items)
- Search (find specific todo items)
- Filter (apply filters to todo list)
- Sort (order todo items by criteria)
- List (display todo items)
- Info (get information about system/features)

**Input:** User command text
**Output:** Classified intent with confidence score

## Entity Extraction Skill

**Skill Name:** entity-extraction
**Description:** Extract structured data from user commands
**Function:** Identify and extract key information from natural language
**Entities Extracted:**
- Title (main task title)
- Description (detailed task description)
- Keywords (relevant tags/labels)
- Status (to-do, in-progress, completed, etc.)
- Dates (due dates, start dates, etc.)

**Input:** User command text
**Output:** Structured data with extracted entities and their values