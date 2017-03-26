from twilio.rest import TwilioRestClient
import MySQLdb
import yaml
import MySQLdb.cursors

config = yaml.load(open('credentials.yaml', 'r'))
db_config = config['db']
tw_config = config['twilio']

def get_twilio_client():
	return TwilioRestClient(tw_config['account_sid'], tw_config['auth_token'])

def get_db_conn():
	db = MySQLdb.connect(
		host=db_config['host'], 
		user=db_config['user'], 
		passwd=db_config['password'], 
		db=db_config['database'])
	return db, db.cursor(MySQLdb.cursors.DictCursor)

def send_sms(tw_client, to, msg):
	return tw_client.messages.create(to=to, from_=tw_config['twilio_num'], body=msg)