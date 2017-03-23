from twilio.rest import TwilioRestClient 
import yaml

def get_twilio_client(config):
	return TwilioRestClient(config['account_sid'], config['auth_token'])

def send_sms(client, frm, to, msg):
	return client.messages.create(to=to, from_=frm, body=msg)

twilio_config = yaml.load(open('credentials.yaml', 'r'))['twilio']
client = get_twilio_client(twilio_config)	

def test(msg):
	send_sms(client, twilio_config['twilio_num'], twilio_config['test_num'], msg)
