# TGForwarder

tgsearch、tgsou需要配置一堆频道群组，完全可以跑个定时任务监控这些频道群组，把网盘、磁力资源全都转发到自己的频道，这样只需要配置一个就可以

效果参考：https://t.me/s/tgsearchers4

## 功能特性

### 功能

* 可以突破频道禁止消息转发的限制

* 支持带关键词的纯文本、图文、视频消息转发到自己频道，可以自定义搜索关键词和禁止关键词

* 默认仅转发当日的消息，通过only_today参数修改

* 以主动发送的方式发布到自己频道，可以降低被限制风险，消息先后顺序与原频道/群组保持一致

* 使用复制消息的方式主动发送，无需下载多媒体文件，直接发送视频、图文消息

* 每次转发后自动统计今日转发数量并置顶，发送前会删除之前发出的统计消息

* 支持使用markdown语法自定义置顶转发统计消息内容

* 支持根据链接和视频大小去重，已经存在的资源不再转发，默认检测最近`checknum`条消息去重，当日转发总数大于`checknum`时，则检测当日转发总数消息

* 自动清理资源链接重复的历史消息，只保留最新消息

* 支持尝试加入频道群组(不支持自动过验证)，支持私有频道

* 支持转发消息评论中的资源链接，全局配置(check_replies默认False、replies_limit),可针对个别频道设置监控评论区，格式`频道名|reply_评论数limit_频道消息数limit`，频道消息数limit可以缺省。配置方式 channels_groups_monitor = ['DuanJuQuark|reply_1'] 或 ['DuanJuQuark|reply_1_20']

* 支持对不同的频道/群组，可以自定义监听最近消息数量，默认取limit值，配置方式 channels_groups_monitor = ['Quark_Movies|20', 'Aliyun_4K_Movies|5']

* 支持自定义替换消息中的关键字，如标签、频道/群组等

* 支持根据关键字匹配(可根据网盘类型、资源类型tag)，自动分发到不同频道/群组，支持设置独立的包含/排除关键词。如果不需要分发，设置channel_match=[]

* 默认过滤掉今年之前的资源，pass_years=True则允许转发老年份资源

* 支持消息中文字超链接为网盘链接的场景，自动还原为url，支持多个网盘超链接替换场景

* 支持https://telegra.ph/  链接中的资源链接替换回消息中(如果链接过多，超出消息长度限制则会发送失败)

* 支持消息中文字超链接跳转机器人发送`/start`获取资源链接，自动还原为url

* 可清理指定时间段的消息，执行`TGForwarder().clear()`方法

* 每次转发消息的耗时统计

### 检测删除有风险，自行测试

`TGNetDiskLinkChecker.py`脚本用于检测网盘链接有效性，并自动删除链接失效的消息，目前支持 夸克、天翼、阿里云、115、123、百度、UC

* 新增删除模式delete_mode，  1: 检测并删除失效链接, 2: 仅检测并标记失效，但不删除, 3: 不检测，仅删除标记为失效的消息

* 为进一步防止误判断，最后会对检测失效的链接进行重新检测

* 允许只检测最近Limit条消息中的网盘链接，None则整个频道的消息全量检测（每次检测都是json中保存的历史链接+limit条新检测的）

* 123网盘风控严格，单独保存一个json文件，即时检测失败也不会删除

* 链接请求失败的一律当做有效，避免误判。

* 默认只开放夸克检测，目前只有这个容易失效，可通过`NET_DISK_DOMAINS`参数设置

### 可视化后台管理

* 配置编辑：通过Web界面编辑所有配置参数

* 脚本启停：一键启动/停止转发脚本和链接检测脚本

* 状态监控：实时显示脚本运行状态

* 输出日志：实时查看脚本运行输出

## 安装教程

### 1. 环境要求

* Python 3.7+

* 稳定的网络连接（可能需要代理）

* Telegram 账号

### 2. 安装步骤

#### Windows 系统

1. **下载项目**：克隆或下载本项目到本地

2. **安装依赖**：

   * 双击运行 `start_backend.bat` 脚本

   * 脚本会自动安装所需依赖

3. **启动后台服务**：

   * 依赖安装完成后，服务会自动启动

   * 访问 `http://localhost:5000` 进入管理界面

