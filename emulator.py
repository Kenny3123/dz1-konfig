import os
import sys
import tarfile
from pathlib import Path
import toml


class ShellEmulator:
    def __init__(self, config_path_or_dict):
        """Конструктор принимает путь к конфигурации или словарь."""
        if isinstance(config_path_or_dict, str):
            self.load_config(config_path_or_dict)
        elif isinstance(config_path_or_dict, dict):
            self.config = config_path_or_dict
        else:
            raise ValueError("Invalid configuration format. Must be a path or dict.")

        self.fs_root = Path("/tmp/filesystem")
        self.current_dir = self.fs_root
        self.user = self.config["user"]

        self.extract_filesystem()

    def load_config(self, config_path):
        """Загрузка конфигурации из TOML-файла."""
        self.config = toml.load(config_path)

    def extract_filesystem(self):
        tar_path = self.config["filesystem"]
        if not Path(tar_path).exists():
            raise FileNotFoundError(f"Filesystem archive '{tar_path}' not found.")
        if not os.access(tar_path, os.R_OK):
            raise PermissionError(f"Permission denied for filesystem archive '{tar_path}'.")

        self.fs_root = Path("/tmp/filesystem")
        self.fs_root.mkdir(parents=True, exist_ok=True)
        with tarfile.open(tar_path, "r") as tar:
            tar.extractall(self.fs_root)

    def run(self):
        """Запуск основного цикла shell."""
        while True:
            try:
                command = input(f"{self.user}@emulator:{self.current_dir}> ").strip()
                if command == "exit":
                    print("Exiting...")
                    break
                self.execute_command(command)
            except Exception as e:
                print(f"Error: {e}")

    def execute_command(self, command):
        """Обработка команд shell."""
        parts = command.split()
        if not parts:
            return
        cmd, *args = parts
        if cmd == "ls":
            self.ls()
        elif cmd == "cd":
            self.cd(args)
        elif cmd == "mkdir":
            self.mkdir(args)
        elif cmd == "tac":
            self.tac(args)
        else:
            print(f"Unknown command: {cmd}")

    def ls(self):
        """Команда ls."""
        try:
            print("\n".join(os.listdir(self.current_dir)))
        except Exception as e:
            print(f"Error: Could not list directory. {e}")

    def cd(self, args):
        """Команда cd."""
        if len(args) != 1:
            print("Usage: cd <directory>")
            return

        target = self.current_dir / args[0]
        try:
            target = target.resolve()
            if not target.exists():
                print(f"Error: Directory '{args[0]}' does not exist.")
            elif not target.is_dir():
                print(f"Error: '{args[0]}' is not a directory.")
            else:
                self.current_dir = target
        except Exception as e:
            print(f"Error: Could not change directory. {e}")

    def mkdir(self, args):
        """Команда mkdir."""
        if len(args) != 1:
            print("Usage: mkdir <directory>")
            return

        target = self.current_dir / args[0]
        try:
            if target.exists():
                print(f"Error: Directory '{args[0]}' already exists.")
            else:
                target.mkdir(parents=True)
                print(f"Directory '{args[0]}' created.")
        except Exception as e:
            print(f"Error: Could not create directory. {e}")

    def tac(self, args):
        """Команда tac."""
        if len(args) != 1:
            print("Usage: tac <file>")
            return

        filepath = self.current_dir / args[0]
        if filepath.is_file():
            try:
                with open(filepath, "r") as f:
                    lines = f.readlines()
                print("".join(reversed(lines)))
            except Exception as e:
                print(f"Error: Could not read file. {e}")
        else:
            print(f"Error: File '{args[0]}' not found.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python emulator.py <config_path>")
        sys.exit(1)

    config_path = sys.argv[1]
    emulator = ShellEmulator(config_path)
    emulator.run()
