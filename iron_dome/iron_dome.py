# This library is to parse easily the args
import argparse
# Library for getting signals from the computer
import signal
# Library for working with time commonly used for time.sleep(t)
import time
# Library for getting info from processes, controlling processes
import psutil
# Library for getting the local time, commonly used for save the current_time in a variable
import datetime
# Library for creating, moving, deleting, checking if exists, etc, files, folders
import os
# This works for math operations
import math
# Library for saving the logs in a text.log or any extension. Its really useful.
import logging
# Library for checking all the events that happens in a folder or in a file.
# Those events would be created, deleted, modified, moved, closed, opened
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, EVENT_TYPE_CREATED, EVENT_TYPE_DELETED, EVENT_TYPE_MODIFIED, \
    EVENT_TYPE_MOVED, EVENT_TYPE_CLOSED, EVENT_TYPE_OPENED
# This is our compatible extensions for our project(iron_dome.py)
list_extensions = ['.txt', '.csv', '.log', '.xml', '.json',
                   '.doc', '.docx', '.pdf', '.ppt', '.pptx', '.xls', '.xlsx',
                   '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',
                   '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv',
                   '.mp3', '.wav', '.flac', '.aac', '.wma',
                   '.zip', '.rar', '.tar', '.gz', '.7z',
                   '.py', '.java', '.cpp', '.html', '.css', '.js',
                   '.ini', '.cfg', '.yaml', '.toml',
                   '.db', '.sqlite', '.sql', '.csv',
                   '.exe', '.dll', '.sh', '.bat', '.app']
