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

def get_client_location(client_uuid):
	client_location_map = yaml.load(open('clientuuid_to_location.yaml', 'r'))
	return client_location_map.get(client_uuid)

def get_partners_for_location(location):
	location_partner_map = yaml.load(open('location_to_partneruuid.yaml', 'r'))
	return location_partner_map.get(location)

def get_partner_numbers(cur, partner_uuids):
	partner_numbers = []
	for p in partner_uuids:
		if cur.execute('SELECT phone_number FROM user WHERE uuid = %s', (p,)) == 0:
			continue
		partner_numbers.append(cur.fetchall()[0]['phone_number'])
	return partner_numbers
	