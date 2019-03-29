# google-reminders-cli

This is a simple tool for creating Google reminders from the command line.
The only supported feature is creating a single reminder in a specified time and 
date, and is done interactively:

```
$ ./remind 
What's the reminder: Pay bills
When do you want to be reminded: tomorrow at 4pm

"Pay bills" on Saturday, 2019-2-16 at 16:00

Do you want to save this? [Y/n] y
Reminder set successfully
```

Run `remind -h` to see additional acceptable time formats

## Run as a module

```
import google_reminders_cli.remind

google_reminders_cli.remind.create("kill myself", 2019, 3, 30, 15, 0)
```

Currently there is no official support for reminders in Google API, so instead, this 
tool imitates a browser request.  
App API keys are provided in a separate file and you may either use them or change them with 
your own keys.
