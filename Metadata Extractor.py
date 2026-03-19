"""
Metadata Extractor - 2025 version
Suitable for: Mr. Sabaz Ali Khan & friends

Supported formats:
• Images: JPG, JPEG, PNG, HEIC, TIFF, WebP
• PDF
• Video: MP4, MOV, AVI, MKV
• Audio: MP3, M4A, WAV, FLAC, OGG

Required libraries:
pip install pillow PyPDF2 mutagen hachoir tinytag python-magic
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import json

try:
    from PIL import Image, ExifTags
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError:
    Image = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from hachoir.metadata import extractMetadata
    from hachoir.parser import createParser
except ImportError:
    extractMetadata = None
    createParser = None

try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None

try:
    from tinytag import TinyTag
except ImportError:
    TinyTag = None

# Optional - helps identify file type when others fail
try:
    import magic
except ImportError:
    magic = None


def get_gps_info(exif_data):
    """Convert GPS EXIF data to readable format"""
    if not exif_data:
        return None
        
    gps_info = exif_data.get(34853)  # GPSInfo tag
    if not gps_info:
        return None
    
    def get_gps_field(field):
        return gps_info.get(GPSTAGS.get(field, field))
    
    lat = get_gps_field('GPSLatitude')
    lat_ref = get_gps_field('GPSLatitudeRef')
    lon = get_gps_field('GPSLongitude')
    lon_ref = get_gps_field('GPSLongitudeRef')
    
    if lat and lat_ref and lon and lon_ref:
        lat = (lat[0] + lat[1]/60 + lat[2]/3600) * (1 if lat_ref == 'N' else -1)
        lon = (lon[0] + lon[1]/60 + lon[2]/3600) * (1 if lon_ref == 'E' else -1)
        
        return {
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "altitude": get_gps_field('GPSAltitude'),
            "timestamp": get_gps_field('GPSTimeStamp')
        }
    return None


def extract_image_metadata(filepath):
    """Extract metadata from image files using Pillow"""
    if not Image:
        return {"error": "Pillow library not installed"}
        
    try:
        with Image.open(filepath) as img:
            exif_data = img.getexif()
            info = img.info.copy() if hasattr(img, 'info') else {}
            
            metadata = {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,           # (width, height)
                "width": img.width,
                "height": img.height,
                "file_size_bytes": os.path.getsize(filepath),
                "modified_time": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
            }
            
            if exif_data:
                decoded_exif = {}
                for tag_id, value in exif_data.items():
                    decoded_tag = TAGS.get(tag_id, tag_id)
                    if decoded_tag == "GPSInfo":
                        gps = get_gps_info(exif_data)
                        if gps:
                            decoded_exif["GPS"] = gps
                    else:
                        decoded_exif[decoded_tag] = str(value)
                
                if decoded_exif:
                    metadata["EXIF"] = decoded_exif
            
            # Some useful info often found in info dict
            for key in ['DateTime', 'Software', 'Make', 'Model', 'LensModel', 
                       'Copyright', 'Artist', 'Description']:
                if key in info:
                    metadata[key] = info[key]
            
            return metadata
    except Exception as e:
        return {"error": f"Image metadata extraction failed: {str(e)}"}


def extract_pdf_metadata(filepath):
    """Extract metadata from PDF files"""
    if not PyPDF2:
        return {"error": "PyPDF2 library not installed"}
        
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            info = reader.metadata
            
            if info:
                metadata = {k: v for k, v in info.items() if v}
                metadata["page_count"] = len(reader.pages)
                return metadata
            else:
                return {"info": "No metadata found in PDF"}
    except Exception as e:
        return {"error": f"PDF metadata extraction failed: {str(e)}"}


def extract_media_metadata(filepath):
    """Try multiple libraries to extract audio/video metadata"""
    results = {}
    ext = Path(filepath).suffix.lower()
    
    # Strategy 1: mutagen (best for audio + some video)
    if MutagenFile:
        try:
            audio = MutagenFile(filepath)
            if audio:
                for k, v in audio.items():
                    if k not in ('cover', 'APIC', 'PICT'):  # skip images
                        results[f"mutagen_{k}"] = str(v)
                results["duration_seconds"] = audio.info.length if hasattr(audio, 'info') else None
        except:
            pass
    
    # Strategy 2: tinytag (good fallback for audio)
    if TinyTag and ext in ['.mp3','.m4a','.flac','.wav','.ogg']:
        try:
            tag = TinyTag.get(filepath)
            for field in ['title','artist','album','genre','year','track','duration']:
                value = getattr(tag, field, None)
                if value is not None:
                    results[f"tinytag_{field}"] = value
        except:
            pass
    
    # Strategy 3: hachoir (good for video)
    if extractMetadata and createParser:
        try:
            parser = createParser(filepath)
            if parser:
                meta = extractMetadata(parser)
                if meta:
                    for line in meta.exportPlaintext():
                        if ":" in line:
                            k, v = line.split(":", 1)
                            results[f"hachoir_{k.strip()}"] = v.strip()
        except:
            pass
    
    if results:
        return results
    else:
        return {"status": "No metadata extracted (try installing mutagen / tinytag / hachoir)"}


def extract_file_metadata(filepath):
    """
    Main function - detects file type and calls appropriate extractor
    """
    if not os.path.isfile(filepath):
        return {"error": "File not found"}
    
    path = Path(filepath)
    ext = path.suffix.lower()
    
    result = {
        "filename": path.name,
        "full_path": str(path.absolute()),
        "extension": ext,
        "size_bytes": os.path.getsize(filepath),
        "created": datetime.fromtimestamp(path.stat().st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
    }
    
    # Image files
    if ext in ['.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.tiff', '.tif']:
        image_data = extract_image_metadata(filepath)
        result.update(image_data)
    
    # PDF
    elif ext == '.pdf':
        pdf_data = extract_pdf_metadata(filepath)
        result.update(pdf_data)
    
    # Audio / Video
    elif ext in ['.mp3','.m4a','.wav','.flac','.ogg','.mp4','.mov','.avi','.mkv']:
        media_data = extract_media_metadata(filepath)
        result.update(media_data)
    
    # Try magic as last resort to identify type
    if magic:
        try:
            mime = magic.Magic(mime=True).from_file(filepath)
            result["mime_type"] = mime
        except:
            pass
    
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python metadata_extractor.py <file_or_folder_path>")
        print(
            "       python metadata_extractor.py photo.jpg")
        return
    
    path = sys.argv[1]
    
    if os.path.isfile(path):
        data = extract_file_metadata(path)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    
    elif os.path.isdir(path):
        print(f"Scanning folder: {path}\n")
        for root, _, files in os.walk(path):
            for file in files:
                filepath = os.path.join(root, file)
                print(f"\n→ {file}")
                data = extract_file_metadata(filepath)
                print(json.dumps(data, indent=2, ensure_ascii=False)[:600] + "..." if len(json.dumps(data)) > 600 else "")
    else:
        print("Path not found")


if __name__ == "__main__":
    main()
