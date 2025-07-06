import asyncio
import aiohttp
from multiprocessing import Process
import os
import random

# ============================
# Daftar User-Agent
# ============================

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3.1 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3.1 Mobile/15E148 Safari/604.1",
]

# ============================
# Muat Target dari File
# ============================

def load_targets(filename="list.txt"):
    if not os.path.exists(filename):
        print(f"File {filename} tidak ditemukan.")
        return []
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]

# ============================
# Daftar Plugin
# ============================

plugin_list = [
    "jkdevkit",
    "wp-downloadmanager",
    "contact-form-7",
    "woocommerce",
    "elementor",
    "revslider",
    "wordfence",
    "yoast-seo",
    "wp-file-manager",
    "filebird"
]

# ============================
# Simpan Hasil ke File
# ============================

def save_to_plugin_file(plugin, text):
    fname = f"{plugin}.txt"
    with open(fname, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# ============================
# Async Scan Plugin
# ============================

async def scan_plugin(session, plugin, target):
    paths = [
        f"/wp-content/plugins/{plugin}/",
        f"/wp-content/plugins/{plugin}/readme.txt",
        f"/wp-content/plugins/{plugin}/{plugin}.php",
        f"/wp-content/plugins/{plugin}/style.css",
        f"/wp-content/plugins/{plugin}/js/admin.js"
    ]

    for path in paths:
        url = target.rstrip("/") + path
        try:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    result = f"[✓] {target} ➜ {plugin} ditemukan di {url}"
                    print(result)
                    save_to_plugin_file(plugin, result)
                    return
        except Exception:
            pass

    result = f"[×] {target} ➜ {plugin} tidak terdeteksi"
    print(result)
    save_to_plugin_file(plugin, result)

# ============================
# Async Runner per Target
# ============================

async def async_scanner(target, user_agent):
    headers = {"User-Agent": user_agent}
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [scan_plugin(session, plugin, target) for plugin in plugin_list]
        await asyncio.gather(*tasks)

# ============================
# Multiprocessing Worker
# ============================

def run_scanner(target):
    user_agent = random.choice(USER_AGENTS)
    print(f"🚀 Memulai proses untuk {target} dengan User-Agent:\n{user_agent}\n")
    asyncio.run(async_scanner(target, user_agent))

# ============================
# Entry Point
# ============================

if __name__ == "__main__":
    targets = load_targets("list.txt")

    if not targets:
        print("🚫 Tidak ada target ditemukan di list.txt")
        exit(1)

    print("🚀 Memulai pemindaian plugin...\n")

    processes = []
    for t in targets:
        p = Process(target=run_scanner, args=(t,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    print("\n✅ Semua proses selesai. Hasil tersimpan per plugin.")
