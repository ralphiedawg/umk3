import argparse
from src.media.Server import Server
from src.media.Client import Client

parser = argparse.ArgumentParser(description="UMK - the universal media kontroller")

parser.add_argument("-c", "--client", action="store_false", help= "Launch the app in Client Mode")
parser.add_argument("-s", "--server", action="store_true", help= "Launch the app in Server Mode")

args = parser.parse_args()

mode = 'client'
if args.server:
    mode = "server"
    print(f"App initializing in {mode} mode.")
    server = Server()
    server.run_server()
else:
    mode = "client"
    print(f"App initializing in {mode} mode.")
    client = Client()
    client.connect()
    client.run()
    
#TODO: Graceful error handling
