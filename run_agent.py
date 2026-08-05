"""
CLI runner for the ADK MIDI Agent.
Demonstrates end-to-end execution of root_agent for prompt-driven MIDI and WAV generation.
"""

import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from midi_agent.agent import root_agent
from midi_agent.tools import generate_music


def main():
    print("==================================================")
    print("       ADK MIDI Agent - Music Generator          ")
    print("==================================================")

    sample_prompts = [
        ("Prompt 1 (Short Chinese)", "生成一段曲风悠扬的音乐", "all"),
        (
            "Prompt 2 (Detailed Chinese - Composition format)",
            "曲风：清新日系轻音乐，治愈民谣，轻柔钢琴为主，搭配分解木吉他、微弱弦乐垫音\n"
            "场景：晴空万里，午后草坪，微风舒缓，氛围松弛慵懒，宁静和谐，无伤感，温暖明亮\n"
            "速度：72BPM，4/4拍，C大调，旋律平缓起伏不大，节奏舒展\n"
            "配器：原声钢琴（主旋律）、尼龙木吉他分解和弦、极淡小提琴长音铺垫、轻微风铃点缀\n"
            "要求：旋律流畅治愈，音量柔和，不要鼓点；输出完整曲谱，导出文本格式，调式规范，音符排布适合五线谱展示，时长60秒",
            "composition"
        ),
        (
            "Prompt 3 (English - Binary WAV format)",
            "Compose a cheerful pop melody in G Major at 120 BPM with acoustic grand piano, acoustic guitar steel, and bass. Output as binary WAV file.",
            "wav"
        )
    ]

    for title, prompt, fmt in sample_prompts:
        print(f"\n--- Running Demo: {title} ---")
        print(f"User Prompt:\n{prompt}\n")
        
        result = generate_music(prompt, output_format=fmt)
        print(f"Execution Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("--------------------------------------------------")


if __name__ == "__main__":
    main()