# The path as a global variable where all the events is going to be logged
path_log = '/var/log/irondome.log'
# The critical zone will be the path where we want to monitor
critical_zone = ['/home']
# To be tidy, I guess that using a dict is really useful.
# The next structure is what we want to get of dict_log
dict_log = {'path': {
    'created': {
        'creation_date': '',
        'previous_entropy': 0,
        'previous_size': 0,
        'last_opened': 'No-date'
    },
    'opened': {
        'previous_entropy': 0,
        'previous_size': 0,
        'opened_date': 'No-date',
        'last_opened': 'No-date'
    },
    'modified': {
        'current_size': 0,
        'modification_date': 'No-date',
        'current_entropy': 0,
        'last_modification': 'No-date'
    },
    'deleted': {
        'previous_entropy': 0,
        'previous_size': 0,
        'creation_date' : 'No-date',
        'deleted_date': 'No-date'
    }
}}
# Adjust the threshold value as per your requirements
threshold_seconds = 1
# The FileSystemEventHandler class provided by the 'watchdog' library does not have an attribute for
# storing previous_size, previous_entropy, previous date,etc.
# So we need to create a custom class that inherits from 'FileSystemEventHandler' and add the necessary attribute
class CustomEventHandler(FileSystemEventHandler):
    # As a object, we need to define the args that our object is going to need from outside
    # As a constructor, it will need two attributes extensions and folders
    """
        Base file system event handler that you can override methods from.
        """
    def __init__(self, extensions, folders):
        super().__init__()
        self.folders = folders
        self.extensions = extensions
        self.previous_size = {}
        self.previous_entropy = {}
        self.previous_date = {}
        self.creation_date = {}
        self.last_opened = {}

    def dispatch(self, event):
        """Dispatches events to the appropriate methods.

        :param event:
            The event object representing the file system event.
        :type event:
            :class:`FileSystemEvent`
        """

        self.on_any_event(event)
        {
            EVENT_TYPE_CREATED: self.on_created,
            EVENT_TYPE_DELETED: self.on_deleted,
            EVENT_TYPE_MODIFIED: self.on_modified,
            EVENT_TYPE_MOVED: self.on_moved,
            EVENT_TYPE_CLOSED: self.on_closed,
            EVENT_TYPE_OPENED: self.on_opened,
        }[event.event_type](event)
        monitor_usage()
        for folder in self.folders:
            check_file_reading_abuse(folder, threshold_seconds)
        # else: pass
    def on_closed(self, event):
        """Called when a file opened for writing is closed.

                :param event:
                    Event representing file closing.
                :type event:
                    :class:`FileClosedEvent`
                """
        self.dispatcher_type(event)

    def on_moved(self, event):
        """Called when a file or a directory is moved or renamed.

                :param event:
                    Event representing file/directory movement.
                :type event:
                    :class:`DirMovedEvent` or :class:`FileMovedEvent`
                """
        self.dispatcher_type(event)
    def on_opened(self, event):
        self.dispatcher_type(event)
    def on_created(self, event):
        """Called when a file or directory is created.

                :param event:
                    Event representing file/directory creation.
                :type event:
                    :class:`DirCreatedEvent` or :class:`FileCreatedEvent`
                """
        self.dispatcher_type(event)
    def on_deleted(self, event):
        """Called when a file or directory is deleted.

                :param event:
                    Event representing file/directory deletion.
                :type event:
                    :class:`DirDeletedEvent` or :class:`FileDeletedEvent`
                """
        self.dispatcher_type(event)
    def on_modified(self, event):
        """Called when a file or directory is modified.

                :param event:
                    Event representing file/directory modification.
                :type event:
                    :class:`DirModifiedEvent` or :class:`FileModifiedEvent`
                """
        self.dispatcher_type(event)
    def dispatcher_type(self, event):
        # Firstly, this function will redirect if the event is a directory os a file
        if event.is_directory:
            self.log_folder(event)
        else:
            # Secondly, for each ext in self.extensions(which is our extensions that we have put
            # python iron_dome.py --extensions [extension1 extension2 etc]
            for ext in self.extensions:
                # After iterate individually each ext in extensions we will check if our extensions are
                # in the list_extensions(which is a global variable)
                if ext in list_extensions:
                    extension_file = os.path.splitext(event.src_path)[1]
                    # Finally, the extension of the file of the event has to be the same of the ext(which we are checking
                    # at the beginning of the loop for)
                    if extension_file == ext:
                        # Now we are in the lay where the event.event_type will be redirect to his correct function
                        if event.event_type == 'deleted' or event.event_type == 'moved':
                            self.on_deleted_operation(event)
                        elif event.event_type == 'created':
                            self.on_created_operation(event)
                        elif event.event_type == 'modified':
                            self.on_modified_operation(event)
                        elif event.event_type == 'opened':
                            self.on_opened_operation(event)
                        elif event.event_type == 'closed':
                            self.on_closed_operation(event)
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
    def on_opened_operation(self, event):
        file_path = event.src_path
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        if file_path in self.last_opened:
            opened_dict = {
                'opened': {
                    'previous_size': self.previous_size[file_path],
                    'previous_entropy': self.previous_entropy[file_path],
                    'last_opened': self.last_opened[file_path],
                    'opened_date': current_time
                }
            }
            dict_log[file_path].update(opened_dict)
            logging.info(f"Path: {file_path}- Event: {event.event_type} - {dict_log[file_path]['opened']}")
            self.last_opened[file_path] = current_time

        opened_dict = {
            'opened': {
                'previous_size': self.previous_size[file_path],
                'previous_entropy': self.previous_entropy[file_path],
                'last_opened': self.last_opened[file_path],
                'opened_date': current_time
            }
        }
        dict_log[file_path].update(opened_dict)
    def on_created_operation(self, event):
        file_path = event.src_path
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.creation_date[file_path] = current_time
        self.previous_entropy[file_path] = 0
        self.previous_size[file_path] = 0
        self.last_opened[file_path] = 'nodate'
        created_dict = {
            'created': {
                'creation_date': current_time,
                'previous_entropy': 0,
                'previous_size': 0,
                'last_opened': 'No-date'
            }
        }
        dict_log[file_path] = created_dict
        logging.info(
            f"Path: {file_path} - Event: {event.event_type} - {dict_log[file_path]}")
    def on_modified_operation(self, event):
        file_path = event.src_path
        current_size = self.get_file_size(file_path)
        modification_date = self.creation_time(file_path).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        # logging.info(f'Its a file!!{current_size} creation {creation_time}')
        current_entropy = self.calculate_entropy(file_path)

        if file_path in self.previous_size or file_path in self.previous_date or file_path in self.previous_entropy:
            previous_entropy = self.previous_entropy[file_path]
            try:
                previous_date = self.previous_date[file_path]
            except:
                previous_date = self.creation_date[file_path]
            previous_size = self.previous_size[file_path]
            modified_dict = {'modified': {
                'previous_date_of_modification': previous_date,
                'current_size': current_size,
                'previous_size': previous_size,
                'current_entropy': current_entropy,
                'previous_entropy': previous_entropy,
                'creation_date': dict_log[file_path]['created']['creation_date']
            }}
            dict_log[file_path].update(modified_dict)
            logging.info(f"Path: {file_path} - Event: {event.event_type} - {dict_log[file_path]['modified']}")
        self.previous_entropy[file_path] = current_entropy
        self.previous_size[file_path] = current_size
        self.previous_date[file_path] = modification_date
        modified_dict = {'modified': {
            'previous_date_of_modification': modification_date,
            'current_size': current_size,
            'previous_size': self.previous_size,
            'current_entropy': current_entropy,
            'previous_entropy': self.previous_entropy,
            'creation_date': dict_log[file_path]['created']['creation_date']
        }}
        dict_log[file_path].update(modified_dict)
    def on_deleted_operation(self, event):
        file_path = event.src_path
        event_type = event.event_type
        logging.info(f"{event_type}: {file_path} Last size: {dict_log[file_path]['modified']['current_size']} KB Last entropy: {dict_log[file_path]['modified']['current_entropy']} Date of creation: {dict_log[file_path]['created']['creation_date']}")
    def calculate_entropy(self, file_path):
        # Adjust the chunk size as per your requirements
        chunk_size = 64 * 1024
        total_bytes = 0
        entropy = 0
        with open(file_path, 'rb') as file:
            while True:
                data = file.read(chunk_size)
                if not data:
                    break
                total_bytes += len(data)
                byte_frequencies = [0] * 256

                for byte in data:
                    byte_frequencies[byte] += 1

                for frequency in byte_frequencies:
                    if frequency == 0:
                        continue
                    probability = frequency / chunk_size
                    entropy -= probability * math.log2(probability)
                    try:
                        return entropy / math.log2(total_bytes)
                    except:

                        return entropy

    def get_file_size(self, file_path) -> int:
        return os.path.getsize(file_path)
    def creation_time(self, file_path) -> datetime:
        stat_info = os.stat(file_path)
        creation_time = stat_info.st_ctime
        creation_datetime = datetime.datetime.fromtimestamp(creation_time)
        return creation_datetime
    def log_folder(self, event):
        # It is the logger of the folder
        dir_path = event.src_path
        type_event = event.event_type
        try:
            files_in_path = os.listdir(dir_path)
            logging.info(f"{type_event}: {dir_path} Contents: {len(files_in_path)}")
        except:
            logging.info(f"{type_event}: {dir_path} Contents: There is no items")
    def on_closed_operation(self, event):
        file_path = event.src_path
        event_type = event.event_type
        logging.info(f"{event_type}: {file_path} Last size: {dict_log[file_path]['modified']['current_size']} KB Last entropy: {dict_log[file_path]['modified']['current_entropy']} Date of creation: {dict_log[file_path]['created']['creation_date']}")
