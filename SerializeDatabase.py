from Database import Database
# import pickle
import logging
import win32file


class SerializeDatabase(Database):
    def __init__(self):
        """
        Initializes the SerializeDatabase by calling the parent Database
        initializer, creating an empty database with serialization capabilities.
        """
        super().__init__()
        # self.file = open('data.pkl', 'wb')
        self.path = "data1.pkl"
        self.handle = win32file.CreateFile(
            self.path,  # Path to the file
            win32file.GENERIC_WRITE,
            0,  # Do not share access
            None,  # Default security attributes
            win32file.CREATE_ALWAYS,  # Open existing file or create a new one
            win32file.FILE_ATTRIBUTE_NORMAL,  # Default file attributes
            None  # No template file
        )

    def value_set(self, key, value):
        """
        Overrides the value_set method from the Database class.
        Sets the key-value pair in the database and then serializes and saves the data.
        :param key: The key under which the value will be stored
        :param value:
        :return:
        """
        result = super().value_set(key, value)
        if result:
            try:
                data = f"{key}:{value}\n".encode('utf-8')  # Simple serialization
                win32file.SetFilePointer(self.handle, 0, win32file.FILE_END)

                # Write data to the file
                win32file.WriteFile(self.handle, data)
                # pickle.dump({key: value}, self.file)  # Serialize the single key-value pair
                logging.info(f"Serialized and saved key-value pair: {key} = {value}")
                # self.file.flush()  # Force writing buffered data to disk
            except Exception as e:
                logging.error(f"Failed to save data for key {key}: {e}")
        else:
            logging.error(f"Failed to set value for key: {key}")
        return result

    # def save(self):
    #     """
    #     Serializes the current database data and saves it to a file named 'data.pkl'.
    #     Attempts to save the contents of the database to a file using
    #     Python's pickle module
    #     :return: None
    #     """
    #     try:
    #         with open('data.pkl', 'wb') as file:
    #             pickle.dump(self.data, file)
    #         print("Data loaded from data.pkl:", self.data)
    #         logging.info("Data serialized and saved to data.pkl")
    #     except Exception as e:
    #         logging.error(f"Failed to save data: {e}")

    # def load(self):
    #     """
    #     Loads database data from a serialized file named 'data.pkl'
    #     Attempts to load data from 'data.pkl' to restore the database's
    #     state. If the file is found and successfully read, the data is loaded and
    #     a log entry is made indicating the data was loaded.
    #     :return: None
    #     """
    #     # try:
    #     #     with open('data.pkl', 'rb') as file:
    #     #         self.data = pickle.load(file)
    #     #     logging.info("Data loaded from data.pkl: %s", self.data)
    #     # except FileNotFoundError:
    #     #     logging.warning("Load failed: data.pkl no t found.")
    #     # except Exception as e:
    #     #     logging.error(f"Failed to load data: {e}")
    #
    #     with open('data.pkl', "rb") as f:
    #         while True:
    #             try:
    #                 loaded_object = pickle.load(f)
    #                 for k, v in loaded_object.items():
    #                     self.data[k] = v
    #                     # self.data[k] = value
    #             except EOFError:
    #                 break

    def load(self):
        """
        Loads database data from a serialized file using pywin32.
        Attempts to load data from the file and restore the database's state.
        If the file is found and successfully read, the data is loaded, and
        a log entry is made indicating the data was loaded.
        :return: None
        """
        try:
            # Open the file in read mode using pywin32
            handle = win32file.CreateFile(
                self.path,  # Path to the file
                win32file.GENERIC_READ,
                0,  # Do not share access
                None,  # Default security attributes
                win32file.OPEN_EXISTING,  # Open existing file
                0,  # Default file attributes
                None  # No template file
            )

            # Read the entire file content
            data_bytes = b""
            while True:
                chunk, _ = win32file.ReadFile(handle, 4096)  # Read 4KB chunks
                data_bytes += _
                if not chunk:
                    break


            # Close the file handle
            win32file.CloseHandle(handle)

            # Deserialize data manually (assuming it was stored as key-value pairs in text format)
            data_str = data_bytes.decode('utf-8')
            for line in data_str.splitlines():
                if ":" in line:  # Ensure valid key-value format
                    key, value = line.split(":", 1)
                    self.data[key] = value.strip()  # Restore data to the dictionary

            logging.info("Data successfully loaded from %s", self.path)
        except FileNotFoundError:
            logging.warning("Load failed: %s not found.", self.path)
        except Exception as e:
            logging.error(f"Failed to load data: {e}")
