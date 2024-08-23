from .server import server


def run():
    # Run gRPC server
    server.run_server()


if __name__ == '__main__':
    run()