def init_iron_dome():
    # Create the argument parser
    parser = argparse.ArgumentParser(description='Iron_dome.py - Monitor a folder and provide real-time information about its files.')

    # Add the positional arguments
    parser.add_argument('--folders', nargs='+', help='List of folders', default=critical_zone)
    parser.add_argument('--extensions', nargs='+', help='List of file extensions to filter', default=list_extensions)
    args = parser.parse_args()
    folders = args.folders
    extensions = args.extensions

    if len(folders) == 1:
        critical_path = folders[0]
        print(f"Monitoring the path: {critical_path}\n")
        print(f"Monitoring this extensions: {extensions}\n")
        # Create an observer for one folder
        event_handler = CustomEventHandler(extensions, folders)
        observer = Observer()
        observer.schedule(event_handler, critical_path, recursive=True)
        # Start the observer
        observer.start()
        # Run indefinitely:
        try:
            while True:
                pass
        except KeyboardInterrupt:
            observer.stop()

        observer.join()
    else:
        # Create an observer for each folder
        print(f"Monitoring the path: {folders}\n")
        print(f"Monitoring this extensions: {extensions}\n")
        observers = []
        for folder in folders:
            observer = Observer()
            event_handler = CustomEventHandler(extensions, folders)
            observer.schedule(event_handler, folder, recursive=True)
            observers.append(observer)
        # Start the observers
        for observer in observers:
            observer.start()
        # Run indefinitely:
        try:
            while True:
                pass
        except KeyboardInterrupt:
            for observer in observers:
                observer.stop()
        for observer in observers:
            observer.join()

