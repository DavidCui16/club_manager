import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import database as db


class EventUI(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.build_ui()
        self.refresh_list()

    def build_ui(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=X, padx=10, pady=10)

        ttk.Button(toolbar, text="添加活动", bootstyle=SUCCESS, command=self.open_add_dialog).pack(side=LEFT, padx=3)
        ttk.Button(toolbar, text="编辑活动", bootstyle=PRIMARY, command=self.open_edit_dialog).pack(side=LEFT, padx=3)
        ttk.Button(toolbar, text="删除活动", bootstyle=DANGER, command=self.delete_event).pack(side=LEFT, padx=3)
        ttk.Button(toolbar, text="管理报名", bootstyle=WARNING, command=self.manage_participants).pack(side=LEFT, padx=3)

        ttk.Label(toolbar, text="  搜索：", font=("", 10)).pack(side=LEFT, padx=(30, 2))
        self.search_var = ttk.StringVar()
        ttk.Entry(toolbar, textvariable=self.search_var, width=20, bootstyle=PRIMARY).pack(side=LEFT, padx=3)
        ttk.Button(toolbar, text="搜索", bootstyle="info-outline", command=self.search).pack(side=LEFT, padx=2)
        ttk.Button(toolbar, text="显示全部", bootstyle="secondary-outline", command=self.refresh_list).pack(side=LEFT, padx=2)

        columns = ("id", "name", "event_date", "location", "participant_count", "max_participants", "fee", "status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", bootstyle=PRIMARY, selectmode="browse")
        headings = {"id": "ID", "name": "活动名称", "event_date": "日期", "location": "地点",
                    "participant_count": "已报名", "max_participants": "上限", "fee": "费用(元)", "status": "状态"}
        widths = {"id": 50, "name": 160, "event_date": 110, "location": 120,
                  "participant_count": 70, "max_participants": 70, "fee": 80, "status": 90}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor=CENTER)

        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side=RIGHT, fill=Y, padx=(0, 10), pady=(0, 10))
        self.tree.bind("<Double-1>", lambda e: self.open_edit_dialog())

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        status_colors = {"upcoming": "#0dcaf0", "ongoing": "#198754", "finished": "#6c757d", "cancelled": "#dc3545"}
        for e in db.get_all_events():
            self.tree.insert("", END, values=(
                e["id"], e["name"], e["event_date"], e["location"],
                e["participant_count"], e["max_participants"], e["fee"], e["status"]
            ), tags=(e["status"],))
        for k, v in status_colors.items():
            self.tree.tag_configure(k, foreground=v)

    def search(self):
        kw = self.search_var.get().strip()
        if not kw:
            self.refresh_list()
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        for e in db.search_events(kw):
            self.tree.insert("", END, values=(
                e["id"], e["name"], e["event_date"], e["location"],
                e["participant_count"], e["max_participants"], e["fee"], e["status"]
            ), tags=(e["status"],))

    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            Messagebox.show_warning("请先选择一个活动", "提示")
            return None
        return self.tree.item(sel[0])

    def open_add_dialog(self):
        EventDialog(self, "添加活动")

    def open_edit_dialog(self):
        item = self.get_selected()
        if item is None:
            return
        EventDialog(self, "编辑活动", values=item["values"])

    def delete_event(self):
        item = self.get_selected()
        if item is None:
            return
        if Messagebox.yesno(f"确定要删除活动「{item['values'][1]}」吗？所有报名记录也将删除。", "确认删除"):
            db.delete_event(item["values"][0])
            self.refresh_list()

    def manage_participants(self):
        item = self.get_selected()
        if item is None:
            return
        event_id, event_name = item["values"][0], item["values"][1]
        ParticipantDialog(self, event_id, event_name, self.refresh_list)


