import os
import csv
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

def to_decimal(coords, ref):
    degrees = float(coords[0])
    minutes = float(coords[1])
    seconds = float(coords[2])
    decimal = degrees + minutes / 60 + seconds / 3600
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def get_exif_data(image_path):
    try:
        image = Image.open(image_path)
        exif_data_raw = image._getexif()
        if not exif_data_raw:
            return None
    except Exception as e:
        return None

    gps_data = {}

    for tag_id, value in exif_data_raw.items():
        tag = TAGS.get(tag_id, tag_id)
        if tag == "GPSInfo":
            for key in value:
                gps_tag = GPSTAGS.get(key, key)
                gps_data[gps_tag] = value[key]

    if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
        lat = to_decimal(gps_data['GPSLatitude'], gps_data['GPSLatitudeRef'])
        lon = to_decimal(gps_data['GPSLongitude'], gps_data['GPSLongitudeRef'])
        alt = gps_data.get('GPSAltitude', None)
        if alt is not None:
            try:
                alt = float(alt)
            except:
                alt = None
        return lat, lon, alt
    else:
        return None

def run_extraction():
    folder = filedialog.askdirectory(title="Wybierz folder ze zdjęciami")
    if not folder:
        return

    files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.tif', '.tiff'))]
    if not files:
        messagebox.showinfo("Brak zdjęć", "W wybranym folderze nie ma plików JPG/TIF.")
        return

    output_csv = os.path.join(folder, "gps_data.csv")
    results_text.delete(1.0, tk.END)

    with open(output_csv, mode='w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Filename', 'Latitude', 'Longitude', 'Altitude'])

        for filename in files:
            full_path = os.path.join(folder, filename)
            gps = get_exif_data(full_path)
            if gps:
                lat, lon, alt = gps
                csvwriter.writerow([filename, lat, lon, alt])
                results_text.insert(tk.END, f"{filename} -> GPS: {lat}, {lon}, {alt}\n")
            else:
                results_text.insert(tk.END, f"{filename} -> brak danych GPS\n")

    results_text.insert(tk.END, f"\nZapisano dane do pliku:\n{output_csv}")

root = tk.Tk()
root.title("Extractor GPS z zdjęć")

btn = tk.Button(root, text="Wybierz folder i zacznij", command=run_extraction)
btn.pack(pady=10)

results_text = scrolledtext.ScrolledText(root, width=80, height=20)
results_text.pack(padx=10, pady=10)

root.mainloop()