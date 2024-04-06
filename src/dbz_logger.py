from pathlib import Path

class DBZLogger:
    def __init__(self, node_id) -> None:
        self.id = node_id

    def write_dump(self, message):
        file_path = f"./log_nodes_{self.id}"
        # Make sure the directory exists
        Path(file_path).mkdir(parents=True, exist_ok=True)
        # Write the message to the file

        with open(f"log_nodes_{self.id}/dump.txt", "a") as dump_file:
            dump_file.write(message + "\n")
        print(f"Server {self.id}: {message}")

    def write_metadata(self, commit_length, current_term, voted_for):
        file_path = f"./log_nodes_{self.id}"
        Path(file_path).mkdir(parents=True, exist_ok=True)
        # store metadata as commit_length(\n)term(\n)nodeId_voted_for
        with open(f"log_nodes_{self.id}/metadata.txt", "w") as metadata_file:
            metadata_file.write("{}\n{}\n{}".format(commit_length, current_term, voted_for))

    def write_logs(self, message):
        file_path = f"./log_nodes_{self.id}"
        Path(file_path).mkdir(parents=True, exist_ok=True)
        with open(f"log_nodes_{self.id}/logs.txt", "a") as logs_file:
            logs_file.write(message + "\n")
        print(f"Server {self.id}: {message}")