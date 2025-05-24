import os, shutil
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk, ImageEnhance

# HEIC support
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except:
    pass

# ─── Paths ──────────────────────────────────────────────────────────────────────
BASE    = r"C:\Lots"
ADUMP   = os.path.join(BASE, "ADump")
ARCHIVE = os.path.join(ADUMP, "Original Lot Sticker Images")
FINAL   = os.path.join(ADUMP, "Final Lot Sticker Images")
TMP     = os.path.join(ADUMP, "Temp Processing")
BIN     = os.path.join(BASE, "zBin")
for p in (ADUMP, ARCHIVE, FINAL, TMP, BIN):
    os.makedirs(p, exist_ok=True)

# ─── Main window ────────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("Auctionspear.com Lot Builder Pro")
root.geometry("900x900")

# ─── Shared log helper ─────────────────────────────────────────────────────────
def log(msg):
    output_panel.config(state="normal")
    output_panel.insert("end", msg + "\n")
    output_panel.see("end")
    output_panel.config(state="disabled")

# ─── Background helper ─────────────────────────────────────────────────────────
def apply_bg(frame):
    bg_path = os.path.join(BIN, "logo2.png")
    if os.path.exists(bg_path):
        try:
            bg = Image.open(bg_path).resize((900,600), Image.Resampling.LANCZOS).convert("RGBA")
            alpha = bg.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(0.5)
            bg.putalpha(alpha)
            img = ImageTk.PhotoImage(bg)
            lbl = tk.Label(frame, image=img)
            lbl.image = img
            lbl.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            pass

# ─── Top bar (logo only) ───────────────────────────────────────────────────────
top = tk.Frame(root)
top.pack(fill="x", padx=10, pady=5)

# Logo
logo_png = os.path.join(BIN, "logo.png")
if os.path.exists(logo_png):
    logo_im = Image.open(logo_png).resize((32,32), Image.Resampling.LANCZOS)
    logo_img = ImageTk.PhotoImage(logo_im)
    tk.Label(top, image=logo_img).pack(side="left", padx=(0,10))

# ─── Notebook ──────────────────────────────────────────────────────────────────
nb = ttk.Notebook(root)
wiz = ttk.Frame(nb)
tools = ttk.Frame(nb)
nb.add(wiz, text="Wizard")
nb.add(tools, text="Tools")
nb.pack(expand=1, fill="both", padx=10, pady=(0,10))

# ─── Global output panel ───────────────────────────────────────────────────────
output_panel = ScrolledText(root, height=10, wrap="word", state="disabled")
output_panel.config(font=("Segoe UI Emoji", 10))
output_panel.pack(fill="both", padx=10, pady=(0,10))

# ─── Frame factory ─────────────────────────────────────────────────────────────
def create_step_frame(idx):
    f = ttk.Frame(wiz)
    apply_bg(f)
    return f

# ─── Globals ───────────────────────────────────────────────────────────────────
frames = []
current = 0
# for step1 preview
thumbs1 = []
# for step3 preview
thumbs3 = []

# ─── Step 1: Master Images ─────────────────────────────────────────────────────
step1 = create_step_frame(1)
tk.Label(
    step1,
    text="🖼️ Step 1: Master Images",
    font=("Segoe UI Emoji",16)
).pack(pady=10)
tk.Label(step1, text=
    "1️⃣ Place up to 500 Lot Sticker images in the ADump folder\n"
    "2️⃣ Click 'Run Step 1' to convert & archive originals\n"
    "3️⃣ Drag thumbnails to reorder\n"
    "4️⃣ Click 'Apply Order & Refresh' to finalize",
    justify="left", font=("Segoe UI Emoji",12)
).pack(pady=5)

btn_fr1 = tk.Frame(step1); btn_fr1.pack(pady=5)
run_btn1   = tk.Button(btn_fr1, text="Run Step 1", command=lambda: run_master()); run_btn1.pack(side="left", padx=5)
apply_btn1 = tk.Button(btn_fr1, text="Apply Order & Refresh", state="disabled", command=lambda: apply_refresh()); apply_btn1.pack(side="left", padx=5)

pc1 = tk.Frame(step1); pc1.pack(fill="x", padx=10, pady=(5,0))
canvas1 = tk.Canvas(pc1, height=130)
hbar1   = tk.Scrollbar(pc1, orient="horizontal", command=canvas1.xview)
canvas1.configure(xscrollcommand=hbar1.set)
canvas1.pack(side="top", fill="x", expand=True)
hbar1.pack(side="bottom", fill="x")
preview_frame1 = tk.Frame(canvas1)
canvas1.create_window((0,0), window=preview_frame1, anchor="nw")

from PIL import Image

