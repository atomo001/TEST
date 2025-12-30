import os
import shutil
import threading
import json
import socket
import subprocess
import platform
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# ======================
# 基础配置
# ======================
HTTP_PORT = 8000
UDP_PORT = 9999
APK_DIR = "send_apks"

os.makedirs(APK_DIR, exist_ok=True)

# ======================
# 工具函数
# ======================
def get_local_ip():
    """获取本机局域网IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def open_file_explorer(path):
    """打开文件夹"""
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        print(f"无法打开文件夹: {e}")

# ======================
# 网络服务（修复版）
# ======================
class ApkRequestHandler(SimpleHTTPRequestHandler):
    """
    关键修复点：
    - 不再手动把 self.path 拼接 APK_DIR（那会导致 /send_apks/send_apks/... 套娃）
    - 直接把静态文件根目录设置为 APK_DIR
    - /apk_list 特殊返回 JSON 列表
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=APK_DIR, **kwargs)

    def do_GET(self):
        if self.path == "/apk_list":
            try:
                apks = [f for f in os.listdir(APK_DIR) if f.lower().endswith(".apk")]
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(apks).encode("utf-8"))
            except Exception:
                self.send_error(500)
            return

        # 其他请求（例如 /app-debug.apk）直接走静态文件
        return super().do_GET()


def start_http_server():
    TCPServer.allow_reuse_address = True
    try:
        with TCPServer(("", HTTP_PORT), ApkRequestHandler) as httpd:
            print(f"[HTTP] APK server running on port {HTTP_PORT}")
            httpd.serve_forever()
    except OSError as e:
        print(f"[HTTP] Port {HTTP_PORT} is busy or error: {e}")


def start_udp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(("", UDP_PORT))
        print(f"[UDP] Listening on port {UDP_PORT}")
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                if data.decode().strip() == "DISCOVER_APK_SERVER":
                    sock.sendto(b"APK_SERVER_RESPONSE", addr)
            except Exception:
                pass
    except OSError:
        print(f"[UDP] Port {UDP_PORT} busy.")

# ======================
# 美化后的 UI（保持不变）
# ======================
class ModernApkServerUI(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        # 应用主题
        # 可以尝试其他主题: 'cosmo', 'flatly', 'superhero', 'darkly'
        self.style = ttk.Style(theme="yeti")

        self.title("APK 局域网分发服务器")
        self.geometry("600x650")
        self.resizable(False, False)

        self.local_ip = get_local_ip()
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        # --- 顶部信息栏 ---
        header_frame = ttk.Frame(self, padding=20)
        header_frame.pack(fill=X)

        title_lbl = ttk.Label(
            header_frame,
            text="APK 局域网分发",
            font=("微软雅黑", 20, "bold"),
            bootstyle="primary"
        )
        title_lbl.pack(side=LEFT)

        ip_info = f"服务地址: http://{self.local_ip}:{HTTP_PORT}"
        ip_lbl = ttk.Label(
            header_frame,
            text=ip_info,
            font=("Consolas", 10),
            bootstyle="secondary"
        )
        ip_lbl.pack(side=RIGHT, anchor=S)

        # --- 拖拽区域 ---
        self.drop_frame = ttk.Labelframe(self, text=" 上传区域 ", padding=20, bootstyle="info")
        self.drop_frame.pack(fill=X, padx=20, pady=10)

        self.drop_label = ttk.Label(
            self.drop_frame,
            text="📂\n\n拖拽 APK 文件到这里\n(支持批量)",
            font=("微软雅黑", 14),
            justify=CENTER,
            bootstyle="secondary",
            anchor=CENTER
        )
        self.drop_label.pack(fill=BOTH, expand=True, ipady=30)

        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind("<<Drop>>", self.on_drop)
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind("<<Drop>>", self.on_drop)

        # --- 分割线 ---
        ttk.Separator(self, orient=HORIZONTAL).pack(fill=X, padx=20, pady=10)

        # --- 文件列表区域 ---
        list_frame = ttk.Frame(self, padding=(20, 0, 20, 10))
        list_frame.pack(fill=BOTH, expand=True)

        ttk.Label(list_frame, text="已共享文件:", font=("微软雅黑", 10, "bold")).pack(anchor=W, pady=(0, 5))

        tree_container = ttk.Frame(list_frame)
        tree_container.pack(fill=BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical")
        scrollbar.pack(side=RIGHT, fill=Y)

        self.tree = ttk.Treeview(
            tree_container,
            columns=("filename", "size"),
            show="headings",
            selectmode="extended",
            yscrollcommand=scrollbar.set,
            height=10
        )

        scrollbar.config(command=self.tree.yview)

        self.tree.heading("filename", text="文件名", anchor=W)
        self.tree.heading("size", text="大小", anchor=W)
        self.tree.column("filename", width=350, anchor=W)
        self.tree.column("size", width=100, anchor=E)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        # --- 底部按钮 ---
        btn_frame = ttk.Frame(self, padding=20)
        btn_frame.pack(fill=X)

        open_btn = ttk.Button(
            btn_frame,
            text="📂 打开文件夹",
            bootstyle="outline-primary",
            command=lambda: open_file_explorer(APK_DIR)
        )
        open_btn.pack(side=LEFT)

        refresh_btn = ttk.Button(
            btn_frame,
            text="🔄 刷新",
            bootstyle="outline-info",
            command=self.refresh_list
        )
        refresh_btn.pack(side=LEFT, padx=10)

        del_btn = ttk.Button(
            btn_frame,
            text="🗑 删除选中",
            bootstyle="danger",
            command=self.delete_selected
        )
        del_btn.pack(side=RIGHT)

    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        count = 0
        for file_path in files:
            if file_path.lower().endswith(".apk"):
                try:
                    shutil.copy(file_path, APK_DIR)
                    count += 1
                except Exception as e:
                    print(f"Copy Error: {e}")

        if count > 0:
            self.refresh_list()
            original_text = self.drop_label.cget("text")
            self.drop_label.configure(text=f"✅ 成功添加 {count} 个文件", bootstyle="success")
            self.after(2000, lambda: self.drop_label.configure(text=original_text, bootstyle="secondary"))

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if os.path.exists(APK_DIR):
            for f in os.listdir(APK_DIR):
                if f.lower().endswith(".apk"):
                    try:
                        full_path = os.path.join(APK_DIR, f)
                        size_mb = os.path.getsize(full_path) / (1024 * 1024)
                        self.tree.insert("", "end", values=(f, f"{size_mb:.2f} MB"))
                    except OSError:
                        pass

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        if messagebox.askyesno("确认", "确定要删除选中的文件吗？"):
            for item in selected_items:
                filename = self.tree.item(item, "values")[0]
                try:
                    os.remove(os.path.join(APK_DIR, filename))
                except Exception as e:
                    print(f"Delete Error: {e}")
            self.refresh_list()

# ======================
# 主入口
# ======================
if __name__ == "__main__":
    t_http = threading.Thread(target=start_http_server, daemon=True)
    t_udp = threading.Thread(target=start_udp_server, daemon=True)

    t_http.start()
    t_udp.start()

    app = ModernApkServerUI()
    app.mainloop()
