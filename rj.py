import os
import json
import time
import subprocess

# =========================================================================
# HUDY HUB - MULTI-ACCOUNT WATCHDOG (FIX FOR CLONED APPS)
# Tính năng: Kiểm tra mỗi 60s, Kill App và Ép Join thẳng vào King Legacy
# Thêm công cụ dò tìm Tên Gói (Package Name) cho các bản Clone ẩn danh.
# =========================================================================

BASE_WORKSPACE = "/storage/emulated/0/Delta/workspace/"
TIMEOUT_SECONDS = 60
KING_LEGACY_PLACE_ID = "4520749081"

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def find_roblox_packages():
    clear_screen()
    print("=========================================")
    print("🔍 ĐANG QUÉT CÁC BẢN ROBLOX TRÊN MÁY...")
    print("=========================================")
    try:
        # Lọc tất cả package có chữ roblox
        out = subprocess.check_output("su -c 'pm list packages | grep -i roblox'", shell=True).decode('utf-8')
        packages = out.strip().split('\n')
        
        if not packages or packages == ['']:
            print("⚠️ Không tìm thấy tên có chữ 'roblox', đang tìm chữ 'delta' hoặc 'vng'...")
            out = subprocess.check_output("su -c 'pm list packages | grep -iE \"delta|vng\"'", shell=True).decode('utf-8')
            packages = out.strip().split('\n')
            
        if not packages or packages == ['']:
            print("❌ Vẫn không tìm thấy! Bạn hãy tự vào Cài đặt -> Ứng dụng để xem tên gói.")
        else:
            print("✅ TÌM THẤY CÁC GÓI SAU ĐÂY (Hãy copy tên của bản Clone):")
            for pkg in packages:
                if pkg:
                    print(f"   👉 {pkg.replace('package:', '').strip()}")
    except Exception as e:
        print(f"❌ Lỗi khi tìm kiếm: {e}")
    
    print("=========================================")
    input("Bấm phím Enter để quay lại Menu chính...")

def kill_and_start_roblox(package_name, workspace_path, place_id=None):
    print(f"\n[!] PHÁT HIỆN [{package_name}] BỊ TREO/VĂNG! TIẾN HÀNH RESTART...")
    
    # 1. Force Stop Clone App cụ thể (Chém 2 nhát cho chắc)
    print(f"[*] Đang đóng app: {package_name}...")
    os.system(f"su -c 'am force-stop {package_name}'")
    os.system(f"su -c 'killall -9 {package_name} > /dev/null 2>&1'") 
    time.sleep(3)
    
    # 2. Mở lại App
    if place_id:
        print(f"[*] Đang ép mở thẳng vào Game (PlaceID: {place_id})...")
        # Sử dụng -p thay vì -n để bypass lỗi Activity Class does not exist của bản Clone
        intent_cmd = f"su -c 'am start -p {package_name} -a android.intent.action.VIEW -d \"roblox://experiences/start?placeId={place_id}\"'"
        os.system(intent_cmd)
    else:
        print(f"[*] Đang mở lại app ra màn hình Home...")
        os.system(f"su -c 'monkey -p {package_name} -c android.intent.category.LAUNCHER 1 > /dev/null 2>&1'")
    
    print("[+] Hoàn tất! Chờ 45s để game load vào máy chủ...")
    
    # 3. Cập nhật lại nhịp tim giả để Python không bị lặp Kill trong lúc chờ game load
    try:
        with open(workspace_path, "w") as f:
            json.dump({"time": int(time.time())}, f)
    except:
        pass
        
    time.sleep(45)

def watch_heartbeat(package_name, workspace_path, place_id):
    clear_screen()
    print("=========================================")
    print(f"🤖 HuDy Hub - Đang bảo vệ: {package_name}")
    print(f"[*] Đọc nhịp tim tại : {workspace_path.split('/')[-1]}")
    if place_id:
        print(f"[*] Chế độ: AUTO JOIN KING LEGACY ({place_id})")
    print("=========================================")
    
    while True:
        try:
            if not os.path.exists(workspace_path):
                print(f"[*] Đang chờ Script Lua tạo file {workspace_path.split('/')[-1]}...", end="\r")
                time.sleep(5)
                continue

            with open(workspace_path, "r") as f:
                data = json.load(f)
                last_time = data.get("time", 0)

            current_time = int(time.time())
            diff = current_time - last_time

            print(f"[*] Nhịp tim: Cập nhật {diff}s trước | App: {package_name}   ", end="\r")

            if diff > TIMEOUT_SECONDS:
                kill_and_start_roblox(package_name, workspace_path, place_id)

        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"\n[!] Lỗi: {e}")

        time.sleep(3)

def main():
    while True:
        clear_screen()
        print("=========================================")
        print(" 🤖 HUDY HUB - MENU MULTI-ACCOUNT")
        print("=========================================")
        print("Chọn Bản Roblox bạn muốn bảo vệ cho Tab này:")
        print("[1] Roblox Gốc   (com.roblox.client)  -> Đọc file: rj_1.json")
        print("[2] Roblox VNG   (com.vng.roblox)     -> Đọc file: rj_2.json")
        print("[3] Roblox Clone (com.roblox.client2) -> Đọc file: rj_3.json")
        print("[4] Tự nhập thông tin THỦ CÔNG (Dành cho bản Clone lạ)")
        print("[5] 🔎 TÌM TÊN GÓI (PACKAGE NAME) THẬT SỰ TRÊN MÁY NÀY")
        print("=========================================")
        
        choice = input("👉 Nhập số (1-5): ")
        
        if choice == "5":
            find_roblox_packages()
            continue
        elif choice == "1":
            pkg = "com.roblox.client"
            ws = BASE_WORKSPACE + "rj_1.json"
        elif choice == "2":
            pkg = "com.vng.roblox"
            ws = BASE_WORKSPACE + "rj_2.json"
        elif choice == "3":
            pkg = "com.roblox.client2"
            ws = BASE_WORKSPACE + "rj_3.json"
        elif choice == "4":
            print("\n-- HƯỚNG DẪN: Dùng Menu [5] để tìm Tên gói, sau đó copy dán vào đây --")
            pkg = input("Nhập Package Name thật (VD: com.vng.robloxx): ").strip()
            filename = input("Nhập tên file json (VD: rj_1.json): ").strip()
            ws = BASE_WORKSPACE + filename
        else:
            print("❌ Lựa chọn không hợp lệ!")
            time.sleep(2)
            continue

        print("\n=========================================")
        print("Bạn có muốn tự động Join thẳng vào game khi Rejoin không?")
        print("[1] Có, Join thẳng vào King Legacy")
        print("[2] Không, chỉ mở ra màn hình chờ của Roblox")
        print("=========================================")
        
        join_choice = input("👉 Nhập số (1-2): ")
        place_id = KING_LEGACY_PLACE_ID if join_choice == "1" else None
            
        watch_heartbeat(pkg, ws, place_id)
        break

if __name__ == "__main__":
    main()