def run_master():
    log("🔄 Starting Step 1...")
    exts = (".jpg",".jpeg",".png",".bmp",".tiff",".webp",".heic")
    files = sorted([f for f in os.listdir(ADUMP)
                    if f.lower().endswith(exts) and not f.lower().startswith("lot")])
    # clean old
    for f in os.listdir(ADUMP):
        if f.lower().startswith("lot") and f.lower().endswith(".jpg"):
            os.remove(os.path.join(ADUMP, f))
    # convert & force size
    for i, fname in enumerate(files, start=1):
        src = os.path.join(ADUMP, fname); new = f"Lot{i:03}.jpg"
        try:
            orig = Image.open(src).convert("RGB")
            if orig.width>=orig.height:
                resized = orig.resize((800,600), Image.Resampling.LANCZOS)
            else:
                resized = orig.resize((600,800), Image.Resampling.LANCZOS)
            resized.save(os.path.join(ADUMP,new),"JPEG")
            shutil.move(src, os.path.join(ARCHIVE,fname))
            log(f"✅ {fname} → {new} (archived)")
        except Exception as e:
            log(f"⚠️ Skipped {fname}: {e}")
    refresh_preview1()
    log(f"🎉 Step 1 Complete! {len(thumbs1)} master images ready.")
    apply_btn1.config(state="normal")

def refresh_preview1():
    thumbs1.clear()
    thumbs1.extend(sorted([f for f in os.listdir(ADUMP) if f.lower().endswith(".jpg")]))
    render_previews1()

