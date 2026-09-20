"""
app.py

Streamlit front-end for the RetroDither pipeline.
Upload an image -> resize/grayscale -> Atkinson dither -> preview + download
as a MacBinary-wrapped MacPaint (.bin) file.

Expects ditherAlgo.py and macPaint.py to be in the same directory / on the
Python path.
"""

import io
import tempfile
from pathlib import Path

import streamlit as st
from PIL import Image

from ditherAlgo import ditherAlgo
from macPaint import MAX_WIDTH, MAX_HIEGHT, writeMacPaintFile


def resize_and_grayscale(image: Image.Image) -> Image.Image:
    """Fit the image within the MacPaint canvas bounds and convert to grayscale."""
    if image.width > MAX_WIDTH or image.height > MAX_HIEGHT:
        desired_ratio = MAX_WIDTH / MAX_HIEGHT
        ratio = image.width / image.height
        if ratio >= desired_ratio:
            new_size = (MAX_WIDTH, int(image.height * (MAX_WIDTH / image.width)))
        else:
            new_size = (int(image.width * (MAX_HIEGHT / image.height)), MAX_HIEGHT)
        image.thumbnail(new_size, Image.Resampling.LANCZOS)
    return image.convert("L")


st.set_page_config(page_title="RetroDither", page_icon="", layout="centered")
st.title("RetroDither", text_alignment="center")
st.markdown("Transform modern images into classic 1-bit MacPaint-style", text_alignment="center")
# Upload an image and convert it to a classic 1-bit MacPaint-style dither.

uploaded_file = st.file_uploader(
    "Choose an image", type=["png", "jpg", "jpeg", "bmp", "gif", "webp"]
)

if uploaded_file is not None:
    original = Image.open(uploaded_file)
    prepared = resize_and_grayscale(original.copy())

    with st.spinner("Dithering..."):
        dithered_data = ditherAlgo(prepared)
        dithered_image = Image.frombytes("L", prepared.size, dithered_data.tobytes())

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original")
        st.image(original, use_container_width=True)
    with col2:
        st.subheader("Dithered")
        st.image(dithered_image, use_container_width=True)

    # PNG download of the dithered preview
    png_buffer = io.BytesIO()
    dithered_image.save(png_buffer, format="PNG")

    # MacBinary + MacPaint (.bin) download
    output_stem = Path(uploaded_file.name).stem
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = str(Path(tmp_dir) / output_stem)
        writeMacPaintFile(dithered_data, out_path, prepared.width, prepared.height)
        bin_bytes = Path(out_path + ".bin").read_bytes()

    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        st.download_button(
            "Download PNG",
            data=png_buffer.getvalue(),
            file_name=f"{output_stem}_dithered.png",
            mime="image/png",
        )
    with dl_col2:
        st.download_button(
            "Download MacPaint (.bin)",
            data=bin_bytes,
            file_name=f"{output_stem}.bin",
            mime="application/octet-stream",
        )
else:
    st.info("Upload an image to get started.")