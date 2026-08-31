import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import database as db


class FinanceUI(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.build_ui()
        self.refresh_list()
        self.update_summary()

    def build_ui(self):
        # Summary cards
        summary_frame = ttk.Frame(self)
        summary_frame.pack(fill=X, padx=10, pady=10)

        cards = [
            ("sum_income", "总收入", 0, SUCCESS, lambda: Messagebox.show_info("所有收入记录的总和", "总收入")),
            ("sum_expense", "总支出", 1, DANGER, lambda: Messagebox.show_info("所有支出记录的总和", "总支出")),
            ("sum_balance", "结余", 2, PRIMARY, lambda: Messagebox.show_info("总收入 - 总支出", "结余")),
        ]
        self.summary_labels = {}
        for i in range(3):
            card = ttk.Frame(summary_frame)
            card.pack(side=LEFT, expand=True, fill=X, padx=5)
            inner = ttk.LabelFrame(card, text=cards[i][1], bootstyle=cards[i][3], padding=10)
            inner.pack(fill=BOTH, expand=True)
            lbl = ttk.Label(inner, text="¥ 0.00", font=("Microsoft YaHei UI", 16, "bold"))
            lbl.pack()
            self.summary_labels[cards[i][0]] = lbl
            inner.bind("<Button-1>", cards[i][4])
            lbl.bind("<Button-1>", cards[i][4])

        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=X, padx=10, pady=5)

        ttk.Button(toolbar, text="添加记录", bootstyle=SUCCESS, command=self.open_add_dialog).pack(side=LEFT, padx=3)
        ttk.Button(toolbar, text="编辑记录", bootstyle=PRIMARY, command=self.open_edit_dialog).pack(side=LEFT, padx=3)
        ttk.Button(toolbar, text="删除记录", bootstyle=DANGER, command=self.delete_record).pack(side=LEFT, padx=3)

        # Treeview
        columns = ("id", "date", "type", "amount", "category", "member", "event", "description")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", bootstyle=PRIMARY, selectmode="browse")
        headings = {"id": "ID", "date": "日期", "type": "类型", "amount": "金额(元)",
                    "category": "类别", "member": "关联成员", "event": "关联活动", "description": "描述"}
        widths = {"id": 50, "date": 100, "type": 70, "amount": 90, "category": 90,
                  "member": 110, "event": 130, "description": 180}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor=CENTER)

        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side=RIGHT, fill=Y, padx=(0, 10), pady=(0, 10))
        self.tree.bind("<Double-1>", lambda e: self.open_edit_dialog())

    def update_summary(self):
        income, expense, balance = db.get_finance_summary()
        self.summary_labels["sum_income"].config(text=f"¥ {income:,.2f}")
        self.summary_labels["sum_expense"].config(text=f"¥ {expense:,.2f}")
        color = "#198754" if balance >= 0 else "#dc3545"
        self.summary_labels["sum_balance"].config(text=f"¥ {balance:,.2f}", foreground=color)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for f in db.get_all_finances():
            member_name = f["member_name"] if f["member_name"] else ""
            event_name = f["event_name"] if f["event_name"] else ""
            type_text = "收入" if f["type"] == "income" else "支出"
            tag = "income" if f["type"] == "income" else "expense"
            self.tree.insert("", END, values=(
                f["id"], f["date"], type_text, f["amount"], f["category"],
                member_name, event_name, f["description"]
            ), tags=(tag,))
        self.tree.tag_configure("income", foreground="#198754")
        self.tree.tag_configure("expense", foreground="#dc3545")

    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            Messagebox.show_warning("请先选择一条记录", "提示")
            return None
        return self.tree.item(sel[0])

    def open_add_dialog(self):
        FinanceDialog(self, "添加财务记录", callback=lambda: [self.refresh_list(), self.update_summary()])

    def open_edit_dialog(self):
        item = self.get_selected()
        if item is None:
            return
        FinanceDialog(self, "编辑财务记录", values=item["values"],
                      callback=lambda: [self.refresh_list(), self.update_summary()])

    def delete_record(self):
        item = self.get_selected()
        if item is None:
            return
        if Messagebox.yesno("确定要删除该财务记录吗？", "确认删除"):
            db.delete_finance(item["values"][0])
            self.refresh_list()
            self.update_summary()


