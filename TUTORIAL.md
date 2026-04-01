# TGForwarder 使用教程和搭建方法

## 1. 环境搭建指南

### 1.1 安装 Python

TGForwarder 需要 Python 3.7 或更高版本。请按照以下步骤安装 Python：

#### Windows 系统
1. 访问 [Python 官方网站](https://www.python.org/downloads/windows/)
2. 下载适合你系统的 Python 3.7+ 安装包
3. 运行安装程序，确保勾选 "Add Python to PATH"
4. 点击 "Install Now" 完成安装
5. 打开命令提示符，运行 `python --version` 验证安装成功

#### macOS 系统
1. 访问 [Python 官方网站](https://www.python.org/downloads/macos/)
2. 下载适合你系统的 Python 3.7+ 安装包
3. 运行安装程序并按照提示完成安装
4. 打开终端，运行 `python3 --version` 验证安装成功

#### Linux 系统
大多数 Linux 发行版默认已安装 Python 3。如果没有安装或版本过低，请按照以下步骤安装：

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**CentOS/RHEL**:
```bash
sudo yum install python3 python3-pip
```

**验证安装**:
```bash
python3 --version
pip3 --version
```

### 1.2 安装依赖库

1. 下载或克隆 TGForwarder 项目到本地
2. 进入项目目录
3. 运行以下命令安装依赖：

```bash
pip install -r requirements.txt
```

如果使用的是 Python 3，请使用 `pip3`：

```bash
pip3 install -r requirements.txt
```

依赖库包括：
- Telethon: Telegram API 客户端库
- httpx: HTTP 客户端库
- beautifulsoup4: HTML 解析库
- PySocks: 代理支持库

## 2. API 信息获取指南

### 2.1 获取 Telegram API ID 和 Hash

1. 访问 [Telegram 开发者网站](https://my.telegram.org/)
2. 使用你的 Telegram 账号登录
3. 点击 "API development tools"
4. 填写应用信息：
   - App title: 可以填写 "TGForwarder"
   - Short name: 可以填写 "tgforwarder"
   - Platform: 选择 "Desktop"
5. 点击 "Create application"
6. 记录生成的 API ID 和 API Hash

### 2.2 获取 String Session

String Session 是 Telegram 客户端的会话字符串，用于授权访问你的 Telegram 账号。

**方法一：使用在线工具**
1. 访问 [tgs.252035.xyz](https://tgs.252035.xyz/) (选择 V1)
2. 输入你的 API ID 和 API Hash
3. 按照提示完成 Telegram 登录验证
4. 复制生成的 String Session

**方法二：使用 Telethon 代码生成**
```python
from telethon import TelegramClient
from telethon.sessions import StringSession

api_id = YOUR_API_ID
api_hash = 'YOUR_API_HASH'

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print(client.session.save())
```

### 2.3 API 信息安全存储

- 不要将 API ID、API Hash 和 String Session 公开分享
- 不要将这些信息硬编码在代码中（除非是个人使用）
- 建议使用环境变量或配置文件存储这些信息

## 3. 项目配置说明

### 3.1 TGForwarder.py 配置

打开 `TGForwarder.py` 文件，修改以下配置参数：

```python
# 监控的频道/群组列表
channels_groups_monitor = ['频道1', '频道2', 'https://t.me/邀请链接']

# 转发目标频道
forward_to_channel = '你的目标频道'

# 监控最近消息数
limit = 20

# 包含关键词（消息中包含这些关键词才会被转发）
include = ['链接', '片名', '名称', '剧名', 'ed2k', 'magnet', 'drive.uc.cn', 'caiyun.139.com', 'cloud.189.cn', '123684.com', '123865.com', '123912.com', '123pan.com', '123pan.cn', '123592.com', 'pan.quark.cn', '115cdn.com', '115.com', 'anxia.com', 'alipan.com', 'aliyundrive.com', '夸克云盘', '阿里云盘', '磁力链接', 'Alipan', 'Quark', '115', 'Baidu', '获取资源', '查看资源', '💡 评论区评论', '直达链接']

# 排除关键词（消息中包含这些关键词不会被转发）
exclude = ['小程序', '预告', '预感', '盈利', '即可观看', '书籍', '电子书', '图书', '丛书', '期刊', 'app', '软件', '破解版', '解锁', '专业版', '高级版', '最新版', '食谱', '免安装', '免广告', '安卓', 'Android', '课程', '教程', '教学', '全书', '名著', 'mobi', 'MOBI', 'epub', '任天堂', 'PC', '单机游戏', '搜素', '色色', 'pdf', 'PDF', 'PPT', '抽奖', '完整版', '读者', '文学', '写作', '节课', '套装', '话术', '纯净版', '日历', 'txt', 'MP3', '网赚', 'mp3', 'WAV', 'CD', '音乐', '专辑', '模板', '书中', '读物', '入门', '零基础', '常识', '电商', '小红书', 'JPG', '短视频', '工作总结', '写真', '抖音', '资料', '华为', '短剧', '纪录片', '记录片', '纪录', '纪实', '学习', '付费', '小学', '初中', '数学', '语文']

# 消息中的超链接文字，如果存在超链接，会用url替换文字
hyperlink_text = {
    "magnet": ["点击查看","📥 点击下方按钮获取资源","@@"],
    "ed2k": ["点击查看","📥 点击下方按钮获取资源","@@"],
    "uc": ["点击获取UC链接","点击查看","UC网盘","📥 点击下方按钮获取资源","@@"],
    "mobile": ["点击查看","📥 点击下方按钮获取资源","@@"],
    "tianyi": ["直达链接","📥 点击下方按钮获取资源","💡 评论区评论","@@"],
    "xunlei": ["点击获取迅雷链接","直达链接","迅雷网盘","📥 点击下方按钮获取资源","@@"],
    "quark": ["点击获取夸克链接","😀 Quark","【夸克网盘】点击获取","夸克云盘","点击查看","夸克网盘","📥 点击下方按钮获取资源","@@"],
    "115": ["😀 115","115云盘","点击查看","点击转存","115网盘","📥 点击下方按钮获取资源","📢 频道：@Lsp115","@@"],
    "aliyun": ["点击获取阿里云盘链接","😀 Alipan","【阿里云盘】点击获取","阿里云盘","点击查看","📥 点击下方按钮获取资源","@@"],
    "pikpak": ["PikPak云盘","点击查看","📥 点击下方按钮获取资源","@@"],
    "baidu": ["点击获取百度链接","😀 Baidu","【百度网盘】点击获取","百度云盘","点击查看","百度网盘","直达链接","📥 点击下方按钮获取资源","@@"],
    "123": ["点击查看","📥 点击下方按钮获取资源","@@"],
    "others": ["点击查看","📥 点击下方按钮获取资源","@@"],
}

# 替换消息中关键字(tag/频道/群组)
replacements = {
    forward_to_channel: ['xlshare','yunpangroup','pan123pan','juziminmao',"yunpanall","NewAliPan","ucquark", "uckuake", "yunpanshare", "yunpangroup", "Quark_0",'ShiShuTiaoA','Oscar_4Kmovies','Oscarono','leoziyuan','leopansou','leipanbot','LEO网盘搜集',"guaguale115", "Aliyundrive_Share_Channel", "alyd_g", "shareAliyun", "aliyundriveShare","yeqinghuibot","yeqingjie_GJG666",'yydf_hzl','share_123pan_bot','tpbox_bot','sougou115',"hao115", "Mbox115", "NewQuark", "Quark_Share_Group", "QuarkRobot", "memosfanfan_bot",'pankuake_share','SharePanBaidu','share_pan','sharepan_bot','Aliyun_4K_Movies','Netdisk_Movies',"Quark_Movies", "aliyun_share_bot", "AliYunPanBot","None","大风车","雷锋","热心网友","xx123pan","xx123pan1","share_123pan_bot","🧑🏻‍🚀  订阅同步","🧑🏻‍🚀  订阅直达"],
    "": ['via Hamilton 分享','via 孔 子','🕸源站：https://tv.yydsys.top','via 特别大 爱新觉罗',"🦜投稿", "• ", "🐝", "树洞频道", "云盘投稿", "广告合作", "✈️ 画境频道", "🌐 画境官网", "🎁 详情及下载", " - 影巢", "帮助咨询", "🌈 分享人: 自动发布","分享者：123盘社区","🌥云盘频道 - 📦",'频道｜投稿｜合作',"🌍： 群主自用机场: 守候网络, 9折活动!", "🔥： 阿里云盘播放神器: VidHub","🔥： 阿里云盘全能播放神器: VidHub","🔥： 移动云盘免流丝滑挂载播放: VidHub", "画境流媒体播放器-免费看奈飞，迪士尼！",'播放神器: VidHub','🔥： https://www.alipan.com/s/2gk164mf2oN','via 🤖編號 9527','via o o o o o',"AIFUN 爱翻 BGP入口极速专线", "AIFUN 爱翻 机场", "from 天翼云盘日更频道","via 匿名","🖼️ 奥斯卡4K蓝光影视站","投稿: 点击投稿","────────────────","【1】需要迅雷云盘链接请进群，我会加入更新", '⚠️ 版权：版权反馈/DMCA','📢 频道 👥 群组 🔍 投稿/搜索','✈️ 机场：红杏云 糖果云','即可获取资源，括号内名称点击可复制📋',"【2】求随手单点频道内容，点赞❤️👍等表情","【3】帮找❗️资源，好片源（别客气）","【4】目前共４个频道，分类内容发布↓","【5】更多请看简介［含™「莫愁片海•拾贝十倍」社群］与🐧/🌏正式群", " - 📌","🚀 频 道: 热剧追更","🔍 群 组: 聚合搜索","💬 公众号: 爱影搜","🌈 分享自: 爱影VIP"]
}

# 自定义统计置顶消息，markdown格式
message_md = (
    "**Github：[https://github.com/fish2018](https://github.com/fish2018)**\n\n"
    "**本频道实时更新最新影视资源并自动清理失效链接(123、夸克、阿里云、天翼、UC、115、移动、磁力、百度、迅雷)**\n\n"
    "**推荐播放器：[影视](https://t.me/ys_tvb)** \t\t**网盘搜索：[盘搜](https://github.com/fish2018/pansou)**\n\n"
    "**[PG](https://t.me/pandagroovechat)接口：    [备用](https://cnb.cool/fish2018/pg/-/git/raw/master/jsm.json)   [备用2](http://www.fish2018.ip-ddns.com/p/jsm.json)   [备用3](http://www3.fish2018.ip-ddns.com/p/jsm.json) **"
    "```https://www.252035.xyz/p/jsm.json```"
    "**tgsearch服务器(PG)：    [备用](http://tg.fish2018.ip-ddns.com)    [备用2](http://tg3.fish2018.ip-ddns.com)**"
    "```https://tg.252035.xyz```"
    "**[真心](https://t.me/juejijianghuchat)接口：    [备用](https://cnb.cool/fish2018/zx/-/git/raw/master/FongMi.json)   [备用2](http://www.fish2018.ip-ddns.com/z/FongMi.json)   [备用3](http://www3.fish2018.ip-ddns.com/z/FongMi.json) **"
    "```https://www.252035.xyz/z/FongMi.json```"
    "**tgsou服务器(真心)：    [备用](http://tgsou.fish2018.ip-ddns.com)    [备用2](http://tgsou3.fish2018.ip-ddns.com)**"
    "```https://tgsou.252035.xyz```"
)

# 匹配关键字分发到不同频道/群组，不需要分发直接设置channel_match=[]即可
channel_match = []

# 尝试加入公共群组频道，无法过验证
try_join = False

# 如果需要监控评论中资源则开启，否则建议关闭
check_replies = False

# 监控评论数
replies_limit = 1

# API信息
api_id = 6627460
api_hash = '27a53a0965e486a2bc1b1fcde473b1c4'
string_session = '你的String Session'

# 默认不开启代理
proxy = None
# proxy = (socks.SOCKS5, '127.0.0.1', 7897)

# 首次检测自己频道最近checknum条消息去重，后续检测累加已转发的消息数，如果当日转发数超过checknum条，则检测当日转发总数
checknum = 50

# 允许转发今年之前的资源
past_years = False

# 只允许转发当日的
only_today = True
```

### 3.2 TGNetDiskLinkChecker.py 配置

打开 `TGNetDiskLinkChecker.py` 文件，修改以下配置参数：

```python
# 配置项
CONFIG = {
    # Telethon客户端配置
    "API_ID": 6627460,
    "API_HASH": "27a53a0965e486a2bc1b1fcde473b1c4",
    "STRING_SESSION": "你的String Session",
    "JSON_PATH_NORMAL": os.path.join(os.getcwd(), "messages.json"),
    "JSON_PATH_123": os.path.join(os.getcwd(), "messages_123.json"),
    "TARGET_CHANNEL": "你的目标频道",
    "PROXY": None,
    "BATCH_SIZE": 500,
    # 运行配置
    "DELETE_MODE": 2,  # 1: 检测并删除 (重新检测后再删除), 2: 仅检测, 3: 删除标记为失效的消息
    "LIMIT": 1000,     # 每次检测的最大消息数量
    "CONCURRENCY": 20, # 并发数
    "RECHECK": True,    # 是否重新检测标记为失效的链接
    "NET_DISK_DOMAINS": 
    [
        'pan.quark.cn',
        # 'aliyundrive.com', 'alipan.com',
        # '115.com', '115cdn.com', 'anxia.com',
        # 'pan.baidu.com', 'yun.baidu.com',
        # 'mypikpak.com',
        # '123684.com', '123685.com', '123912.com', '123pan.com', '123pan.cn', '123592.com',
        # 'cloud.189.cn',
        # 'drive.uc.cn'
    ]
}
```

## 4. 核心功能使用方法

### 4.1 启动 TGForwarder

在项目目录下运行：

```bash
python TGForwarder.py
```

如果使用 Python 3：

```bash
python3 TGForwarder.py
```

### 4.2 资源转发工作原理

1. **监控频道**：脚本会监控配置的频道/群组列表
2. **过滤消息**：根据包含和排除关键词过滤消息
3. **提取链接**：从消息中提取网盘链接和磁力链接
4. **去重处理**：检查链接是否已转发，避免重复
5. **转发消息**：将符合条件的消息转发到目标频道
6. **统计置顶**：自动统计当日转发数量并置顶

### 4.3 定时运行设置

#### Windows 系统
1. 打开 "任务计划程序"
2. 创建基本任务
3. 设置触发器（例如每天定时运行）
4. 操作选择 "启动程序"
5. 程序/脚本选择 `python.exe`，添加参数 `TGForwarder.py`，起始于设置为项目目录

#### macOS/Linux 系统
使用 crontab 设置定时任务：

```bash
crontab -e
```

添加以下内容（每天 8 点运行）：

```
0 8 * * * cd /path/to/forwarder && python3 TGForwarder.py
```

## 5. 网盘链接检测功能使用方法

### 5.1 启动链接检测

在项目目录下运行：

```bash
python TGNetDiskLinkChecker.py
```

如果使用 Python 3：

```bash
python3 TGNetDiskLinkChecker.py
```

### 5.2 检测模式说明

- **模式 1**：检测并删除失效链接（重新检测后再删除）
- **模式 2**：仅检测失效链接，不删除
- **模式 3**：删除已标记为失效的消息

### 5.3 不同网盘类型的检测特点

- **夸克网盘**：默认开启检测，容易失效
- **123网盘**：风控严格，单独保存检测结果，即使检测失败也不会删除
- **阿里云盘**：使用 API 检测，可靠性较高
- **百度网盘**：使用网页检测，可能需要处理验证码
- **天翼云盘**：使用 API 检测
- **UC网盘**：使用网页检测
- **115网盘**：使用 API 检测

## 6. 常见问题和解决方案

### 6.1 网络连接问题

**问题**：无法连接到 Telegram API
**解决方案**：
- 检查网络连接
- 配置代理服务器
- 尝试更换网络环境

### 6.2 API 限制问题

**问题**：遇到 API 限制错误
**解决方案**：
- 减少请求频率
- 增加请求间隔
- 避免短时间内大量操作

### 6.3 权限问题

**问题**：无法访问频道或发送消息
**解决方案**：
- 确保机器人或账号已加入目标频道
- 确保账号有发送消息的权限
- 检查频道设置是否允许消息转发

### 6.4 链接检测失败

**问题**：网盘链接检测失败
**解决方案**：
- 检查网络连接
- 增加检测超时时间
- 对于 123 网盘，考虑降低检测频率

### 6.5 消息转发失败

**问题**：消息无法转发
**解决方案**：
- 检查目标频道权限
- 确保账号未被限制
- 检查消息内容是否符合 Telegram 规则

## 7. 高级配置

### 7.1 频道分发配置

如果需要根据关键词将资源分发到不同频道，可以配置 `channel_match`：

```python
channel_match = [
    {
        'include': ['pan.quark.cn'],  # 包含这些关键词
        'exclude': ['mp3'],  # 排除这些关键词
        'target': 'quark'  # 转发到目标频道/群组
    },
    {
        'include': ['aliyundrive.com'],
        'exclude': [],
        'target': 'aliyun'
    }
]
```

### 7.2 代理配置

如果需要使用代理，可以配置 `proxy` 参数：

```python
# SOCKS5 代理
proxy = (socks.SOCKS5, '127.0.0.1', 7897, '用户名', '密码')

# HTTP 代理
proxy = (socks.HTTP, '127.0.0.1', 7890, '用户名', '密码')
```

## 8. 注意事项

1. **遵守 Telegram 规则**：不要滥用工具，遵守 Telegram 的使用条款
2. **保护账号安全**：不要分享 API 信息和 String Session
3. **合理使用**：避免过度请求，以免被 Telegram 限制
4. **定期更新**：定期检查项目更新，获取最新功能和 bug 修复
5. **备份数据**：定期备份历史记录文件，避免数据丢失

## 9. 故障排除

如果遇到问题，请按照以下步骤排查：

1. **检查日志**：查看程序输出的错误信息
2. **验证配置**：确保所有配置参数正确
3. **测试网络**：确保网络连接正常，能访问 Telegram
4. **检查权限**：确保账号有相应的权限
5. **参考常见问题**：查看本文档的常见问题部分
6. **寻求帮助**：如果问题无法解决，可以在项目 GitHub 页面提交 issue

## 10. 总结

TGForwarder 是一个功能强大的 Telegram 资源转发工具，能够帮助你自动监控和转发频道资源，同时检测和清理失效的网盘链接。通过本教程的指导，你应该能够顺利部署和使用该工具，为你的 Telegram 频道提供持续的资源更新。

如果你有任何问题或建议，欢迎在项目 GitHub 页面反馈。

---

**项目地址**：[https://github.com/fish2018/TGForwarder](https://github.com/fish2018/TGForwarder)
**作者**：fish2018