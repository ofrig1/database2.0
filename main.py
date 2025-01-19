from SyncDatabase import SyncDatabase
import threading
import logging
import win32file


def writer(db, key, value):
    """
    Write a key-value pair to the database
    :param db: An instance of SyncDatabase
    :param key: The key to store in the database
    :param value: The value associated with the key
    """
    logging.info(f"Writer thread attempting to set key '{key}' with value '{value}'")
    db.value_set(key, value)
    print(f"Writer set {key} to {value}")
    logging.info(f"Writer thread set key '{key}' to '{value}'")


def reader(db, key):
    """
    Read a value associated with a key from the database
    :param db: An instance of SyncDatabase
    :param key: The key to retrieve from the database
    """
    thread_id = threading.get_ident()  # Get the current thread ID
    try:
        logging.info(f"Reader thread with ID {thread_id} attempting to get key '{key}'")
        value = db.value_get(key)
        print(f"Reader (Thread ID: {thread_id}) got {key}: {value}")
        if value is not None:
            logging.info(f"Reader thread with ID {thread_id} retrieved key '{key}' with value '{value}'")
        else:
            logging.warning(f"Reader thread with ID {thread_id} could not find key '{key}'")
    except Exception as e:
        logging.error(f"Failed: Reader thread with ID {thread_id} attempting to get key '{key}'")


def main():
    """
    Initializes a SyncDatabase instance, performs several write and delete
    operations, saves and loads the database state, and launches concurrent threads
    to read and write data.
    """
    # Initialize database and add initial data
    my_database = SyncDatabase()
    my_database.value_set('house', '39 lylewood')
    my_database.value_set('city', 'tenafly')
    my_database.value_set('country', 'US')
    my_database.value_set('state', 'new Jersey')

    # Retrieve and delete a value
    print("Get 'city':", my_database.value_get('city'))
    my_database.value_delete('city')
    if my_database.value_get('city') is None:
        print("no value")
    else:
        print(my_database.value_get('city'))
    # Close the file handle
    win32file.CloseHandle(my_database.handle)
    # Save and load data
    # logging.info("Saving current database state")
    # my_database.save()
    logging.info("Loading saved database state")
    my_database.data = {}
    my_database.load()

    # Start concurrent read operations
    # threads = []
    # logging.info("Starting multiple reader threads.")
    # for i in range(11):
    #     t_read = threading.Thread(target=reader, args=(my_database, 'country'))
    #     threads.append(t_read)
    #
    # # Start all threads
    # for t in threads:
    #     t.start()
    #
    # # Wait for all threads to finish
    # for t in threads:
    #     t.join()
    #
    # # Final load to check data consistency
    # logging.info("Loading database state after concurrent read operations.")
    # my_database.data = {}
    # my_database.load()
    # print(my_database.data)

    # Start concurrent read and write operations
    threads = []
    logging.info("Starting concurrent read and write threads.")
    for i in range(4):
        t_read = threading.Thread(target=reader, args=(my_database, 'country'))
        threads.append(t_read)
    t_write = threading.Thread(target=writer, args=(my_database, f'world', f'earth'))
    threads.append(t_write)

    # Start all threads
    for t in threads:
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    my_database.data = {}
    # Final load to check data consistency
    logging.info("Loading final database state after concurrent operations.")
    my_database.load()
    print(my_database.data)


if __name__ == '__main__':
    main()
