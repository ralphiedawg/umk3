import argparse
import signal
import multiprocessing

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', force=True)

    from src.media.Server import Server
    from src.media.Client import Client

    parser = argparse.ArgumentParser(description="UMK - the universal media kontroller")

    parser.add_argument("-c", "--client", action="store_false", help= "Launch the app in Client Mode")
    parser.add_argument("-s", "--server", action="store_true", help= "Launch the app in Server Mode")

    args = parser.parse_args()

    server_instance = None

    def shutdown_handler(signum, frame):
        if server_instance:
            server_instance.shutdown()
        print('Exiting...')
        exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)

    try:
        mode = 'client'
        if args.server:
            mode = "server"
            print(f"App initializing in {mode} mode.")
            server_instance = Server(port=2022)
            server_instance.run_server()
        else:
            mode = "client"
            print(f"App initializing in {mode} mode.")
            client = Client()
            client.run()
    except KeyboardInterrupt:
        print('\nExiting...')
        exit(0)
