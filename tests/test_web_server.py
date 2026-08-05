"""
End-to-end test suite for FastAPI Web Server & REST API endpoints.
"""

import unittest
import requests
import json

BASE_URL = "http://localhost:8000"


class TestWebServer(unittest.TestCase):

    def test_01_health_check(self):
        """Test GET /api/health."""
        resp = requests.get(f"{BASE_URL}/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")

    def test_02_generate_composition_text(self):
        """Test POST /api/generate with composition text format."""
        payload = {
            "prompt": "生成一段清新日系轻音乐，C大调，72BPM",
            "format": "composition"
        }
        resp = requests.post(f"{BASE_URL}/api/generate", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        gen = data["generation"]
        self.assertIsNotNone(gen.get("composition"))
        self.assertEqual(gen["composition"]["bpm"], 72)

    def test_03_generate_wav_binary(self):
        """Test POST /api/generate with WAV binary audio format."""
        payload = {
            "prompt": "Upbeat pop tune in G Major 120BPM with piano and steel guitar",
            "format": "wav"
        }
        resp = requests.post(f"{BASE_URL}/api/generate", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        gen = data["generation"]
        self.assertIsNotNone(gen.get("wav_url"))
        
        # Test downloading the served WAV file
        wav_resp = requests.get(f"{BASE_URL}{gen['wav_url']}")
        self.assertEqual(wav_resp.status_code, 200)
        self.assertEqual(wav_resp.headers["content-type"], "audio/wav")
        self.assertTrue(len(wav_resp.content) > 1000)

    def test_04_convert_composition_to_wav(self):
        """Test POST /api/convert converting text composition JSON to WAV audio."""
        comp_payload = {
            "composition": {
                "title": "Test Conversion Track",
                "bpm": 90,
                "tracks": [
                    {
                        "instrument": "acoustic-grand-piano",
                        "notes": [
                            {"pitch": "C4", "duration": "4"},
                            {"pitch": "E4", "duration": "4"},
                            {"pitch": "G4", "duration": "4"},
                            {"pitch": "C5", "duration": "2"}
                        ]
                    }
                ]
            }
        }
        resp = requests.post(f"{BASE_URL}/api/convert", json=comp_payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        gen = data["generation"]
        self.assertIsNotNone(gen.get("wav_url"))

    def test_05_get_generations_history(self):
        """Test GET /api/generations retrieving saved generation history."""
        resp = requests.get(f"{BASE_URL}/api/generations")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        generations = data["generations"]
        self.assertTrue(len(generations) >= 3)


if __name__ == "__main__":
    unittest.main()
