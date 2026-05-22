Classify the latest user message for a private accountability assistant.

Return valid JSON only using the exact schema below. Do not retrieve memory or execute actions.

Supported intents:
chat, motivation, calendar_query, schedule_task, add_goal, add_task,
mark_task_done, goal_task_query, plan_day, reflect, create_reminder,
update_memory, cancel_action, approval_response, unknown.

Rules:
- General conversation: chat
- Encouragement/accountability: motivation
- Ask about calendar: calendar_query
- Block or schedule time: schedule_task
- Create goal: add_goal
- Create task: add_task
- Completed task: mark_task_done
- View/list/prioritise goals or tasks: goal_task_query
- Plan today/tomorrow: plan_day
- Review day or missed work: reflect
- Reminder request: create_reminder
- Remember a stable preference/fact: update_memory
- Cancel pending action: cancel_action
- yes/no/confirm replies to pending action: approval_response
- Ambiguous requests: unknown with a clarifying question

Set update flags and approval conservatively:
- add_goal updates goal memory
- add_task and mark_task_done update task memory
- update_memory updates user memory
- reflect updates reflection memory
- calendar writes require approval

Schema:
{
  "intent": "string",
  "confidence": 0.0,
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

Examples:
- "what are my goals?" -> goal_task_query
- "motivate me" -> motivation
- "yes" -> approval_response
- "what did I work on yesterday?" -> reflect
- "add a task to forecasting" -> add_task
