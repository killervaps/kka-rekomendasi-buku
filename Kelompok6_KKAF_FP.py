import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import requests
import io

# Daftar genre yang tersedia
available_genres = [
    "fantasy", "romance", "science fiction", "mystery", "thriller",
    "horror", "history", "biography", "adventure", "poetry"
]

# Peta mood dan kata kunci
mood_keywords_map = {
    "santai": [
        "calm", "relaxing", "gentle", "feel-good", "peaceful", "soothing", "light-hearted",
        "serene", "tranquil", "easy-going", "casual", "refreshing", "laid-back", "comforting",
        "quiet", "restful", "breezy", "harmonious", "stillness", "unwind", "stress-free"
    ],
    "bersemangat": [
        "exciting", "action", "adventure", "fast-paced", "heroic", "thrilling", "energetic",
        "dynamic", "lively", "bold", "spirited", "courageous", "ambitious", "enthusiastic",
        "charged", "electrifying", "fired-up", "exhilarating", "high-energy", "unstoppable"
    ],
    "sedih": [
        "emotional", "sad", "touching", "tragic", "heartbreaking", "melancholic", "sorrowful",
        "grief", "poignant", "tear-jerking", "bittersweet", "mournful", "blue", "depressing",
        "miserable", "woeful", "downcast", "forlorn", "heartache", "despair", "gloomy"
    ],
    "bahagia": [
        "uplifting", "happy", "cheerful", "comedy", "joyful", "bright", "funny", "delightful",
        "positive", "optimistic", "gleeful", "sunny", "hilarious", "content", "satisfying",
        "radiant", "jubilant", "ecstatic", "smiling", "laughing", "exuberant", "blissful"
    ],
    "penasaran": [
        "curious", "suspenseful", "mystery", "investigative", "exploratory", "intriguing",
        "enigmatic", "questioning", "detective", "whodunit", "puzzling", "unknown", "engaging",
        "analytical", "uncovering", "searching", "inquisitive", "solving", "secretive", "hidden"
    ],
    "horor": [
        "scary", "eerie", "haunted", "supernatural", "chilling", "terrifying", "macabre",
        "spine-tingling", "dark", "creepy", "paranormal", "gothic", "ghostly", "ominous",
        "disturbing", "fearful", "horrifying", "nightmarish", "spooky", "sinister", "menacing"
    ],
    "motivasi": [
        "inspiring", "motivational", "uplifting", "self-help", "empowering", "encouraging",
        "driven", "goal-oriented", "success", "achievement", "confidence", "ambition",
        "productive", "self-improvement", "growth", "perseverance", "resilience", "determination",
        "aspirational", "life-changing", "goal-setting", "dreams", "dedicated", "focus"
    ],
    "melamun": [
        "nostalgic", "dreamy", "magical", "historical", "reflective", "wistful", "contemplative",
        "otherworldly", "imaginative", "daydreaming", "ethereal", "reminiscent", "sentimental",
        "fantastical", "yearning", "meditative", "tranquil", "romanticized", "visions", "thoughtful"
    ],
    "penuh imajinasi": [
        "imaginative", "creative", "fantasy", "unique", "inventive", "visionary", "artistic",
        "futuristic", "unconventional", "original", "innovative", "out-of-the-box", "unusual",
        "mythical", "expressive", "boundless", "limitless", "explorative", "novel", "unreal"
    ],
    "intelektual": [
        "thought-provoking", "intellectual", "philosophy", "science", "deep", "complex",
        "analytical", "academic", "insightful", "rational", "logical", "critical", "knowledgeable",
        "educational", "mind-expanding", "cerebral", "enlightening", "scholarly", "systematic",
        "theoretical", "conceptual", "studious", "thoughtful", "diligent", "factual"
    ]
}


