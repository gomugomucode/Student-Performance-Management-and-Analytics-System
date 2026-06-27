from database.schema import create_tables

def main():
    print("Initializing Student Performance Management System...")
    # Setup database tables on startup
    create_tables()

if __name__ == "__main__":
    main()

