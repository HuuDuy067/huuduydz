import os
import json
import time

# =========================================================================
# HUDY HUB - MULTI-ACCOUNT WATCHDOG (DIRECT JOIN VERSION)
# Tính năng: Kiểm tra mỗi 60s, Kill App và Ép Join thẳng vào King Legacy
# =========================================================================

# Thư mục gốc chứa file json của Executor (Sửa nếu dùng Codex/Fluxus)
BASE_WORKSPACE = "/storage/emulated/0/Delta/workspace/"
TIMEOUT_SECONDS = 60
KING_LEGACY_PLACE_ID = "4520749081"

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def kill_and_start_roblox(package_name, workspace_path, place_id=None):
    print(f"\n[!] PHÁT HIỆN [{package_name}] BỊ TREO/VĂNG! TIẾN HÀNH RESTART...")
    
    # 1. Force Stop Clone App cụ thể
    print(f"[*] Đang đóng app: {package_name}...")
    os.system(f"su -c 'am force-stop {package_name}'")
    time.sleep(3)
    
    # 2. Mở lại App
    if place_id:
        print(f"[*] Đang ép mở thẳng vào Game (PlaceID: {place_id})...")
        # Sử dụng Android Intent để ép Roblox mở thẳng vào PlaceID
        intent_cmd = f"su -c 'am start -n {package_name}/com.roblox.client.Activity -a android.intent.action.VIEW -d \"roblox://experiences/start?placeId={place_id}\"'"
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
        
    time.sleep(45) # Chờ 45s cho game load hẳn vào trong

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

            # KIỂM TRA MỖI 60 GIÂY
            if diff > TIMEOUT_SECONDS:
                kill_and_start_roblox(package_name, workspace_path, place_id)

        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"\n[!] Lỗi: {e}")

        time.sleep(3)

def main():
    clear_screen()
    print("=========================================")
    print(" 🤖 HUDY HUB - MENU MULTI-ACCOUNT")
    print("=========================================")
    print("Chọn Bản Roblox bạn muốn bảo vệ cho Tab này:")
    print("[1] Roblox Gốc   (com.roblox.client)  -> Đọc file: rj_1.json")
    print("[2] Roblox VNG   (com.vng.roblox)     -> Đọc file: rj_2.json")
    print("[3] Roblox Clone (com.roblox.client2) -> Đọc file: rj_3.json")
    print("=========================================")
    
    choice = input("👉 Nhập số (1-3): ")
    
    if choice == "1":
        pkg = "com.roblox.client"
        ws = BASE_WORKSPACE + "rj_1.json"
    elif choice == "2":
        pkg = "com.vng.roblox"
        ws = BASE_WORKSPACE + "rj_2.json"
    elif choice == "3":
        pkg = "com.roblox.client2"
        ws = BASE_WORKSPACE + "rj_3.json"
    else:
        print("❌ Lựa chọn không hợp lệ!")
        return

    print("\n=========================================")
    print("Bạn có muốn tự động Join thẳng vào game khi Rejoin không?")
    print("[1] Có, Join thẳng vào King Legacy")
    print("[2] Không, chỉ mở ra màn hình chờ của Roblox")
    print("=========================================")
    
    join_choice = input("👉 Nhập số (1-2): ")
    place_id = KING_LEGACY_PLACE_ID if join_choice == "1" else None
        
    watch_heartbeat(pkg, ws, place_id)

if __name__ == "__main__":
    main()