# Peta mood alternatif untuk menghindari output kosong
mood_alternatives = {
    "santai": ["bahagia", "melamun", "motivasi"],
    "bersemangat": ["penasaran", "penuh imajinasi", "motivasi"],
    "sedih": ["melamun", "intelektual", "horor"],
    "bahagia": ["santai", "motivasi", "penuh imajinasi"],
    "penasaran": ["bersemangat", "penuh imajinasi", "intelektual"],
    "horor": ["penasaran", "melamun", "sedih"],
    "motivasi": ["bahagia", "santai", "bersemangat"],
    "melamun": ["santai", "penuh imajinasi", "sedih"],
    "penuh imajinasi": ["bersemangat", "penasaran", "melamun"],
    "intelektual": ["penasaran", "sedih", "motivasi"]
}


# Fungsi untuk mendapatkan daftar buku dengan gambar dari Open Library API
def get_books_by_genres(genres):
    books = []
    for genre in genres:
        url = f"https://openlibrary.org/search.json?subject={genre}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for book in data['docs'][:100]:  # Ambil buku per genre
                title = book.get('title', 'Unknown Title')
                author = ', '.join(book.get('author_name', ['Unknown Author']))
                publish_year = book.get('first_publish_year', 'Unknown Year')
                cover_id = book.get('cover_i')  # ID gambar sampul
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else None
                description = book.get('subject', [])
                books.append({
                    'title': title,
                    'author': author,
                    'year': publish_year,
                    'cover_url': cover_url,
                    'description': description
                })
        else:
            messagebox.showerror("Error", f"Failed to fetch data for genre '{genre}'.")
    return books

# Fungsi untuk memberikan skor heuristik berdasarkan mood
def calculate_heuristic(book, mood_keywords):
    score = 0
    for keyword in mood_keywords:
        if keyword.lower() in ' '.join(book.get('description', [])).lower():
            score += 1
    return score

# Fungsi untuk mencari mood alternatif jika tidak ada buku yang cocok
def find_alternative_mood(mood):
    return mood_alternatives.get(mood, [])

# Fungsi untuk mencari buku berdasarkan mood
def recommend_books_by_mood(books, mood):
    # Cari buku berdasarkan mood utama
    mood_keywords = mood_keywords_map.get(mood, [])
    scored_books = []

    for book in books:
        heuristic_score = calculate_heuristic(book, mood_keywords)
        if heuristic_score > 0:
            scored_books.append((book, heuristic_score))

    # Jika tidak ada hasil, coba mood alternatif
    if not scored_books:
        alternative_moods = find_alternative_mood(mood)
        for alt_mood in alternative_moods:
            alt_keywords = mood_keywords_map.get(alt_mood, [])
            for book in books:
                heuristic_score = calculate_heuristic(book, alt_keywords)
                if heuristic_score > 0:
                    scored_books.append((book, heuristic_score))
            
            # Jika mood alternatif pertama menghasilkan hasil, berhenti mencari
            if scored_books:
                messagebox.showinfo(
                    "Info",
                    f"Tidak ada buku yang cocok dengan mood '{mood}'. Menampilkan hasil untuk mood alternatif '{alt_mood}'."
                )
                break

    # Jika masih tidak ada hasil, fallback ke semua buku
    if not scored_books:
        messagebox.showinfo(
            "Info",
            "Tidak ada buku yang cocok dengan mood Anda. Menampilkan buku tanpa filter mood."
        )
        scored_books = [(book, 0) for book in books]

    # Urutkan berdasarkan skor heuristik
    scored_books = sorted(scored_books, key=lambda x: x[1], reverse=True)
    return scored_books[:10]  # Ambil maksimal 10 buku terbaik



def fetch_recommendations():
    global loading_label
    selected_genres = [genre for genre, var in genre_vars.items() if var.get() == 1]
    mood = mood_input.get().lower()

    if not selected_genres or not mood:
        messagebox.showwarning("Input Error", "Genre dan mood tidak boleh kosong.")
        return

    # Proses rekomendasi
    root.after(100, lambda: process_recommendations(selected_genres, mood))

