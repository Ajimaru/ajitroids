#!/usr/bin/env python3
"""Simple procedural boss_death.wav generator.
Produces a short, punchy impact with noise and low-frequency rumble.
"""
import math
import random
import wave
import struct
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'modul' / 'assets' / 'boss_death.wav'
SAMPLE_RATE = 44100
DURATION = 1.6  # seconds
N = int(SAMPLE_RATE * DURATION)

# Parameters for components
bass_freq = 80.0
hit_freq = 300.0
sines = [bass_freq, hit_freq, 600.0]

# Envelopes
def env(t, attack=0.005, decay=0.9):
    # quick attack then exponential decay
    if t < attack:
        return t / attack
    return math.exp(- (t - attack) * decay)

random.seed(0)

samples = []
for i in range(N):
    t = i / SAMPLE_RATE
    e = env(t)
    # low rumble
    rumble = 0.6 * math.sin(2 * math.pi * bass_freq * t) * e
    # hit transient
    hit = 0.9 * math.sin(2 * math.pi * hit_freq * t) * (e ** 0.6)
    # higher harmonic
    harm = 0.4 * math.sin(2 * math.pi * 600.0 * t) * (e ** 0.8)
    # filtered noise burst (approx)
    noise = (random.uniform(-1, 1) * 0.8) * (math.exp(-t * 6) + 0.01) * e
    # combine
    val = (rumble + hit + harm + noise)
    # gentle overall fade-out to avoid clicks at end
    fade = 1.0 if t < DURATION - 0.02 else (DURATION - t) / 0.02
    val *= fade
    # clamp
    val = max(-1.0, min(1.0, val))
    samples.append(int(val * 32767))

# Write WAV
OUT.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(OUT), 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    frame_data = b''.join(struct.pack('<h', s) for s in samples)
    wf.writeframes(frame_data)

print(f"Wrote {OUT}")
