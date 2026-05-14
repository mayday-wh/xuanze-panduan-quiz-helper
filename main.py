# /// script
# dependencies = ["pandas", "openpyxl"]
# ///

import pandas as pd
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox
import re
import os
import json
import sys

CONFIG_FILE = "study_progress.json"
APP_VERSION = "1.2"

def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_app_dir()
CONFIG_PATH = os.path.join(BASE_DIR, CONFIG_FILE)
QUIZ_DIR = os.path.join(BASE_DIR, "题库")
REQUIRED_COLUMNS = 3

FONT_FAMILY = "Microsoft YaHei UI"
FONT_SMALL = (FONT_FAMILY, 10)
FONT_NORMAL = (FONT_FAMILY, 11)
FONT_HEADER = (FONT_FAMILY, 12, "bold")
FONT_BODY = (FONT_FAMILY, 11)
FONT_BODY_BOLD = (FONT_FAMILY, 11, "bold")
FONT_BUTTON = (FONT_FAMILY, 11, "bold")

COLORS = {
    "app_bg": "#fbf6ee",
    "surface": "#fffaf2",
    "sidebar": "#f3e4d2",
    "sidebar_alt": "#fbf1e5",
    "sidebar_header": "#ead2b7",
    "top_header": "#f0ddc4",
    "border": "#d8c3a5",
    "text": "#3f3428",
    "muted": "#7a6752",
    "primary": "#a66a3f",
    "primary_hover": "#8c5530",
    "primary_soft": "#f1dec9",
    "file_item": "#fff4e7",
    "file_item_hover": "#f5dfc5",
    "file_item_selected": "#a66a3f",
    "success": "#5f7f4a",
    "success_soft": "#e5efd9",
    "warning": "#9a6a2f",
    "warning_soft": "#f7e9d5",
    "danger": "#a45a4f",
    "danger_soft": "#f4ded8",
    "disabled": "#cbbca8",
    "option_bg": "#fffaf3",
    "option_hover": "#f7eadb",
}

BUTTON_WIDTH = 10
BUTTON_HEIGHT = 1
HEADER_HEIGHT = 100
BASE_SCREEN_WIDTH = 3840
BASE_SCREEN_HEIGHT = 2160
BASE_WINDOW_WIDTH = 1800
BASE_WINDOW_HEIGHT = 900
BASE_MIN_WIDTH = 1536
BASE_MIN_HEIGHT = 832
BASE_TK_SCALING = 1.3333333333333333
UI_SCALE = 1.0

def sx(value):
    """Scale fixed pixel values from the original 4K layout."""
    return max(1, int(round(value * UI_SCALE)))

def configure_screen_scaling(root):
    """Scale fixed pixel layout while keeping Tk font scaling readable."""
    global BASE_TK_SCALING, UI_SCALE

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    try:
        BASE_TK_SCALING = float(root.tk.call("tk", "scaling"))
    except (tk.TclError, ValueError):
        pass

    UI_SCALE = max(
        0.6,
        min(1.0, screen_w / BASE_SCREEN_WIDTH, screen_h / BASE_SCREEN_HEIGHT),
    )
    root.tk.call("tk", "scaling", BASE_TK_SCALING)

    win_w = min(sx(BASE_WINDOW_WIDTH), int(screen_w * 0.92))
    win_h = min(sx(BASE_WINDOW_HEIGHT), int(screen_h * 0.88))
    root.geometry(f"{win_w}x{win_h}+{(screen_w - win_w) // 2}+{(screen_h - win_h) // 2}")
    root.minsize(sx(BASE_MIN_WIDTH), sx(BASE_MIN_HEIGHT))

