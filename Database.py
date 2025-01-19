import logging

logging.basicConfig(filename="database.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', )


class Database:
    def __init__(self):
        """
        Initializes the database by creating an empty dictionary to store data
        """
        self.data = {}
        logging.info("Database initialized")

    def value_set(self, key, value):
        """
        Stores a key-value pair in the database.
        :param key: The key under which the value will be stored
        :param value: The value to store in the database
        :return: True if the operation is successful
        """
        self.data[key] = value
        logging.info(f"Set: {key} = {value}")
        return True

    def value_get(self, key):
        """
        Retrieves the value associated with a given key
        :param key: The key whose value is to be retrieved
        :return: The value associated with the key if it exists, otherwise None
        """
        if key in self.data:
            logging.info(f"Get: {key} = {self.data[key]}")
            return self.data[key]
        else:
            logging.info(f"Get: {key} = None (key does not exist)")
            return None

    def value_delete(self, key):
        """
        Deletes a key-value pair from the database.
        If the specified key exists in the database, this method removes the key
        along with its associated value. If the key does not exist, no deletion
        occurs and the method logs that the key was not found.
        :param key: The key to delete from the database
        :return: None
        """
        if key in self.data:
            self.data.pop(key)
            logging.info(f"Delete: {key} (successful)")
        else:
            logging.info(f"Delete: {key} (key does not exist)")
            return None
