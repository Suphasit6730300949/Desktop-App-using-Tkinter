import tkinter as tk
import requests
from PIL import Image, ImageTk
import io

API_URL = "http://127.0.0.1:5001/books"

current_books = []
image_cache = {}

# ---------------- ดึงข้อมูล ----------------
def get_books(keyword=""):
    res = requests.get(API_URL)
    books = res.json()["books"]

    if keyword:
        books = [b for b in books if keyword.lower() in b["title"].lower() or keyword.lower() in b["author"].lower()]

    return books

# ---------------- แสดงหนังสือ ----------------
def show_books(books):
    for widget in scroll_frame.winfo_children():
        widget.destroy()

    result_label.config(text=f"Found {len(books)} books")

    row = 0
    col = 0

    width = canvas.winfo_width()
    max_cols = max(1, width // 240)

    for i in range(max_cols):
        scroll_frame.grid_columnconfigure(i, weight=1)

    for book in books:
        card = tk.Frame(
            scroll_frame,
            width=220,
            height=340,
            bg="#ffffff",  # พื้นขาว
            bd=2,
            relief="solid",
            highlightbackground="#000000",  # ขอบดำ
            highlightthickness=2
        )
        card.grid(row=row, column=col, padx=15, pady=15)
        card.pack_propagate(False)

        # รูปหนังสือ
        img_url = book["image_url"]
        if img_url in image_cache:
            photo = image_cache[img_url]
        else:
            img_data = requests.get(img_url).content
            img = Image.open(io.BytesIO(img_data))
            img = img.resize((120,180))
            photo = ImageTk.PhotoImage(img)
            image_cache[img_url] = photo

        img_label = tk.Label(card, image=photo, bg="#ffffff")
        img_label.image = photo
        img_label.pack(pady=10)

        # ชื่อหนังสือ
        tk.Label(
            card,
            text=book["title"],
            bg="#ffffff",
            fg="#000000",  # ดำ
            font=("Arial", 10, "bold"),
            wraplength=200,
            justify="center"
        ).pack(pady=(5,0))

        # ผู้เขียน
        tk.Label(
            card,
            text="By " + book["author"],
            bg="#ffffff",
            fg="#333333",
            font=("Arial", 9),
            wraplength=200,
            justify="center"
        ).pack(pady=(2,0))

        # ราคา
        tk.Label(
            card,
            text="$" + str(book["price"]),
            bg="#ffffff",
            fg="#ef476f",  # แดง
            font=("Arial", 10, "bold")
        ).pack(pady=(5,0))
        
        col += 1
        if col >= max_cols:
            col = 0
            row += 1

# ---------------- ค้นหา ----------------
def search_books():
    global current_books
    keyword = search_entry.get().strip()
    if keyword == "":
        books = get_books()
    else:
        books = get_books(keyword)
    current_books = books
    show_books(current_books)

# ---------- UI หลัก ----------
root = tk.Tk()
root.title("Anime Book Store")
root.geometry("1000x650")
root.configure(bg="#ffffff")  # พื้นหลังขาว

# Header
header = tk.Frame(root, bg="#ffffff", height=120)
header.pack(fill="x")

tk.Label(
    header,
    text="ANIME BOOK STORE",
    font=("Arial", 28, "bold"),
    bg="#ffffff",
    fg="#000000"
).pack(pady=(20,5))

tk.Label(
    header,
    text="Find your next favorite story.",
    font=("Segoe UI", 12),
    bg="#ffffff",
    fg="#333333"
).pack()

# ---------- Search bar ----------
search_frame = tk.Frame(root, bg="#ffffff")
search_frame.pack(fill="x", pady=15, padx=20)

search_entry = tk.Entry(
    search_frame,
    font=("Segoe UI", 12),
    bd=1,
    relief="solid",
    highlightthickness=0,
    fg="#000000",
    bg="#f0f0f0"
)
search_entry.insert(0, "Search by title or author...")
search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, tk.END))
search_entry.pack(side="left", fill="x", expand=True, padx=(0,10), ipady=6)

search_btn = tk.Button(
    search_frame,
    text="Search",
    command=search_books,
    bg="#ef476f",  # แดง
    fg="white",
    font=("Segoe UI", 10, "bold"),
    bd=0,
    padx=20,
    pady=6,
    activebackground="#d43f5c",
    cursor="hand2"
)
search_btn.pack(side="left")

# Result label
result_label = tk.Label(
    root,
    text="",
    bg="#ffffff",
    fg="#000000",
    font=("Arial", 10)
)
result_label.pack(pady=(0,10))

# ---------- Scroll area ----------
canvas = tk.Canvas(root, bg="#ffffff", highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)

scroll_frame = tk.Frame(canvas, bg="#ffffff")
frame_id = canvas.create_window((0,0), window=scroll_frame, anchor="nw")

# resize canvas (debounce)
def resize_frame(event):
    canvas.itemconfig(frame_id, width=event.width)
    if hasattr(root,"resize_job"):
        root.after_cancel(root.resize_job)
    root.resize_job = root.after(120, lambda: show_books(current_books))

canvas.bind("<Configure>", resize_frame)

# update scroll
def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

scroll_frame.bind("<Configure>", on_configure)

# mouse scroll
def on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", on_mousewheel)

# โหลดครั้งแรก
current_books = get_books()
show_books(current_books)

root.mainloop()