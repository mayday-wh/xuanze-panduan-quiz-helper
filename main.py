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
import random

CONFIG_FILE = "study_progress.json"
APP_VERSION = "2.0"

def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_app_dir()
CONFIG_PATH = os.path.join(BASE_DIR, CONFIG_FILE)
QUIZ_DIR = os.path.join(BASE_DIR, "题库")
REQUIRED_COLUMNS = 3
ANALYSIS_COLUMN = 3

FONT_FAMILY = "Microsoft YaHei UI"
FONT_SMALL = (FONT_FAMILY, 10)
FONT_NORMAL = (FONT_FAMILY, 11)
FONT_HEADER = (FONT_FAMILY, 12, "bold")
FONT_BODY = (FONT_FAMILY, 11)
FONT_BODY_BOLD = (FONT_FAMILY, 11, "bold")
FONT_BUTTON = (FONT_FAMILY, 11, "bold")

DEFAULT_COLORS = {
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

EYE_COLORS = {
    "app_bg": "#eef6e8",
    "surface": "#fbfff7",
    "sidebar": "#dcebd0",
    "sidebar_alt": "#f5fbef",
    "sidebar_header": "#d8e8c6",
    "top_header": "#dcebd0",
    "border": "#c5d4b6",
    "text": "#2f372d",
    "muted": "#68765c",
    "primary": "#617b4d",
    "primary_hover": "#4f673d",
    "primary_soft": "#dcebcf",
    "file_item": "#f8fff2",
    "file_item_hover": "#e8f3dd",
    "file_item_selected": "#617b4d",
    "success": "#4f7b45",
    "success_soft": "#dff0d7",
    "warning": "#7a683a",
    "warning_soft": "#edf2d5",
    "danger": "#9b554f",
    "danger_soft": "#f2ddd9",
    "disabled": "#b3c2a4",
    "option_bg": "#fbfff7",
    "option_hover": "#eef8e7",
}

NIGHT_COLORS = {
    "app_bg": "#15181b",
    "surface": "#22272b",
    "sidebar": "#1b1f23",
    "sidebar_alt": "#1c2025",
    "sidebar_header": "#20252a",
    "top_header": "#1f2328",
    "border": "#3a4148",
    "text": "#e3e0d8",
    "muted": "#b7b0a5",
    "primary": "#d4ae70",
    "primary_hover": "#c79f5e",
    "primary_soft": "#2a3035",
    "file_item": "#22272b",
    "file_item_hover": "#2a3035",
    "file_item_selected": "#d4ae70",
    "success": "#7fb071",
    "success_soft": "#26382c",
    "warning": "#d4ae70",
    "warning_soft": "#2f2a22",
    "danger": "#d17c72",
    "danger_soft": "#3b2828",
    "disabled": "#444b55",
    "option_bg": "#22272b",
    "option_hover": "#2a3035",
}

COLOR_THEMES = {
    "default": DEFAULT_COLORS,
    "eye": EYE_COLORS,
    "night": NIGHT_COLORS,
}
COLORS = DEFAULT_COLORS.copy()

def set_color_theme(theme_name):
    COLORS.clear()
    COLORS.update(COLOR_THEMES.get(theme_name, DEFAULT_COLORS))

def keep_cjk_inline_spacing(text):
    text = str(text)
    text = re.sub(r'(?<=[\u4e00-\u9fff]) (?=[A-Za-z0-9])', '\u00a0', text)
    text = re.sub(r'(?<=[A-Za-z0-9]) (?=[\u4e00-\u9fff])', '\u00a0', text)
    text = re.sub(r'（ +）', lambda match: '（\u2060' + ('\u00a0' * (len(match.group(0)) - 2)) + '\u2060）', text)
    text = re.sub(r'\( +\)', lambda match: '(\u2060' + ('\u00a0' * (len(match.group(0)) - 2)) + '\u2060)', text)
    return text

BUTTON_WIDTH = 10
BUTTON_HEIGHT = 1
HEADER_HEIGHT = 100
PAGE_PADX = 48
TOOLBAR_PADX = 28
GROUP_GAP = 14
SECTION_GAP = 10
CONTROL_RADIUS = 12
CARD_RADIUS = 14
BUTTON_PADY = 7
MODE_BUTTON_WIDTH = 7
QUESTION_WRAP = 1280
OPTION_WRAP = 1260
BASE_SCREEN_WIDTH = 3840
BASE_SCREEN_HEIGHT = 2160
BASE_WINDOW_WIDTH = 1500
BASE_WINDOW_HEIGHT = 960
BASE_MIN_WIDTH = 1180
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
        radius = self._corner_radius or max(sx(8), min(sx(16), height_px // 2 - 1, int(width_px * 0.06)))
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

class RoundedOption(tk.Canvas):
    def __init__(
        self,
        parent,
        text="",
        font=FONT_BODY,
        bg=COLORS["option_bg"],
        fg=COLORS["text"],
        padx=None,
        pady=None,
        wraplength=None,
        justify="left",
        anchor="w",
        highlightbackground=COLORS["border"],
        corner_radius=None,
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
        self._font = font
        self._bg = bg
        self._fg = fg
        self._padx = sx(14) if padx is None else padx
        self._pady = sx(8) if pady is None else pady
        self._wraplength = wraplength
        self._justify = justify
        self._anchor = anchor
        self._border = highlightbackground
        self._state = kwargs.pop("state", "normal")
        self._corner_radius = corner_radius or sx(CONTROL_RADIUS)
        self._drawing = False

        self.config(height=self._preferred_height())
        self.bind("<Configure>", lambda _event: self._draw())
        self._draw()

    def _rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        radius = min(radius, int((x2 - x1) / 2), int((y2 - y1) / 2))
        self.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kwargs)
        self.create_rectangle(x1, y1 + radius, x2, y2 - radius, **kwargs)
        self.create_arc(x1, y1, x1 + radius * 2, y1 + radius * 2, start=90, extent=90, style="pieslice", **kwargs)
        self.create_arc(x2 - radius * 2, y1, x2, y1 + radius * 2, start=0, extent=90, style="pieslice", **kwargs)
        self.create_arc(x2 - radius * 2, y2 - radius * 2, x2, y2, start=270, extent=90, style="pieslice", **kwargs)
        self.create_arc(x1, y2 - radius * 2, x1 + radius * 2, y2, start=180, extent=90, style="pieslice", **kwargs)

    def _preferred_height(self):
        font_obj = tkfont.Font(font=self._font)
        return max(sx(42), font_obj.metrics("linespace") + self._pady * 2 + sx(4))

    def _draw(self):
        if self._drawing:
            return
        self._drawing = True
        try:
            self.delete("all")
            width_px = max(1, self.winfo_width())
            height_px = max(self._preferred_height(), self.winfo_height())
            radius = min(self._corner_radius, height_px // 3)
            self._rounded_rect(1, 1, width_px - 2, height_px - 2, radius, fill=self._border, outline=self._border)
            self._rounded_rect(2, 2, width_px - 3, height_px - 3, max(1, radius - 1), fill=self._bg, outline=self._bg)

            text_width = max(1, width_px - self._padx * 2)
            text_id = self.create_text(
                self._padx,
                self._pady,
                text=keep_cjk_inline_spacing(self._text),
                font=self._font,
                fill=self._fg,
                anchor="nw",
                width=text_width,
                justify=self._justify,
            )
            bbox = self.bbox(text_id)
            if bbox:
                needed_height = max(self._preferred_height(), bbox[3] + self._pady)
                configured_height = int(float(super().cget("height")))
                if abs(needed_height - configured_height) > 1:
                    super().config(height=needed_height)
                    return
        finally:
            self._drawing = False

    def configure(self, cnf=None, **kwargs):
        options = {}
        if cnf:
            options.update(cnf)
        options.update(kwargs)
        passthrough = {}
        for key, value in options.items():
            if key == "text":
                self._text = value
            elif key == "font":
                self._font = value
            elif key == "bg":
                self._bg = value
            elif key == "fg":
                self._fg = value
            elif key == "padx":
                self._padx = value
            elif key == "pady":
                self._pady = value
            elif key == "wraplength":
                self._wraplength = value
            elif key == "justify":
                self._justify = value
            elif key == "anchor":
                self._anchor = value
            elif key == "highlightbackground":
                self._border = value
            elif key == "corner_radius":
                self._corner_radius = value
            elif key == "state":
                self._state = value
                passthrough["cursor"] = "arrow" if value == "disabled" else "hand2"
            elif key in {"relief", "highlightthickness", "borderwidth"}:
                continue
            else:
                passthrough[key] = value
        if passthrough:
            super().config(**passthrough)
        self._draw()

    config = configure

    def cget(self, key):
        if key == "text":
            return self._text
        if key == "state":
            return self._state
        return super().cget(key)

class RoundedEntry(tk.Canvas):
    def __init__(
        self,
        parent,
        width=7,
        font=FONT_NORMAL,
        bg=COLORS["sidebar_alt"],
        fg=COLORS["text"],
        border=COLORS["border"],
        justify="center",
        padx=None,
        pady=None,
        corner_radius=None,
        **kwargs,
    ):
        self._parent_bg = parent.cget("bg") if "bg" in parent.keys() else COLORS["app_bg"]
        self._font = font
        self._bg = bg
        self._border = border
        self._padx = sx(8) if padx is None else padx
        self._pady = sx(4) if pady is None else pady
        self._corner_radius = corner_radius or sx(CARD_RADIUS)

        font_obj = tkfont.Font(font=self._font)
        self._width_px = max(sx(58), font_obj.measure("0") * width + self._padx * 2)
        self._height_px = max(sx(34), font_obj.metrics("linespace") + self._pady * 2)

        super().__init__(
            parent,
            width=self._width_px,
            height=self._height_px,
            bg=self._parent_bg,
            highlightthickness=0,
            bd=0,
            relief="flat",
            cursor=kwargs.pop("cursor", "xterm"),
        )

        self.entry = tk.Entry(
            self,
            width=width,
            font=font,
            bg=bg,
            fg=fg,
            relief="flat",
            borderwidth=0,
            justify=justify,
            insertbackground=fg,
        )
        self._entry_window = self.create_window(
            self._width_px / 2,
            self._height_px / 2,
            width=self._width_px - self._padx * 2,
            height=self._height_px - self._pady,
            window=self.entry,
        )

        self.bind("<Configure>", lambda _event: self._draw())
        self.bind("<Button-1>", lambda _event: self.entry.focus_set())
        self._draw()

    def _rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        radius = min(radius, int((x2 - x1) / 2), int((y2 - y1) / 2))
        self.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kwargs)
        self.create_rectangle(x1, y1 + radius, x2, y2 - radius, **kwargs)
        self.create_arc(x1, y1, x1 + radius * 2, y1 + radius * 2, start=90, extent=90, style="pieslice", **kwargs)
        self.create_arc(x2 - radius * 2, y1, x2, y1 + radius * 2, start=0, extent=90, style="pieslice", **kwargs)
        self.create_arc(x2 - radius * 2, y2 - radius * 2, x2, y2, start=270, extent=90, style="pieslice", **kwargs)
        self.create_arc(x1, y2 - radius * 2, x1 + radius * 2, y2, start=180, extent=90, style="pieslice", **kwargs)

    def _draw(self):
        super().delete("shape")
        width_px = max(1, self.winfo_width())
        height_px = max(1, self.winfo_height())
        radius = min(self._corner_radius, height_px // 3)
        self._rounded_rect(1, 1, width_px - 2, height_px - 2, radius, fill=self._border, outline=self._border, tags="shape")
        self._rounded_rect(2, 2, width_px - 3, height_px - 3, max(1, radius - 1), fill=self._bg, outline=self._bg, tags="shape")
        self.coords(self._entry_window, width_px / 2, height_px / 2)
        self.itemconfig(self._entry_window, width=max(1, width_px - self._padx * 2), height=max(1, height_px - self._pady))
        self.tag_lower("shape")

    def get(self):
        return self.entry.get()

    def delete(self, first, last=None):
        self.entry.delete(first, last)

    def bind(self, sequence=None, func=None, add=None):
        self.entry.bind(sequence, func, add)
        return super().bind(sequence, func, add)

class RoundedDropdown(tk.Canvas):
    def __init__(
        self,
        parent,
        variable,
        values=None,
        command=None,
        font=FONT_NORMAL,
        width=24,
        bg=COLORS["surface"],
        fg=COLORS["text"],
        border=COLORS["border"],
        activebackground=COLORS["option_hover"],
        corner_radius=None,
        padx=None,
        pady=None,
        **kwargs,
    ):
        self._parent_bg = parent.cget("bg") if "bg" in parent.keys() else COLORS["app_bg"]
        self._variable = variable
        self._values = values or []
        self._command = command
        self._font = font
        self._bg = bg
        self._fg = fg
        self._border = border
        self._active_bg = activebackground
        self._corner_radius = corner_radius or sx(CONTROL_RADIUS)
        self._padx = sx(14) if padx is None else padx
        self._pady = sx(5) if pady is None else pady
        self._hover = False

        font_obj = tkfont.Font(font=self._font)
        text_width = font_obj.measure("0") * width
        height = max(sx(36), font_obj.metrics("linespace") + self._pady * 2 + sx(6))
        super().__init__(
            parent,
            width=max(sx(220), text_width + self._padx * 2 + sx(28)),
            height=height,
            bg=self._parent_bg,
            highlightthickness=0,
            bd=0,
            relief="flat",
            cursor=kwargs.pop("cursor", "hand2"),
        )
        self._trace_id = self._variable.trace_add("write", lambda *_args: self._draw())
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._show_menu)
        self.bind("<Configure>", lambda _event: self._draw())
        self._draw()

    def destroy(self):
        try:
            self._variable.trace_remove("write", self._trace_id)
        except tk.TclError:
            pass
        super().destroy()

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
        radius = min(self._corner_radius, height_px // 3)
        fill = self._active_bg if self._hover else self._bg
        self._rounded_rect(1, 1, width_px - 2, height_px - 2, radius, fill=self._border, outline=self._border)
        self._rounded_rect(2, 2, width_px - 3, height_px - 3, max(1, radius - 1), fill=fill, outline=fill)
        self.create_text(
            self._padx,
            height_px / 2,
            text=self._variable.get(),
            font=self._font,
            fill=self._fg,
            anchor="w",
        )
        self.create_text(
            width_px - self._padx,
            height_px / 2,
            text="▾",
            font=self._font,
            fill=self._fg,
            anchor="e",
        )

    def _on_enter(self, _event):
        self._hover = True
        self._draw()

    def _on_leave(self, _event):
        self._hover = False
        self._draw()

    def set_values(self, values):
        self._values = values

    def _select(self, value):
        self._variable.set(value)
        if self._command:
            self._command(value)

    def _show_menu(self, event):
        if not self._values:
            return
        menu = tk.Menu(
            self,
            tearoff=0,
            bg=self._bg,
            fg=self._fg,
            activebackground=COLORS["primary_soft"],
            activeforeground=COLORS["primary"],
            relief="flat",
            borderwidth=1,
        )
        for value in self._values:
            menu.add_command(label=value, command=lambda selected=value: self._select(selected))
        menu.tk_popup(event.x_root, event.y_root)

class RoundedToggle(tk.Canvas):
    def __init__(
        self,
        parent,
        text,
        variable,
        command=None,
        font=FONT_NORMAL,
        width=MODE_BUTTON_WIDTH,
        corner_radius=None,
        **kwargs,
    ):
        self._parent_bg = parent.cget("bg") if "bg" in parent.keys() else COLORS["app_bg"]
        self._text = text
        self._variable = variable
        self._command = command
        self._font = font
        self._corner_radius = corner_radius or sx(CONTROL_RADIUS)
        self._hover = False

        font_obj = tkfont.Font(font=self._font)
        text_width = max(font_obj.measure(self._text), font_obj.measure("0") * width)
        checked_width = font_obj.measure(f"✓ {self._text}")
        height = max(sx(36), font_obj.metrics("linespace") + sx(12))
        super().__init__(
            parent,
            width=max(text_width, checked_width) + sx(28),
            height=height,
            bg=self._parent_bg,
            highlightthickness=0,
            bd=0,
            relief="flat",
            cursor=kwargs.pop("cursor", "hand2"),
        )
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Configure>", lambda _event: self._draw())
        self._draw()

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
        selected = self._variable.get()
        border = COLORS["primary"] if selected else COLORS["border"]
        fill = COLORS["primary"] if selected else (COLORS["option_hover"] if self._hover else COLORS["surface"])
        fg = "#ffffff" if selected else COLORS["text"]
        radius = min(self._corner_radius, height_px // 3)
        self._rounded_rect(1, 1, width_px - 2, height_px - 2, radius, fill=border, outline=border)
        self._rounded_rect(2, 2, width_px - 3, height_px - 3, max(1, radius - 1), fill=fill, outline=fill)
        prefix = "✓ " if selected else ""
        self.create_text(width_px / 2, height_px / 2, text=f"{prefix}{self._text}", font=self._font, fill=fg)

    def _on_enter(self, _event):
        self._hover = True
        self._draw()

    def _on_leave(self, _event):
        self._hover = False
        self._draw()

    def _on_click(self, _event):
        self._variable.set(not self._variable.get())
        self._draw()
        if self._command:
            self._command()

    def refresh(self):
        self._draw()

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
        self.analysis_text = ""
        self.current_theme = "default"
        self.quiz_files = []
        self.quiz_names = []
        self.quiz_var = tk.StringVar(value="请选择题库")
        self.review_mode_var = tk.BooleanVar(value=False)
        self.auto_submit_var = tk.BooleanVar(value=False)
        self.random_mode_var = tk.BooleanVar(value=False)
        self.eye_mode_var = tk.BooleanVar(value=False)
        self.night_mode_var = tk.BooleanVar(value=False)
        
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

    def is_header_row(self, row):
        headers = [
            {"题目", "题干", "question"},
            {"选项", "options", "option"},
            {"答案", "正确答案", "answer"},
        ]
        values = [str(row[i]).strip().lower() for i in range(REQUIRED_COLUMNS)]
        return all(value in valid_headers for value, valid_headers in zip(values, headers))

    def strip_option_prefix(self, text):
        return re.sub(r'^[A-H]\s*[、\.:：]\s*', '', str(text).strip())

    def parse_choice_options(self, opts_raw):
        options = re.split(r'\s*[A-H][、\.:：]\s*', opts_raw)
        options = [p.strip() for p in options if p.strip()]
        if options:
            return options
        return [option for part in opts_raw.split() if (option := self.strip_option_prefix(part))]

    def get_row_analysis(self, row):
        if len(row) <= ANALYSIS_COLUMN or self.is_blank(row[ANALYSIS_COLUMN]):
            return ""
        analysis = str(row[ANALYSIS_COLUMN]).strip()
        return re.sub(r'^解析\s*[：:]\s*', '', analysis)

    def ensure_analysis_column(self):
        if self.current_df is None:
            return
        while self.current_df.shape[1] <= ANALYSIS_COLUMN:
            self.current_df[self.current_df.shape[1]] = ""

    def validate_quiz_data(self, df, filename):
        if df.empty:
            raise ValueError("题库为空。")
        if df.shape[1] < REQUIRED_COLUMNS:
            raise ValueError("题库至少需要 3 列：题干、选项、答案。")

        df = df.dropna(how="all").reset_index(drop=True)
        if not df.empty and self.is_header_row(df.iloc[0]):
            df = df.iloc[1:].reset_index(drop=True)
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
            "secondary": (COLORS["primary_soft"], COLORS["primary"], COLORS["option_hover"]),
            "success": (COLORS["primary"], "#ffffff", COLORS["primary_hover"]),
            "warning": (COLORS["warning_soft"], COLORS["warning"], COLORS["option_hover"]),
            "danger": (COLORS["danger_soft"], COLORS["danger"], COLORS["option_hover"]),
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

    def reveal_correct_answer(self):
        if self.is_pd:
            correct_indices = [0 if self.ans == "对" else 1]
        else:
            correct_indices = [
                ord(answer) - ord("A")
                for answer in self.clean_choice_answer(self.ans)
                if "A" <= answer <= "H"
            ]

        for idx in correct_indices:
            if idx < len(self.opt_widgets):
                self.opt_widgets[idx].config(bg=COLORS["success_soft"], highlightbackground=COLORS["success"])

    def show_analysis(self):
        if self.analysis_text:
            self.analysis_box.config(text=f"解析：{self.analysis_text}")
            self.analysis_box.pack(fill="x", padx=sx(PAGE_PADX), pady=(sx(6), sx(4)))
        else:
            self.analysis_box.pack_forget()

    def view_analysis(self):
        if self.current_df is None or len(self.current_df) == 0:
            return
        if self.analysis_text:
            self.show_analysis()
        else:
            self.analysis_box.config(text="解析：暂无解析")
            self.analysis_box.pack(fill="x", padx=sx(PAGE_PADX), pady=(sx(6), sx(4)))

    def edit_analysis(self):
        if self.current_df is None or len(self.current_df) == 0:
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("修改解析")
        dialog.configure(bg=COLORS["app_bg"])
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(True, True)
        dialog_w = max(sx(760), 760)
        dialog_h = max(sx(420), 420)
        dialog.minsize(max(sx(560), 560), max(sx(320), 320))
        dialog.geometry(f"{dialog_w}x{dialog_h}+{self.root.winfo_rootx() + sx(140)}+{self.root.winfo_rooty() + sx(140)}")

        text_frame = tk.Frame(dialog, bg=COLORS["app_bg"])
        text_frame.pack(fill="both", expand=True, padx=sx(24), pady=(sx(18), sx(12)))
        text_box = tk.Text(
            text_frame,
            height=7,
            font=FONT_BODY,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            borderwidth=0,
            wrap="word",
            padx=sx(12),
            pady=sx(10),
        )
        text_box.pack(fill="both", expand=True)
        text_box.insert("1.0", self.analysis_text)
        text_box.focus_set()

        button_frame = tk.Frame(dialog, bg=COLORS["app_bg"])
        button_frame.pack(fill="x", padx=sx(24), pady=(0, sx(18)))

        def save_analysis():
            self.ensure_analysis_column()
            value = text_box.get("1.0", "end").strip()
            self.current_df.iat[self.current_index, ANALYSIS_COLUMN] = value
            output_path = self.get_file_path(self.current_file)
            temp_path = f"{output_path}.tmp.xlsx"
            try:
                self.current_df.to_excel(temp_path, index=False, header=False)
                os.replace(temp_path, output_path)
            except PermissionError as exc:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass
                messagebox.showerror(
                    "保存解析失败",
                    f"无法写入解析：{self.current_file}\n\n请先关闭正在打开的 Excel/WPS 表格后再保存。\n\n{exc}",
                    parent=dialog,
                )
                return
            except Exception as exc:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass
                messagebox.showerror("保存解析失败", f"无法写入解析：{self.current_file}\n\n{exc}", parent=dialog)
                return
            self.analysis_text = self.get_row_analysis(self.current_df.iloc[self.current_index])
            self.view_analysis()
            self.label_res.config(text="解析已保存", fg=COLORS["success"])
            dialog.destroy()

        btn_cancel = self.make_button(button_frame, "取消", dialog.destroy, "secondary", width=8)
        btn_cancel.pack(side="right", padx=(sx(10), 0))
        btn_save = self.make_button(button_frame, "保存解析", save_analysis, "primary", width=10)
        btn_save.pack(side="right")

    def on_review_mode_changed(self):
        if self.review_mode_var.get():
            self.auto_submit_var.set(False)
        self.update_mode_toggles()
        if self.current_df is not None:
            self.show_question()

    def on_auto_submit_changed(self):
        if self.auto_submit_var.get() and self.review_mode_var.get():
            self.review_mode_var.set(False)
            if self.current_df is not None:
                self.show_question()
        self.update_mode_toggles()

    def on_random_mode_changed(self):
        self.update_mode_toggles()

    def on_eye_mode_changed(self):
        if self.eye_mode_var.get():
            self.night_mode_var.set(False)
            self.apply_theme("eye")
        elif not self.night_mode_var.get():
            self.apply_theme("default")
        self.update_mode_toggles()

    def on_night_mode_changed(self):
        if self.night_mode_var.get():
            self.eye_mode_var.set(False)
            self.apply_theme("night")
        elif not self.eye_mode_var.get():
            self.apply_theme("default")
        self.update_mode_toggles()

    def update_mode_toggles(self):
        for name in ("review_mode_toggle", "auto_submit_toggle", "random_mode_toggle", "eye_mode_toggle", "night_mode_toggle"):
            widget = getattr(self, name, None)
            if widget is not None:
                widget.refresh()

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        set_color_theme(theme_name)
        self.root.configure(bg=COLORS["app_bg"])
        for child in self.root.winfo_children():
            child.destroy()
        self.setup_ui()
        self.refresh_file_list()
        if self.current_file:
            display_name = os.path.splitext(self.current_file)[0]
            self.quiz_var.set(display_name)
        if self.current_df is not None:
            self.show_question()

    def on_option_enter(self, idx):
        if self.review_mode_var.get():
            return
        if idx not in self.selected_indices:
            self.set_option_style(idx, hover=True)

    def on_option_leave(self, idx):
        if self.review_mode_var.get():
            return
        self.set_option_style(idx, selected=idx in self.selected_indices)

    def setup_ui(self):
        self.main_frame = tk.Frame(self.root, bg=COLORS["app_bg"])
        self.main_frame.pack(fill="both", expand=True)

        self.top_bar = tk.Frame(self.main_frame, height=sx(HEADER_HEIGHT), bg=COLORS["top_header"])
        self.top_bar.pack(fill="x", pady=(0, sx(SECTION_GAP)))
        self.top_bar.pack_propagate(False)

        self.quiz_group = tk.Frame(self.top_bar, bg=COLORS["top_header"])
        self.quiz_group.pack(side="left", padx=(sx(TOOLBAR_PADX), sx(GROUP_GAP)), pady=0)

        self.btn_refresh = self.make_button(
            self.quiz_group,
            "↻",
            self.refresh_file_list,
            "secondary",
            width=3,
        )
        self.btn_refresh.pack(side="left", padx=(0, sx(GROUP_GAP)), pady=0)

        tk.Label(
            self.quiz_group,
            text="题库",
            font=FONT_SMALL,
            bg=COLORS["top_header"],
            fg=COLORS["muted"],
        ).pack(side="left", padx=(0, sx(8)), pady=0)

        self.quiz_combo = RoundedDropdown(
            self.quiz_group,
            variable=self.quiz_var,
            values=self.quiz_names,
            command=self.load_file,
            width=18,
            font=FONT_NORMAL,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            border=COLORS["border"],
            activebackground=COLORS["option_hover"],
            corner_radius=sx(CONTROL_RADIUS),
        )
        self.quiz_combo.pack(side="left", padx=0)

        self.status_group = tk.Frame(self.top_bar, bg=COLORS["top_header"])
        self.status_group.pack(side="left", padx=(0, sx(GROUP_GAP)), pady=0)

        self.info_label = tk.Label(
            self.status_group,
            text="请选择题库",
            font=FONT_NORMAL,
            bg=COLORS["top_header"],
            fg=COLORS["muted"],
        )
        self.info_label.pack(side="left", padx=0, pady=0)

        # 跳转模块
        self.jump_frame = tk.Frame(self.top_bar, bg=COLORS["top_header"])
        self.jump_frame.pack(side="right", padx=(0, sx(TOOLBAR_PADX)), pady=0)
        tk.Label(
            self.jump_frame,
            text="跳转",
            font=FONT_SMALL,
            bg=COLORS["top_header"],
            fg=COLORS["muted"],
        ).pack(side="left")
        
        self.jump_entry = RoundedEntry(
            self.jump_frame,
            width=5,
            font=FONT_NORMAL,
            bg=COLORS["sidebar_alt"],
            fg=COLORS["text"],
            border=COLORS["border"],
            justify="center",
            corner_radius=sx(CONTROL_RADIUS),
        )
        self.jump_entry.pack(side="left", padx=(sx(8), 0))
        self.jump_entry.bind("<Return>", self.jump_to_question)

        # 动态错题集管理按钮
        self.btn_action = self.make_button(self.top_bar, "加入错题集", variant="warning", width=10)
        self.btn_action.config(font=FONT_NORMAL, height=1, padx=sx(2), pady=0)
        self.btn_action.pack(side="right", padx=(0, sx(GROUP_GAP)), pady=0)

        self.mode_frame = tk.Frame(
            self.main_frame,
            bg=COLORS["app_bg"],
            highlightthickness=0,
        )
        self.mode_frame.pack(fill="x", padx=sx(PAGE_PADX), pady=(0, sx(8)))
        for col in range(5):
            self.mode_frame.grid_columnconfigure(col, weight=1)

        self.review_mode_toggle = RoundedToggle(
            self.mode_frame,
            "背题功能",
            self.review_mode_var,
            self.on_review_mode_changed,
        )
        self.review_mode_toggle.grid(row=0, column=0, padx=sx(6), pady=sx(4))

        self.auto_submit_toggle = RoundedToggle(
            self.mode_frame,
            "自动提交",
            self.auto_submit_var,
            self.on_auto_submit_changed,
        )
        self.auto_submit_toggle.grid(row=0, column=1, padx=sx(6), pady=sx(4))

        self.random_mode_toggle = RoundedToggle(
            self.mode_frame,
            "随机刷题",
            self.random_mode_var,
            self.on_random_mode_changed,
        )
        self.random_mode_toggle.grid(row=0, column=2, padx=sx(6), pady=sx(4))

        self.eye_mode_toggle = RoundedToggle(
            self.mode_frame,
            "护眼模式",
            self.eye_mode_var,
            self.on_eye_mode_changed,
        )
        self.eye_mode_toggle.grid(row=0, column=3, padx=sx(6), pady=sx(4))

        self.night_mode_toggle = RoundedToggle(
            self.mode_frame,
            "夜间模式",
            self.night_mode_var,
            self.on_night_mode_changed,
        )
        self.night_mode_toggle.grid(row=0, column=4, padx=sx(6), pady=sx(4))

        # 题干显示
        self.question_frame = tk.Frame(self.main_frame, bg=COLORS["app_bg"])
        self.question_frame.pack(fill="x", padx=sx(PAGE_PADX), pady=(0, sx(8)))

        self.label_q = RoundedOption(
            self.question_frame,
            text="",
            wraplength=sx(QUESTION_WRAP),
            font=FONT_BODY,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            justify="left",
            anchor="nw",
            padx=sx(18),
            pady=sx(12),
            cursor="arrow",
            highlightbackground=COLORS["border"],
            corner_radius=sx(CARD_RADIUS),
        )
        self.label_q.pack(fill="x")
        
        # 选项容器
        self.opt_frame = tk.Frame(self.main_frame, bg=COLORS["app_bg"])
        self.opt_frame.pack(fill="both", expand=True, padx=sx(PAGE_PADX))
        
        self.opt_widgets = []
        for i in range(8):
            l = RoundedOption(
                self.opt_frame,
                text="",
                font=FONT_BODY,
                bg=COLORS["option_bg"],
                fg=COLORS["text"],
                relief="flat",
                padx=sx(14),
                pady=sx(8),
                wraplength=sx(OPTION_WRAP),
                justify="left",
                anchor="w",
                cursor="hand2",
                highlightthickness=1,
                highlightbackground=COLORS["border"],
                corner_radius=sx(CARD_RADIUS),
            )
            l.bind("<Button-1>", lambda e, idx=i: self.on_click_option(idx))
            l.bind("<Enter>", lambda e, idx=i: self.on_option_enter(idx))
            l.bind("<Leave>", lambda e, idx=i: self.on_option_leave(idx))
            self.opt_widgets.append(l)

        self.analysis_box = RoundedOption(
            self.main_frame,
            text="",
            font=FONT_BODY,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            relief="flat",
            padx=sx(18),
            pady=sx(12),
            wraplength=sx(OPTION_WRAP),
            justify="left",
            anchor="w",
            cursor="arrow",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            corner_radius=sx(CARD_RADIUS),
        )
        
        # 反馈文本
        self.label_res = tk.Label(
            self.main_frame,
            text="",
            font=FONT_BODY_BOLD,
            bg=COLORS["app_bg"],
            fg=COLORS["muted"],
        )
        self.label_res.pack(pady=(sx(2), sx(4)))

        # 底部控制栏
        self.bottom_frame = tk.Frame(
            self.main_frame,
            bg=COLORS["app_bg"],
            highlightthickness=0,
        )
        self.bottom_frame.pack(side="bottom", fill="x", pady=(0, sx(13)))
        
        for col in range(5):
            self.bottom_frame.grid_columnconfigure(col, weight=1)

        self.btn_prev = self.make_button(self.bottom_frame, "上一题", self.prev_question, "secondary")
        self.btn_prev.config(pady=sx(BUTTON_PADY))
        self.btn_prev.grid(row=0, column=0, padx=sx(22), pady=sx(5))

        self.btn_view_analysis = self.make_button(self.bottom_frame, "查看解析", self.view_analysis, "secondary")
        self.btn_view_analysis.config(pady=sx(BUTTON_PADY))
        self.btn_view_analysis.grid(row=0, column=1, padx=sx(22), pady=sx(5))
        
        self.btn_submit = self.make_button(self.bottom_frame, "确认提交", self.submit_answer, "disabled")
        self.btn_submit.config(state="disabled", pady=sx(BUTTON_PADY))
        self.btn_submit.grid(row=0, column=2, padx=sx(22), pady=sx(5))

        self.btn_edit_analysis = self.make_button(self.bottom_frame, "修改解析", self.edit_analysis, "secondary")
        self.btn_edit_analysis.config(pady=sx(BUTTON_PADY))
        self.btn_edit_analysis.grid(row=0, column=3, padx=sx(22), pady=sx(5))
        
        self.btn_next = self.make_button(self.bottom_frame, "下一题", self.next_question, "secondary")
        self.btn_next.config(pady=sx(BUTTON_PADY))
        self.btn_next.grid(row=0, column=4, padx=sx(22), pady=sx(5))

    def refresh_file_list(self):
        if not self.ensure_quiz_dir():
            return
            
        try:
            files = sorted([f for f in os.listdir(QUIZ_DIR) if f.endswith('.xlsx')])
        except OSError as exc:
            self.show_error("读取题库目录失败", f"无法读取题库目录：\n{QUIZ_DIR}\n\n{exc}")
            return

        self.quiz_files = files
        self.quiz_names = [os.path.splitext(f)[0] for f in files]
        if hasattr(self, "quiz_combo"):
            self.quiz_combo.set_values(self.quiz_names)

        if self.current_file in files:
            self.quiz_var.set(os.path.splitext(self.current_file)[0])
        elif not files:
            self.quiz_var.set("没有题库")
            self.info_label.config(text="题库文件夹为空")
        elif self.quiz_var.get() not in self.quiz_names:
            self.quiz_var.set("请选择题库")

    def load_selected_file(self, event):
        selected = self.quiz_var.get()
        if selected in self.quiz_names:
            self.load_file(selected)

    def load_file(self, filename):
        self.current_file = filename + ".xlsx"
        self.quiz_var.set(filename)
        
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
        self.analysis_text = ""
        self.label_res.config(text="")
        self.analysis_box.pack_forget()
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
        self.analysis_text = self.get_row_analysis(row)
        
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
                activebackground=COLORS["warning_soft"],
                activeforeground=COLORS["warning"],
                command=self.remove_from_wrong,
            )
        else:
            self.btn_action.config(
                text="加入错题集",
                bg=COLORS["warning_soft"],
                fg=COLORS["warning"],
                activebackground=COLORS["warning_soft"],
                activeforeground=COLORS["warning"],
                command=self.add_to_wrong_manually,
            )
        
        self.btn_action.config(font=FONT_NORMAL, width=10, height=1, padx=sx(2), pady=0)
        self.btn_action.pack(side="right", padx=sx(18), pady=0)
        
        if self.is_pd:
            options = ["对", "错"]  
        else:
            options = self.parse_choice_options(opts_raw)

        for i, widget in enumerate(self.opt_widgets):
            if i < len(options):
                if self.is_pd:
                    text_display = options[i] 
                else:
                    text_display = f"{chr(65+i)}. {self.strip_option_prefix(options[i])}" 
                widget.config(text=text_display, state="normal")
                widget.pack(pady=sx(4), fill="x")
            else: 
                widget.pack_forget()

        if self.review_mode_var.get():
            self.reveal_correct_answer()
            self.show_analysis()

    def on_click_option(self, idx):
        if self.review_mode_var.get():
            return
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
            self.show_analysis()
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
            self.analysis_text = ""
            self.analysis_box.pack_forget()
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
        if self.current_df is None or len(self.current_df) == 0:
            return
        if self.random_mode_var.get() and len(self.current_df) > 1:
            next_index = random.randrange(len(self.current_df))
            while next_index == self.current_index:
                next_index = random.randrange(len(self.current_df))
            self.current_index = next_index
            self.show_question()
        elif self.current_index < len(self.current_df) - 1:
            self.current_index += 1
            self.show_question()

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
