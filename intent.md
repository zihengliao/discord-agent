Intent Classifier Agent

Purpose
-------
The purpose of this agent is to classify the type of message/request being sent
by the user.

This agent does not execute actions directly. Its job is to understand what the
user wants, identify what context/tools are needed, and return a structured
classification that the main orchestrator can use.

For example, if the user says:

    "I need to work on my forecasting project tonight"

this agent should not create a calendar event itself. Instead, it should classify
the message as a scheduling request and return information such as:

    - intent: schedule_task
    - needs_calendar: true
    - needs_goal_memory: true
    - requires_approval: true
    - task_title: forecasting project
    - time_preference: tonight

The orchestrator will then use this classification to decide what to do next.

Responsibilities
----------------
This agent should:

1. Identify the user's intent.
2. Extract useful entities from the message.
3. Decide what context is needed.
4. Decide whether the request may update memory.
5. Decide whether the request may require tool execution.
6. Decide whether user approval is required before action.
7. Return a structured JSON object.

This agent should NOT:

1. Call Google Calendar directly.
2. Update the database directly.
3. Send Discord messages directly.
4. Create reminders directly.
5. Make final safety decisions.
6. Execute any action.

The classifier only classifies. The orchestrator acts on the classification.

Supported Intents
-----------------
The initial supported intents are:

- chat
- motivation
- calendar_query
- schedule_task
- add_goal
- add_task
- mark_task_done
- plan_day
- reflect
- create_reminder
- update_memory
- cancel_action
- approval_response
- unknown

Intent Definitions
------------------

1. chat

Use this when the user is having a general conversation or asking a general
question that does not require goals, tasks, calendar access, reminders, or
memory updates.

Examples:
    "what is an API?"
    "explain async functions"
    "how does discord.py work?"
    "tell me a joke"

Expected output:
    intent = chat
    needs_calendar = false
    needs_goal_memory = false
    needs_task_memory = false
    requires_approval = false


2. motivation

Use this when the user is asking for encouragement, accountability, discipline,
or help getting unstuck.

Examples:
    "I feel lazy today"
    "I can't be bothered working"
    "motivate me"
    "keep me accountable tonight"
    "I feel like doing nothing"

This usually needs goal/task memory because the best response should connect
motivation back to the user's real goals.

Expected output:
    intent = motivation
    needs_goal_memory = true
    needs_task_memory = true
    needs_calendar = false
    requires_approval = false


3. calendar_query

Use this when the user is asking about their calendar, schedule, availability,
or existing events.

Examples:
    "what do I have tomorrow?"
    "am I free tonight?"
    "what's on my calendar today?"
    "when is my next meeting?"
    "do I have time after dinner?"

This requires reading calendar context but does not necessarily require writing
to the calendar.

Expected output:
    intent = calendar_query
    needs_calendar = true
    needs_goal_memory = false
    needs_task_memory = false
    requires_approval = false


4. schedule_task

Use this when the user wants to block time, schedule work, or add a task/event
to their calendar.

Examples:
    "block time for forecasting tonight"
    "schedule a run tomorrow morning"
    "I need to work on my project tonight"
    "put 90 minutes of job applications on my calendar"
    "find time for me to study tomorrow"

This requires calendar context. It may also require goal/task memory if the task
relates to an existing goal.

Calendar writes should require approval.

Expected output:
    intent = schedule_task
    needs_calendar = true
    needs_goal_memory = true
    needs_task_memory = true
    requires_approval = true


5. add_goal

Use this when the user wants to create a new goal.

Examples:
    "add a goal to finish my forecasting project"
    "my goal is to apply to 5 jobs this week"
    "I want to run three times this week"
    "make finishing the Discord agent a goal"

This updates goal memory.

Expected output:
    intent = add_goal
    needs_goal_memory = true
    needs_task_memory = false
    updates_goal_memory = true
    requires_approval = false


6. add_task

Use this when the user wants to create a task under a goal or as a standalone
to-do item.

Examples:
    "add a task to compare baseline and regression results"
    "remind me that I need to clean the weather data"
    "I need to write the model evaluation section"
    "add job applications as a task for tomorrow"

This updates task memory.

Expected output:
    intent = add_task
    needs_goal_memory = true
    needs_task_memory = true
    updates_task_memory = true
    requires_approval = false


7. mark_task_done

Use this when the user says they completed something.

Examples:
    "I finished the regression section"
    "done"
    "I completed the model comparison"
    "mark the forecasting task as done"
    "I applied to three jobs"

This requires task memory so the system can find the matching task. If the match
is uncertain, the system should ask for confirmation.

Expected output:
    intent = mark_task_done
    needs_goal_memory = true
    needs_task_memory = true
    updates_task_memory = true
    requires_approval = false or true depending on confidence


8. plan_day

Use this when the user wants a plan for today, tomorrow, tonight, or a broader
period.