class FinanceDialog(ttk.Toplevel):
    def __init__(self, parent, title, values=None, callback=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("440x370")
        self.resizable(False, False)
        self.callback = callback
        self.edit_id = values[0] if values else None

        self.member_map = db.get_member_dict()
        self.event_map = db.get_event_dict()

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=BOTH, expand=True)

        row = 0
        ttk.Label(frame, text="类型", font=("", 10)).grid(row=row, column=0, sticky=W, pady=5)
        self.type_var = ttk.StringVar(value="income")
        if values:
            self.type_var.set("income" if values[2] == "收入" else "expense")
        ttk.Combobox(frame, textvariable=self.type_var, values=["income", "expense"],
                     state="readonly", width=28, bootstyle=PRIMARY).grid(row=row, column=1, padx=10, pady=5)
        row += 1

        ttk.Label(frame, text="金额*", font=("", 10)).grid(row=row, column=0, sticky=W, pady=5)
        self.amount_var = ttk.StringVar(value=str(values[3]) if values else "")
        ttk.Entry(frame, textvariable=self.amount_var, width=30, bootstyle=PRIMARY).grid(row=row, column=1, padx=10, pady=5)
        row += 1

        ttk.Label(frame, text="类别", font=("", 10)).grid(row=row, column=0, sticky=W, pady=5)
        self.category_var = ttk.StringVar(value=values[4] if values else "")
        categories = ["会费", "赞助", "活动收入", "其他收入", "活动支出", "物资采购", "场地费", "其他支出"]
        ttk.Combobox(frame, textvariable=self.category_var, values=categories,
                     width=28, bootstyle=PRIMARY).grid(row=row, column=1, padx=10, pady=5)
        row += 1

        ttk.Label(frame, text="关联成员", font=("", 10)).grid(row=row, column=0, sticky=W, pady=5)
        member_names = ["（无）"] + list(self.member_map.keys())
        self.member_var = ttk.StringVar(value=values[5] if values and values[5] else "（无）")
        ttk.Combobox(frame, textvariable=self.member_var, values=member_names,
                     state="readonly", width=28, bootstyle=PRIMARY).grid(row=row, column=1, padx=10, pady=5)
        row += 1

        ttk.Label(frame, text="关联活动", font=("", 10)).grid(row=row, column=0, sticky=W, pady=5)
        event_names = ["（无）"] + list(self.event_map.keys())
        self.event_var = ttk.StringVar(value=values[6] if values and values[6] else "（无）")
        ttk.Combobox(frame, textvariable=self.event_var, values=event_names,
                     state="readonly", width=28, bootstyle=PRIMARY).grid(row=row, column=1, padx=10, pady=5)
        row += 1

        ttk.Label(frame, text="描述", font=("", 10)).grid(row=row, column=0, sticky=W, pady=5)
        self.desc_var = ttk.StringVar(value=values[7] if values else "")
        ttk.Entry(frame, textvariable=self.desc_var, width=30, bootstyle=PRIMARY).grid(row=row, column=1, padx=10, pady=5)
        row += 1

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="保存", bootstyle=SUCCESS, width=12, command=self.save).pack(side=LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", bootstyle=SECONDARY, width=12, command=self.destroy).pack(side=LEFT, padx=10)

    def save(self):
        fin_type = self.type_var.get()
        try:
            amount = float(self.amount_var.get())
        except ValueError:
            Messagebox.show_warning("请输入有效的金额", "提示")
            return
        if amount <= 0:
            Messagebox.show_warning("金额必须大于0", "提示")
            return

        category = self.category_var.get().strip()
        if not category:
            category = "其他收入" if fin_type == "income" else "其他支出"

        desc = self.desc_var.get().strip()
        member_id = self.member_map.get(self.member_var.get())
        event_id = self.event_map.get(self.event_var.get())

        if self.edit_id:
            db.update_finance(self.edit_id, fin_type, amount, category, desc)
        else:
            db.add_finance(fin_type, amount, category, desc, member_id, event_id)

        if self.callback:
            self.callback()
        self.destroy()
