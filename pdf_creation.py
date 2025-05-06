from fpdf import FPDF
from Lyrics import Song_Artist
import re
import os
from pathlib import Path


# Deletes the Previous pdfs to avoid storage issues
def clean_files(path='pdfs'):
    folder = Path(path)
    folder.mkdir(exist_ok=True)
    for file in folder.iterdir():
        if file.is_file():
            file.unlink()


def pdf_setup(song_name):
    # Generate the pdf itself
    song_artist = Song_Artist(song_name)
    safe_name = re.sub(r'[\\/*?:"<>|]', "", song_name.replace(" ", "_"))
    folder = 'pdfs'
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f'{safe_name}.pdf')
    return safe_name, song_artist, file_path


def pdf_generation(song_name, song_artist, chords_text, file_path):
    pdf = FPDF('P', 'mm', 'Letter')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Font and Title
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVu', '', 16)
    pdf.cell(0, 10, f'{song_name.capitalize()}', ln=1, align='C')
    pdf.cell(0, 10, f'from - {song_artist}', ln=1, align='C')

    # Line Break
    pdf.ln(10)

    # Chords and Lyrics of Pdf
    pdf.set_font('DejaVu', size=12)
    for line in chords_text.split('\n'):
        pdf.cell(0, 8, line, ln=1)

    # File Saving
    pdf.output(file_path, 'F')


def generate_song_pdf(song_name, chords_text):
    clean_files()
    safe_name, song_artist, file_path = pdf_setup(song_name)
    pdf_generation(song_name, song_artist, chords_text, file_path)

    return file_path