Examples:
    "plan my day"
    "what should I do tonight?"
    "help me plan tomorrow"
    "what should I focus on this week?"
    "sort out my evening"

This usually needs goals, tasks, and calendar context.

Expected output:
    intent = plan_day
    needs_calendar = true
    needs_goal_memory = true
    needs_task_memory = true
    requires_approval = false unless proposing calendar writes


9. reflect

Use this when the user is reviewing their day, explaining what happened, or
talking about missed/completed work.

Examples:
    "I didn't do what I planned"
    "today went badly"
    "I got distracted"
    "I finished some of it but not all"
    "reflect on my day with me"

This may update reflection memory and behaviour/topic memory.

Expected output:
    intent = reflect
    needs_goal_memory = true
    needs_task_memory = true
    needs_calendar = false or true depending on message
    updates_reflection_memory = true


10. create_reminder

Use this when the user wants to be reminded about something at a future time.

Examples:
    "remind me to apply to Origin Energy tomorrow morning"
    "remind me at 8pm to check my calendar"
    "ping me in 30 minutes to start working"
    "remind me every Sunday to review my goals"

This may require a reminder system but not necessarily Google Calendar.

Expected output:
    intent = create_reminder
    needs_calendar = false
    needs_goal_memory = false
    needs_task_memory = false
    requires_approval = false for simple reminders


11. update_memory

Use this when the user explicitly wants the bot to remember a preference,
personal rule, or stable piece of context.

Examples:
    "remember that I prefer working in the morning"
    "from now on, don't schedule me after 10pm"
    "remember that I hate fake motivational quotes"
    "my main project right now is the forecasting dashboard"

This updates memory.

Expected output:
    intent = update_memory
    updates_user_memory = true
    requires_approval = false


12. cancel_action

Use this when the user wants to cancel a pending action or current flow.

Examples:
    "cancel that"
    "never mind"
    "don't do it"
    "skip it"
    "forget that"

This usually needs operational memory because "that" refers to a pending action.

Expected output:
    intent = cancel_action
    needs_operational_memory = true
    requires_approval = false


13. approval_response

Use this when the user is responding to a pending action with yes/no/confirm.

Examples:
    "yes"
    "yep"
    "do it"
    "confirm"
    "no"
    "nah"
    "cancel"

This requires operational memory so the system knows what the approval refers to.

Expected output:
    intent = approval_response
    needs_operational_memory = true
    requires_approval = false


14. unknown

Use this when the message is ambiguous and cannot be classified confidently.

Examples:
    "that thing"
    "maybe later"
    "fix it"
    "move stuff around"

Expected output:
    intent = unknown
    needs_clarification = true
    clarifying_question = "What would you like me to move or change?"

Output Format
-------------
The classifier must return valid JSON only.

Expected schema:

{
  "intent": "string",
  "confidence": 0.0,
  "needs_calendar": false,
  "needs_goal_memory": false,
  "needs_task_memory": false,
  "needs_operational_memory": false,
  "needs_conversation_history": false,
  "updates_goal_memory": false,
  "updates_task_memory": false,
  "updates_user_memory": false,
  "updates_reflection_memory": false,
  "requires_approval": false,
  "needs_clarification": false,
  "clarifying_question": null,
  "entities": {
    "task_title": null,
    "goal_title": null,
    "date": null,
    "time_preference": null,
    "duration_minutes": null,
    "reminder_text": null,
    "completed_task": null
  }
}

Entity Extraction Guidelines
----------------------------

Extract entities only when they are present or strongly implied.

Examples:

Message:
    "I need to work on forecasting tonight"

Entities:
    task_title = "forecasting"
    date = "today"
    time_preference = "tonight"
    duration_minutes = null

Message:
    "block 90 minutes for job applications tomorrow morning"

Entities:
    task_title = "job applications"
    date = "tomorrow"
    time_preference = "morning"
    duration_minutes = 90

Message:
    "I finished the regression section"

Entities:
    completed_task = "regression section"

Message:
    "remind me to apply to Origin Energy tomorrow morning"

Entities:
    reminder_text = "apply to Origin Energy"
    date = "tomorrow"
    time_preference = "morning"

Memory Retrieval Guidelines
---------------------------

The classifier should not retrieve memory itself. It should only indicate what
memory is needed.

The context builder will handle retrieval.

Use these general rules:

- motivation:
    needs_goal_memory = true
    needs_task_memory = true

- schedule_task:
    needs_calendar = true
    needs_goal_memory = true
    needs_task_memory = true

- calendar_query:
    needs_calendar = true

- add_goal:
    needs_goal_memory = true
    updates_goal_memory = true

- add_task:
    needs_goal_memory = true
    needs_task_memory = true
    updates_task_memory = true

- mark_task_done:
    needs_goal_memory = true
    needs_task_memory = true
    updates_task_memory = true

- approval_response:
    needs_operational_memory = true

- cancel_action:
    needs_operational_memory = true

