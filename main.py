import sys
import subprocess

# Auto-install dependencies if they are missing
try:
    import eel
    import fitz  # PyMuPDF
    import requests
    from dotenv import load_dotenv, set_key
    from google import genai
    from groq import Groq
except ImportError:
    print("Dependencies missing. Auto-installing from requirements.txt...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except Exception as e:
        print(f"Error auto-installing dependencies: {e}")
        print("Please run: pip install -r requirements.txt")

import os
import json
import base64
import datetime
import hashlib
import fitz  # PyMuPDF
import eel
from dotenv import load_dotenv, set_key

# Load env variables
load_dotenv()

APP_DATA_DIR = os.path.join(os.getenv('APPDATA', ''), 'BintangOCRHanziPinyin')
os.makedirs(APP_DATA_DIR, exist_ok=True)

# Authentication
USERS_FILE = os.path.join(APP_DATA_DIR, 'users.json')

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except json.JSONDecodeError: return {}
    return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)

@eel.expose
def register_user(username, password):
    users = load_users()
    if username in users:
        return {"success": False, "message": "Username already exists."}
    if not username.strip() or not password.strip():
        return {"success": False, "message": "Username and password cannot be empty."}
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    users[username] = {"password": hashed_pw}
    save_users(users)
    return {"success": True}

@eel.expose
def login_user(username, password):
    users = load_users()
    if username not in users:
        return {"success": False, "message": "User not found. Please register."}
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    if users[username]["password"] == hashed_pw:
        return {"success": True}
    return {"success": False, "message": "Invalid password."}

@eel.expose
def get_api_keys():
    return {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
        "GEMINI_API_KEY2": os.getenv("GEMINI_API_KEY2", ""),
        "GEMINI_API_KEY3": os.getenv("GEMINI_API_KEY3", ""),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""),
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", ""),
        "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY", ""),
        "MISTRAL_API_KEY": os.getenv("MISTRAL_API_KEY", "")
    }

@eel.expose
def save_api_keys(keys):
    env_file = ".env"
    if not os.path.exists(env_file):
        open(env_file, 'a').close()
    for k, v in keys.items():
        if v is not None:
            os.environ[k] = v
            set_key(env_file, k, v)
    return {"success": True}

# Setup History
def get_history_file(username):
    # Sanitize username for filename
    clean_uname = "".join(c for c in username if c.isalnum())
    if not clean_uname: clean_uname = "default"
    return os.path.join(APP_DATA_DIR, f"history_{clean_uname}.json")

