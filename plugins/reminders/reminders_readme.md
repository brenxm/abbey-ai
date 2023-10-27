
User end's manual
To use reminder plugin in prompt, the prompt must include the trigger keyword 'my reminders'
and must be preceded or followed by one action keyword (If action keyword is omitted, it won't trigger the use of reminders)
If two action keyword is given in a single prompt, the first action keyword in the prompt will be applied.

There are four functions the user can use the reminder plugin
1. Create 
    keywords: 'create', 'make' and 'add'
    - It creates or make a new reminder. It stores all necessary information needed to make up a reminder.
        Title - Title of the reminder
        Description - brief description of the reminder
        Date - exact date of the reminder
        Time - exact time of the reminder (can be omitted)
    
2. Read
    keywords: 'check' and 'read'
    - It reads all the content of the reminder

3. Update
    keywords: 'update', 'overwrite', 'change' and 'rewrite'
    - It update an existing reminder

4. Delete
    keywords: 'remove', 'delete', 'cancel' and 'mark as completed'
    - Deletes an existing reminder

5. Mark as completed
    keywords: 'mark as completed' and 'is complete'
    - Mark a reminder as complete. If the reminder is a repetitive, it will stop reminding you until the next cycle. If the next due is next day, it will reset the next day (due day) and if it's 2 days or more before the next due day, it will reset the day before the next due day.

    If the reminder is set as exact day, marking as complete will delete the reminder and will be sent to the history.


