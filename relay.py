#!/usr/bin/env python3
import os
import sys
import time
import subprocess

SOURCE_URL = os.environ.get("SOURCE_URL", "https://null-stream.nullsave-ai.workers.dev/bein1.m3u8").strip()
RTMP_URL = os.environ.get("RTMP_URL", "rtmp://vsu.okcdn.ru/input/16307144695544_18989621971704_nvtng3f2ni").strip()
LOGO_PATH = "logo.png"

print("=" * 60)
print("🚀 MEDIA SYNC RELAY ENGINE (WITH BEOUT LOGO & PACING)")
print(f"📡 Source HLS : {SOURCE_URL}")
print(f"📺 Target RTMP: {RTMP_URL[:38]}...")
print(f"🎨 Logo Exists: {os.path.exists(LOGO_PATH)}")
print("=" * 60)

cmd = [
    "ffmpeg",
    "-nostdin",
    "-y",
    "-hide_banner",
    "-loglevel", "info",
    "-thread_queue_size", "2048",
    "-re",
    "-reconnect", "1",
    "-reconnect_at_eof", "1",
    "-reconnect_streamed", "1",
    "-reconnect_delay_max", "2",
    "-rw_timeout", "15000000",
    "-fflags", "+nobuffer+genpts+discardcorrupt",
    "-err_detect", "ignore_err",
    "-i", SOURCE_URL,
]

if os.path.exists(LOGO_PATH):
    cmd.extend([
        "-i", LOGO_PATH,
        "-filter_complex", "[1:v]scale=220:-1[logo];[0:v][logo]overlay=W-w-30:30[outv]",
        "-map", "[outv]",
        "-map", "0:a?"
    ])
else:
    cmd.extend(["-map", "0:v", "-map", "0:a?"])

cmd.extend([
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
])

retry_count = 0
while True:
    print(f"⚡ Starting Transmission Loop (Run #{retry_count + 1})...", flush=True)
    start_time = time.time()
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in proc.stdout:
            clean = line.strip()
            if "frame=" in clean:
                print(clean, flush=True)
            elif any(k in clean.lower() for k in ["error", "warn", "failed", "connected", "stream #"]):
                print(clean, flush=True)
        proc.wait()
    except Exception as e:
        print(f"❌ Exception: {e}", flush=True)

    elapsed = time.time() - start_time
    retry_count += 1
    print(f"⚠️ Stream loop ended after {int(elapsed)}s. Re-establishing link in 2s...", flush=True)
    time.sleep(2)
