import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pyttsx3
import threading

class TextReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文本朗读器")
        self.root.geometry("700x800")
        
        # 文件路径
        self.file_path_var = tk.StringVar()
        tk.Label(root, text="选择的文件:").pack(anchor="w", padx=10, pady=5)
        tk.Entry(root, textvariable=self.file_path_var, width=90).pack(padx=10, pady=5)

        tk.Button(root, text="选择文件", command=self.choose_file).pack(pady=5)

        # 文本框
        tk.Label(root, text="文件内容预览:").pack(anchor="w", padx=10)
        self.text_box = tk.Text(root, height=30, width=90, wrap="word")
        self.text_box.pack(padx=10, pady=5)

        # 语言
        tk.Label(root, text="选择朗读语言:").pack(anchor="w", padx=10)
        self.language_var = tk.StringVar(value="中文")
        ttk.Combobox(root, textvariable=self.language_var, values=("中文", "英文", "日文"), state="readonly").pack(pady=5)

        # 速度
        tk.Label(root, text="朗读速度:").pack(anchor="w", padx=10)
        self.speed_var = tk.IntVar(value=150)
        tk.Scale(root, from_=80, to=200, orient="horizontal", variable=self.speed_var).pack(pady=5)

        # 按钮
        frame = tk.Frame(root)
        frame.pack(pady=5)

        tk.Button(frame, text="开始朗读", command=self.start_reading).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="停止朗读", command=self.stop_reading).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="重新朗读", command=self.restart_reading).grid(row=0, column=2, padx=5)

        # 进度条
        tk.Label(root, text="朗读进度:").pack(anchor="w", padx=10)
        self.progress = ttk.Progressbar(root, length=650)
        self.progress.pack(pady=5)

        # 状态
        self.text = ""
        self.is_reading = False
        self.stop_flag = False
        self.engine = None   # ⚠️ 不提前创建

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            self.file_path_var.set(path)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.text = f.read()
            except:
                with open(path, 'r', encoding='gbk') as f:
                    self.text = f.read()

            self.text_box.delete("1.0", tk.END)
            self.text_box.insert(tk.END, self.text)

    def get_voice(self, engine):
        lang = self.language_var.get()
        for v in engine.getProperty('voices'):
            vid = v.id.lower()
            if (lang == "中文" and "zh" in vid) or \
               (lang == "英文" and "en" in vid) or \
               (lang == "日文" and "ja" in vid):
                return v.id
        return None

    def start_reading(self):
        if not self.text:
            messagebox.showwarning("提示", "请先选择文件")
            return
        if self.is_reading:
            return

        self.stop_flag = False
        self.is_reading = True

        threading.Thread(target=self.read_text, daemon=True).start()

    def stop_reading(self):
        self.stop_flag = True
        if self.engine:
            self.engine.stop()

    def restart_reading(self):
        self.stop_reading()
        self.root.after(300, self.start_reading)

    def read_text(self):
        # ✅ 每次新建 engine（关键）
        self.engine = pyttsx3.init()

        # 设置语音
        voice_id = self.get_voice(self.engine)
        if voice_id:
            self.engine.setProperty("voice", voice_id)

        # 设置速度
        self.engine.setProperty("rate", self.speed_var.get())

        self.progress["value"] = 0

        self.engine.say(self.text)
        self.engine.runAndWait()

        self.is_reading = False

        if not self.stop_flag:
            self.progress["value"] = 100
            messagebox.showinfo("完成", "朗读完成")
        else:
            self.progress["value"] = 0

        # ✅ 清理 engine
        self.engine = None


if __name__ == "__main__":
    root = tk.Tk()
    app = TextReaderApp(root)
    root.mainloop()