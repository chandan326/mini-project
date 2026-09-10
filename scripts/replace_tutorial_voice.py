"""Replace tutorial narration locally with Kokoro, preserving every video frame.

Install kokoro-onnx and soundfile in a separate build environment. Download the
Kokoro v1.0 ONNX model and voices from https://github.com/thewh1teagle/kokoro-onnx
and pass --model-dir. No hosted speech service or API credits are used.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile

from offline_voice_guard import disable_network
disable_network()

import numpy as np
import onnxruntime as ort
ort.disable_telemetry_events()
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parents[1]
NARRATION = [
    'Meet Agri Health AI. A simple way for farmers and gardeners to explore plant health, using clear photos and helpful guidance.',
    'Search for your crop in English or Hindi. Choose from thirty Indian crops, then select one to go straight to photos.',
    'Add one to five photos from your gallery, or use your camera. Show leaves, stems, and affected areas in good light.',
    'Share the symptoms, weather, and when changes began. Gemini reviews your photos and answers together, to suggest possible causes.',
    'Review possible conditions and care steps, even beyond local disease guides. Download a PDF report to share with an expert.',
    'AI guidance is not a diagnosis. Ask an agricultural expert before treatment, and keep monitoring your plants.',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-dir', type=Path, required=True)
    parser.add_argument('--video', type=Path, default=ROOT / 'static/video/agrihealth-tutorial.mp4')
    parser.add_argument('--voice', default='af_heart')
    args = parser.parse_args()
    options = ort.SessionOptions()
    options.intra_op_num_threads = 4
    session = ort.InferenceSession(str(args.model_dir / 'kokoro-v1.0.onnx'), options, providers=['CPUExecutionProvider'])
    kokoro = Kokoro.from_session(session, str(args.model_dir / 'voices-v1.0.bin'))
    segments = []
    with tempfile.TemporaryDirectory(prefix='agri-neural-voice-') as directory:
        directory = Path(directory)
        for index, text in enumerate(NARRATION):
            samples, rate = kokoro.create(text, voice=args.voice, speed=0.96, lang='en-us')
            duration = len(samples) / rate
            if duration > 9.5:
                raise ValueError(f'Scene {index + 1} is {duration:.2f}s; shorten its script instead of rushing or truncating speech.')
            print(f'Scene {index + 1}: {duration:.2f}s, natural pacing', flush=True)
            # Keep a small lead-in and breathing room inside each ten-second scene.
            segment = np.zeros(rate * 10, dtype=np.float32)
            start = int(rate * 0.25)
            segment[start:start + len(samples)] = samples
            segments.append(segment)
        narration = directory / 'narration.wav'
        sf.write(narration, np.concatenate(segments), rate)
        output = directory / 'tutorial.mp4'
        subprocess.run([
            'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
            '-i', str(args.video), '-i', str(narration),
            '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy',
            '-af', 'loudnorm=I=-18:TP=-2:LRA=7', '-ar', '48000',
            '-c:a', 'aac', '-b:a', '128k', '-t', '60',
            '-movflags', '+faststart', str(output),
        ], check=True)
        args.video.write_bytes(output.read_bytes())
        print('Updated narration; original video stream preserved.', flush=True)


if __name__ == '__main__':
    main()
