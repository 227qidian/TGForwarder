import os
import json

class Config:
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            # 默认配置
            self.config = {
                "api_id": 6627460,
                "api_hash": "27a53a0965e486a2bc1b1fcde473b1c4",
                "string_session": "",
                "channels_groups_monitor": [],
                "forward_to_channel": "",
                "limit": 20,
                "include": ["链接", "片名", "名称", "剧名", "ed2k", "magnet", "drive.uc.cn", "caiyun.139.com", "cloud.189.cn", "123684.com", "123865.com", "123912.com", "123pan.com", "123pan.cn", "123592.com", "pan.quark.cn", "115cdn.com", "115.com", "anxia.com", "alipan.com", "aliyundrive.com", "夸克云盘", "阿里云盘", "磁力链接", "Alipan", "Quark", "115", "Baidu", "获取资源", "查看资源", "💡 评论区评论", "直达链接"],
                "exclude": ["小程序", "预告", "预感", "盈利", "即可观看", "书籍", "电子书", "图书", "丛书", "期刊", "app", "软件", "破解版", "解锁", "专业版", "高级版", "最新版", "食谱", "免安装", "免广告", "安卓", "Android", "课程", "教程", "教学", "全书", "名著", "mobi", "MOBI", "epub", "任天堂", "PC", "单机游戏", "搜素", "色色", "pdf", "PDF", "PPT", "抽奖", "完整版", "读者", "文学", "写作", "节课", "套装", "话术", "纯净版", "日历", "txt", "MP3", "网赚", "mp3", "WAV", "CD", "音乐", "专辑", "模板", "书中", "读物", "入门", "零基础", "常识", "电商", "小红书", "JPG", "短视频", "工作总结", "写真", "抖音", "资料", "华为", "短剧", "纪录片", "记录片", "纪录", "纪实", "学习", "付费", "小学", "初中", "数学", "语文"],
                "hyperlink_text": {
                    "magnet": ["点击查看", "📥 点击下方按钮获取资源", "@@"],
                    "ed2k": ["点击查看", "📥 点击下方按钮获取资源", "@@"],
                    "uc": ["点击获取UC链接", "点击查看", "UC网盘", "📥 点击下方按钮获取资源", "@@"],
                    "mobile": ["点击查看", "📥 点击下方按钮获取资源", "@@"],
                    "tianyi": ["直达链接", "📥 点击下方按钮获取资源", "💡 评论区评论", "@@"],
                    "xunlei": ["点击获取迅雷链接", "直达链接", "迅雷网盘", "📥 点击下方按钮获取资源", "@@"],
                    "quark": ["点击获取夸克链接", "😀 Quark", "【夸克网盘】点击获取", "夸克云盘", "点击查看", "夸克网盘", "📥 点击下方按钮获取资源", "@@"],
                    "115": ["😀 115", "115云盘", "点击查看", "点击转存", "115网盘", "📥 点击下方按钮获取资源", "📢 频道：@Lsp115", "@@"],
                    "aliyun": ["点击获取阿里云盘链接", "😀 Alipan", "【阿里云盘】点击获取", "阿里云盘", "点击查看", "📥 点击下方按钮获取资源", "@@"],
                    "pikpak": ["PikPak云盘", "点击查看", "📥 点击下方按钮获取资源", "@@"],
                    "baidu": ["点击获取百度链接", "😀 Baidu", "【百度网盘】点击获取", "百度云盘", "点击查看", "百度网盘", "直达链接", "📥 点击下方按钮获取资源", "@@"],
                    "123": ["点击查看", "📥 点击下方按钮获取资源", "@@"],
                    "others": ["点击查看", "📥 点击下方按钮获取资源", "@@"]
                },
                "replacements": {
                    "": []
                },
                "message_md": "**本频道实时更新最新影视资源**",
                "channel_match": [],
                "try_join": False,
                "check_replies": False,
                "replies_limit": 1,
                "proxy": None,
                "checknum": 50,
                "past_years": False,
                "only_today": True,
                "link_checker": {
                    "delete_mode": 2,
                    "limit": 1000,
                    "concurrency": 20,
                    "recheck": True,
                    "net_disk_domains": ["pan.quark.cn"]
                }
            }
            self.save_config()
    
    def save_config(self):
        """保存配置文件"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get(self, key, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置值"""
        self.config[key] = value
        self.save_config()
    
    def update(self, data):
        """更新配置"""
        self.config.update(data)
        self.save_config()

# 全局配置实例
config = Config()