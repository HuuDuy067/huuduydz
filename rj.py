import os
import json
import time

# =========================================================================
# CẤU HÌNH ĐƯỜNG DẪN WORKSPACE CỦA EXECUTOR
# Mặc định đang để Delta. Nếu dùng Codex, Fluxus thì đổi dấu #
# =========================================================================
WORKSPACE_PATH = "/storage/emulated/0/Delta/workspace/rj.json"
# WORKSPACE_PATH = "/storage/emulated/0/codex/workspace/rj.json"
# WORKSPACE_PATH = "/storage/emulated/0/fluxus/workspace/rj.json"
# WORKSPACE_PATH = "/storage/emulated/0/arceusx/workspace/rj.json"

TIMEOUT_SECONDS = 60 # Giới hạn thời gian chết (60 giây)
PACKAGE_NAME = "com.roblox.client"

def kill_and_start_roblox():
    print("\n[!] PHÁT HIỆN GAME TREO HOẶC VĂNG! TIẾN HÀNH RESTART...")
    
    # 1. Force Stop Roblox (Yêu cầu quyền ROOT - su)
    print("[*] Đang đóng Roblox...")
    os.system(f"su -c 'am force-stop {PACKAGE_NAME}'")
    time.sleep(3)
    
    # 2. Khởi động lại Roblox
    print("[*] Đang mở lại Roblox...")
    os.system(f"su -c 'am start -n {PACKAGE_NAME}/com.roblox.client.Activity'")
    
    print("[+] Hoàn tất! Chờ 30s để game load lên...")
    
    # 3. Tạo lại nhịp tim giả để không bị lặp loop kill trong lúc chờ load
    try:
        with open(WORKSPACE_PATH, "w") as f:
            json.dump({"time": int(time.time())}, f)
    except:
        pass
        
    time.sleep(30) # Chờ 30s cho game khởi động hẳn

def watch_heartbeat():
    print("=========================================")
    print("🤖 HuDy Hub - Watchdog Auto Rejoin")
    print(f"[*] Theo dõi nhịp tim tại: {WORKSPACE_PATH}")
    print("=========================================")
    
    while True:
        try:
            # Nếu file chưa tồn tại (chưa bật script bao giờ)
            if not os.path.exists(WORKSPACE_PATH):
                print("[*] Đang chờ Script Lua tạo nhịp tim...", end="\r")
                time.sleep(5)
                continue

            # Đọc file rj.json
            with open(WORKSPACE_PATH, "r") as f:
                data = json.load(f)
                last_time = data.get("time", 0)

            current_time = int(time.time())
            diff = current_time - last_time

            print(f"[*] Nhịp tim ổn định. Cập nhật cuối: {diff} giây trước...   ", end="\r")

            # NẾU QUÁ THỜI GIAN -> RESTART
            if diff > TIMEOUT_SECONDS:
                kill_and_start_roblox()

        except json.JSONDecodeError:
            # File đang bị ghi/đọc dở dang, bỏ qua
            pass
        except Exception as e:
            print(f"\n[!] Lỗi không xác định: {e}")

        time.sleep(3) # Kiểm tra mỗi 3 giây

if __name__ == "__main__":
    watch_heartbeat()
