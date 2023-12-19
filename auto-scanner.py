import sys
import subprocess
import os
import time

# recursively scan folder, grabbing the write date
# compare it to the output files. 

class Scanner:
    def __init__(self, folder):
        self.debug = True

        self.valid_audio_files = [".mp3", ".m4a", ".wav", ".mp4", ".aac"]
        self.tracked_items = []
        self.folder = folder
        if not os.path.exists(folder):
            raise Exception("root folder does not exist: " + folder)
        
        self.debug_log(f"INFO: scanning folder set to {folder}")


    def debug_log(self, message):
        if self.debug:
            print(message)

    
    # scan a folder for potential work items
    def scan_folder(self, folder):
        entries = os.listdir(folder)
        self.debug_log(f"INFO: scanning {folder} for entries. {len(entries)} found")

        subfolders = []
        for entry in entries:
            fullpath = os.path.join(folder, entry)
            if os.path.isdir(fullpath):
                subfolders.append(fullpath)
                continue

            # only care about audio files, or files we can get audio from
            splits = os.path.splitext(fullpath)
            if splits[1] not in self.valid_audio_files:
                continue

            if entry not in self.tracked_items:
                self.debug_log(f"new file found, adding to queue: {fullpath}")
                self.tracked_items.append(fullpath)
            
        for subfolder in subfolders:
            self.scan_folder(subfolder)


    def run_whisper(self, filename):
        print(f"INFO: Running whisper on {filename}")

        command = "whisper"
        command_args = [command, "--model", "medium", "--language", "English", f'{filename}']

        result = subprocess.run(command_args)
 

    # remove files that have been deleted from the tracked list
    def cleanup_tracked_files(self):
        cleanup_items = []

        for filepath in self.tracked_items:
            if not os.path.exists(filepath):
                cleanup_items.append(filepath)

        for filepath in cleanup_items:
            self.debug_log(f"INFO: removing {filepath} from tracking")
            self.tracked_items.remove(filepath)


    # process a single tracked file
    def process_tracked_file(self, filepath):
        processfile = False
        splits = os.path.splitext(filepath)

        outputfilepath = splits[0] + ".txt"
        if not os.path.exists(outputfilepath):
            processfile = True

        else:
            mtime = os.path.getmtime(filepath)
            outputmtime = os.path.getmtime(outputfilepath)

            if outputmtime < mtime:
                processfile = True
            else:
                self.debug_log(f"WARN: ignoring file {filepath} as its already been done")
        
        if not processfile:
            return
        
        self.run_whisper(filepath)


    # process all the tracked files
    def process_tracked_files(self):
        self.debug_log(f"processing {len(self.tracked_items)} files")
        for entry in self.tracked_items:
            if not os.path.exists(entry):
                self.debug_log("ERROR: {entry} does not exist, skipping")
                continue

            self.process_tracked_file(entry)


    # scan for new work
    def poll_for_work(self):
        while True:
            self.scan_folder(self.folder)
            self.cleanup_tracked_files()
            self.process_tracked_files()
            time.sleep(10 * 60)


if __name__ == "__main__":
    # default scan location
    SCANNER_FOLDER = "/transcribequeue"
    if len(sys.argv) >= 2:
        SCANNER_FOLDER = sys.argv[1]

    scanner = Scanner(SCANNER_FOLDER)
    scanner.poll_for_work()