4. **配置系统**：

   * 在界面中填写 API 信息、频道设置等

   * 点击 "保存配置" 按钮保存修改

5. **运行脚本**：

   * 在 "状态监控" 部分点击 "启动" 按钮运行脚本

#### macOS 系统

1. **下载项目**：克隆或下载本项目到本地

2. **安装依赖**：

   * 打开终端，进入项目目录

   * 运行 `pip3 install -r requirements.txt`

3. **启动后台服务**：

   * 运行 `python3 backend/app.py`

   * 访问 `http://localhost:5000` 进入管理界面

4. **配置系统**：

   * 在界面中填写 API 信息、频道设置等

   * 点击 "保存配置" 按钮保存修改

5. **运行脚本**：

   * 在 "状态监控" 部分点击 "启动" 按钮运行脚本

#### Linux 系统

1. **下载项目**：克隆或下载本项目到本地

2. **安装依赖**：

   * 打开终端，进入项目目录

   * 运行 `pip3 install -r requirements.txt`

3. **启动后台服务**：

   * 运行 `python3 backend/app.py`

   * 访问 `http://localhost:5000` 进入管理界面

4. **配置系统**：

   * 在界面中填写 API 信息、频道设置等

   * 点击 "保存配置" 按钮保存修改

5. **运行脚本**：

   * 在 "状态监控" 部分点击 "启动" 按钮运行脚本

### 3. 信息获取

* **在线获取TG session**(选择V1)： https://tgs.252035.xyz/

* **api_id和api_hash获取**：https://my.telegram.org/

github上公开的

> api_id = 2934000
> api_hash = "7407f1e353d48363c48df4c8b3904acb"
>
>
>
> api_id = '27335138'
> pi_hash = '2459555ba95421148c682e2dc3031bb6'
>
>
>
> api_id = 6627460
> api_hash = '27a53a0965e486a2bc1b1fcde473b1c4'

### 4. 代理参数说明

* **SOCKS5**

  ```python
  proxy = (socks.SOCKS5, proxy_address, proxy_port, proxy_username, proxy_password)
  ```

* **HTTP**

  ```python
  proxy = (socks.HTTP, proxy_address, proxy_port, proxy_username, proxy_password)
  ```

* **HTTP_PROXY**

  ```python
  proxy = (socks.HTTP, http_proxy_list[1][2:], int(http_proxy_list[2]), proxy_username, proxy_password)
  ```

## 使用说明

### 1. 配置管理

* 通过后台管理界面编辑配置

* 配置文件存储在 `config/config.json`

* 支持实时保存和加载

### 2. 脚本管理

* **转发脚本**：监控频道群组，转发资源到目标频道

* **链接检测脚本**：检测并处理失效的网盘链接

* 可通过后台界面一键启停

### 3. 定时运行

* **Windows**：使用任务计划程序设置定时任务

* **macOS/Linux**：使用 crontab 设置定时任务

## 常见问题

### 1. 无法连接到 Telegram API

* 检查网络连接

* 配置代理服务器

* 尝试更换网络环境

### 2. API 限制错误

* 减少请求频率

* 增加请求间隔

* 避免短时间内大量操作

### 3. 权限问题

* 确保机器人或账号已加入目标频道

* 确保账号有发送消息的权限

* 检查频道设置是否允许消息转发

### 4. 链接检测失败

* 检查网络连接

* 增加检测超时时间

* 对于 123 网盘，考虑降低检测频率

## 注意事项

1. **遵守 Telegram 规则**：不要滥用工具，遵守 Telegram 的使用条款

2. **保护账号安全**：不要分享 API 信息和 String Session

3. **合理使用**：避免过度请求，以免被 Telegram 限制

4. **定期更新**：定期检查项目更新，获取最新功能和 bug 修复

5. **备份数据**：定期备份历史记录文件，避免数据丢失

## 技术架构

* **核心脚本**：TGForwarder.py、TGNetDiskLinkChecker.py

* **配置系统**：config/config.py

* **后台管理**：基于 Flask 框架

* **前端界面**：使用 Bootstrap 构建

## 原项目地址

[https://github.com/fish2018/TGForwarder](https://github.com/fish2018/TGForwarder)

## 原作者

fish2018
