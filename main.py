import argparse
import server

parser = argparse.ArgumentParser(description="UMK - the universal media kontroller")

parser.add_argument("-c", "--client", action="store_false", help= "Launch the app in Client Mode")
parser.add_argument("-s", "--server", action="store_true", help= "Launch the app in Server Mode")

args = parser.parse_args()

mode = 'client'
if args.server:
    mode = "server"
    print(f"App initializing in {mode} mode.")
else:
    mode = "client"
    print(f"App initializing in {mode} mode.")
    
