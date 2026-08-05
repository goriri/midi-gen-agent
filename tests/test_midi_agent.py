"""
Test suite for ADK MIDI Agent.
Tests generation in both text (composition JSON) and binary (.mid / .wav) formats
using English and Chinese prompts with explicit music theory parameter checks.
"""

import os
import sys
import unittest
from pathlib import Path

# Add paths
ROOT_DIR = Path(__file__).parent.parent
SKILL_DIR = ROOT_DIR / "midi-agent-skill"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from midi_agent.gm_mapping import parse_prompt_specs, get_scale_pitches
from midi_agent.music_generator import create_composition_dict
from midi_agent.tools import (
    generate_composition_text,
    generate_midi_binary,
    generate_wav_binary,
    generate_music
)
from midi_agent.agent import root_agent
from midi_types.gm_instruments import resolve_instrument


class TestMidiAgentSpecsAndTools(unittest.TestCase):

    def test_chinese_short_prompt_generation(self):
        """Test Prompt 1: Short Chinese prompt generation in composition & MIDI format."""
        prompt = "生成一段曲风悠扬的音乐"
        
        # Test prompt spec parsing
        specs = parse_prompt_specs(prompt)
        self.assertIsNotNone(specs["bpm"])
        self.assertTrue(len(specs["instruments"]) > 0)
        
        # Test composition text format generation
        res_comp = generate_composition_text(prompt)
        self.assertEqual(res_comp["status"], "success")
        self.assertEqual(res_comp["format"], "composition")
        
        comp = res_comp["composition"]
        self.assertIn("title", comp)
        self.assertIn("bpm", comp)
        self.assertIn("tracks", comp)
        self.assertTrue(len(comp["tracks"]) >= 2)
        
        # Verify tracks contain notes with pitch and duration
        for track in comp["tracks"]:
            self.assertIn("instrument", track)
            self.assertIn("notes", track)
            self.assertTrue(len(track["notes"]) > 0)
            for note in track["notes"]:
                self.assertIn("pitch", note)
                self.assertIn("duration", note)

        # Test MIDI binary format generation
        res_midi = generate_midi_binary(prompt)
        self.assertEqual(res_midi["status"], "success")
        self.assertEqual(res_midi["format"], "midi")
        self.assertTrue(os.path.exists(res_midi["file_path"]))
        self.assertTrue(res_midi["file_size_bytes"] > 0)

    def test_chinese_detailed_prompt_conformance(self):
        """Test Prompt 2: Detailed Chinese prompt with explicit BPM, Key, Instruments, and format."""
        prompt = (
            "曲风：清新日系轻音乐，治愈民谣，轻柔钢琴为主，搭配分解木吉他、微弱弦乐垫音\n"
            "场景：晴空万里，午后草坪，微风舒缓，氛围松弛慵懒，宁静和谐，无伤感，温暖明亮\n"
            "速度：72BPM，4/4拍，C大调，旋律平缓起伏不大，节奏舒展\n"
            "配器：原声钢琴（主旋律）、尼龙木吉他分解和弦、极淡小提琴长音铺垫、轻微风铃点缀\n"
            "要求：旋律流畅治愈，音量柔和，不要鼓点；输出完整曲谱，导出文本格式，调式规范，音符排布适合五线谱展示，时长60秒"
        )
        
        # Parse specs
        specs = parse_prompt_specs(prompt)
        self.assertEqual(specs["bpm"], 72)
        self.assertEqual(specs["key"], "C")
        self.assertEqual(specs["scale_type"], "major")
        self.assertEqual(specs["export_format"], "composition")
        self.assertTrue(specs["no_drums"])
        
        # Verify expected instruments were mapped
        expected_insts = ["acoustic-grand-piano", "acoustic-guitar-nylon", "violin", "tinkle-bell"]
        for inst in expected_insts:
            self.assertIn(inst, specs["instruments"])

        # Generate composition dictionary
        comp = create_composition_dict(prompt)
        self.assertEqual(comp["bpm"], 72)
        
        # Check track instruments
        track_insts = [t["instrument"] for t in comp["tracks"]]
        self.assertIn("acoustic-grand-piano", track_insts)
        self.assertIn("acoustic-guitar-nylon", track_insts)
        self.assertIn("violin", track_insts)
        
        # Check scale conformance (C Major scale contains C, D, E, F, G, A, B)
        c_major_notes = {"C", "D", "E", "F", "G", "A", "B"}
        for track in comp["tracks"]:
            for note in track["notes"]:
                pitch = note["pitch"]
                base_note = pitch[:-1] if pitch[-1].isdigit() else pitch[:-2]
                self.assertIn(base_note, c_major_notes, f"Note {pitch} not in C major scale")

    def test_english_upbeat_pop_wav_format(self):
        """Test English upbeat prompt requesting WAV binary output."""
        prompt = "Compose an upbeat pop melody in G Major at 120 BPM with acoustic grand piano, acoustic guitar steel, and bass line. Export as binary WAV file."
        
        specs = parse_prompt_specs(prompt)
        self.assertEqual(specs["bpm"], 120)
        self.assertEqual(specs["key"], "G")
        self.assertEqual(specs["scale_type"], "major")
        
        # Test unified tool with WAV format
        res = generate_music(prompt, output_format="wav")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["format"], "wav")
        self.assertTrue(os.path.exists(res["file_path"]))
        self.assertTrue(res["file_size_bytes"] > 0)
        self.assertTrue(res["file_path"].endswith(".wav"))

    def test_english_slow_ballad_all_formats(self):
        """Test English slow ballad prompt with 'all' output format."""
        prompt = "Generate a soothing ballad in A minor, 60 BPM, 4/4 time signature, with acoustic grand piano, cello, and flute. Duration 30 seconds."
        
        specs = parse_prompt_specs(prompt)
        self.assertEqual(specs["bpm"], 60)
        self.assertEqual(specs["key"], "A")
        self.assertEqual(specs["scale_type"], "minor")
        self.assertEqual(specs["target_duration_seconds"], 30)

        res = generate_music(prompt, output_format="all")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["format"], "all")
        self.assertIn("composition", res)
        self.assertTrue(os.path.exists(res["midi_file"]))
        self.assertTrue(os.path.exists(res["wav_file"]))


class TestADKRootAgent(unittest.TestCase):

    def test_agent_definition(self):
        """Verify ADK root agent configuration and tool binding."""
        self.assertEqual(root_agent.name, "midi_agent")
        self.assertTrue(len(root_agent.tools) >= 4)
        tool_names = [t.__name__ for t in root_agent.tools]
        self.assertIn("generate_music", tool_names)
        self.assertIn("generate_composition_text", tool_names)
        self.assertIn("generate_midi_binary", tool_names)
        self.assertIn("generate_wav_binary", tool_names)


if __name__ == "__main__":
    unittest.main()
