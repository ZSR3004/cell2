# add a clear command, maybe make this a class?

def main():
    while True:
        try:
            command = input("> ").strip()
            print(command)
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()