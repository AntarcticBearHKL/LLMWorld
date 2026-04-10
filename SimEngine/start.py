from .server import SimServer

def main():
    server = SimServer()
    server.interactive_mode()

if __name__ == "__main__":
    main()