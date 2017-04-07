import os
import fetch_messages as f
import process_client_messages as c
import process_partner_messages as p

[m.kill_process() for m in [f, c, p]]
