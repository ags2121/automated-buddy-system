import fetch_messages as f
import process_messages as p

while True
	f.write_messages_to_db()
	sleep(2)

while True
	p.process_partner_msgs()
	sleep(2)

while True
	p.process_client_msgs()
	sleep(2)
	