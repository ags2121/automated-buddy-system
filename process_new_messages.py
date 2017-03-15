import pandas as pd
from datetime import datetime

time_format = '%m/%d/%y %H:%M'

def is_high_risk(messsage):
	return messsage in ['Help', 'help', 'h', 'H']

def process_new_messages():
	df = pd.read_csv('clientTab.csv')
	update_time = datetime.today()

	df.ix[df['messageViewedAtTime'].isnull() & (df['clientMessage'].apply(is_high_risk)), 'clientMessageType'] = 'highRisk'
	df.ix[df['messageViewedAtTime'].isnull() & (df['clientMessageType'].isnull()), 'clientMessageType'] = 'lowRisk'
	df.ix[df['messageViewedAtTime'].isnull(), 'messageViewedAtTime'] = update_time.strftime(time_format)

	df.to_csv('updated_tables/clientTab_updated_{}'.format(update_time))

if __name__ == '__main__':
	process_new_messages()
