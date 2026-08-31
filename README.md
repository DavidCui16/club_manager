# 社团管理系统

一个用于管理社团日常事务的系统，提供成员管理、活动管理和财务管理三大功能，支持桌面端和 Web 端两种使用方式。

## 功能特性

- **成员管理**：成员信息的增删改查、搜索，支持从 Excel 批量导入
- **活动管理**：活动的创建与管理、活动报名、参与人数统计
- **财务管理**：收入/支出记录、按成员或活动关联、收支汇总
- **双端支持**：桌面 GUI 应用（ttkbootstrap）和 Web 应用（Flask）

## 技术栈

- Python 3
- [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) — 桌面端 UI
- [Flask](https://flask.palletsprojects.com/) — Web 端
- SQLite — 本地数据库
- [openpyxl](https://openpyxl.readthedocs.io/) — Excel 导入

## 安装与运行

```bash
# 1. 安装依赖
pip install -r requirements.txt
```

### 桌面版

```bash
python main.py
```

### Web 版

```bash
python webapp.py
```

启动后：
- 本机访问：http://127.0.0.1:5000
- 局域网访问：http://本机IP:5000（默认监听 0.0.0.0:5000）

Web 版默认登录密码为 `admin123`，可在 `webapp.py` 中修改。

## 打包为可执行文件

使用 PyInstaller：

```bash
# 桌面版
pyinstaller ClubManager.spec

# Web 版
pyinstaller ClubWeb.spec
```

生成的程序位于 `dist/` 目录。

## 项目结构

```
├── main.py            # 桌面版入口
├── webapp.py          # Web 版入口（Flask）
├── database.py        # 数据库操作（SQLite）
├── ui/                # 桌面版界面模块
│   ├── member_ui.py   #   成员管理界面
│   ├── event_ui.py    #   活动管理界面
│   └── finance_ui.py  #   财务管理界面
├── templates/         # Web 版 HTML 模板
├── supabase/          # Supabase 部署脚本（可选）
├── ClubManager.spec   # 桌面版打包配置
├── ClubWeb.spec       # Web 版打包配置
└── requirements.txt   # 依赖列表
```

## 可选：部署到 Supabase

如需使用云端数据库，可在 [Supabase](https://supabase.com/) SQL Editor 中运行 `supabase/schema.sql` 初始化表结构。
