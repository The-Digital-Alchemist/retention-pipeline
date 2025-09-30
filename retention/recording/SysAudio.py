# Simple audio recording with sounddevice
import numpy as np
import sounddevice as sd
import soundfile as sf
import typer

app = typer.Typer()


def list_devices():
    # Get all audio devices
    devices = sd.query_devices()
    return devices


def get_device_samplerate(device_id):
    # Get the sample rate for a device
    info = sd.query_devices(device_id)
    rate = info.get('default_samplerate')  # type: ignore
    if rate:
        return int(rate)
    return 44100


def record_blocking(duration_seconds, device_id, channels=1, preroll_seconds=0.25):
    # Record audio for X seconds from a device
    sample_rate = get_device_samplerate(device_id)
    
    # Calculate how many audio samples we need
    usable_frames = int(duration_seconds * sample_rate)
    preroll_frames = int(preroll_seconds * sample_rate)
    total_frames = usable_frames + preroll_frames
    
    # Record the audio
    data = sd.rec(
        frames=total_frames,
        samplerate=sample_rate,
        channels=channels,
        device=device_id,
    )
    sd.wait()
    
    # Remove the first bit to avoid static
    data = data[preroll_frames:]
    return data, sample_rate


def save_wav(path, audio_data, sample_rate):
    # Save audio data to a WAV file
    sf.write(file=path, data=audio_data, samplerate=sample_rate)


def record_system_audio_to_wav(output_path, duration_seconds, device_id, channels=1, preroll_seconds=0.25):
    # Record audio and save it to a file
    audio, sr = record_blocking(
        duration_seconds=duration_seconds,
        device_id=device_id,
        channels=channels,
        preroll_seconds=preroll_seconds,
    )
    save_wav(output_path, audio, sr)
    return output_path


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
def record(output_path, duration=5.0, device_id=14, channels=1, preroll=0.25):
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