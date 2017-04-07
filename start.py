import os

os.system('python fetch_messages.py &')
os.system('python process_client_messages.py &')
os.system('python process_partner_messages.py &')
