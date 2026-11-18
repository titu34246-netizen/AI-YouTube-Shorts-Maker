
import streamlit as st
import subprocess
import tempfile
from pathlib import Path
import math
import shutil

st.set_page_config(page_title="AI Shorts Maker", page_icon="🎬")

st.title("🎬 AI YouTube Shorts Maker")
st.write("Convert your video into vertical Shorts!")

if not shutil.which("ffmpeg"):
    st.error("FFmpeg is not installed.")
    st.stop()

video = st.file_uploader(
    "Upload your video",
    type=["mp4", "mov", "mkv", "webm"]
)

if video:
    with tempfile.TemporaryDirectory() as folder:
        folder = Path(folder)
        source = folder / "input.mp4"
        source.write_bytes(video.getbuffer())

        result = subprocess.run(
            ["ffprobe", "-v", "error",
             "-show_entries", "format=duration",
             "-of", "csv=p=0", str(source)],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            st.error("Video could not be read.")
            st.stop()

        duration = float(result.stdout.strip())
        st.write(f"Video duration: {int(duration)} seconds")

        clip_length = st.slider(
            "Short duration (seconds)", 15, 60, 30
        )

        count = st.slider("Number of Shorts", 1, 5, 3)

        if st.button("Create Shorts"):
            for i in range(count):
                start = max(
                    0, (duration - clip_length) * i / max(1, count - 1)
                )
                output = folder / f"short_{i+1}.mp4"

                command = [
                    "ffmpeg", "-y",
                    "-ss", str(start),
                    "-i", str(source),
                    "-t", str(min(clip_length, duration-start)),
                    "-vf",
                    "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    str(output)
                ]

                subprocess.run(command, capture_output=True)

                if output.exists():
                    st.download_button(
                        f"Download Short {i+1}",
                        output.read_bytes(),
                        file_name=f"short_{i+1}.mp4",
                        mime="video/mp4"
                    )

st.caption("Use only videos you own or have permission to edit.")
