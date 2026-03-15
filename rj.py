import os
import json
import time
import threading
import subprocess

# =========================================================================
# HUDY HUB - BẢNG ĐIỀU KHIỂN TRUNG TÂM TREO NHIỀU ACC CÙNG LÚC
# Chức năng: Đa luồng kiểm tra nhiều file rj_AccName.json
# Tự động ném Script Lua vào thư mục Autoexec!
# =========================================================================

CONFIG_FILE = "watchdog_config.json"
CONFIG = {
    "base_path": "/storage/emulated/0/Delta",
    "place_id": "4520749081",
    "accounts": [] # Danh sách dạng {"name": "Acc1", "pkg": "com.xxx"}
}

WATCHING = False
status_dict = {}

# ĐÂY LÀ SCRIPT LUA TỰ ĐỘNG NHẬN DIỆN ACC SẼ ĐƯỢC BƠM VÀO AUTOEXEC
LUA_SCRIPT = """task.wait(3) -- Chờ game load ổn định trước khi chạy
if getgenv().HuDyHeartbeat_Running then return end
getgenv().HuDyHeartbeat_Running = true

local Players = game:GetService("Players")
local CoreGui = game:GetService("CoreGui")
local isGameDead = false

while not Players.LocalPlayer do task.wait(0.1) end
local lplr = Players.LocalPlayer
local HEARTBEAT_FILE = "rj_" .. tostring(lplr.Name) .. ".json" 

print("💓 [HuDy Hub] Đã kích hoạt hệ thống Nhịp Tim Đa Tab: " .. HEARTBEAT_FILE)

coroutine.wrap(function()
    while task.wait(1) do 
        if isGameDead then break end
        pcall(function() 
            if writefile then 
                writefile(HEARTBEAT_FILE, '{"time":' .. math.floor(os.time()) .. '}') 
            end 
        end)
    end
end)()

coroutine.wrap(function()
    while task.wait(1) do
        pcall(function()
            local prompt = CoreGui:FindFirstChild("RobloxPromptGui")
            if prompt then
                local overlay = prompt:FindFirstChild("promptOverlay")
                if overlay and overlay:FindFirstChild("ErrorPrompt") and overlay.ErrorPrompt.Visible then
                    local errText = string.lower(overlay.ErrorPrompt.MessageArea.ErrorFrame.ErrorMessage.Text)
                    -- Bắt các lỗi văng game nghiêm trọng
                    if string.find(errText, "273") or string.find(errText, "277") or string.find(errText, "268") or string.find(errText, "279") or string.find(errText, "288") or string.find(errText, "disconnect") then
                        isGameDead = true 
                    end
                end
            end
        end)
    end
end)()

pcall(function()
    game:GetService("GuiService").ErrorMessageChanged:Connect(function(errMsg)
        if not errMsg or errMsg == "" then return end
        local eStr = string.lower(errMsg)
        if string.find(eStr, "273") or string.find(eStr, "277") or string.find(eStr, "268") or string.find(eStr, "279") or string.find(eStr, "288") or string.find(eStr, "disconnect") then isGameDead = true end
    end)
end)
"""

def load_config():
    global CONFIG
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                CONFIG.update(json.load(f))
        except: pass

def save_config():
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(CONFIG, f)
    except: pass

# =====================================================================
# THUẬT TOÁN TÌM THƯ MỤC CHUẨN XÁC (KHÔNG TẠO RÁC)
# =====================================================================
def get_exact_folder(base_path, folder_names_to_try):
    if not os.path.exists(base_path):
        return os.path.join(base_path, folder_names_to_try[0])
        
    existing_dirs = os.listdir(base_path)
    # Lấy danh sách thư mục hiện có (loại bỏ ký tự lạ, chuyển về chữ thường để so sánh)
    clean_dirs = {d.lower().strip(): d for d in existing_dirs}
    
    for target in folder_names_to_try:
        clean_target = target.lower().strip()
        if clean_target in clean_dirs:
            # Trả về tên thư mục GỐC CỦA HỆ THỐNG đang xài (Đúng 100% in hoa/thường)
            return os.path.join(base_path, clean_dirs[clean_target])
            
    # Nếu không có thì mới tạo mới bằng cái tên chuẩn đầu tiên
    return os.path.join(base_path, folder_names_to_try[0])

def install_lua():
    # Tìm chính xác thư mục Autoexecute đang có sẵn
    autoexec_dir = get_exact_folder(CONFIG["base_path"], ["autoexecute", "autoexec"])
    os.makedirs(autoexec_dir, exist_ok=True)

    file_path = os.path.join(autoexec_dir, "HuDy_MultiHeartbeat.lua")
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(LUA_SCRIPT)
        
        print(f"\n✅ ĐÃ CÀI ĐẶT THÀNH CÔNG SCRIPT VÀO AUTOEXEC!")
        print(f"File được lưu chính xác tại: {file_path}")
        print("Bây giờ bạn có thể mở Game lên, Script nhịp tim sẽ tự chạy!")
    except Exception as e:
        print(f"\n❌ Lỗi cài đặt: {e}")
    time.sleep(4)

