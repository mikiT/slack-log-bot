import io
import os
import unittest
import uuid


INTEGRATION_ENABLED = os.environ.get("SLACK_LOG_INTEGRATION") == "1"


@unittest.skipUnless(
    INTEGRATION_ENABLED,
    "SLACK_LOG_INTEGRATION=1 を指定した実APIテストです",
)
class GoogleDriveIntegrationTests(unittest.TestCase):
    def setUp(self):
        from google_auth import load_credentials
        from google_drive import drive_service, shared_drive_id

        import config

        self.config = config
        self.credentials = load_credentials()
        self.drive = drive_service(self.credentials)
        self.shared_drive_id = shared_drive_id(
            self.drive, config.GOOGLE_DRIVE_FOLDER_ID
        )
        self.drive.bind_drive(self.shared_drive_id)
        if not self.shared_drive_id:
            self.skipTest("共有ドライブの親フォルダが必要です")

        self.created_ids: list[str] = []
        self._outstanding_ids: list[str] = []

    def tearDown(self):
        for file_id in reversed(getattr(self, "created_ids", [])):
            try:
                self.drive.files().delete(fileId=file_id).execute()
            except Exception:
                try:
                    self.drive.files().update(
                        fileId=file_id, body={"trashed": True}
                    ).execute()
                except Exception:
                    self._outstanding_ids.append(file_id)

    def test_private_folder_and_children_use_real_drive_api(self):
        import gspread
        from googleapiclient.http import MediaIoBaseUpload

        folder = self.drive.files().create(
            body={
                "name": f"__slack-log-bot-integration-{uuid.uuid4().hex}__",
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [self.config.GOOGLE_DRIVE_FOLDER_ID],
            },
            fields="id",
        ).execute()
        folder_id = folder["id"]
        self.created_ids.append(folder_id)

        # The real Sheets client uses the same OAuth credential as Drive.
        spreadsheet = gspread.authorize(self.credentials).create(
            "__slack-log-bot-integration__", folder_id=folder_id
        )
        self.created_ids.append(spreadsheet.id)

        uploaded = self.drive.files().create(
            body={"name": "__slack-log-bot-integration__.txt", "parents": [folder_id]},
            media_body=MediaIoBaseUpload(
                io.BytesIO(b"integration test"), mimetype="text/plain"
            ),
            fields="id,parents",
        ).execute()
        self.created_ids.append(uploaded["id"])
        self.assertIn(folder_id, uploaded.get("parents", []))

        self.assertEqual(self._outstanding_ids, [])