- reflect:
    needs_goal_memory = true
    needs_task_memory = true
    updates_reflection_memory = true

Approval Guidelines
-------------------

The classifier should mark requires_approval = true when the user is asking for
an action that changes an external system or important state.

Usually requires approval:
- creating a Google Calendar event
- moving a Google Calendar event
- deleting or cancelling a calendar event
- sending a message to another person
- making a significant memory change if ambiguous

Usually does not require approval:
- answering a question
- giving motivation
- reading calendar
- adding a simple internal goal
- adding a simple internal task
- logging a reflection

Calendar writes should always require approval in the MVP.

Examples
--------

User:
    "I feel lazy today"

Output:
{
  "intent": "motivation",
  "confidence": 0.92,
  "needs_calendar": false,
  "needs_goal_memory": true,
  "needs_task_memory": true,
  "needs_operational_memory": false,
  "needs_conversation_history": false,
  "updates_goal_memory": false,
  "updates_task_memory": false,
  "updates_user_memory": false,
  "updates_reflection_memory": false,
  "requires_approval": false,
  "needs_clarification": false,
  "clarifying_question": null,
  "entities": {
    "task_title": null,
    "goal_title": null,
    "date": null,
    "time_preference": null,
    "duration_minutes": null,
    "reminder_text": null,
    "completed_task": null
  }
}

User:
    "What do I have tomorrow?"

Output:
{
  "intent": "calendar_query",
  "confidence": 0.96,
  "needs_calendar": true,
  "needs_goal_memory": false,
  "needs_task_memory": false,
  "needs_operational_memory": false,
  "needs_conversation_history": false,
  "updates_goal_memory": false,
  "updates_task_memory": false,
  "updates_user_memory": false,
  "updates_reflection_memory": false,
  "requires_approval": false,
  "needs_clarification": false,
  "clarifying_question": null,
  "entities": {
    "task_title": null,
    "goal_title": null,
    "date": "tomorrow",
    "time_preference": null,
    "duration_minutes": null,
    "reminder_text": null,
    "completed_task": null
  }
}

User:
    "Block 90 minutes for forecasting tonight"

Output:
{
  "intent": "schedule_task",
  "confidence": 0.95,
  "needs_calendar": true,
  "needs_goal_memory": true,
  "needs_task_memory": true,
  "needs_operational_memory": false,
  "needs_conversation_history": false,
  "updates_goal_memory": false,
  "updates_task_memory": false,
  "updates_user_memory": false,
  "updates_reflection_memory": false,
  "requires_approval": true,
  "needs_clarification": false,
  "clarifying_question": null,
  "entities": {
    "task_title": "forecasting",
    "goal_title": null,
    "date": "today",
    "time_preference": "tonight",
    "duration_minutes": 90,
    "reminder_text": null,
    "completed_task": null
  }
}

User:
    "yes"

Output:
{
  "intent": "approval_response",
  "confidence": 0.99,
  "needs_calendar": false,
  "needs_goal_memory": false,
  "needs_task_memory": false,
  "needs_operational_memory": true,
  "needs_conversation_history": false,
  "updates_goal_memory": false,
  "updates_task_memory": false,
  "updates_user_memory": false,
  "updates_reflection_memory": false,
  "requires_approval": false,
  "needs_clarification": false,
  "clarifying_question": null,
  "entities": {
    "task_title": null,
    "goal_title": null,
    "date": null,
    "time_preference": null,
    "duration_minutes": null,
    "reminder_text": null,
    "completed_task": null
  }
}

User:
    "I finished the regression section"

Output:
{
  "intent": "mark_task_done",
  "confidence": 0.91,
  "needs_calendar": false,
  "needs_goal_memory": true,
  "needs_task_memory": true,
  "needs_operational_memory": false,
  "needs_conversation_history": false,
  "updates_goal_memory": false,
  "updates_task_memory": true,
  "updates_user_memory": false,
  "updates_reflection_memory": false,
  "requires_approval": false,
  "needs_clarification": false,
  "clarifying_question": null,
  "entities": {
    "task_title": null,
    "goal_title": null,
    "date": null,
    "time_preference": null,
    "duration_minutes": null,
    "reminder_text": null,
    "completed_task": "regression section"
  }
}

Clarification Behaviour
-----------------------

If the classifier is not confident, it should set:

    needs_clarification = true

and provide a clear clarifying question.

Example:

User:
    "move it"

Output:
{
  "intent": "unknown",
  "confidence": 0.42,
  "needs_operational_memory": true,
  "needs_clarification": true,
  "clarifying_question": "What would you like me to move?"
}

Important Notes
---------------

- The classifier should be conservative.
- If the message may write to calendar, mark requires_approval = true.
- If the message is a simple yes/no, check operational memory.
- If the user asks for motivation, goal/task memory is usually helpful.
- If the user asks about schedule or availability, calendar memory is needed.
- If the user says something was completed, task memory is needed.
- The classifier should return JSON only.