class RoundedButton(tk.Canvas):
    def __init__(
        self,
        parent,
        text="",
        command=None,
        font=FONT_BUTTON,
        width=BUTTON_WIDTH,
        height=BUTTON_HEIGHT,
        bg=COLORS["primary_soft"],
        fg=COLORS["primary"],
        activebackground=COLORS["primary_hover"],
        activeforeground=None,
        disabledforeground="#fffaf2",
        padx=None,
        pady=None,
        corner_radius=None,
        anchor="center",
        **kwargs,
    ):
        self._parent_bg = parent.cget("bg") if "bg" in parent.keys() else COLORS["app_bg"]
        super().__init__(
            parent,
            bg=self._parent_bg,
            highlightthickness=0,
            bd=0,
            relief="flat",
            cursor=kwargs.pop("cursor", "hand2"),
        )
        self._text = text
        self._command = command
        self._font = font
        self._width_units = width
        self._height_units = height
        self._bg = bg
        self._fg = fg
        self._active_bg = activebackground
        self._active_fg = activeforeground or fg
        self._disabled_fg = disabledforeground
        self._padx = sx(4) if padx is None else padx
        self._pady = sx(1) if pady is None else pady
        self._corner_radius = corner_radius
        self._anchor = anchor
        self._state = kwargs.pop("state", "normal")
        self._hover = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Configure>", lambda _event: self._draw())
        self._resize()
        self._draw()

    def _measure(self):
        font_obj = tkfont.Font(font=self._font)
        text_width = font_obj.measure(self._text)
        unit_width = max(1, font_obj.measure("0"))
        line_height = font_obj.metrics("linespace")
        width_px = max(sx(34), text_width + self._padx * 2 + sx(18), unit_width * self._width_units + self._padx * 2)
        height_px = max(sx(28), line_height * self._height_units + self._pady * 2 + sx(10))
        return int(width_px), int(height_px)

    def _resize(self):
        width_px, height_px = self._measure()
        super().config(width=width_px, height=height_px)

    def _rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        radius = min(radius, int((x2 - x1) / 2), int((y2 - y1) / 2))
        self.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kwargs)
        self.create_rectangle(x1, y1 + radius, x2, y2 - radius, **kwargs)
        self.create_arc(x1, y1, x1 + radius * 2, y1 + radius * 2, start=90, extent=90, style="pieslice", **kwargs)
        self.create_arc(x2 - radius * 2, y1, x2, y1 + radius * 2, start=0, extent=90, style="pieslice", **kwargs)
        self.create_arc(x2 - radius * 2, y2 - radius * 2, x2, y2, start=270, extent=90, style="pieslice", **kwargs)
        self.create_arc(x1, y2 - radius * 2, x1 + radius * 2, y2, start=180, extent=90, style="pieslice", **kwargs)

    def _draw(self):
        self.delete("all")
        width_px = max(1, self.winfo_width())
        height_px = max(1, self.winfo_height())
        is_disabled = self._state == "disabled"
        fill = self._active_bg if self._hover and not is_disabled else self._bg
        fg = self._disabled_fg if is_disabled else (self._active_fg if self._hover else self._fg)
        radius = self._corner_radius or max(sx(4), min(sx(10), height_px // 3, int(width_px * 0.04)))
        self._rounded_rect(0, 0, width_px, height_px, radius, fill=fill, outline=fill)
        if self._anchor == "w":
            text_x = self._padx + sx(8)
            text_anchor = "w"
        else:
            text_x = width_px / 2
            text_anchor = "center"
        self.create_text(text_x, height_px / 2, text=self._text, font=self._font, fill=fg, anchor=text_anchor)

    def _on_enter(self, _event):
        if self._state != "disabled":
            self._hover = True
            self._draw()

    def _on_leave(self, _event):
        self._hover = False
        self._draw()

    def _on_click(self, _event):
        if self._state != "disabled" and self._command:
            self._command()

    def configure(self, cnf=None, **kwargs):
        options = {}
        if cnf:
            options.update(cnf)
        options.update(kwargs)
        passthrough = {}
        for key, value in options.items():
            if key == "text":
                self._text = value
            elif key == "command":
                self._command = value
            elif key == "font":
                self._font = value
            elif key == "width":
                self._width_units = value
            elif key == "height":
                self._height_units = value
            elif key == "bg":
                self._bg = value
            elif key == "fg":
                self._fg = value
            elif key == "activebackground":
                self._active_bg = value
            elif key == "activeforeground":
                self._active_fg = value
            elif key == "disabledforeground":
                self._disabled_fg = value
            elif key == "state":
                self._state = value
                passthrough["cursor"] = "arrow" if value == "disabled" else "hand2"
            elif key == "padx":
                self._padx = value
            elif key == "pady":
                self._pady = value
            elif key == "corner_radius":
                self._corner_radius = value
            elif key == "anchor":
                self._anchor = value
            elif key in {"relief", "borderwidth"}:
                continue
            else:
                passthrough[key] = value
        if passthrough:
            super().config(**passthrough)
        self._resize()
        self._draw()

    config = configure

    def cget(self, key):
        if key == "text":
            return self._text
        if key == "state":
            return self._state
        return super().cget(key)

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"选择判断刷题助手 v{APP_VERSION}")
        configure_screen_scaling(self.root)
        self.root.configure(bg=COLORS["app_bg"])
        
        self.progress_data = self.load_config()
        self.current_df = None
        self.current_index = 0
        self.current_file = ""
        self.selected_indices = []
        self.ans = ""
        self.auto_submit_var = tk.BooleanVar(value=False)
        
        self.ensure_quiz_dir()
        self.setup_ui()
        self.refresh_file_list()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError) as exc:
                self.show_error("读取进度失败", f"无法读取进度文件：\n{CONFIG_PATH}\n\n{exc}")
        return {}

    def save_config(self):
        if self.current_file:
            self.progress_data[self.current_file] = self.current_index
            try:
                with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                    json.dump(self.progress_data, f, ensure_ascii=False, indent=2)
            except OSError as exc:
                self.show_error("保存进度失败", f"无法保存进度文件：\n{CONFIG_PATH}\n\n{exc}")

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def ensure_quiz_dir(self):
        try:
            os.makedirs(QUIZ_DIR, exist_ok=True)
            return True
        except OSError as exc:
            self.show_error("创建题库目录失败", f"无法创建题库目录：\n{QUIZ_DIR}\n\n{exc}")
            return False

    def get_file_path(self, filename):
        return os.path.join(QUIZ_DIR, filename)

    def is_blank(self, value):
        return pd.isna(value) or str(value).strip() == ""

    def normalize_answer(self, value):
        answer = str(value).strip().upper()
        answer = answer.replace("，", ",").replace("；", ",").replace(";", ",")
        if answer == "TRUE":
            return "对"
        if answer == "FALSE":
            return "错"
        return answer

    def clean_choice_answer(self, answer):
        return answer.replace(",", "").replace(" ", "")

    def normalize_row_for_compare(self, df):
        return df.fillna("").astype(str).apply(lambda col: col.str.strip())

    def validate_quiz_data(self, df, filename):
        if df.empty:
            raise ValueError("题库为空。")
        if df.shape[1] < REQUIRED_COLUMNS:
            raise ValueError("题库至少需要 3 列：题干、选项、答案。")

        df = df.dropna(how="all").reset_index(drop=True)
        if df.empty:
            raise ValueError("题库没有有效题目。")

        invalid_rows = []
        for index, row in df.iterrows():
            answer = self.normalize_answer(row[2])
            if self.is_blank(row[0]) or self.is_blank(row[2]):
                invalid_rows.append(index + 1)
                continue
            if answer not in ["对", "错"] and self.is_blank(row[1]):
                invalid_rows.append(index + 1)

        if invalid_rows:
            preview = ", ".join(str(i) for i in invalid_rows[:10])
            suffix = "..." if len(invalid_rows) > 10 else ""
            raise ValueError(f"第 {preview}{suffix} 行格式不完整，请检查题干、选项和答案。")
        return df

    def make_button(self, parent, text, command=None, variant="secondary", width=BUTTON_WIDTH):
        styles = {
            "primary": (COLORS["primary"], "#ffffff", COLORS["primary_hover"]),
            "secondary": (COLORS["primary_soft"], COLORS["primary"], "#e6c8a8"),
            "success": (COLORS["primary"], "#ffffff", COLORS["primary_hover"]),
            "warning": (COLORS["warning_soft"], COLORS["warning"], "#ead4b6"),
            "danger": (COLORS["danger_soft"], COLORS["danger"], "#e7c8bf"),
            "disabled": (COLORS["disabled"], "#ffffff", COLORS["disabled"]),
        }
        bg, fg, active_bg = styles[variant]
        return RoundedButton(
            parent,
            text=text,
            font=FONT_BUTTON,
            width=width,
            height=BUTTON_HEIGHT,
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=fg,
            disabledforeground="#fffaf2",
            command=command,
            cursor="hand2",
            relief="flat",
            borderwidth=0,
            padx=sx(4),
            pady=sx(1),
        )

    def set_option_style(self, idx, selected=False, hover=False):
        bg = COLORS["option_bg"]
        border = COLORS["border"]
        if selected:
            bg = COLORS["primary_soft"]
            border = COLORS["primary"]
        elif hover:
            bg = COLORS["option_hover"]
        self.opt_widgets[idx].config(bg=bg, fg=COLORS["text"], highlightbackground=border)

    def mark_answer_options(self, user_ans_str, correct_ans_str):
        if self.is_multi:
            return
        answer_to_index = {"对": 0, "错": 1} if self.is_pd else {
            chr(65 + i): i for i in range(len(self.opt_widgets))
        }
        wrong_idx = self.selected_indices[0] if self.selected_indices else None
        correct_idx = answer_to_index.get(correct_ans_str)

        if wrong_idx is not None and wrong_idx < len(self.opt_widgets):
            self.opt_widgets[wrong_idx].config(bg=COLORS["danger_soft"], highlightbackground=COLORS["danger"])
        if correct_idx is not None and correct_idx < len(self.opt_widgets):
            self.opt_widgets[correct_idx].config(bg=COLORS["success_soft"], highlightbackground=COLORS["success"])

    def on_file_list_mousewheel(self, event):
        self.file_list_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def on_file_list_configure(self, _event=None):
        self.file_list_canvas.configure(scrollregion=self.file_list_canvas.bbox("all"))

    def on_file_canvas_configure(self, event):
        self.file_list_canvas.itemconfigure(self.file_list_window, width=event.width)

    def select_file_button(self, selected_button):
        for button in self.file_buttons:
            is_selected = button is selected_button
            button.config(
                bg=COLORS["file_item_selected"] if is_selected else COLORS["file_item"],
                fg="#ffffff" if is_selected else COLORS["text"],
                activebackground=COLORS["primary_hover"] if is_selected else COLORS["file_item_hover"],
                activeforeground="#ffffff" if is_selected else COLORS["text"],
            )

    def on_option_enter(self, idx):
        if idx not in self.selected_indices:
            self.set_option_style(idx, hover=True)

    def on_option_leave(self, idx):
        self.set_option_style(idx, selected=idx in self.selected_indices)

    def setup_ui(self):
        # 左侧题库列表
        self.left_frame = tk.Frame(self.root, width=sx(352), bg=COLORS["sidebar"])
        self.left_frame.pack(side="left", fill="y")
        self.left_frame.pack_propagate(False) 

        self.left_header = tk.Frame(self.left_frame, height=sx(HEADER_HEIGHT), bg=COLORS["sidebar_header"])
        self.left_header.pack(fill="x")
        self.left_header.pack_propagate(False)

        tk.Label(
            self.left_header,
            text="题库列表",
            font=FONT_HEADER,
            bg=COLORS["sidebar_header"],
            fg=COLORS["text"],
            anchor="w",
        ).pack(side="left", fill="x", expand=True, padx=(sx(13), sx(10)), pady=0)

        self.btn_refresh = self.make_button(
            self.left_header,
            "↻",
            self.refresh_file_list,
            "secondary",
            width=3,
        )
        self.btn_refresh.pack(side="right", padx=(0, sx(16)), pady=0)
        
        self.file_list_frame = tk.Frame(self.left_frame, bg=COLORS["sidebar"])
        self.file_list_frame.pack(fill="both", expand=True, padx=sx(13), pady=(0, sx(13)))

        self.file_list_canvas = tk.Canvas(
            self.file_list_frame,
            bg=COLORS["sidebar"],
            highlightthickness=0,
            bd=0,
        )
        self.file_scrollbar = tk.Scrollbar(
            self.file_list_frame,
            orient="vertical",
            command=self.file_list_canvas.yview,
            bg=COLORS["sidebar_header"],
            activebackground=COLORS["sidebar_header"],
            troughcolor=COLORS["sidebar"],
            relief="flat",
            borderwidth=0,
        )
        self.file_listbox = tk.Frame(self.file_list_canvas, bg=COLORS["sidebar"])
        self.file_list_window = self.file_list_canvas.create_window((0, 0), window=self.file_listbox, anchor="nw")
        self.file_list_canvas.configure(yscrollcommand=self.file_scrollbar.set)
        self.file_list_canvas.pack(side="left", fill="both", expand=True)
        self.file_scrollbar.pack(side="right", fill="y")
        self.file_buttons = []
        self.file_listbox.bind("<Configure>", self.on_file_list_configure)
        self.file_list_canvas.bind("<Configure>", self.on_file_canvas_configure)
        self.file_list_canvas.bind("<MouseWheel>", self.on_file_list_mousewheel)
        self.file_listbox.bind("<MouseWheel>", self.on_file_list_mousewheel)
        # 右侧主界面
        self.right_frame = tk.Frame(self.root, bg=COLORS["app_bg"])
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.top_bar = tk.Frame(self.right_frame, height=sx(HEADER_HEIGHT), bg=COLORS["top_header"])
        self.top_bar.pack(fill="x", pady=(0, sx(10)))
        self.top_bar.pack_propagate(False)
        
        self.info_label = tk.Label(
            self.top_bar,
            text="点击左侧选择题库",
            font=FONT_NORMAL,
            bg=COLORS["top_header"],
            fg=COLORS["muted"],
        )
        self.info_label.pack(side="left", padx=sx(48), pady=0)

        # 跳转模块
        self.jump_frame = tk.Frame(self.top_bar, bg=COLORS["top_header"])
        self.jump_frame.pack(side="right", padx=(0, sx(48)), pady=0)
        tk.Label(
            self.jump_frame,
            text="跳转",
            font=FONT_SMALL,
            bg=COLORS["top_header"],
            fg=COLORS["muted"],
        ).pack(side="left")
        
        self.jump_entry = tk.Entry(
            self.jump_frame,
            width=7,
            font=FONT_NORMAL,
            bg=COLORS["sidebar_alt"],
            fg=COLORS["text"],
            relief="solid",
            borderwidth=1,
            justify="center",
        )
        self.jump_entry.pack(side="left", padx=(sx(8), 0), ipady=sx(1))
        self.jump_entry.bind("<Return>", self.jump_to_question)

        # 动态错题集管理按钮
        self.btn_action = self.make_button(self.top_bar, "加入错题集", variant="warning", width=10)
        self.btn_action.config(font=FONT_NORMAL, height=1, padx=sx(2), pady=0)
        self.btn_action.pack(side="right", padx=sx(18), pady=0)

        self.auto_submit_frame = tk.Frame(self.top_bar, bg=COLORS["top_header"])
        self.auto_submit_frame.pack(side="right", padx=(0, sx(10)), pady=0)

        tk.Label(
            self.auto_submit_frame,
            text="自动提交",
            font=FONT_SMALL,
            bg=COLORS["top_header"],
            fg=COLORS["text"],
        ).pack(side="left")

        self.auto_submit_check = tk.Checkbutton(
            self.auto_submit_frame,
            text="",
            variable=self.auto_submit_var,
            font=FONT_SMALL,
            bg=COLORS["top_header"],
            fg=COLORS["text"],
            activebackground=COLORS["top_header"],
            activeforeground=COLORS["text"],
            selectcolor=COLORS["surface"],
            cursor="hand2",
            relief="flat",
            borderwidth=0,
        )
        self.auto_submit_check.pack(side="left", padx=(sx(4), 0), pady=0)

        # 题干显示
        self.question_frame = tk.Frame(self.right_frame, bg=COLORS["app_bg"])
        self.question_frame.pack(fill="x", padx=sx(48), pady=(0, sx(6)))

        self.label_q = tk.Label(
            self.question_frame,
            text="",
            wraplength=sx(1280),
            font=FONT_BODY,
            bg=COLORS["app_bg"],
            fg=COLORS["text"],
            justify="left",
            anchor="nw",
            padx=0,
            pady=sx(5),
        )
        self.label_q.pack(fill="x")
        
        # 选项容器
        self.opt_frame = tk.Frame(self.right_frame, bg=COLORS["app_bg"])
        self.opt_frame.pack(fill="both", expand=True, padx=sx(48))
        
        self.opt_widgets = []
        for i in range(8):
            l = tk.Label(
                self.opt_frame,
                text="",
                font=FONT_BODY,
                bg=COLORS["option_bg"],
                fg=COLORS["text"],
                relief="flat",
                padx=sx(14),
                pady=sx(8),
                wraplength=sx(1260),
                justify="left",
                anchor="w",
                cursor="hand2",
                highlightthickness=1,
                highlightbackground=COLORS["border"],
            )
            l.bind("<Button-1>", lambda e, idx=i: self.on_click_option(idx))
            l.bind("<Enter>", lambda e, idx=i: self.on_option_enter(idx))
            l.bind("<Leave>", lambda e, idx=i: self.on_option_leave(idx))
            self.opt_widgets.append(l)
        
        # 反馈文本
        self.label_res = tk.Label(
            self.right_frame,
            text="",
            font=FONT_BODY_BOLD,
            bg=COLORS["app_bg"],
            fg=COLORS["muted"],
        )
        self.label_res.pack(pady=(sx(2), sx(4)))

        # 底部控制栏
        self.bottom_frame = tk.Frame(
            self.right_frame,
            bg=COLORS["app_bg"],
            highlightthickness=0,
        )
        self.bottom_frame.pack(side="bottom", fill="x", pady=(0, sx(13)))
        
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(1, weight=1)
        self.bottom_frame.grid_columnconfigure(2, weight=1)

        self.btn_prev = self.make_button(self.bottom_frame, "◀ 上一题", self.prev_question, "secondary")
        self.btn_prev.grid(row=0, column=0, padx=sx(58), pady=sx(5))
        
        self.btn_submit = self.make_button(self.bottom_frame, "确认提交", self.submit_answer, "disabled")
        self.btn_submit.config(state="disabled")
        self.btn_submit.grid(row=0, column=1, padx=sx(58), pady=sx(5))
        
        self.btn_next = self.make_button(self.bottom_frame, "下一题 ▶", self.next_question, "secondary")
        self.btn_next.grid(row=0, column=2, padx=sx(58), pady=sx(5))

    def refresh_file_list(self):
        for widget in self.file_listbox.winfo_children():
            widget.destroy()
        self.file_buttons = []

        if not self.ensure_quiz_dir():
            return
            
        try:
            files = sorted([f for f in os.listdir(QUIZ_DIR) if f.endswith('.xlsx')])
        except OSError as exc:
            self.show_error("读取题库目录失败", f"无法读取题库目录：\n{QUIZ_DIR}\n\n{exc}")
            return
        
        for f in files:
            display_name = os.path.splitext(f)[0]
            button = RoundedButton(
                self.file_listbox,
                text=display_name,
                command=lambda name=display_name: self.load_file(name),
                font=FONT_NORMAL,
                width=22,
                height=1,
                bg=COLORS["file_item"],
                fg=COLORS["text"],
                activebackground=COLORS["file_item_hover"],
                activeforeground=COLORS["text"],
                padx=sx(10),
                pady=sx(4),
                anchor="w",
            )
            button.pack(fill="x", pady=(0, sx(6)))
            button.bind("<MouseWheel>", self.on_file_list_mousewheel)
            self.file_buttons.append(button)
            if self.current_file == f:
                self.select_file_button(button)
        self.on_file_list_configure()

    def load_selected_file(self, event):
        return

    def load_file(self, filename):
        for button in self.file_buttons:
            if button.cget("text") == filename:
                self.select_file_button(button)
                break
        self.current_file = filename + ".xlsx"
        
        try:
            df = pd.read_excel(self.get_file_path(self.current_file), header=None)
            self.current_df = self.validate_quiz_data(df, self.current_file)
            self.current_index = self.progress_data.get(self.current_file, 0)
            if self.current_index >= len(self.current_df): self.current_index = 0
            self.show_question()
        except Exception as exc:
            self.current_df = None
            self.show_error("加载题库失败", f"无法加载题库：{self.current_file}\n\n{exc}")

    def jump_to_question(self, event):
        try:
            val = int(self.jump_entry.get())
            if self.current_df is not None and 1 <= val <= len(self.current_df):
                self.current_index = val - 1
                self.show_question()
            else:
                self.label_res.config(text="请输入有效题号", fg=COLORS["warning"])
            self.jump_entry.delete(0, tk.END)
        except ValueError:
            self.label_res.config(text="题号必须是数字", fg=COLORS["warning"])
            self.jump_entry.delete(0, tk.END)

    def show_question(self):
        if self.current_df is None or len(self.current_df) == 0: return
        self.save_config()
        self.selected_indices = []
        self.label_res.config(text="")
        self.btn_submit.config(
            state="disabled",
            bg=COLORS["disabled"],
            fg="#ffffff",
            activebackground=COLORS["disabled"],
        )
        for i in range(len(self.opt_widgets)):
            self.set_option_style(i)
        
        row = self.current_df.iloc[self.current_index]
        q_text = str(row[0]).strip()
        opts_raw = "" if self.is_blank(row[1]) else str(row[1])
        raw_answer = str(row[2]).strip()
        self.ans = self.normalize_answer(raw_answer)
        
        self.is_multi = "多选题" in q_text or "," in self.ans
        self.is_pd = self.ans in ["对", "错"]
        
        q_type = "【单选题】"
        if self.is_multi: q_type = "【多选题】"
        elif self.is_pd: q_type = "【判断题】"
        
        self.info_label.config(text=f"进度：{self.current_index+1}/{len(self.current_df)}  {q_type}")
        self.label_q.config(text=q_text)

        is_wrong_mode = "错题集" in self.current_file
        if is_wrong_mode:
            self.btn_action.config(
                text="移出错题集",
                bg=COLORS["warning_soft"],
                fg=COLORS["warning"],
                activebackground="#ead4b6",
                activeforeground=COLORS["warning"],
                command=self.remove_from_wrong,
            )
        else:
            self.btn_action.config(
                text="加入错题集",
                bg=COLORS["warning_soft"],
                fg=COLORS["warning"],
                activebackground="#ead4b6",
                activeforeground=COLORS["warning"],
                command=self.add_to_wrong_manually,
            )
        
        self.btn_action.config(font=FONT_NORMAL, width=10, height=1, padx=sx(2), pady=0)
        self.btn_action.pack(side="right", padx=sx(18), pady=0)
        
        if self.is_pd:
            options = ["对", "错"]  
        else:
            options = re.split(r'\s*[A-H][、\.]\s*', opts_raw)
            options = [p.strip() for p in options if p.strip()]
            if not options: options = opts_raw.split()

        for i, widget in enumerate(self.opt_widgets):
            if i < len(options):
                if self.is_pd:
                    text_display = options[i] 
                else:
                    text_display = f"{chr(65+i)}. {options[i]}" 
                widget.config(text=text_display, state="normal")
                widget.pack(pady=sx(4), fill="x")
            else: 
                widget.pack_forget()

    def on_click_option(self, idx):
        if self.is_multi:
            if idx in self.selected_indices:
                self.selected_indices.remove(idx)
                self.set_option_style(idx)
            else:
                self.selected_indices.append(idx)
                self.set_option_style(idx, selected=True)
        else:
            for i in self.selected_indices:
                self.set_option_style(i)
            self.selected_indices = [idx]
            self.set_option_style(idx, selected=True)
        
        if self.selected_indices:
            self.btn_submit.config(
                state="normal",
                bg=COLORS["primary"],
                fg="#ffffff",
                activebackground=COLORS["primary_hover"],
            )
        else:
            self.btn_submit.config(
                state="disabled",
                bg=COLORS["disabled"],
                fg="#ffffff",
                activebackground=COLORS["disabled"],
            )

        if self.auto_submit_var.get() and self.selected_indices and not self.is_multi:
            self.submit_answer()

    def submit_answer(self):
        if not self.selected_indices: return
        
        if self.is_pd:
            user_ans_str = "对" if self.selected_indices[0] == 0 else "错"
        else:
            user_ans_str = "".join(sorted([chr(65+i) for i in self.selected_indices]))

        clean_correct = self.clean_choice_answer(self.ans)
        
        if user_ans_str == clean_correct:
            self.label_res.config(text="✔ 正确", fg=COLORS["success"])
            self.root.after(800, self.next_question)
        else:
            self.label_res.config(text=f"✘ 错误。正确答案是: {self.ans}", fg=COLORS["danger"])
            self.mark_answer_options(user_ans_str, clean_correct)
            self.save_wrong()

    # --- 新增功能：自动清理提示文字（仅清理操作提示，不清理对错判断） ---
    def clear_action_msg(self):
        current_text = self.label_res.cget("text")
        if "手动加入" in current_text or "从错题集中移除" in current_text:
            self.label_res.config(text="")

    def add_to_wrong_manually(self):
        self.save_wrong()
        self.label_res.config(text="⭐ 本题已手动加入错题集！", fg=COLORS["warning"])
        self.root.after(1000, self.clear_action_msg) # 1秒后自动消失

    def remove_from_wrong(self):
        if self.current_df is None or len(self.current_df) == 0: return
        
        self.current_df = self.current_df.drop(self.current_index).reset_index(drop=True)
        
        # 即使空了，也覆写一次Excel文件（保留文件物理存在）
        try:
            self.current_df.to_excel(self.get_file_path(self.current_file), index=False, header=False)
        except Exception as exc:
            self.show_error("保存错题集失败", f"无法更新文件：{self.current_file}\n\n{exc}")
            return
        
        if len(self.current_df) == 0:
            self.current_df = None
            self.label_q.config(text="🎉 太棒了！该错题集的所有题目均已掌握！")
            self.info_label.config(text="进度：0/0")
            self.label_res.config(text="")
            for w in self.opt_widgets: w.pack_forget()
            self.btn_submit.config(state="disabled", bg=COLORS["disabled"])
            self.btn_action.pack_forget() 
        else:
            if self.current_index >= len(self.current_df):
                self.current_index = len(self.current_df) - 1
            self.show_question()
            self.label_res.config(text="本题已从错题集中移除", fg=COLORS["success"])
            self.root.after(1000, self.clear_action_msg) # 1秒后自动消失

    def save_wrong(self):
        base_name = os.path.splitext(self.current_file)[0]
        if "错题集" in base_name: return
        wrong_file = f"{base_name}_错题集.xlsx"
        row_data = self.current_df.iloc[[self.current_index]]
        wrong_path = self.get_file_path(wrong_file)
        if os.path.exists(wrong_path):
            try:
                existing = pd.read_excel(wrong_path, header=None)
                existing_cmp = self.normalize_row_for_compare(existing)
                row_cmp = self.normalize_row_for_compare(row_data)
                duplicate_mask = existing_cmp.eq(row_cmp.iloc[0], axis="columns").all(axis=1)
                if not duplicate_mask.any():
                    pd.concat([existing, row_data]).to_excel(wrong_path, index=False, header=False)
            except Exception as exc:
                self.show_error("保存错题失败", f"无法写入错题集：{wrong_file}\n\n{exc}")
        else:
            try:
                row_data.to_excel(wrong_path, index=False, header=False)
            except Exception as exc:
                self.show_error("保存错题失败", f"无法创建错题集：{wrong_file}\n\n{exc}")

    def next_question(self):
        if self.current_df is not None and self.current_index < len(self.current_df) - 1:
            self.current_index += 1; self.show_question()

    def prev_question(self):
        if self.current_index > 0:
            self.current_index -= 1; self.show_question()

def enable_high_dpi_awareness():
    if os.name != "nt":
        return
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

if __name__ == "__main__":
    enable_high_dpi_awareness()
    root = tk.Tk()
    QuizApp(root)
    root.mainloop()
