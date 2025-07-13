import streamlit as st
from PIL import Image, ExifTags
import pandas as pd
from io import BytesIO
import base64

# Konfigurasi halaman
st.set_page_config(
    page_title="Photo Metadata Reader",
    page_icon="📷",
    layout="wide"
)

def get_image_download_link(img, filename):
    """Generate download link for image"""
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f'<a href="data:file/jpg;base64,{img_str}" download="{filename}">Download Image</a>'

def extract_metadata(image):
    """Extract all metadata from image"""
    metadata = {}
    try:
        exif_data = image._getexif()
        if exif_data:
            for tag_id, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                if isinstance(value, bytes):
                    value = value.decode(errors="replace")
                metadata[tag_name] = value
    except Exception as e:
        st.warning(f"Error extracting metadata: {e}")
    return metadata

def display_metadata(metadata):
    """Display metadata in expandable sections"""
    with st.expander("📊 Basic Information", expanded=True):
        cols = st.columns(2)
        cols[0].metric("Width", f"{image.width} px")
        cols[1].metric("Height", f"{image.height} px")
    
    with st.expander("📌 EXIF Metadata"):
        for key, value in metadata.items():
            st.text(f"{key}: {value}")

def main():
    st.title("📷 Photo Metadata Reader")
    st.markdown("Upload an image to view its metadata and EXIF data")

    uploaded_file = st.file_uploader(
        "Choose an image...", 
        type=["jpg", "jpeg", "png", "heic"],
        accept_multiple_files=False
    )

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Extract and display metadata
            metadata = extract_metadata(image)
            display_metadata(metadata)

            # Download button
            st.markdown(get_image_download_link(image, uploaded_file.name), unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error processing image: {e}")

if __name__ == "__main__":
    main()
