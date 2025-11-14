# GMDB 加密中间件管理平台

## 项目简介
GMDB 加密中间件管理平台提供一个面向医院信息化场景的 B/S 管理界面后端，实现敏感字段配置、数据迁移任务编排、加密服务监控、审计日志管理、系统配置、备份恢复以及在线帮助等核心能力。后端采用 [FastAPI](https://fastapi.tiangolo.com/) + SQLAlchemy 架构，默认使用 SQLite 存储，并通过统一的数据库配置支持切换到 PostgreSQL、MySQL、SQL Server、Oracle 等主流关系型数据库。

核心模块：
- **认证与权限**：用户名密码登录、Token 发放与注销、角色枚举（管理员、运维、审计）。
- **用户管理**：管理员可维护用户账号、角色、状态。
- **敏感字段清单**：字段元数据查询、创建、更新、逻辑禁用。
- **迁移任务**：任务创建、进度查询、启动/暂停/恢复/取消控制、历史档案。
- **服务监控**：运行状态、密钥信息、系统负载占位数据、近期错误列表。
- **审计日志**：多条件筛选、详情记录、CSV/Excel 导出。
- **系统配置**：默认参数、环境连接、密码策略等配置项管理。
- **备份恢复**：记录配置与任务备份元数据，追踪备份历史，为恢复流程预留接口。
- **帮助文档**：在线帮助内容与下载链接管理。

> 默认启动时会自动创建 SQLite 数据库文件 `gmdb_middleware.db`，并初始化一个用户名为 `admin`、密码为 `ChangeMe123!` 的系统管理员账号。

## 目录结构
```
app/
├── api/               # FastAPI 路由模块
├── core/              # 全局配置、安全工具
├── db/                # SQLAlchemy 模型与会话管理
├── schemas/           # Pydantic 模型
└── main.py            # 应用入口与启动钩子

docs/
└── middleware-management-requirements.md  # 需求文档

tests/
└── test_app.py        # 端到端示例测试
```

## 环境准备
- Python 3.10+
- 操作系统：Linux / macOS / Windows
- 可选：虚拟环境管理工具（如 `venv`、`conda`）

## 本地运行
1. **创建虚拟环境（推荐）**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
   ```

2. **安装依赖**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
   > 如果部署环境无法联网，可在可联网机器提前下载依赖轮子文件后离线安装。

3. **启动服务**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   启动后可访问：`http://localhost:8000/docs` 查看自动生成的 Swagger 文档。

## 配置说明
应用配置统一由 `app/core/config.py` 的 `Settings` 管理，并支持通过环境变量覆盖。环境变量需添加前缀 `GMDB_`，常用项如下：

| 环境变量 | 说明 | 默认值 |
| --- | --- | --- |
| `GMDB_APP_NAME` | 应用标题 | `GMDB Security Middleware` |
| `GMDB_SECRET_KEY` | JWT 密钥 | `change-this-secret` |
| `GMDB_ACCESS_TOKEN_EXPIRE_MINUTES` | Token 过期时间（分钟） | `60` |
| `GMDB_DATABASE_URL` | SQLAlchemy 数据库连接串 | `sqlite:///./gmdb_middleware.db` |
| `GMDB_INITIAL_ADMIN_USERNAME` | 默认管理员用户名 | `admin` |
| `GMDB_INITIAL_ADMIN_PASSWORD` | 默认管理员密码 | `ChangeMe123!` |

> 修改默认管理员密码后请同时更新文档与部署环境的变量配置，以免暴露弱口令。

## 数据库迁移
默认使用 SQLite，无需额外配置。如需切换到其他数据库，请确保安装对应的驱动并按以下示例配置连接串：

| 数据库 | 推荐驱动 | 连接串示例 |
| --- | --- | --- |
| PostgreSQL | `psycopg2` 或 `asyncpg` | `postgresql+psycopg2://user:password@host:5432/dbname` |
| MySQL / MariaDB | `pymysql` 或 `mysqlclient` | `mysql+pymysql://user:password@host:3306/dbname` |
| SQL Server | `pyodbc` | `mssql+pyodbc://user:password@host:1433/dbname?driver=ODBC+Driver+18+for+SQL+Server` |
| Oracle | `cx_Oracle` | `oracle+cx_oracle://user:password@host:1521/?service_name=ORCLCDB` |

部署步骤：
1. 在系统中安装对应数据库的客户端依赖与 Python 驱动（可按需在 `requirements.txt` 中追加）。
2. 启动服务前设置环境变量 `GMDB_DATABASE_URL` 为目标数据库的连接串。
3. 首次启动会自动建表并加载默认配置。

## 运行测试
```bash
pytest
```

## 部署建议
- 生产环境推荐使用 `uvicorn` + 进程管理器（如 `gunicorn`、`supervisor`）或容器化部署。
- 通过 `--workers` 参数提升并发能力，例如：
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
  ```
- 配合反向代理（Nginx、Traefik）启用 HTTPS。
- 设置环境变量 `GMDB_SECRET_KEY`、`GMDB_INITIAL_ADMIN_PASSWORD`，并根据医院内网策略调整 Token 过期时间、密码策略等。
- 定期备份数据库文件 `gmdb_middleware.db` 或所使用的外部数据库。

## 默认数据与健康检查
- 健康检查地址：`GET /health`。
- 初始配置包括默认并发数、批次大小、日志保留天数、默认算法、密钥版本与轮换时间，可通过配置接口查询与更新。

## 常见问题
1. **启动失败提示依赖缺失**：确认虚拟环境已激活，并重新执行 `pip install -r requirements.txt`。
2. **Token 失效过快**：通过环境变量调整 `GMDB_ACCESS_TOKEN_EXPIRE_MINUTES`。
3. **需要扩展日志或监控字段**：参考 `app/db/models.py` 中的模型定义，新增字段后同步更新对应 Schema 与路由。

如需更多背景与需求细节，请参阅 `docs/middleware-management-requirements.md`。