def monitor_loop(acc):
    name = acc['name']
    pkg = acc['pkg']
    
    # Tìm chính xác thư mục Workspace đang có sẵn
    ws_dir = get_exact_folder(CONFIG["base_path"], ["workspace"])
    os.makedirs(ws_dir, exist_ok=True)
    
    ws_file = os.path.join(ws_dir, f"rj_{name}.json")
    
    while WATCHING:
        try:
            if not os.path.exists(ws_file):
                status_dict[name] = f"⚪ Chờ file rj_{name}.json..."
            else:
                with open(ws_file, "r") as f:
                    data = json.load(f)
                diff = int(time.time()) - data.get('time', 0)
                
                if diff > 60:
                    status_dict[name] = f"🔴 VĂNG {diff}s! Đang Rejoin..."
                    
                    # Kill 2 lớp
                    os.system(f"su -c 'am force-stop {pkg}'")
                    os.system(f"su -c 'killall -9 {pkg} > /dev/null 2>&1'")
                    time.sleep(2)
                    
                    # Ép Join Game
                    pid = CONFIG.get("place_id", "4520749081")
                    cmd = f"su -c 'am start -p {pkg} -a android.intent.action.VIEW -d \"roblox://experiences/start?placeId={pid}\"'"
                    os.system(cmd)
                    
                    # Reset nhịp tim để không kill nhầm lúc đang load
                    with open(ws_file, "w") as f:
                        json.dump({"time": int(time.time())}, f)
                        
                    status_dict[name] = "🟡 Đang chờ game load (45s)..."
                    time.sleep(45)
                else:
                    status_dict[name] = f"🟢 ĐANG CHẠY ({diff}s trước)"
        except json.JSONDecodeError:
            pass # Đang ghi file
        except Exception as e:
            status_dict[name] = f"❌ Lỗi: {str(e)[:20]}"
            
        time.sleep(2)

def start_watchdog():
    global WATCHING
    if len(CONFIG['accounts']) == 0:
        print("\n❌ Bạn chưa thêm Account nào! Bấm [A] để thêm trước.")
        time.sleep(2)
        return
        
    WATCHING = True
    status_dict.clear()
    threads = []
    
    # Bật đa luồng
    for acc in CONFIG['accounts']:
        t = threading.Thread(target=monitor_loop, args=(acc,))
        t.daemon = True
        t.start()
        threads.append(t)
        
    try:
        while WATCHING:
            os.system("clear")
            print("======================================================================")
            print(f" 🤖 HUDY HUB - MULTI-ACCOUNT DASHBOARD (ĐANG BẢO VỆ {len(CONFIG['accounts'])} ACC)")
            print("======================================================================")
            print(f" {'TÊN NHÂN VẬT':<15} | {'PACKAGE NAME (APP)':<20} | TRẠNG THÁI")
            print("----------------------------------------------------------------------")
            for acc in CONFIG['accounts']:
                name = acc['name']
                pkg = acc['pkg']
                status = status_dict.get(name, "⚪ Đang khởi tạo...")
                print(f" {name:<15} | {pkg:<20} | {status}")
            print("======================================================================")
            print(" [Bấm Ctrl + C để thoát Bảng Điều Khiển]")
            time.sleep(2)
    except KeyboardInterrupt:
        WATCHING = False
        print("\nĐang dừng hệ thống soi... Vui lòng đợi...")
        time.sleep(2)

def menu():
    load_config()
    while True:
        os.system("clear")
        print("=============================================================")
        print(" 🤖 HUDY HUB - THIẾT LẬP MASTER WATCHDOG (AUTO REJOIN)")
        print("=============================================================")
        print(f" 📂 Thư mục Executor : {CONFIG['base_path']}")
        print(f" 🎮 PlaceID Tự Join  : {CONFIG['place_id']}")
        print(f" 👥 Số lượng Acc     : {len(CONFIG['accounts'])} Account đang thiết lập")
        print("=============================================================")
        for i, acc in enumerate(CONFIG['accounts']):
            print(f" [{i+1}] {acc['name']} (App: {acc['pkg']})")
        print("=============================================================")
        print(" [A] Thêm Account cần treo")
        print(" [X] Xóa Account")
        print(" [S] Sửa đường dẫn Executor & PlaceID")
        print(" [I] TỰ ĐỘNG BƠM LUA SCRIPT VÀO AUTOEXEC (DÙNG 1 LẦN LÀ ĐƯỢC)")
        print(" [R] 🚀 MỞ MÀN HÌNH DASHBOARD & BẮT ĐẦU TREO")
        print(" [Q] Thoát")
        print("=============================================================")
        
        c = input("👉 Nhập lựa chọn: ").upper()
        if c == 'A':
            print("\n-- LƯU Ý: Tên nhân vật (Name in game) phải gõ chính xác in hoa, in thường --")
            name = input("Nhập Tên Nhân Vật: ").strip()
            pkg = input("Nhập Package Name (VD: com.vng.roblox, aiu.eyz.stto): ").strip()
            if name and pkg:
                CONFIG['accounts'].append({"name": name, "pkg": pkg})
                save_config()
        elif c == 'X':
            try:
                idx = int(input("\nNhập số thứ tự Acc muốn xóa: ")) - 1
                CONFIG['accounts'].pop(idx)
                save_config()
            except: pass
        elif c == 'S':
            path = input(f"\nNhập đường dẫn gốc Executor (Bỏ trống để giữ {CONFIG['base_path']}): ").strip()
            if path: CONFIG['base_path'] = path
            pid = input(f"Nhập PlaceID tự Join (Bỏ trống để giữ {CONFIG['place_id']}): ").strip()
            if pid: CONFIG['place_id'] = pid
            save_config()
        elif c == 'I':
            install_lua()
        elif c == 'R':
            start_watchdog()
        elif c == 'Q':
            break

if __name__ == "__main__":
    menu()
