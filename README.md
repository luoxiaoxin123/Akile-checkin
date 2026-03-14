**Akile.io 自动签到脚本**

基于 Selenium 实现的自动签到工具

## ✨ 特性

- 🤖 **全自动签到** - 自动登录并完成每日签到任务
- 🐳 **Docker支持** - 开箱即用的容器化部署
- 📬 **消息推送** - 支持 Server酱 推送签到结果

## 📦 快速开始

### Docker 部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/nianzhibai/Akile-checkin.git
cd Akile-checkin

# 2. 配置文件
cp config.ini.example config.ini
# 编辑 config.ini 填入你的账号信息

# 3. 构建并运行
docker build -t akile-checkin .
docker run --rm -v $(pwd)/config.ini:/app/config.ini akile-checkin
```

### 直接Python运行

```bash
# 1. 克隆项目
git clone https://github.com/nianzhibai/Akile-checkin.git
cd Akile-checkin

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置文件
cp config.ini.example config.ini
# 编辑 config.ini 填入你的账号信息

# 4. 运行脚本
python Akile-Checkin.py
```

### GitHub Actions（推荐免服务器）

1. Fork 本仓库到你的 GitHub 账号。
2. 在仓库 `Settings -> Secrets and variables -> Actions` 中添加以下 Secrets：
   - `AKILE_EMAIL`：Akile 登录邮箱
   - `AKILE_PASSWORD`：Akile 登录密码
3. 默认已配置定时任务：**每天北京时间 09:00 自动运行**（UTC 01:00）。
4. 你也可以在 Actions 页面手动触发 `Akile Daily Check-in` 工作流。

## ⚙️ 配置说明

编辑 `config.ini` 文件：

```ini
[akile]
email = your_email@example.com     # Akile 账号邮箱
password = your_password            # Akile 账号密码
push_key =                          # Server酱推送Key（可选）
```

## 🕐 定时任务

### Linux Crontab

```bash
# 每天上午 9:00 自动签到
0 9 * * * docker run --rm -v /root/Akile-checkin/config.ini:/app/config.ini akile-checkin > /root/Akile-checkin/checkin.log 2>&1
```
**⚠️注意**：将 `/root/Akile-checkin` 替换为你的实际项目路径。

## 📝 运行日志

成功签到：
```
签到成功, 获得10个AK币, 当前有100个AK币
```

重复签到：
```
今日已签到, 现在有100AK币
```


## 📂 项目结构

```
Akile-checkin/
├── Akile-Checkin.py      # 主程序
├── notice.py             # 消息推送模块
├── config.ini.example    # 配置文件示例
├── requirements.txt      # Python依赖
├── Dockerfile            # Docker镜像
├── .gitignore            # Git忽略文件
└── README.md             # 项目说明
```

## 📄 依赖项

```
selenium
undetected-chromedriver
requests
```

## ⚠️ 免责声明

- 本项目仅供学习交流使用
- 请勿将本项目用于商业用途
- 使用本项目所产生的一切后果由使用者自行承担
- 请遵守 Akile.io 的用户协议和使用条款

## 📜 开源协议

本项目基于 [MIT](LICENSE) 协议开源

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进项目！

---

<div align="center">

**如果觉得这个项目对你有帮助，欢迎 Star ⭐**

</div>