class EventDialog(ttk.Toplevel):
    def __init__(self, parent, title, values=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("440x380")
        self.resizable(False, False)
        self.refresh = parent.refresh_list
        self.edit_id = values[0] if values else None

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=BOTH, expand=True)

        row = 0
        fields = [
            ("活动名称*", "event_name", values[1] if values else ""),
            ("日期", "event_date", values[2] if values else "2026-08-01"),
            ("地点", "location", values[3] if values else ""),
        ]
        self.entries = {}
        for label, key, val in fields:
            ttk.Label(frame, text=label, font=("", 10)).grid(row=row, column=0, sticky=W, pady=5)
            e = ttk.Entry(frame, width=30, bootstyle=PRIMARY)
            e.insert(0, val)
            e.grid(row=row, column=1, padx=10, pady=5)
            self.entries[key] = e
            row += 1

        ttk.Label(frame, text="人数上限", font=("", 10)).grid(row=row, column=0, sticky=W, pady=5)
        self.max_var = ttk.StringVar(value=str(values[5]) if values else "0")
        ttk.Spinbox(frame, textvariable=self.max_var, from_=0, to=9999, width=28, bootstyle=PRIMARY).grid(row=row, column=1, padx=10, pady=5)
        ttk.Label(frame, text="0 = 无限制", font=("", 9), foreground="gray").grid(row=row, column=2, padx=5)
        row += 1

        ttk.Label(frame, text="费用(元)", font=("", 10)).grid(row=row, column=0, sticky=W, pady=5)
        self.fee_var = ttk.StringVar(value=str(values[6]) if values else "0")
        ttk.Spinbox(frame, textvariable=self.fee_var, from_=0, to=99999, width=28, bootstyle=PRIMARY).grid(row=row, column=1, padx=10, pady=5)
        row += 1

        ttk.Label(frame, text="描述", font=("", 10)).grid(row=row, column=0, sticky=W, pady=5)
        e = ttk.Entry(frame, width=30, bootstyle=PRIMARY)
        e.insert(0, values[4] if values else "")
        e.grid(row=row, column=1, padx=10, pady=5)
        self.entries["desc"] = e
        row += 1

        if values:
            ttk.Label(frame, text="状态", font=("", 10)).grid(row=row, column=0, sticky=W, pady=5)
            self.status_var = ttk.StringVar(value=values[7])
            ttk.Combobox(frame, textvariable=self.status_var,
                         values=["upcoming", "ongoing", "finished", "cancelled"],
                         state="readonly", width=28, bootstyle=PRIMARY).grid(row=row, column=1, padx=10, pady=5)
            row += 1

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=20)
        ttk.Button(btn_frame, text="保存", bootstyle=SUCCESS, width=12, command=self.save).pack(side=LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", bootstyle=SECONDARY, width=12, command=self.destroy).pack(side=LEFT, padx=10)

    def save(self):
        name = self.entries["event_name"].get().strip()
        if not name:
            Messagebox.show_warning("活动名称不能为空", "提示")
            return
        event_date = self.entries["event_date"].get().strip()
        location = self.entries["location"].get().strip()
        max_count = int(self.max_var.get())
        fee = float(self.fee_var.get())
        desc = self.entries["desc"].get().strip()

        if self.edit_id:
            db.update_event(self.edit_id, name, event_date, location, desc, max_count, fee, self.status_var.get())
        else:
            db.add_event(name, event_date, location, desc, max_count, fee)

        self.refresh()
        self.destroy()


class ParticipantDialog(ttk.Toplevel):
    def __init__(self, parent, event_id, event_name, refresh_callback):
        super().__init__(parent)
        self.title(f"报名管理 - {event_name}")
        self.geometry("600x450")
        self.event_id = event_id
        self.refresh_callback = refresh_callback

        top = ttk.Frame(self, padding=15)
        top.pack(fill=X)

        ttk.Label(top, text="选择成员：", font=("", 10)).pack(side=LEFT)
        self.member_map = db.get_member_dict()
        member_names = list(self.member_map.keys())
        self.combo_var = ttk.StringVar()
        self.combo = ttk.Combobox(top, textvariable=self.combo_var, values=member_names,
                                  state="readonly", width=28, bootstyle=PRIMARY)
        self.combo.pack(side=LEFT, padx=5)
        ttk.Button(top, text="添加报名", bootstyle=SUCCESS, command=self.add_participant).pack(side=LEFT, padx=3)
        ttk.Button(top, text="取消报名", bootstyle=DANGER, command=self.remove_participant).pack(side=LEFT, padx=3)

        columns = ("member_id", "name", "student_id", "department", "phone")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", bootstyle=PRIMARY, selectmode="browse")
        for col, head, w in zip(columns, ["ID", "姓名", "学号", "院系", "电话"], [50, 120, 120, 120, 120]):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=w, anchor=CENTER)

        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True, padx=(15, 0), pady=(0, 15))
        scrollbar.pack(side=RIGHT, fill=Y, padx=(0, 15), pady=(0, 15))

        self.refresh_participants()

    def refresh_participants(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for m in db.get_event_participants(self.event_id):
            self.tree.insert("", END, values=(m["id"], m["name"], m["student_id"], m["department"], m["phone"]))

    def add_participant(self):
        name = self.combo_var.get()
        if not name:
            Messagebox.show_warning("请选择一个成员", "提示")
            return
        member_id = self.member_map[name]
        if db.add_participant(self.event_id, member_id):
            self.refresh_participants()
            self.refresh_callback()
        else:
            Messagebox.show_warning("该成员已报名此活动", "提示")

    def remove_participant(self):
        sel = self.tree.selection()
        if not sel:
            Messagebox.show_warning("请选择要取消报名的成员", "提示")
            return
        member_id = self.tree.item(sel[0])["values"][0]
        db.remove_participant(self.event_id, member_id)
        self.refresh_participants()
        self.refresh_callback()
