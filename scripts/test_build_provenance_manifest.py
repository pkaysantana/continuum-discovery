import unittest
import os
import tempfile
import shutil
import subprocess
import json
import csv
import time

from build_provenance_manifest import build_manifest, get_file_metadata, get_git_tracked_files

class TestBuildProvenanceManifest(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for our mock repository
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = tempfile.mkdtemp()
        
        # Initialize a git repository
        subprocess.run(["git", "init"], cwd=self.test_dir, check=True, stdout=subprocess.DEVNULL)
        
        # Configure local git for commits
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.test_dir, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.test_dir, check=True)
        
        # Create a dummy file 1 (simulating a text file)
        self.file1_path = os.path.join(self.test_dir, "dummy1.txt")
        with open(self.file1_path, "wb") as f:
            f.write(b"Hello, this is a test.\n")
            
        # Create a dummy file 2 (simulating an opaque scientific file, like PDB)
        self.file2_path = os.path.join(self.test_dir, "structure.pdb")
        with open(self.file2_path, "wb") as f:
            f.write(b"HEADER    TEST STRUCTURE\nATOM      1  N   ALA A   1      11.104  10.231  12.012  1.00 10.00           N\n")
            
        # Commit file 1
        subprocess.run(["git", "add", "dummy1.txt"], cwd=self.test_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Add dummy1"], cwd=self.test_dir, check=True, stdout=subprocess.DEVNULL)
        
        # Wait a moment so timestamps differ (if resolution allows, mostly for order)
        time.sleep(1)
        
        # Commit file 2
        subprocess.run(["git", "add", "structure.pdb"], cwd=self.test_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Add structure"], cwd=self.test_dir, check=True, stdout=subprocess.DEVNULL)
        
        # Modify file 1 and commit again
        with open(self.file1_path, "ab") as f:
            f.write(b"More data.\n")
        
        subprocess.run(["git", "add", "dummy1.txt"], cwd=self.test_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Modify dummy1"], cwd=self.test_dir, check=True, stdout=subprocess.DEVNULL)

    def tearDown(self):
        # Clean up temporary directories
        def remove_readonly(func, path, _):
            import stat
            os.chmod(path, stat.S_IWRITE)
            func(path)
            
        shutil.rmtree(self.test_dir, onerror=remove_readonly)
        shutil.rmtree(self.output_dir, onerror=remove_readonly)

    def test_get_git_tracked_files(self):
        files = get_git_tracked_files(self.test_dir)
        self.assertIn("dummy1.txt", files)
        self.assertIn("structure.pdb", files)
        self.assertEqual(len(files), 2)
        
    def test_get_file_metadata(self):
        meta_txt = get_file_metadata(self.test_dir, "dummy1.txt")
        self.assertIsNotNone(meta_txt)
        self.assertEqual(meta_txt["relative_path"], "dummy1.txt")
        self.assertEqual(meta_txt["extension"], ".txt")
        self.assertEqual(meta_txt["byte_size"], len(b"Hello, this is a test.\nMore data.\n"))
        self.assertTrue(len(meta_txt["sha256"]) == 64) # SHA-256 length in hex
        self.assertTrue(len(meta_txt["first_commit"]) > 0)
        self.assertTrue(len(meta_txt["last_commit"]) > 0)
        self.assertNotEqual(meta_txt["first_commit"], meta_txt["last_commit"]) # file 1 has 2 commits
        
        meta_pdb = get_file_metadata(self.test_dir, "structure.pdb")
        self.assertIsNotNone(meta_pdb)
        self.assertEqual(meta_pdb["relative_path"], "structure.pdb")
        self.assertEqual(meta_pdb["extension"], ".pdb")
        self.assertEqual(meta_pdb["byte_size"], len(b"HEADER    TEST STRUCTURE\nATOM      1  N   ALA A   1      11.104  10.231  12.012  1.00 10.00           N\n"))
        self.assertEqual(meta_pdb["first_commit"], meta_pdb["last_commit"]) # file 2 has 1 commit
        
    def test_build_manifest(self):
        build_manifest(self.test_dir, self.output_dir)
        
        json_path = os.path.join(self.output_dir, "provenance_manifest.json")
        csv_path = os.path.join(self.output_dir, "provenance_manifest.csv")
        
        self.assertTrue(os.path.isfile(json_path))
        self.assertTrue(os.path.isfile(csv_path))
        
        # Verify JSON content
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.assertEqual(len(data), 2)
        
        # Find entries
        txt_entry = next((item for item in data if item["relative_path"] == "dummy1.txt"), None)
        pdb_entry = next((item for item in data if item["relative_path"] == "structure.pdb"), None)
        
        self.assertIsNotNone(txt_entry)
        self.assertIsNotNone(pdb_entry)
        self.assertEqual(txt_entry["extension"], ".txt")
        self.assertEqual(pdb_entry["extension"], ".pdb")
        
        # Verify CSV content
        with open(csv_path, "r", encoding="utf-8", newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        self.assertEqual(len(rows), 2)
        
        csv_txt = next((item for item in rows if item["relative_path"] == "dummy1.txt"), None)
        self.assertIsNotNone(csv_txt)
        self.assertEqual(csv_txt["extension"], ".txt")
        # CSV reads back as strings
        self.assertEqual(int(csv_txt["byte_size"]), txt_entry["byte_size"])
        self.assertEqual(csv_txt["sha256"], txt_entry["sha256"])

if __name__ == "__main__":
    unittest.main()
