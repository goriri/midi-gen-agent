"""
Test suite for Duration Conformance and Self-Correction.
Verifies prompt #235c4af0 (60-second target duration at 72 BPM) and short prompt specs.
"""

import unittest
from midi_agent.music_generator import create_composition_dict, calculate_composition_duration_seconds


class TestDurationConformance(unittest.TestCase):

    def test_sample_prompt_2_duration_conformance(self):
        """Verify Sample Prompt 2 (时长60秒 at 72BPM) generates music within ±5s of 60 seconds."""
        prompt = (
            "曲风：清新日系轻音乐，治愈民谣，轻柔钢琴为主，搭配分解木吉他、微弱弦乐垫音\n"
            "场景：晴空万里，午后草坪，微风舒缓，氛围松弛慵懒，宁静和谐，无伤感，温暖明亮\n"
            "速度：72BPM，4/4拍，C大调，旋律平缓起伏不大，节奏舒展\n"
            "配器：原声钢琴（主旋律）、尼龙木吉他分解和弦、极淡小提琴长音铺垫、轻微风铃点缀\n"
            "要求：旋律流畅治愈，音量柔和，不要鼓点；输出完整曲谱，导出文本格式，时长60秒"
        )
        
        comp = create_composition_dict(prompt)
        duration_sec = calculate_composition_duration_seconds(comp)
        
        print(f"\n[Test Prompt #235c4af0] Target: 60s, Generated: {duration_sec:.1f}s, BPM: {comp['bpm']}")
        self.assertAlmostEqual(duration_sec, 60.0, delta=5.0)

    def test_short_duration_prompt(self):
        """Verify 15-second prompt generates music within ±5s of 15 seconds."""
        prompt = "Pop tune 120BPM in C Major, 15 seconds duration"
        comp = create_composition_dict(prompt)
        duration_sec = calculate_composition_duration_seconds(comp)
        
        print(f"[Test Short Prompt] Target: 15s, Generated: {duration_sec:.1f}s, BPM: {comp['bpm']}")
        self.assertAlmostEqual(duration_sec, 15.0, delta=5.0)


if __name__ == "__main__":
    unittest.main()
