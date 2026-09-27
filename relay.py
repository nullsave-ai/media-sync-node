#!/usr/bin/env python3
import os
import sys
import time
import subprocess

SOURCE_URL = os.environ.get("SOURCE_URL", "https://null-stream.nullsave-ai.workers.dev/bein1.m3u8").strip()
RTMP_URL = os.environ.get("RTMP_URL", "rtmp://vsu.okcdn.ru/input/16304908738296_18985914141432_kww2uv476e").strip()

print("=" * 60)
print("🚀 MEDIA SYNC RELAY ENGINE INITIALIZED")
print(f"📡 Source HLS : {SOURCE_URL}")
print(f"📺 Target RTMP: {RTMP_URL[:38]}...")
print("=" * 60)

cmd = [
    "ffmpeg",
    "-nostdin",
    "-y",
    "-hide_banner",
    "-loglevel", "info",
    "-thread_queue_size", "2048",
    "-reconnect", "1",
    "-reconnect_at_eof", "1",
    "-reconnect_streamed", "1",
    "-reconnect_delay_max", "3",
    "-rw_timeout", "15000000",
    "-fflags", "+nobuffer+genpts+discardcorrupt",
    "-err_detect", "ignore_err",
    "-i", SOURCE_URL,
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-tune", "zerolatency",
    "-b:v", "2000k",
    "-maxrate", "2200k",
    "-bufsize", "3000k",
    "-pix_fmt", "yuv420p",
    "-g", "50",
    "-keyint_min", "50",
    "-sc_threshold", "0",
    "-flags", "+cgop+low_delay",
    "-c:a", "aac",
    "-b:a", "128k",
    "-ar", "44100",
    "-f", "flv",
    RTMP_URL
]

retry_count = 0
max_retries = 30

while retry_count < max_retries:
    print(f"⚡ Starting FFmpeg transmission (Attempt {retry_count + 1})...", flush=True)
    start_time = time.time()
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in proc.stdout:
            clean = line.strip()
            if "frame=" in clean or "speed=" in clean:
                print(clean, flush=True)
            elif any(k in clean.lower() for k in ["error", "warn", "failed", "connected", "stream"]):
                print(clean, flush=True)
        proc.wait()
    except Exception as e:
        print(f"❌ Exception: {e}", flush=True)

    elapsed = time.time() - start_time
    if elapsed > 120:
        retry_count = 0
    else:
        retry_count += 1
    print(f"⚠️ Connection dropped after {int(elapsed)}s. Reconnecting in 3s...", flush=True)
    time.sleep(3)
