#!/usr/bin/env python
import json
import sys
import zulip

# Pass the path to your zuliprc file here.
client = zulip.Client(config_file="./zuliprc")

# Print every message the current user would receive
# This is a blocking call that will run forever
# client.call_on_each_message(lambda msg: sys.stdout.write(str(msg) + "\n"))

result = client.get_members({'client_gravatar': True})
print(json.dumps(result))

# Print every event relevant to the user
# This is a blocking call that will run forever
# client.call_on_each_event(lambda event: sys.stdout.write(str(event) + "\n"))
