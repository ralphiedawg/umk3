import argparse

parser = argparse.ArgumentParser(description="UMK-- the universal media kontroller")

parser.add_argument("-c", "--client", action="store_false", help= "Launch the App in Client Mode")
parser.add_argument("-s", "--server", action="store_true", help= "Launch the App in Server Mode")

args = parser.parse_args()

mode = ''
if args.server:
    mode = "server"
else:
    mode = "client"
    
print(f"The app is currently running in {mode} mode.")
