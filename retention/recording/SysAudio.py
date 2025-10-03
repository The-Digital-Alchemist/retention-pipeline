# Simple audio recording with sounddevice
from typing import Optional

import numpy as np
import sounddevice as sd
import soundfile as sf
import typer

app = typer.Typer()


def list_devices():
    # Get all audio devices
    devices = sd.query_devices()
    return devices


def _get_default_input_device_index(devices):
    default_device = sd.default.device
    candidate = None
    if isinstance(default_device, (list, tuple)):
        candidate = default_device[0]
    else:
        candidate = default_device
    try:
        if candidate is not None:
            candidate = int(candidate)
    except (TypeError, ValueError):
        candidate = None
    if candidate is None:
        return None
    if 0 <= candidate < len(devices):
        max_in = int(devices[candidate].get('max_input_channels', 0) or 0)
        if max_in > 0:
            return candidate
    return None


def _first_input_device_index(devices, exclude=None):
    exclude = set(exclude or [])
    for idx, dev in enumerate(devices):
        if idx in exclude:
            continue
        max_in = int(dev.get('max_input_channels', 0) or 0)
        if max_in > 0:
            return idx
    return None


def resolve_device_settings(device_id=None, channels=None):
    devices = list_devices()
    resolved_id = None

    if device_id is not None:
        try:
            resolved_id = int(device_id)
        except (TypeError, ValueError):
            resolved_id = None

    if resolved_id is None:
        resolved_id = _get_default_input_device_index(devices)

    if resolved_id is None or not (0 <= resolved_id < len(devices)):
        resolved_id = _first_input_device_index(devices)

    if resolved_id is None:
        raise RuntimeError("No input device available for recording.")

    info = devices[resolved_id]
    max_input = int(info.get('max_input_channels', 0) or 0)

    if max_input <= 0:
        fallback = _first_input_device_index(devices, exclude={resolved_id})
        if fallback is None:
            raise RuntimeError(
                f"Device '{info.get('name', 'Unknown input')}' has no input channels and no alternative input device was found."
            )
        resolved_id = fallback
        info = devices[resolved_id]
        max_input = int(info.get('max_input_channels', 0) or 0)

    requested_channels = None
    if channels is not None:
        try:
            requested_channels = int(channels)
        except (TypeError, ValueError):
            requested_channels = None

    if requested_channels and 0 < requested_channels <= max_input:
        resolved_channels = requested_channels
    else:
        resolved_channels = max_input

    if resolved_channels <= 0:
        raise RuntimeError(
            f"Device '{info.get('name', 'Unknown input')}' does not have any input channels available for recording."
        )

    sample_rate_value = info.get('default_samplerate') or 44100
    try:
        sample_rate = int(sample_rate_value)
    except (TypeError, ValueError):
        sample_rate = 44100

    return resolved_id, resolved_channels, sample_rate, info


def get_device_samplerate(device_id=None):
    # Get the sample rate for a device
    _, _, sample_rate, _ = resolve_device_settings(device_id=device_id)
    return sample_rate


def record_blocking(duration_seconds, device_id=None, channels=None, preroll_seconds=0.25):
    # Record audio for X seconds from a device
    resolved_device_id, resolved_channels, sample_rate, _ = resolve_device_settings(
        device_id=device_id,
        channels=channels,
    )

    # Calculate how many audio samples we need
    usable_frames = int(duration_seconds * sample_rate)
    preroll_frames = int(preroll_seconds * sample_rate)
    total_frames = usable_frames + preroll_frames

    # Record the audio
    data = sd.rec(
        frames=total_frames,
        samplerate=sample_rate,
        channels=resolved_channels,
        device=resolved_device_id,
    )
    sd.wait()

    # Remove the first bit to avoid static
    data = data[preroll_frames:]
    return data, sample_rate


def save_wav(path, audio_data, sample_rate):
    # Save audio data to a WAV file
    sf.write(file=path, data=audio_data, samplerate=sample_rate)


def record_system_audio_to_wav(output_path, duration_seconds, device_id=None, channels=None, preroll_seconds=0.25):
    # Record audio and save it to a file
    audio, sr = record_blocking(
        duration_seconds=duration_seconds,
        device_id=device_id,
        channels=channels,
        preroll_seconds=preroll_seconds,
    )
    save_wav(output_path, audio, sr)
    return output_path


class AudioRecorder:
    # For GUI - start/stop recording on demand
    def __init__(self, device_id: Optional[int] = None, channels: Optional[int] = None):
        self.requested_device_id = device_id
        self.requested_channels = channels
        resolved_device_id, resolved_channels, sample_rate, info = resolve_device_settings(
            device_id=device_id,
            channels=channels,
        )
        self.device_id = resolved_device_id
        self.channels = resolved_channels
        self.sample_rate = sample_rate
        self.device_name = info.get('name', 'Unknown input')
        self._device_info = info
        self.stream = None
        self.audio_data = []
        self.is_recording = False

    def start_recording(self):
        # Start recording audio
        if self.is_recording:
            return

        try:
            resolved_device_id, resolved_channels, sample_rate, info = resolve_device_settings(
                device_id=self.device_id,
                channels=self.channels,
            )
        except Exception:
            self.is_recording = False
            raise

        self.device_id = resolved_device_id
        self.channels = resolved_channels
        self.sample_rate = sample_rate
        self.device_name = info.get('name', 'Unknown input')
        self._device_info = info
        self.audio_data = []
        self.is_recording = True

        def audio_callback(indata, frames, time, status):
            if self.is_recording:
                self.audio_data.append(indata.copy())

        try:
            self.stream = sd.InputStream(
                device=self.device_id,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=audio_callback,
            )
            self.stream.start()
        except Exception:
            self.is_recording = False
            self.stream = None
            raise

    def stop_recording(self):
        # Stop recording and return audio data
        if not self.is_recording:
            return None, self.sample_rate
        
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        if self.audio_data:
            audio = np.concatenate(self.audio_data, axis=0)
            return audio, self.sample_rate
        return None, self.sample_rate
    
    def save_recording(self, output_path):
        # Save the recorded audio to a file
        if self.audio_data:
            audio = np.concatenate(self.audio_data, axis=0)
            save_wav(output_path, audio, self.sample_rate)
            return output_path
        return None


@app.command()
def devices():
    # Show all audio devices
    devices = list_devices()
    for idx, dev in enumerate(devices):
        name = dev.get('name', '?')  # type: ignore
        max_in = dev.get('max_input_channels', 0)  # type: ignore
        max_out = dev.get('max_output_channels', 0)  # type: ignore
        sr = dev.get('default_samplerate', '?')  # type: ignore
        typer.echo(f"{idx:3d} | in:{max_in} out:{max_out} | {sr} Hz | {name}")


@app.command()
def record(
    output_path: str,
    duration: float = 5.0,
    device_id: Optional[int] = None,
    channels: Optional[int] = None,
    preroll: float = 0.25,
):
    # Record audio from command line
    try:
        path = record_system_audio_to_wav(
            output_path=output_path,
            duration_seconds=duration,
            device_id=device_id,
            channels=channels,
            preroll_seconds=preroll,
        )
        typer.echo(f"Saved: {path}")
    except Exception as e:
        typer.echo(f"Error: {e}")


if __name__ == "__main__":
    app()