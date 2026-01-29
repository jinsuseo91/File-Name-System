# 파일명 변환 툴 (Desktop EXE용)
# Python + ttkbootstrap + Google Sheets API
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from tkinter import filedialog, messagebox, END
from datetime import date
import os
import re
import webbrowser
import tkinter as tk
import sys

# Google Sheet
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -----------------------------
# PyInstaller 리소스 경로
# -----------------------------
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

# -----------------------------
# Google Sheet 설정
# -----------------------------
SPREADSHEET_ID = "1WInTcJt5LjhVRteW5XgL5PQv8aUErNsH5PTJ3eSxX-Y"
WORKSHEET_NAME = "시트1"
GOOGLE_JSON = resource_path("techcareapi.json")

# -----------------------------
# 유틸
# -----------------------------
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'[\\/:*?"<>|]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_date(d: date) -> str:
    return d.strftime("%Y%m%d")

# -----------------------------
# 메인 앱
# -----------------------------
class FileNameTool(tb.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("파일명 변환 툴")
        self.geometry("700x880")
        self.resizable(False, False)

        self.selected_file_path = None

        style = tb.Style()
        style.configure("Bold.TButton", font=("Segoe UI", 10, "bold"))

        self.create_widgets()

    # -----------------------------
    # UI
    # -----------------------------
    def create_widgets(self):
        container = tk.Frame(self, bg="white", padx=20, pady=20)
        container.pack(fill=BOTH, expand=True)

        # 헤더
        header = tk.Frame(container, bg="white")
        header.pack(fill=X, pady=(0, 15))
        tb.Label(header, text="파일명 변환 툴", font=("Segoe UI", 16, "bold")).pack(side=LEFT)
        tb.Button(header, text="초기화", bootstyle="info",
                  style="Bold.TButton", command=self.reset_fields).pack(side=RIGHT)

        card_bg = "#ffffff"
        border_color = "silver"

        # 파일 선택
        file_card = tk.Frame(container, bg=card_bg, highlightbackground=border_color,
                             highlightthickness=1, padx=12, pady=12)
        file_card.pack(fill=X, pady=6)

        tb.Label(file_card, text="파일 선택 (선택사항)",
                 font=("Segoe UI", 13, "bold"),
                 background=card_bg).pack(anchor=W)

        self.file_label = tb.Label(file_card, text="선택된 파일 없음",
                                   foreground="#6B7280", background=card_bg)
        self.file_label.pack(side=LEFT, pady=6)

        tb.Button(file_card, text="파일 선택",
                  bootstyle="info", style="Bold.TButton",
                  command=self.select_file).pack(side=RIGHT)

        # 입력 카드
        input_card = tk.Frame(container, bg=card_bg, highlightbackground=border_color,
                              highlightthickness=1, padx=12, pady=12)
        input_card.pack(fill=X, pady=6)

        def row(label, widget, r, c=1):
            tb.Label(input_card, text=label,
                     font=("Segoe UI", 10, "bold"),
                     background=card_bg).grid(row=r, column=0, sticky=W, pady=6, padx=6)
            widget.grid(row=r, column=c, sticky=W)

        entry_style = {"bootstyle": "secondary"}

        # 대분류
        self.main_category = tb.Combobox(
            input_card,
            values=["HW", "SW", "SYS", "ETC", "기타"],
            width=28, **entry_style)
        self.main_category.set("HW")
        row("대분류", self.main_category, 0)

        self.main_category_custom = tb.Entry(
            input_card, width=30, state="disabled", **entry_style)
        self.main_category_custom.grid(row=0, column=2, padx=6)

        # 중분류
        self.sub_category = tb.Combobox(
            input_card,
            values=["IPC", "NVR", "DVR", "A-CAM", "VMS", "Parking", "기타"],
            width=28, **entry_style)
        self.sub_category.set("IPC")
        row("중분류", self.sub_category, 1)

        self.sub_category_custom = tb.Entry(
            input_card, width=30, state="disabled", **entry_style)
        self.sub_category_custom.grid(row=1, column=2, padx=6)

        # 모델명
        self.model_name = tb.Entry(input_card, width=30, **entry_style)
        row("모델명 / 시스템명", self.model_name, 2)

        # 문서유형
        self.doc_type = tb.Combobox(
            input_card,
            values=["사용자매뉴얼", "사양서", "가이드", "릴리즈노트", "장애조치", "기타"],
            width=28, **entry_style)
        self.doc_type.set("사용자매뉴얼")
        row("문서유형", self.doc_type, 3)

        self.doc_type_custom = tb.Entry(
            input_card, width=30, state="disabled", **entry_style)
        self.doc_type_custom.grid(row=3, column=2, padx=6)

        # 문서명
        self.document_name = tb.Entry(input_card, width=30, **entry_style)
        row("문서명", self.document_name, 4)

        # 버전
        self.version = tb.Entry(input_card, width=30, **entry_style)
        self.version.insert(0, "v1.0")
        row("버전", self.version, 5)

        # 날짜
        self.date_entry = DateEntry(input_card, width=30, bootstyle="dark")
        self.date_entry.set_date(date.today())
        row("최종 수정일", self.date_entry, 6)

        # 작성자
        self.author = tb.Entry(input_card, width=30, **entry_style)
        row("작성자", self.author, 7)

        # 상태
        self.status = tb.Combobox(
            input_card,
            values=["배포중", "배포완료"],
            width=28, state="readonly", **entry_style)
        self.status.set("배포중")
        row("상태", self.status, 8)

        # 버튼
        action = tk.Frame(container, bg="white")
        action.pack(fill=X, pady=6)

        btn = {"bootstyle": "info", "style": "Bold.TButton"}
        tb.Button(action, text="파일명 생성", **btn, command=self.generate_filename).pack(side=LEFT, padx=4)
        tb.Button(action, text="파일명 적용", **btn, command=self.apply_filename).pack(side=LEFT, padx=4)
        tb.Button(action, text="복사", **btn, command=self.copy_filename).pack(side=LEFT, padx=4)
        tb.Button(action, text="관리대장 등록", **btn, command=self.register_to_sheet).pack(side=LEFT, padx=4)

        # 결과
        result = tk.Frame(container, bg=card_bg, highlightbackground=border_color,
                          highlightthickness=1, padx=12, pady=12)
        result.pack(fill=BOTH, expand=True, pady=6)

        tb.Label(result, text="생성된 파일명",
                 font=("Segoe UI", 10, "bold"),
                 background=card_bg).pack(anchor=W)

        self.result_text = tb.Text(result, height=1, bg="#f8f9fa", relief="flat")
        self.result_text.pack(fill=BOTH, expand=True, pady=6)

        # 링크
        link = tk.Frame(container, bg=card_bg, highlightbackground=border_color,
                        highlightthickness=1, padx=12, pady=12)
        link.pack(fill=X)

        tb.Button(link, text="NAS 경로 열기", width=20, **btn,
                  command=self.open_nas).pack(side=LEFT, padx=4)
        tb.Button(link, text="문서관리대장 열기", width=20, **btn,
                  command=self.open_sheet).pack(side=LEFT, padx=4)

        # 이벤트 바인딩
        self.main_category.bind("<<ComboboxSelected>>",
            lambda e: self.toggle_custom(self.main_category, self.main_category_custom))
        self.sub_category.bind("<<ComboboxSelected>>",
            lambda e: self.toggle_custom(self.sub_category, self.sub_category_custom))
        self.doc_type.bind("<<ComboboxSelected>>",
            lambda e: self.toggle_custom(self.doc_type, self.doc_type_custom))

    # -----------------------------
    # 로직
    # -----------------------------
    def toggle_custom(self, combo, entry):
        if combo.get() == "기타":
            entry.config(state="normal")
        else:
            entry.delete(0, END)
            entry.config(state="disabled")

    def select_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.selected_file_path = path
            self.file_label.config(text=os.path.basename(path))

    def generate_filename(self):
        main = self.main_category_custom.get() if self.main_category.get() == "기타" else self.main_category.get()
        sub = self.sub_category_custom.get() if self.sub_category.get() == "기타" else self.sub_category.get()
        doc = self.doc_type_custom.get() if self.doc_type.get() == "기타" else self.doc_type.get()

        parts = [
            clean_text(main),
            clean_text(sub),
            clean_text(self.model_name.get()),
            clean_text(doc),
            clean_text(self.document_name.get())
        ]
        parts = [p for p in parts if p]

        filename = "-".join(parts + [
            f"{clean_text(self.version.get())}_{format_date(self.date_entry.get_date())}"
        ])

        self.result_text.delete("1.0", END)
        self.result_text.insert(END, filename)

    def copy_filename(self):
        text = self.result_text.get("1.0", END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            messagebox.showinfo("복사 완료", "파일명이 복사되었습니다")

    def apply_filename(self):
        if not self.selected_file_path:
            messagebox.showwarning("경고", "파일을 선택하세요")
            return

        new_name = self.result_text.get("1.0", END).strip()
        if not new_name:
            messagebox.showwarning("경고", "파일명을 생성하세요")
            return

        directory = os.path.dirname(self.selected_file_path)
        ext = os.path.splitext(self.selected_file_path)[1]
        new_path = os.path.join(directory, new_name + ext)

        os.rename(self.selected_file_path, new_path)
        self.selected_file_path = new_path
        self.file_label.config(text=os.path.basename(new_path))
        messagebox.showinfo("완료", "파일명이 변경되었습니다")

    # -----------------------------
    # Google Sheet
    # -----------------------------
    def get_worksheet(self):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_JSON, scope)
        client = gspread.authorize(creds)
        return client.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET_NAME)

    def find_next_row(self, ws, start=5):
        col = ws.col_values(2)
        for i in range(start - 1, len(col)):
            if col[i] == "":
                return i + 1
        return len(col) + 1

    def register_to_sheet(self):
        ws = self.get_worksheet()
        row = self.find_next_row(ws)

        data = [
            self.main_category_custom.get() if self.main_category.get() == "기타" else self.main_category.get(),
            self.sub_category_custom.get() if self.sub_category.get() == "기타" else self.sub_category.get(),
            self.model_name.get(),
            self.doc_type_custom.get() if self.doc_type.get() == "기타" else self.doc_type.get(),
            self.document_name.get(),
            self.version.get(),
            self.date_entry.get_date().strftime("%Y-%m-%d"),
            self.result_text.get("1.0", END).strip(),
            self.author.get(),
            self.status.get()
        ]

        ws.update(f"B{row}:K{row}", [data])
        messagebox.showinfo("완료", "관리대장에 등록되었습니다")

    def open_nas(self):
        webbrowser.open("http://csn.idis.co.kr:5500/")

    def open_sheet(self):
        webbrowser.open(
            "https://docs.google.com/spreadsheets/d/1rzqQZc9pfW_gxlifbtZJRPO4YsHl1fGpAaeuL4I-PC8/edit"
        )

    def reset_fields(self):
        self.main_category.set("HW")
        self.sub_category.set("IPC")
        self.doc_type.set("사용자매뉴얼")

        for e in [self.main_category_custom, self.sub_category_custom, self.doc_type_custom]:
            e.delete(0, END)
            e.config(state="disabled")

        self.model_name.delete(0, END)
        self.document_name.delete(0, END)

        self.version.delete(0, END)
        self.version.insert(0, "v1.0")

        self.author.delete(0, END)
        self.status.set("배포중")
        self.date_entry.set_date(date.today())

        self.result_text.delete("1.0", END)
        self.selected_file_path = None
        self.file_label.config(text="선택된 파일 없음")


# -----------------------------
# 실행
# -----------------------------
if __name__ == "__main__":
    FileNameTool().mainloop()