def process_recommendations(selected_genres, mood):
    books = get_books_by_genres(selected_genres)
    if books:
        recommended_books = recommend_books_by_mood(books, mood)
        if recommended_books:
            display_books(recommended_books)
        else:
            result_display.delete('1.0', tk.END)
            result_display.insert(tk.END, "Tidak ada buku yang ditemukan.")
    else:
        result_display.delete('1.0', tk.END)
        result_display.insert(tk.END, "Tidak ada buku yang ditemukan.")



# Tambahkan Frame Scrollable untuk Hasil
class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, bg="#f0f8ff")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#f0f8ff")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

# Fungsi untuk menampilkan buku dengan gambar dan nilai heuristik
def display_books(scored_books):
    # Bersihkan frame sebelumnya
    for widget in result_frame.scrollable_frame.winfo_children():
        widget.destroy()

    for idx, (book, score) in enumerate(scored_books):
        frame = tk.Frame(result_frame.scrollable_frame, bg="white", relief=tk.RAISED, bd=2)
        frame.pack(padx=10, pady=10, fill="x")

        # Gambar buku
        if book['cover_url']:
            try:
                img_data = requests.get(book['cover_url']).content
                img = Image.open(io.BytesIO(img_data))
                img = img.resize((100, 150))
                img_tk = ImageTk.PhotoImage(img)
                img_label = tk.Label(frame, image=img_tk, bg="white")
                img_label.image = img_tk
                img_label.grid(row=0, column=0, rowspan=4, padx=10, pady=10)
            except:
                pass

        # Informasi buku
        tk.Label(frame, text=f"Judul: {book['title']}", bg="white", font=("Arial", 10, "bold")).grid(row=0, column=1, sticky="w")
        tk.Label(frame, text=f"Penulis: {book['author']}", bg="white", font=("Arial", 10)).grid(row=1, column=1, sticky="w")
        tk.Label(frame, text=f"Tahun: {book['year']}", bg="white", font=("Arial", 10)).grid(row=2, column=1, sticky="w")
        tk.Label(frame, text=f"Nilai Heuristik: {score}", bg="white", font=("Arial", 10)).grid(row=3, column=1, sticky="w")


# GUI Tkinter
root = tk.Tk()
root.title("Sistem Rekomendasi Buku")
root.configure(bg="#f0f8ff")

# Header
header = tk.Label(root, text="Rekomendasi Buku Berdasarkan Mood dan Genre",
                  bg="#4682b4", fg="white", font=("Arial", 16, "bold"), pady=10)
header.grid(row=0, column=0, columnspan=3, sticky="ew")

# Label Genre
tk.Label(root, text="Pilih Genre:", bg="#f0f8ff", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="nw")

# Frame untuk Checkbox Genre
genre_frame = tk.Frame(root, bg="#f0f8ff")
genre_frame.grid(row=1, column=1, padx=10, pady=5, sticky="w")

# Variabel untuk menyimpan status checkbox
genre_vars = {}
for idx, genre in enumerate(available_genres):
    var = tk.IntVar()
    cb = tk.Checkbutton(genre_frame, text=genre.title(), variable=var, bg="#f0f8ff")
    cb.grid(row=idx//2, column=idx%2, sticky="w")
    genre_vars[genre] = var

# Input Mood
tk.Label(root, text="Pilih Mood:", bg="#f0f8ff", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
mood_input = ttk.Combobox(root, values=list(mood_keywords_map.keys()))
mood_input.grid(row=2, column=1, padx=10, pady=5, sticky="w")

# Tombol Rekomendasi
recommend_button = tk.Button(root, text="Rekomendasikan Buku", command=fetch_recommendations,
                             bg="#4682b4", fg="white", font=("Arial", 12, "bold"))
recommend_button.grid(row=3, column=0, columnspan=3, pady=10)

# Hasil Rekomendasi (dengan scrollable frame)
result_frame = ScrollableFrame(root)
result_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

# Jalankan aplikasi
root.mainloop()
