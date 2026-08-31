import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog
import database as db


class MemberUI(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.build_ui()
        self.refresh_list()

    def build_ui(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=X, padx=10, pady=10)

        ttk.Button(toolbar, text="添加成员", bootstyle=SUCCESS, command=self.open_add_dialog).pack(side=LEFT, padx=3)
        ttk.Button(toolbar, text="编辑成员", bootstyle=PRIMARY, command=self.open_edit_dialog).pack(side=LEFT, padx=3)
        ttk.Button(toolbar, text="删除成员", bootstyle=DANGER, command=self.delete_member).pack(side=LEFT, padx=3)
        ttk.Button(toolbar, text="导入Excel", bootstyle="success-outline", command=self.import_excel).pack(side=LEFT, padx=3)

        ttk.Label(toolbar, text="  搜索：", font=("", 10)).pack(side=LEFT, padx=(30, 2))
        self.search_var = ttk.StringVar()
        ttk.Entry(toolbar, textvariable=self.search_var, width=20, bootstyle=PRIMARY).pack(side=LEFT, padx=3)
        ttk.Button(toolbar, text="搜索", bootstyle="info-outline", command=self.search).pack(side=LEFT, padx=2)
        ttk.Button(toolbar, text="显示全部", bootstyle="secondary-outline", command=self.refresh_list).pack(side=LEFT, padx=2)

        # Treeview
        columns = ("id", "name", "student_id", "phone", "email", "department", "join_date", "status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", bootstyle=PRIMARY, selectmode="browse")
        headings = {col: h for col, h in zip(columns,
            ["ID", "姓名", "学号", "电话", "邮箱", "院系", "加入日期", "状态"])}
        widths = {"id": 50, "name": 120, "student_id": 100, "phone": 110, "email": 160,
                  "department": 110, "join_date": 100, "status": 70}
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
        for m in db.get_all_members():
            self.tree.insert("", END, values=(
                m["id"], m["name"], m["student_id"], m["phone"],
                m["email"], m["department"], m["join_date"], m["status"]
            ), tags=(m["status"],))
        self.tree.tag_configure("active", foreground="#198754")
        self.tree.tag_configure("inactive", foreground="#6c757d")

    def search(self):
        kw = self.search_var.get().strip()
        if not kw:
            self.refresh_list()
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        for m in db.search_members(kw):
            self.tree.insert("", END, values=(
                m["id"], m["name"], m["student_id"], m["phone"],
                m["email"], m["department"], m["join_date"], m["status"]
            ), tags=(m["status"],))

    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            Messagebox.show_warning("请先在列表中选择一个成员", "提示")
            return None
        return self.tree.item(sel[0])

    def open_add_dialog(self):
        MemberDialog(self, "添加成员")

    def open_edit_dialog(self):
        item = self.get_selected()
        if item is None:
            return
        MemberDialog(self, "编辑成员", values=item["values"])

    def delete_member(self):
        item = self.get_selected()
        if item is None:
            return
        if Messagebox.yesno(f"确定要删除成员「{item['values'][1]}」吗？", "确认删除"):
            db.delete_member(item["values"][0])
            self.refresh_list()

    def import_excel(self):
        filepath = filedialog.askopenfilename(
            title="选择 Excel 文件",
            filetypes=[("Excel 文件", "*.xlsx *.xls"), ("所有文件", "*.*")],
        )
        if not filepath:
            return
        try:
            count, skipped = db.import_members_from_excel(filepath)
            msg = f"成功导入 {count} 人"
            if skipped:
                msg += f"，跳过 {skipped} 人（学号重复）"
            Messagebox.show_info(msg, "导入完成")
            self.refresh_list()
        except Exception as e:
            Messagebox.show_error(f"导入失败: {e}", "错误")


class MemberDialog(ttk.Toplevel):
    def __init__(self, parent, title, values=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("440x380")
        self.resizable(False, False)
        self.parent_refresh = parent.refresh_list
        self.edit_id = values[0] if values else None

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=BOTH, expand=True)

        row = 0
        fields = [
            ("姓名*", "name", values[1] if values else ""),
            ("学号", "student_id", values[2] if values else ""),
            ("电话", "phone", values[3] if values else ""),
            ("邮箱", "email", values[4] if values else ""),
            ("院系", "department", values[5] if values else ""),
        ]
        self.entries = {}
        for label, key, val in fields:
            ttk.Label(frame, text=label, font=("", 10)).grid(row=row, column=0, sticky=W, pady=5)
            e = ttk.Entry(frame, width=30, bootstyle=PRIMARY)
            e.insert(0, val)
            e.grid(row=row, column=1, padx=10, pady=5)
            self.entries[key] = e
            row += 1

        if values:
            ttk.Label(frame, text="状态", font=("", 10)).grid(row=row, column=0, sticky=W, pady=5)
            self.status_var = ttk.StringVar(value=values[7])
            ttk.Combobox(frame, textvariable=self.status_var, values=["active", "inactive"],
                         state="readonly", width=28, bootstyle=PRIMARY).grid(row=row, column=1, padx=10, pady=5)
            row += 1

        ttk.Label(frame, text="备注", font=("", 10)).grid(row=row, column=0, sticky=W, pady=5)
        e = ttk.Entry(frame, width=30, bootstyle=PRIMARY)
        e.insert(0, values[6] if values else "")
        e.grid(row=row, column=1, padx=10, pady=5)
        self.entries["notes"] = e
        row += 1

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="保存", bootstyle=SUCCESS, width=12, command=self.save).pack(side=LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", bootstyle=SECONDARY, width=12, command=self.destroy).pack(side=LEFT, padx=10)

    def save(self):
        name = self.entries["name"].get().strip()
        if not name:
            Messagebox.show_warning("姓名不能为空", "提示")
            return
        sid = self.entries["student_id"].get().strip()
        phone = self.entries["phone"].get().strip()
        email = self.entries["email"].get().strip()
        dept = self.entries["department"].get().strip()
        notes = self.entries["notes"].get().strip()

        if self.edit_id:
            status = self.status_var.get()
            db.update_member(self.edit_id, name, sid, phone, email, dept, status, notes)
        else:
            db.add_member(name, sid, phone, email, dept, notes)

        self.parent_refresh()
        self.destroy()