def check_file_reading_abuse(folder_path, threshold_seconds):
    # To check the file reading abuse, this will compare the time_diff and our threshold_seconds(global variable)
    current_time = time.time()
    abuse_detected = False
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            access_time = os.path.getatime(file_path)
            # The time_diff is the difference between access_time and current_time
            time_diff = current_time - access_time
            if time_diff < threshold_seconds:
                # If the time_diff is less than threshold_seconds
                # The abuse detected will be triggered as True
                abuse_detected = True
                # And will log to our log file
                logging.warning(f"Posible abuse detected: {file_path}")
    if not abuse_detected:
        pass

def monitor_usage():
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        # Get disk usage
        disk_usage = psutil.disk_usage('/')
        disk_percent = disk_usage.percent
        disk_mb = disk_usage.used / (1024 * 1024)
        # Get memory usage total
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_mb = memory.used / (1024 * 1024)
        # Get memory usage pid
        process_pid = psutil.Process(os.getpid())
        memory_usage_pid = process_pid.memory_info().rss / 1024 / 1024  # Memory usage of the current process in MB
        # print(f"\rMemory usage pid {process_pid}: {round(memory_usage_pid, 3)} MB  CPU Usage: {cpu_percent:6.2f}%  Disk Usage: {disk_percent:6.2f}%   {disk_mb:9.2f} MB  Memory Usage: {memory_percent:6.2f}%   {memory_mb:9.2f} MB ", end="")
        log_message = f"Memory usage pid {os.getpid()}: {round(memory_usage_pid, 3)} MB  CPU Usage: {cpu_percent:6.2f}%  Disk Usage: {disk_percent:6.2f}%   {disk_mb:9.2f} MB  Memory Usage: {memory_percent:6.2f}%   {memory_mb:9.2f} MB "
        print("\r"+log_message, end="")
        if memory_usage_pid > 100:
            logging.warning(f"Memory usage exceeds 100MB: {memory_usage_pid} MB")
            os.kill(os.getpid(), signal.SIGTERM)
        else: pass

def print_intro():
    project_name = "Iron_dome"
    version = "alfa"
    powered_by = "jonko and alejandro"

    intro_text = f"Welcome to {project_name} version {version}"
    powered_by_text = f"Powered by {powered_by}"

    # Calculate the width of the frame based on the longest line of text
    frame_width = max(len(intro_text), len(powered_by_text)) + 4

    # Print the top frame border
    print("+" + "-" * (frame_width - 2) + "+")

    # Print the intro text with padding and frame borders
    print("| " + intro_text.center(frame_width - 4) + " |")

    # Print a line to separate the intro text and powered by text
    print("|" + "-" * (frame_width - 2) + "|")

    # Print the powered by text with padding and frame borders
    print("| " + powered_by_text.center(frame_width - 4) + " |")

    # Print the bottom frame border
    print("+" + "-" * (frame_width - 2) + "+")
if __name__ == '__main__':
    logging.basicConfig(filename=path_log, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    if os.getpid() == 0:
        print("The project is not running with root privileges.")
    else:
        print_intro()
        print("The project is running with root privileges")
        init_iron_dome()
