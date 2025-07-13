import streamlit as st
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os

def extract_exif_data(image):
    """Ekstrak data EXIF dari gambar"""
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for gps_tag in value:
                    sub_decoded = GPSTAGS.get(gps_tag, gps_tag)
                    gps_data[sub_decoded] = value[gps_tag]
                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value
    return exif_data

def convert_to_degrees(value):
    """Konversi koordinat GPS ke derajat desimal"""
    d, m, s = value
    return d + (m / 60.0) + (s / 3600.0)

def get_gps_coordinates(exif_data):
    """Ekstrak koordinat GPS dari data EXIF"""
    if "GPSInfo" not in exif_data:
        return None
    
    gps_info = exif_data["GPSInfo"]
    
    gps_latitude = gps_info.get("GPSLatitude")
    gps_latitude_ref = gps_info.get("GPSLatitudeRef")
    gps_longitude = gps_info.get("GPSLongitude")
    gps_longitude_ref = gps_info.get("GPSLongitudeRef")
    
    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = convert_to_degrees(gps_latitude)
        if gps_latitude_ref != "N":
            lat = -lat
        
        lon = convert_to_degrees(gps_longitude)
        if gps_longitude_ref != "E":
            lon = -lon
        
        return lat, lon
    return None

def main():
    st.title("📷 Aplikasi Pembaca Metadata Foto")
    st.write("Unggah foto untuk melihat metadata EXIF-nya")
    
    uploaded_file = st.file_uploader("Pilih file gambar...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Gambar yang diunggah", use_column_width=True)
            
            # Tampilkan info dasar
            st.subheader("Informasi Dasar")
            col1, col2 = st.columns(2)
            col1.metric("Nama File", uploaded_file.name)
            col2.metric("Format", image.format)
            st.metric("Ukuran Gambar", f"{image.width} x {image.height} piksel")
            
            # Ekstrak metadata EXIF
            st.subheader("Metadata EXIF")
            exif_data = extract_exif_data(image)
            
            if not exif_data:
                st.warning("Tidak ada metadata EXIF yang ditemukan pada gambar ini.")
            else:
                # Tampilkan semua metadata
                for key, value in exif_data.items():
                    if isinstance(value, dict):
                        st.write(f"**{key}**")
                        for sub_key, sub_value in value.items():
                            st.write(f"- {sub_key}: {sub_value}")
                    else:
                        st.write(f"**{key}**: {value}")
                
                # Cek dan tampilkan koordinat GPS jika ada
                gps_coords = get_gps_coordinates(exif_data)
                if gps_coords:
                    st.subheader("Lokasi GPS")
                    st.write(f"Latitude: {gps_coords[0]}, Longitude: {gps_coords[1]}")
                    st.map(pd.DataFrame({
                        'lat': [gps_coords[0]],
                        'lon': [gps_coords[1]]
                    }))
                else:
                    st.info("Tidak ada data GPS yang ditemukan dalam metadata.")
        
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses gambar: {e}")

if __name__ == "__main__":
    import pandas as pd  # Untuk menampilkan peta
    main()
