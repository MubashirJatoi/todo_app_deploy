# USER CONTEXT SKILLS

## User Identity Context Skill

**Skill Name:** user-identity-context
**Description:** Use the logged-in user's email and ID
**Function:** Retrieve and maintain the identity context of the currently authenticated user
**Input:** Authentication token/session
**Output:** User identity information (email, ID, and associated metadata)

## User Scoped Data Access Skill

**Skill Name:** user-scoped-data-access
**Description:** Prevent cross-user access
**Function:** Ensure data isolation between users by enforcing proper access controls
**Input:** User identity context and requested data access
**Output:** Authorized data access or access denial with appropriate error handling