def render_previews1():
    for w in preview_frame1.winfo_children():
        w.destroy()
    for idx, fn in enumerate(thumbs1):
        c = tk.Canvas(preview_frame1, width=100, height=120, bd=0, highlightthickness=0)
        c.pack(side="left", padx=5)
        try:
            im = Image.open(os.path.join(ADUMP,fn)); im.thumbnail((100,100), Image.Resampling.LANCZOS)
            tki = ImageTk.PhotoImage(im); c.create_image(0,0,anchor="nw",image=tki); c.image = tki
        except:
            c.create_text(50,50,text="Err")
        c.create_text(50,110,text=fn,font=("Segoe UI Emoji",8))
        def on_rel(e, i=idx):
            x = e.x_root - canvas1.winfo_rootx()
            tgt = max(0,min(len(thumbs1)-1, x//110))
            if tgt!=i:
                thumbs1.insert(tgt, thumbs1.pop(i))
                render_previews1()
        c.bind("<ButtonRelease-1>", on_rel)
    preview_frame1.update_idletasks()
    canvas1.configure(scrollregion=canvas1.bbox("all"))

def apply_refresh():
    log("🔄 Applying new order (Step 1)...")
    mapping,tmp = {},{}
    for i,fn in enumerate(thumbs1, start=1):
        s = os.path.join(ADUMP,fn); d=os.path.join(ADUMP,f"Lot{i:03}.jpg")
        if s.lower()!=d.lower(): mapping[s]=d
    for s,d in mapping.items():
        t=d+".tmp"; os.rename(s,t); tmp[t]=d
    for t,d in tmp.items():
        os.rename(t,d)
    refresh_preview1()
    log("✅ Order applied (Step 1)!")

frames.append(step1)

# ─── Step 2 (unchanged) ─────────────────────────────────────────────────────────
step2 = create_step_frame(2)
tk.Label(
     step2,
     text="📁 Step 2: Final Lot Sticker Images",
     font=("Segoe UI Emoji",16)
 ).pack(pady=10)
tk.Label(step2, text="1️⃣ Your organized Lot Sticker Images will go to:\n"
    f"   {FINAL}\n\n"
    "2️⃣ Now drop your auction photos into ADump folder.\n"
    "3️⃣ Click Next to auto‐run Step 2.",
    justify="left", wraplength=700, font=("Segoe UI Emoji",12)
).pack(padx=20,pady=5,fill="x")

def run_step2():
    log("🔄 Starting Step 2...")
    os.makedirs(FINAL, exist_ok=True)
    lotf = sorted([f for f in os.listdir(ADUMP) if f.lower().startswith("lot") and f.lower().endswith(".jpg")])
    for f in lotf:
        shutil.move(os.path.join(ADUMP,f), os.path.join(FINAL,f))
        log(f"➡️ Moved {f}")
    log(f"🎉 Step 2 Complete! {len(lotf)} archived.")
    # no messagebox—user sees log
frames.append(step2)

# ─── Step 3: REVIEW AUCTION PHOTOS ─────────────────────────────────────────────
step3 = create_step_frame(3)
tk.Label(step3, text="🔍 Step 3: Review Auction Photos", font=("Segoe UI Emoji",16)).pack(pady=10)
tk.Label(
    step3,
    text=(
        "1️⃣ Verify if in order OR arrange your Auction photos so they are in order by lot.\n"
        "2️⃣ Click the Rename & Resize button to get your auction photos organized and ready for the next step."
    ),
    justify="left",
    font=("Segoe UI Emoji",12)
).pack(pady=5)


# Buttons just like Step 1
btn_fr3 = tk.Frame(step3)
btn_fr3.pack(pady=5)
run_btn3 = tk.Button(
    btn_fr3,
    text="Refresh Preview",
    command=lambda: refresh_preview3()
)
run_btn3.pack(side="left", padx=5)
apply_btn3 = tk.Button(
    btn_fr3,
    text="Apply Order & Rename",
    state="disabled",
    command=lambda: apply_refresh3()
)
apply_btn3.pack(side="left", padx=5)

# Preview bar
pc3 = tk.Frame(step3); pc3.pack(fill="x", padx=10, pady=(5,0))
canvas3 = tk.Canvas(pc3, height=130)
hbar3   = tk.Scrollbar(pc3, orient="horizontal", command=canvas3.xview)
canvas3.configure(xscrollcommand=hbar3.set)
canvas3.pack(side="top", fill="x", expand=True)
hbar3.pack(side="bottom", fill="x")
preview_frame3 = tk.Frame(canvas3)
canvas3.create_window((0,0), window=preview_frame3, anchor="nw")

def refresh_preview3():
    thumbs3.clear()
    thumbs3.extend(sorted([
        f for f in os.listdir(ADUMP)
        if os.path.isfile(os.path.join(ADUMP,f))
           and f.lower().endswith((".jpg",".jpeg",".png"))
    ]))
    render_previews3()
    apply_btn3.config(state="normal")
    log(f"🔍 Step 3 Preview: {len(thumbs3)} auction photos found")

def render_previews3():
    for w in preview_frame3.winfo_children():
        w.destroy()
    for idx, fn in enumerate(thumbs3):
        c = tk.Canvas(preview_frame3, width=100, height=120, bd=0, highlightthickness=0)
        c.pack(side="left", padx=5)
        try:
            im = Image.open(os.path.join(ADUMP,fn)); im.thumbnail((100,100), Image.Resampling.LANCZOS)
            tki = ImageTk.PhotoImage(im); c.create_image(0,0,anchor="nw",image=tki); c.image = tki
        except:
            c.create_text(50,50,text="Err")
        c.create_text(50,110,text=fn,font=("Segoe UI Emoji",8))
        def on_rel(e, i=idx):
            x = e.x_root - canvas3.winfo_rootx()
            tgt = max(0,min(len(thumbs3)-1, x//110))
            if tgt!=i:
                thumbs3.insert(tgt, thumbs3.pop(i))
                render_previews3()
        c.bind("<ButtonRelease-1>", on_rel)
    preview_frame3.update_idletasks()
    canvas3.configure(scrollregion=canvas3.bbox("all"))

def apply_refresh3():
    log("🔄 Applying new order (Step 3)...")
    mapping,tmp = {},{}
    for i,fn in enumerate(thumbs3, start=1):
        s = os.path.join(ADUMP,fn)
        d = os.path.join(ADUMP,f"Auction{i:03}.jpg")
        if s.lower()!=d.lower(): mapping[s]=d
    for s,d in mapping.items():
        t = d+".tmp"; os.rename(s,t); tmp[t]=d
    for t,d in tmp.items():
        os.rename(t,d)
    refresh_preview3()
    log("✅ Auction photos renamed and ordered.")

frames.append(step3)

# ─── Step 5 (placeholder) ─────────────────────────────────────────────────────
step5 = create_step_frame(5)
tk.Label(step5, text="🎨 Step 5: Watermark & Resize", font=("Segoe UI Emoji",16)).pack(pady=10)
tk.Label(
    step5,
    text=(
        f"🔄 Next, Final Lot Sticker Images will move to {TMP} for watermarking & resize."
    ),
    justify="left",
    font=("Segoe UI Emoji",12)
).pack(padx=20, pady=5, fill="x")
frames.append(step5)

# ─── Navigation ───────────────────────────────────────────────────────────────
nav = tk.Frame(wiz); nav.pack(side="bottom", fill="x", pady=10)
def navigate(d):
    global current
    if current==0 and d==1:
        run_step2()      # after Step 1→2
    if current==1 and d==1:
        refresh_preview3()  # after Step 2→3
    if 0 <= current+d < len(frames):
        frames[current].pack_forget()
        current += d
        frames[current].pack(fill="both", expand=True)

tk.Button(nav, text="⬅️ Back", command=lambda:navigate(-1)).pack(side="left", padx=20)
tk.Button(nav, text="Next ➡️", command=lambda:navigate(1)).pack(side="right", padx=20)

# ─── Initial ─────────────────────────────────────────────────────────────────
frames[0].pack(fill="both", expand=True)

# ─── Tools tab ────────────────────────────────────────────────────────────────
tk.Button(tools, text="🐞 Report a Bug", command=lambda: os.startfile("mailto:info@buylotsdfw.com")).pack(pady=5)

root.mainloop()