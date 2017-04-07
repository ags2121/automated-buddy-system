import util
import csv
from datetime import datetime, timedelta
from itertools import chain
import logging
import time
import os

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("./fetch_messages.log")
logger.addHandler(fh)

def insert(rows, table, cursor):
	if len(rows) == 0:
		return

	columns = ', '.join(map(lambda x: '`%s`' % x, rows[0].keys()))
	for row in rows:
		values = ', '.join(map(lambda x: x if x == 'NULL' else "'%s'" % x, row.values()))
		cursor.execute('INSERT INTO %s(%s) VALUES(%s)' % (table, columns, values))	

def create_db():
	db, cursor = util.get_db_conn()

	with open('create_tables.sql', 'r') as queryfile:
		queries=queryfile.read().split(';')

	[cursor.execute(query) for query in queries if query != '\n']

	db.commit()
	cursor.close()

def get_missing_dates(time_of_last_sent_msg):
	twilio_date_fmt = '%Y-%m-%d'
	delta = datetime.today() - time_of_last_sent_msg
	return [(time_of_last_sent_msg + timedelta(days=i)).strftime(twilio_date_fmt) for i in range(delta.days + 2)]

# TODO: write to in-memory only DB?
def write_messages_to_db(tw_client):
	twilio_date_fmt = '%Y-%m-%d'
	db, cursor = util.get_db_conn()
	cursor.execute('SELECT MAX(sent_on) as sent_on FROM message')
	time_of_last_sent_msg = cursor.fetchall()[0]['sent_on']

	# get days for which we have no msgs (None if we've never synced msgs before)
	dates = get_missing_dates(time_of_last_sent_msg) if time_of_last_sent_msg != None else [None]

	# fetch msgs and flatten responses into list
	latest_msgs = chain.from_iterable([tw_client.messages.list(date_sent=date_sent) for date_sent in dates])

	# filter msgs by time_of_last_sent_msg and sort msgs ascending by date sent
	epoch_start = datetime(1970, 1, 1, 1)
	latest_msgs = sorted([msg for msg in latest_msgs if (time_of_last_sent_msg or epoch_start) < msg.date_sent], key=lambda m: m.date_sent)

	msgs_for_db = []
	for msg in latest_msgs:
		msg_for_db = {'from': msg.from_, 'to': msg.to, 'body': msg.body, 'direction': msg.direction, 'sent_on': msg.date_sent}
		msgs_for_db.append(msg_for_db)

	insert(msgs_for_db, 'message', cursor)

	db.commit()
	cursor.close()
	return latest_msgs

def seed_db():
	create_db()
	write_messages_to_db(util.get_twilio_client())
	db, cursor = util.get_db_conn()
	cursor.execute("""
		UPDATE message
		SET processed_on = now(), response_threshold_hit_on = now()
		""")
	db.commit()
	cursor.close()

if __name__ == '__main__':
	os.system("pkill -xf 'python fetch_messages.py' || true")
	while True:
		write_messages_to_db(util.get_twilio_client())
		time.sleep(2)
