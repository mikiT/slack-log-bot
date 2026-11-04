import os
import unittest


os.environ.setdefault("SLACK_BOT_TOKEN", "xoxb-test")
os.environ.setdefault("GOOGLE_DRIVE_FOLDER_ID", "root-test")

from google_drive import (  # noqa: E402
    FOLDER_MIME,
    ensure_folder,
    move_into_folder,
)


class FakeRequest:
    def __init__(self, value):
        self.value = value

    def execute(self):
        return self.value


class FakeFiles:
    def __init__(self, listed=None, parents=None):
        self.listed = listed or []
        self.parents = parents or []
        self.created = []
        self.updated = []

    def list(self, **kwargs):
        return FakeRequest({"files": self.listed})

    def create(self, **kwargs):
        self.created.append(kwargs)
        return FakeRequest({"id": "created-folder"})

    def get(self, **kwargs):
        return FakeRequest({"parents": self.parents})

    def update(self, **kwargs):
        self.updated.append(kwargs)
        return FakeRequest({"id": kwargs["fileId"]})


class FakeDrive:
    def __init__(self, files):
        self._files = files

    def files(self):
        return self._files


class GoogleDriveLayoutTests(unittest.TestCase):
    def test_ensure_folder_reuses_existing_child(self):
        files = FakeFiles(listed=[{"id": "public-id"}])

        folder_id = ensure_folder(FakeDrive(files), "public", "root-id")

        self.assertEqual(folder_id, "public-id")
        self.assertEqual(files.created, [])

    def test_ensure_folder_creates_missing_child(self):
        files = FakeFiles()

        folder_id = ensure_folder(FakeDrive(files), "private", "root-id")

        self.assertEqual(folder_id, "created-folder")
        self.assertEqual(files.created[0]["body"]["mimeType"], FOLDER_MIME)
        self.assertEqual(files.created[0]["body"]["parents"], ["root-id"])

    def test_move_into_folder_does_nothing_when_already_inside(self):
        files = FakeFiles(parents=["public-id"])

        moved = move_into_folder(FakeDrive(files), "sheet-id", "public-id")

        self.assertFalse(moved)
        self.assertEqual(files.updated, [])

    def test_move_into_folder_replaces_old_parent(self):
        files = FakeFiles(parents=["old-parent"])

        moved = move_into_folder(FakeDrive(files), "sheet-id", "public-id")

        self.assertTrue(moved)
        self.assertEqual(files.updated[0]["addParents"], "public-id")
        self.assertEqual(files.updated[0]["removeParents"], "old-parent")

if __name__ == "__main__":
    unittest.main()