def load_history_file(username):
    hfile = get_history_file(username)
    if os.path.exists(hfile):
        with open(hfile, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except json.JSONDecodeError: return []
    return []

def save_to_history(username, filename, result_json, ai_choice):
    history = load_history_file(username)
    history.append({
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename": filename,
        "ai_choice": ai_choice,
        "result": result_json
    })
    # Keep only last 50
    history = history[-50:]
    with open(get_history_file(username), 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

@eel.expose
def get_history(username):
    return json.dumps(load_history_file(username), ensure_ascii=False)

def get_system_prompt(enable_correction, target_output):
    if target_output == "Pinyin & Hanzi":
        jenis_ekstraksi = "PINYIN beserta HANZI-nya"
        contoh_baris = "Halaman 1\n\nKolom 1 (Paling Kanan)\n[Pinyin 1] [Hanzi 1]\n[Pinyin 2] [Hanzi 2]\n\nKolom 2\n[Pinyin 1] [Hanzi 1]\n[Pinyin 2] [Hanzi 2]"
    elif target_output == "Hanzi":
        jenis_ekstraksi = "hanya HANZI"
        contoh_baris = "Halaman 1\n\nKolom 1 (Paling Kanan)\n[Hanzi 1]\n[Hanzi 2]\n\nKolom 2\n[Hanzi 1]\n[Hanzi 2]"
    else:
        jenis_ekstraksi = "hanya PINYIN"
        contoh_baris = "Halaman 1\n\nKolom 1 (Paling Kanan)\n[Pinyin 1]\n[Pinyin 2]\n\nKolom 2\n[Pinyin 1]\n[Pinyin 2]"

    base_prompt = f"Anda adalah AHLI LITERASI MANDARIN (VERSI 4.0).\n"
    base_prompt += f"Lakukan ekstraksi Teks ({jenis_ekstraksi}) dari gambar yang diberikan.\n\n"
    
    base_prompt += "ATURAN FORMAT EKSTRAKSI (SANGAT KETAT):\n"
    base_prompt += "1. Urutan kolom dibaca dari KANAN ke KIRI.\n"
    base_prompt += "2. Setiap kata/karakter harus berada di barisnya sendiri (vertikal ke bawah).\n"
    base_prompt += "3. Teks harus dikelompokkan per kolom, seperti contoh di bawah ini.\n\n"
    
    base_prompt += "CONTOH TEKS YANG DIINGINKAN (Ganti dengan teks aslinya):\n"
    base_prompt += f"{contoh_baris}\n...dan seterusnya ke arah kiri.\n\n"

    base_prompt += "ATURAN RESPONSE JSON:\n"
    base_prompt += "Kirimkan output HANYA dalam format JSON Object yang rapi.\n"
    
    if enable_correction:
        base_prompt += "{\n  \"teks_utama\": \"(MASUKKAN SELURUH TEKS EKSTRAKSI DISINI DENGAN FORMAT DI ATAS. Gunakan newline ganda antar kolom.)\",\n  \"koreksi\": [\"koreksi 1\", \"koreksi 2\"]\n}"
    else:
        base_prompt += "{\n  \"teks_utama\": \"(MASUKKAN SELURUH TEKS EKSTRAKSI DISINI DENGAN FORMAT DI ATAS. Gunakan newline ganda antar kolom.)\"\n}"
        
    return base_prompt

def convert_pdf_to_base64_image(base64_data):
    # Decode PDF base64
    pdf_bytes = base64.b64decode(base64_data)
    # Open with PyMuPDF
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    # Get first page
    page = doc.load_page(0)
    # Render to pixmap
    pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
    # Convert to image bytes (PNG)
    img_bytes = pix.tobytes("png")
    # Encode back to base64
    return base64.b64encode(img_bytes).decode('utf-8'), "image/png"

def call_gemini(base64_data, mime_type, model_name, api_key_name, enable_correction, target_output):
    # Import google.genai dynamic initialization
    from google import genai
    from google.genai import types
    
    api_key = os.getenv(api_key_name)
    if not api_key:
        raise Exception(f"API KEY {api_key_name} KOSONG")
        
    client = genai.Client(api_key=api_key)
    
    prompt = get_system_prompt(enable_correction, target_output)
    
    response = client.models.generate_content(
        model=model_name,
        contents=[
             types.Part.from_bytes(
                data=base64.b64decode(base64_data),
                mime_type=mime_type,
             ),
             prompt
        ],
        config=types.GenerateContentConfig(
             response_mime_type="application/json"
        )
    )
    return response.text

def call_groq(base64_data, mime_type, enable_correction, target_output):
    from groq import Groq
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key: raise Exception("GROQ_API_KEY KOSONG")
    client = Groq(api_key=api_key)
    
    # Needs data URI pattern
    data_uri = f"data:{mime_type};base64,{base64_data}"
    prompt = get_system_prompt(enable_correction, target_output)
    
    completion = client.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=[
            {"role": "system", "content": prompt.replace('\n', ' ')},
            {"role": "user", "content": [
                {"type": "text", "text": "Extract correctly as JSON."},
                {"type": "image_url", "image_url": {"url": data_uri}}
            ]}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    return completion.choices[0].message.content

def call_openai_compatible(base64_data, mime_type, endpoint, api_key, model_name, enable_correction, target_output):
    if not api_key: raise Exception(f"API KEY KOSONG untuk {model_name}")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data_uri = f"data:{mime_type};base64,{base64_data}"
    prompt = get_system_prompt(enable_correction, target_output)
    
    payload = {
        "model": model_name,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": [
                {"type": "text", "text": "Respond in JSON format according to the prompt."},
                {"type": "image_url", "image_url": {"url": data_uri}}
            ]}
        ]
    }
    
    response = requests.post(endpoint, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']


def parse_json_result(res_str):
    clean_json = res_str
    if '```json' in clean_json: clean_json = clean_json.split('```json')[1].split('```')[0]
    elif '```' in clean_json: clean_json = clean_json.split('```')[1].split('```')[0]
    return json.loads(clean_json.strip())

@eel.expose
def jalankan_ocr(base64_data, mime_type, filename, ai_choice, enable_correction, target_output, username="default"):
    print(f"Memproses {filename} varian {target_output} via {ai_choice} (Koreksi: {enable_correction})...")
    
    # Image Preparation (Support multi-page PDFs)
    images_to_process = []
    if 'pdf' in mime_type.lower():
        try:
            pdf_bytes = base64.b64decode(base64_data)
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            for i in range(len(doc)):
                page = doc.load_page(i)
                pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
                b64 = base64.b64encode(pix.tobytes("png")).decode('utf-8')
                images_to_process.append((b64, "image/png"))
        except Exception as e:
            return json.dumps({"error": f"Gagal convert PDF: {str(e)}"})
    else:
        images_to_process.append((base64_data, mime_type))

    # Eksekusi AI untuk setiap gambar/halaman
    combined_teks_utama = ""
    combined_koreksi = []
    
    # Progress info function
    def report_progress(current, total):
        pass # Optional to report back
        
    for idx, (b64, mtype) in enumerate(images_to_process):
        result_text = None
        
        def try_gemini1(): return call_gemini(b64, mtype, "gemini-3.5-flash", "GEMINI_API_KEY", enable_correction, target_output)
        def try_gemini2(): return call_gemini(b64, mtype, "gemini-3.5-flash", "GEMINI_API_KEY2", enable_correction, target_output)
        def try_gemini3(): return call_gemini(b64, mtype, "gemini-3.5-flash", "GEMINI_API_KEY3", enable_correction, target_output)
        def try_groq(): return call_groq(b64, mtype, enable_correction, target_output)
        def try_github(): return call_openai_compatible(b64, mtype, "https://models.inference.ai.azure.com/chat/completions", os.getenv("GITHUB_TOKEN"), "gpt-4o", enable_correction, target_output)
        def try_openrouter(): return call_openai_compatible(b64, mtype, "https://openrouter.ai/api/v1/chat/completions", os.getenv("OPENROUTER_API_KEY"), "qwen/qwen-2-vl-72b-instruct:free", enable_correction, target_output)
        def try_mistral(): return call_openai_compatible(b64, mtype, "https://api.mistral.ai/v1/chat/completions", os.getenv("MISTRAL_API_KEY"), "pixtral-12b-2409", enable_correction, target_output)

        if ai_choice == "Auto Fallback":
            fallbacks = [("Gemini 1", try_gemini1), ("Gemini 2", try_gemini2), ("Gemini 3", try_gemini3), ("Groq", try_groq), ("GitHub", try_github), ("OpenRouter", try_openrouter), ("Mistral", try_mistral)]
            last_error = ""
            for name, func in fallbacks:
                try:
                    result_text = func()
                    break
                except Exception as e:
                    last_error = str(e)
                    continue
            if not result_text: return json.dumps({"error": f"Semua service Auto Fallback gagal. Last error: {last_error}"})
        else:
            try:
                if ai_choice == "Gemini 1": result_text = try_gemini1()
                elif ai_choice == "Gemini 2": result_text = try_gemini2()
                elif ai_choice == "Gemini 3": result_text = try_gemini3()
                elif ai_choice == "Groq": result_text = try_groq()
                elif ai_choice == "GitHub": result_text = try_github()
                elif ai_choice == "OpenRouter": result_text = try_openrouter()
                elif ai_choice == "Mistral": result_text = try_mistral()
                else: result_text = try_gemini1()
            except Exception as e:
                return json.dumps({"error": str(e)})

        try:
            parsed = parse_json_result(result_text)
            if combined_teks_utama: combined_teks_utama += "\n\n"
            combined_teks_utama += f"--- HALAMAN {idx+1} ---\n" + parsed.get('teks_utama', '')
            
            koreksi = parsed.get('koreksi', [])
            if isinstance(koreksi, list): combined_koreksi.extend(koreksi)
            elif isinstance(koreksi, str): combined_koreksi.append(koreksi)
        except json.JSONDecodeError:
            return json.dumps({"error": f"Output dari AI bukan JSON yang valid di halaman {idx+1}", "raw": result_text})

    final_result = {
        "teks_utama": combined_teks_utama,
        "koreksi": combined_koreksi,
        "target_output": target_output
    }
    
    save_to_history(username, filename, final_result, ai_choice)
    return json.dumps(final_result, ensure_ascii=False)

if __name__ == '__main__':
    # Initialize Eel application
    if getattr(sys, 'frozen', False):
        web_dir = os.path.join(sys._MEIPASS, 'web')
    else:
        web_dir = 'web'
    eel.init(web_dir)
    
    # Start app
    print("Memulai Bintang OCR Hanzi Pinyin...")
    try:
        if getattr(sys, 'frozen', False):
            # Mode Desktop Native (saat dicompile jadi EXE Windows)
            eel.start('index.html', mode='chrome', host='0.0.0.0', port=3000, block=True, size=(1280, 800), cmdline_args=['--app=http://localhost:3000'])
        else:
            # Mode Cloud / Web Server (Untuk preview di AI Studio ini)
            print("Berjalan di mode Web Server (Port 3000)...")
            eel.start('index.html', mode=None, host='0.0.0.0', port=3000, block=True)
    except Exception as e:
        print(f"Gagal membuka browser otomatis: {e}")
        print("Fallback ke server cloud di port 3000...")
        eel.start('index.html', mode=None, host='0.0.0.0', port=3000, block=True)
