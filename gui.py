# gui.py
# -*- coding: utf-8 -*-

import tkinter as tk
import threading
import webbrowser
import time
import sys
import os
from app import app

def start_flask():
    # Run flask locally on port 8501
    app.run(host='127.0.0.1', port=8501, debug=False)

def open_browser():
    webbrowser.open('http://127.0.0.1:8501')

if __name__ == '__main__':
    # Start Flask server on a background daemon thread
    t = threading.Thread(target=start_flask)
    t.daemon = True
    t.start()
    
    # Wait 1.2 seconds for Flask to initialize
    time.sleep(1.2)
    
    # Auto-open browser
    open_browser()
    
    # Build TKinter Control Dashboard
    root = tk.Tk()
    root.title("K-Beauty Global Lister Pro")
    root.geometry("420x220")
    root.configure(bg="#0a0a0c")
    root.resizable(False, False)
    
    # Title Label
    title_lbl = tk.Label(
        root, 
        text="🧴 K-Beauty Global Lister Pro", 
        fg="#38bdf8", 
        bg="#0a0a0c", 
        font=("Malgun Gothic", 16, "bold")
    )
    title_lbl.pack(pady=20)
    
    # Status Label
    status_lbl = tk.Label(
        root, 
        text="상태: 로컬 서버 정상 작동 중 (포트 8501)", 
        fg="#10b981", 
        bg="#0a0a0c", 
        font=("Malgun Gothic", 10)
    )
    status_lbl.pack(pady=5)
    
    # Info Label
    info_lbl = tk.Label(
        root, 
        text="이 창을 닫으면 프로그램(서버)이 완전히 종료됩니다.", 
        fg="#71717a", 
        bg="#0a0a0c", 
        font=("Malgun Gothic", 9)
    )
    info_lbl.pack(pady=5)
    
    # Action Button
    btn_open = tk.Button(
        root, 
        text="대시보드 브라우저 열기", 
        command=open_browser, 
        fg="#ffffff", 
        bg="#2563eb", 
        activebackground="#1d4ed8", 
        activeforeground="#ffffff", 
        font=("Malgun Gothic", 10, "bold"), 
        relief="flat", 
        bd=0, 
        width=25, 
        height=2,
        cursor="hand2"
    )
    btn_open.pack(pady=15)
    
    # Exit cleanly on window closing
    def on_closing():
        root.destroy()
        os._exit(0)
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
