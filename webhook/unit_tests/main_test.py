# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import importlib
import os
import sys
import types
from unittest import mock


def _load_main_with_stubs(env_overrides):
    fake_flask = types.ModuleType("flask")

    class FakeResponse:
        def __init__(self, response="", status=200):
            self.response = response
            self.status_code = status

    fake_flask.Response = FakeResponse

    stubs = {
        "flask": fake_flask,
        "requests": types.SimpleNamespace(
            post=mock.MagicMock(),
            exceptions=types.SimpleNamespace(Timeout=TimeoutError),
        ),
        "google": types.ModuleType("google"),
        "google.auth": types.ModuleType("google.auth"),
        "google.auth.transport": types.ModuleType("google.auth.transport"),
        "google.auth.transport.requests": types.SimpleNamespace(Request=mock.MagicMock()),
        "google.oauth2": types.ModuleType("google.oauth2"),
        "google.oauth2.id_token": types.SimpleNamespace(fetch_id_token=mock.MagicMock(return_value="tok")),
        "google.cloud": types.ModuleType("google.cloud"),
        "google.cloud.logging": types.SimpleNamespace(Client=mock.MagicMock()),
        "bigquery": types.SimpleNamespace(write_summarization_to_table=mock.MagicMock(return_value=[])),
        "document_extract": types.SimpleNamespace(async_document_extract=mock.MagicMock(return_value="extracted text")),
        "storage": types.SimpleNamespace(upload_to_gcs=mock.MagicMock()),
        "vertex_llm": types.SimpleNamespace(predict_large_language_model=mock.MagicMock(return_value="summary text")),
    }
    base_env = {
        "PROJECT_ID": "demo-proj",
        "INPUT_BUCKET": "demo-proj_uploads",
        "OUTPUT_BUCKET": "demo-proj_output",
        "LOCATION": "us-central1",
        "DATASET_ID": "summary_dataset",
        "TABLE_ID": "summary_table",
        "K_SERVICE": "webhook",
    }
    base_env.update(env_overrides)
    with mock.patch.dict(os.environ, base_env, clear=False):
        with mock.patch.dict(sys.modules, stubs):
            sys.modules.pop("main", None)
            return importlib.import_module("main"), stubs


class _DummyRequest:
    def __init__(self, payload):
        self._payload = payload

    def get_json(self):
        return self._payload


def test_entrypoint_rejects_foreign_bucket_rest():
    main_mod, stubs = _load_main_with_stubs({})
    req = _DummyRequest({
        "bucket": "victim-project-secrets",
        "name": "backup/export.pdf",
        "id": "1",
        "timeCreated": "2024-01-01T00:00:00Z",
    })
    resp = main_mod.entrypoint(req)
    assert resp.status_code == 403
    stubs["document_extract"].async_document_extract.assert_not_called()


def test_entrypoint_rejects_foreign_bucket_storage_event():
    main_mod, stubs = _load_main_with_stubs({})
    req = _DummyRequest({
        "kind": "storage#object",
        "bucket": "victim-project-secrets",
        "name": "backup/export.pdf",
        "id": "1",
        "timeCreated": "2024-01-01T00:00:00Z",
    })
    resp = main_mod.entrypoint(req)
    assert resp.status_code == 403
    stubs["requests"].post.assert_not_called()


def test_entrypoint_allows_configured_uploads_bucket():
    main_mod, stubs = _load_main_with_stubs({})
    req = _DummyRequest({
        "bucket": "demo-proj_uploads",
        "name": "paper.pdf",
        "id": "42",
        "timeCreated": "2024-01-01T00:00:00Z",
    })
    resp = main_mod.entrypoint(req)
    assert resp == {"summary": "summary text"}
    stubs["document_extract"].async_document_extract.assert_called_once_with(
        "demo-proj_uploads", "paper.pdf", output_bucket="demo-proj_output"
    )
