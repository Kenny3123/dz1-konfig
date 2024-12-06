import unittest
from emulator import ShellEmulator
from pathlib import Path

class TestShellCommands(unittest.TestCase):
    def setUp(self):
        self.emulator = ShellEmulator("config.toml")
        self.emulator.current_dir = self.emulator.fs_root / "test"

    def test_ls(self):
        self.emulator.current_dir.mkdir(exist_ok=True)
        (self.emulator.current_dir / "file1.txt").touch()
        (self.emulator.current_dir / "file2.txt").touch()
        output = self.emulator.ls()
        self.assertIn("file1.txt", output)
        self.assertIn("file2.txt", output)

    def test_mkdir(self):
        self.emulator.mkdir(["new_folder"])
        self.assertTrue((self.emulator.current_dir / "new_folder").exists())

if __name__ == "__main__":
    unittest.main()