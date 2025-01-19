from SerializeDatabase import SerializeDatabase
import threading
import multiprocessing
import logging

MAX = 10


class SyncDatabase(SerializeDatabase):
    """
    A synchronized database class that extends SerializeDatabase to handle concurrent
    read and write operations using threading or multiprocessing locks
    """
    def __init__(self, mode='threads'):
        """
        Initializes the SyncDatabase with support for concurrent access control.
        Sets up synchronization mechanisms for concurrent reading and writing,
        allowing up to MAX readers to access the database simultaneously.
        Depending on the specified mode ('threads' or 'processes'), appropriate
        locking mechanisms are selected
        :param mode: Defines the concurrency mode, either 'threads' or 'processes'
        """
        super().__init__()
        self.mode = mode
        self.max_readers = MAX
        self.read_count = 0
        self.read_array = [0]*MAX  # Tracking reading and writing status of entries
        # 0: no one is accessing the file, 1: someone is reading the file, 2: someone is waiting to write in the file
        # Locks for synchronization based on selected mode
        if mode == 'threads':
            self.semaphore = threading.Semaphore(value=MAX)  # Protects read_count
            self.read_lock = threading.Lock()
            self.write_lock = threading.Lock()  # Ensures mutual exclusion for writing
            self.write_try_lock = threading.Lock()  # Ensures mutual exclusion for writing
        elif mode == 'processes':
            self.semaphore = multiprocessing.Semaphore(value=MAX)
            self.read_lock = multiprocessing.Lock()
            self.write_lock = multiprocessing.Lock()
        logging.info(f"SyncDatabase initialized in {self.mode} mode with max readers {self.max_readers}")

    def readers_still_reading(self):
        """
        Checks if there are any active readers in the database.
        Iterates through `read_array` to identify any active readers
        (indicated by 1). If no readers are found, it prepares the array for a
        write operation by setting all entries to 2.
        :return: readers_left: True if there are active readers; otherwise, False
        """
        readers_left = False
        for element in self.read_array:
            if element == 0:  # no active accessing
                self.read_count += 1
                logging.debug("num of readers: " + str(self.read_count))
                self.read_array[self.read_count-1] = 2  # write intent
            elif element == 1:  # active reader
                readers_left = True
        logging.debug(f"Readers still reading: {self.read_count}")
        return readers_left

    def value_set(self, key: object, value: object):
        """
        Sets a key-value pair in the database with concurrent access control.
        Ensures exclusive access for writing by acquiring a write lock.
        If there are active readers, it waits until they are finished before proceeding.
        After setting the value, it resets reader tracking variables.
        :param key: The key under which the value will be stored
        :param value: The value to store in the database
        :return: None
        """
        logging.debug(f"Attempting to set key '{key}' with value '{value}'")
        self.write_try_lock.acquire()
        self.write_lock.acquire()
        try:
            self.write_try_lock.release()
            super().value_set(key, value)
            logging.info(f"Set key '{key}' with value '{value}'")
        # Reset reader tracking (release reader spots)
        finally:
            self.write_lock.release()

    def value_get(self, key):
        """
        Retrieves the value associated with a given key with concurrent read control.
        Acquires a read lock and allows multiple readers up to `max_readers`. If the
        limit is reached, it logs a warning. After retrieval, it releases the read lock
        :param key: The key to retrieve from the database
        :return: The value associated with the key if it exists; otherwise, a warning message.
        """
        self.write_try_lock.acquire()
        self.write_try_lock.release()

        self.semaphore.acquire()
        logging.debug(f"Attempting to get key '{key}'")
        try:
            self.read_lock.acquire()
            self.read_count += 1
            if self.read_count == 1:
                # First reader locks the write lock to prevent writers
                self.write_lock.acquire()
            self.read_lock.release()

            result = super().value_get(key)
            if result is not None:
                logging.info(f"Retrieved key '{key}' with value '{result}'")
            else:
                logging.warning(f"Key '{key}' not found.")
        finally:
            self.read_lock.acquire()
            self.read_count -= 1
            if self.read_count == 0:
                # Last reader releases the write lock
                self.write_lock.release()
            self.read_lock.release()
            self.semaphore.release()
        return result

    def value_delete(self, key):
        """
        Deletes a key-value pair from the database with concurrent access control.
        Ensures exclusive access for deletion by acquiring a write lock.
        It waits until there are no active readers before proceeding with the delete operation.
        After deleting, it resets reader tracking variables
        :param key: The key to delete from the database
        :return: The deleted value if it existed; otherwise, None.
        """
        logging.debug(f"Attempting to delete key '{key}'")
        self.write_lock.acquire()
        try:
            deleted_value = super().value_delete(key)
            logging.info(f"Deleted key '{key}' (if it existed)")
            # # Reset reader tracking (release reading spots)
        finally:
            self.write_lock.release()
            return deleted_value  # Return the deleted value if it existed
