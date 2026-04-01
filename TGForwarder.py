import os
import socks
import shutil
import requests
import random
import time
import json
import re
import asyncio
import urllib.parse
from datetime import datetime, timezone, timedelta
from telethon import TelegramClient,functions
from telethon.tl.types import MessageMediaPhoto, MessageEntityTextUrl, Channel, ChatInviteAlready, ChatInvite, PeerChannel
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetHistoryRequest, CheckChatInviteRequest, ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
from collections import deque

# 导入配置系统
from config.config import config

'''
代理参数说明:
# SOCKS5
proxy = (socks.SOCKS5,proxy_address,proxy_port,proxy_username,proxy_password)
# HTTP
proxy = (socks.HTTP,proxy_address,proxy_port,proxy_username,proxy_password))
# HTTP_PROXY
proxy=(socks.HTTP,http_proxy_list[1][2:],int(http_proxy_list[2]),proxy_username,proxy_password)
'''

if os.environ.get("HTTP_PROXY"):
    http_proxy_list = os.environ["HTTP_PROXY"].split(":")


class TGForwarder:
    def __init__(self, config):
        self.urls_kw = ['ed2k','magnet', 'drive.uc.cn', 'caiyun.139.com', 'cloud.189.cn', 'pan.quark.cn', '115cdn.com','115.com', 'anxia.com', 'alipan.com', 'aliyundrive.com','pan.baidu.com','mypikpak.com','123684.com','123685.com','123912.com','123pan.com','123pan.cn','123592.com']
        self.checkbox = {"links":[],"sizes":[],"bot_links":{},"reply_links":{},"chat_forward_count_msg_id":{},"today":"","today_count":0}
        self.checknum = config.get('checknum', 50)
        self.today_count = 0
        self.history = 'history.json'
        # 正则表达式匹配资源链接
        self.pattern = r'''
            (?:链接：\s*)?                       # 可选的"链接："前缀
            (?!https?://t\.me)                  # 排除电报链接
            (?!https?://image\.tmdb\.org)       # 排除TMDB图片链接
            (
              # 磁力链接
              magnet:\?xt=urn:btih:[a-zA-Z0-9]+|
            
              # ed2k链接 - 修复没有结尾斜杠的情况
              ed2k://\|file\|[^|]+\|\d+\|[A-Fa-f0-9]+\|/?|
            
              # 所有网盘共享链接 - 通用格式
              https?://(?:[\w.-]+\.)+[\w]+       # 任何域名
              (?:
                /(?:s|share|m/i|t|web/share)    # 常见路径模式
                (?:/[\w.-]+)*                    # 可能的路径部分
                (?:\?(?:[\w]+=[\w:]+&?)*)?       # 可能的查询参数，允许冒号作为值的一部分
                [^\s'"<>()]+                     # 捕获剩余部分但排除一些常见终止符
              )
            )
            '''
        self.api_id = config.get('api_id', 6627460)
        self.api_hash = config.get('api_hash', '27a53a0965e486a2bc1b1fcde473b1c4')
        self.string_session = config.get('string_session', '')
        self.channels_groups_monitor = config.get('channels_groups_monitor', [])
        self.forward_to_channel = config.get('forward_to_channel', '')
        self.limit = config.get('limit', 20)
        self.replies_limit = config.get('replies_limit', 1)
        self.include = config.get('include', [])
        # 获取当前中国时区时间
        self.china_timezone_offset = timedelta(hours=8)  # 中国时区是 UTC+8
        self.today = (datetime.utcnow() + self.china_timezone_offset).date()
        # 获取当前年份
        current_year = datetime.now().year - 2
        # 过滤今年之前的影视资源
        past_years = config.get('past_years', False)
        exclude = config.get('exclude', [])
        if not past_years:
            years_list = [str(year) for year in range(1895, current_year)]
            self.exclude = exclude+years_list
        else:
            self.exclude = exclude
        self.only_today = config.get('only_today', True)
        self.hyperlink_text = config.get('hyperlink_text', {})
        self.replacements = config.get('replacements', {})
        self.message_md = config.get('message_md', '**本频道实时更新最新影视资源**')
        self.channel_match = config.get('channel_match', [])
        self.check_replies = config.get('check_replies', False)
        self.download_folder = 'downloads'
        self.try_join = config.get('try_join', False)
        self.proxy = config.get('proxy', None)
        self.client = TelegramClient(StringSession(self.string_session), self.api_id, self.api_hash, proxy=self.proxy)
    def random_wait(self, min_ms, max_ms):
        min_sec = min_ms / 1000
        max_sec = max_ms / 1000
        wait_time = random.uniform(min_sec, max_sec)
        time.sleep(wait_time)
    def contains(self, s, include):
        return any(k in s for k in include)
    def nocontains(self, s, exclude):
        return not any(k in s for k in exclude)
    def replace_targets(self, message: str):
        """
        根据用户自定义的替换规则替换文本内容
        参数:
        message (str): 需要替换的原始文本
        replacements (dict): 替换规则字典，键为目标替换词，值为要被替换的词语列表
        """
        # 遍历替换规则
        if self.replacements:
            for target_word, source_words in self.replacements.items():
                # 确保source_words是列表
                if isinstance(source_words, str):
                    source_words = [source_words]
                # 遍历每个需要替换的词
                for word in source_words:
                    # 使用替换方法，而不是正则
                    message = message.replace(word, target_word)
        message = message.strip()
        return message
    async def dispatch_channel(self, message, jumpLinks=[], F=False):
        hit = False
        if self.channel_match:
            for rule in self.channel_match:
                if rule.get('include'):
                    if not self.contains(message.message, rule['include']):
                        continue
                if rule.get('exclude'):
                    if not self.nocontains(message.message, rule['exclude']):
                        continue
                await self.send(message, rule['target'], jumpLinks, F)
                hit = True
            if not hit:
                await self.send(message, self.forward_to_channel, jumpLinks, F)
        else:
            await self.send(message, self.forward_to_channel, jumpLinks, F)
    async def send(self, message, target_chat_name, jumpLinks=[], F=False):
        text = message.message
        if jumpLinks and self.hyperlink_text:
            categorized_urls = self.categorize_urls(jumpLinks)
            # 遍历每个分类
            for category, keywords in hyperlink_text.items():
                # 获取该分类的第一个 URL（如果有）
                if categorized_urls.get(category):
                    slinks = categorized_urls[category]
                    url = "\n".join(slinks)
                    url += '\n@@'
                    # 遍历关键词并替换
                    for keyword in keywords:
                        if keyword in text:
                            text = text.replace(keyword, url)
                            break
                else:
                    continue  # 如果没有 URL，跳过
        text = text.replace('@@','')
        if self.nocontains(text, self.urls_kw):
            return
        try:
            if message.media and isinstance(message.media, MessageMediaPhoto):
                if F:
                    media = await message.download_media(self.download_folder)
                    await self.client.send_file(target_chat_name, media, caption=self.replace_targets(text))
                else:
                    await self.client.send_message(
                        target_chat_name,
                        self.replace_targets(text),  # 复制消息文本
                        file=message.media  # 复制消息的媒体文件
                    )
            else:
                await self.client.send_message(target_chat_name, self.replace_targets(text))
        except Exception as e:
            print(f'发送消息失败: {e}')
    async def get_peer(self,client, channel_name):
        peer = None
        try:
            peer = await client.get_input_entity(channel_name)
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            return peer
    async def get_all_replies(self,chat_name, message):
        '''
        获取频道消息下的评论，有些视频/资源链接被放在评论中
        '''
        offset_id = 0
        all_replies = []
        peer = await self.get_peer(self.client, chat_name)
        if peer is None:
            return []
        while True:
            try:
                replies = await self.client(functions.messages.GetRepliesRequest(
                    peer=peer,
                    msg_id=message.id,
                    offset_id=offset_id,
                    offset_date=None,
                    add_offset=0,
                    limit=100,
                    max_id=0,
                    min_id=0,
                    hash=0
                ))
                all_replies.extend(replies.messages)
                if len(replies.messages) < 100:
                    break
                offset_id = replies.messages[-1].id
            except Exception as e:
                print(f"Unexpected error while fetching replies: {chat_name} {e} {message}")
                break
        return all_replies
    async def daily_forwarded_count(self,target_channel):
        # 统计今日更新
        # 设置中国时区偏移（UTC+8）
        china_offset = timedelta(hours=8)
        china_tz = timezone(china_offset)
        # 获取中国时区的今天凌晨
        now = datetime.now(china_tz)
        start_of_day_china = datetime.combine(now.date(), datetime.min.time())
        start_of_day_china = start_of_day_china.replace(tzinfo=china_tz)
        # 转换为 UTC 时间
        start_of_day_utc = start_of_day_china.astimezone(timezone.utc)
        # 获取今天第一条消息
        result = await self.client(GetHistoryRequest(
            peer=target_channel,
            limit=1,  # 只需要获取一条消息
            offset_date=start_of_day_utc,
            offset_id=0,
            add_offset=0,
            max_id=0,
            min_id=0,
            hash=0
        ))
        # 获取第一条消息的位置
        first_message_pos = result.offset_id_offset
        # 今日消息总数就是从第一条消息到最新消息的距离
        today_count = first_message_pos if first_message_pos else 0
        msg = f'**今日共更新【{today_count}】条资源 **\n\n'
        msg = msg + self.message_md
        return msg,today_count
    async def del_channel_forward_count_msg(self):
        # 删除消息
        chat_forward_count_msg_id = self.checkbox.get("chat_forward_count_msg_id")
        if not chat_forward_count_msg_id:
            return

        forward_to_channel_message_id = chat_forward_count_msg_id.get(self.forward_to_channel)
        if forward_to_channel_message_id:
            await self.client.delete_messages(self.forward_to_channel, [forward_to_channel_message_id])

        if self.channel_match:
            for rule in self.channel_match:
                target_channel_msg_id = chat_forward_count_msg_id.get(rule['target'])
                await self.client.delete_messages(rule['target'], [target_channel_msg_id])
    async def send_daily_forwarded_count(self):
        await self.del_channel_forward_count_msg()

        chat_forward_count_msg_id = {}
        msg,tc = await self.daily_forwarded_count(self.forward_to_channel)
        sent_message = await self.client.send_message(self.forward_to_channel, msg , parse_mode='md', link_preview=False)
        self.checkbox["today_count"] = tc
        # 置顶消息
        await self.client.pin_message(self.forward_to_channel, sent_message.id)
        await self.client.delete_messages(self.forward_to_channel, [sent_message.id + 1])

        chat_forward_count_msg_id[self.forward_to_channel] = sent_message.id
        if self.channel_match:
            for rule in self.channel_match:
                m,t = await self.daily_forwarded_count(rule['target'])
                sm = await self.client.send_message(rule['target'], m)
                self.checkbox["today_count"] = self.checkbox["today_count"] + t
                chat_forward_count_msg_id[rule['target']] = sm.id
                await self.client.pin_message(rule['target'], sm.id)
                await self.client.delete_messages(rule['target'], [sm.id+1])
        self.checkbox["chat_forward_count_msg_id"] = chat_forward_count_msg_id
    async def extract_links(self, text):
        """从文本中提取各种共享链接"""
        # 使用re.VERBOSE标志允许在正则表达式中使用注释和空白
        matches = re.findall(self.pattern, text, re.VERBOSE)
        # 去除重复项
        unique_matches = []
        for match in matches:
            if match not in unique_matches:
                unique_matches.append(match)
        return unique_matches
    async def redirect_url(self, message):
        links = []
        if message.entities:
            for entity in message.entities:
                if isinstance(entity, MessageEntityTextUrl):
                    if 'start' in entity.url:
                        url = await self.tgbot(entity.url)
                        if url:
                            links.append(url)
                    elif 'https://telegra.ph/' in entity.url:
                        res = requests.get(entity.url)
                        html = res.content.decode('utf-8')
                        matches = await self.extract_links(html)
                        if matches:
                            links += matches
                    elif self.nocontains(entity.url, self.urls_kw):
                        continue
                    else:
                        url = urllib.parse.unquote(entity.url)
                        matches = re.findall(self.pattern, url, re.VERBOSE)
                        if matches:
                            links += matches
        if links:
            return links
        markup = getattr(message, 'reply_markup', None)
        if markup:
            rows = getattr(markup, 'rows', [])
            for row in rows:
                buttons = getattr(row, 'buttons', [])
                for button in buttons:
                    text = getattr(button, 'text', '')
                    tgboturl = getattr(button, 'url', None)
                    if text and self.contains(text, include) and tgboturl:
                        if 'https://telegra.ph/' in tgboturl:
                            res = requests.get(tgboturl)
                            html = res.content.decode('utf-8')
                            matches = await self.extract_links(html)
                            if matches:
                                links += matches
                            break
                        else:
                            url = await self.tgbot(tgboturl)
                            if url:
                                links.append(url)
                                break
                else:
                    continue
                break
        return links
    async def send_reply(self,message,chat_name):
        links = []
        reply_links = self.checkbox["reply_links"]
        link = reply_links.get(f'{chat_name}-{message.id}')
        if link:
            links.append(link)
        else:
            try:
                text = re.search(r'\((【\d+】[^)]+)\)', message.message).group(1)
                from telethon.tl.types import PeerChannel
                discussion_peer = PeerChannel(message.peer_id.channel_id)
                await self.client.send_message(discussion_peer, text, comment_to=message.id)
                # 等待回复
                await asyncio.sleep(2)
                async for reply in self.client.iter_messages(discussion_peer, limit=2, reply_to=message.id):
                        matches = re.findall(self.pattern, reply.message, re.VERBOSE)
                        if matches:
                            links = matches
                            link = links[0]
                            reply_links[f'{chat_name}-{message.id}'] = link
                            self.checkbox["reply_links"] = reply_links
            except Exception as e:
                print(f'{chat_name} {message.id}: {e}')
        return links
    async def tgbot(self,url):
        link = ''
        try:
            # 发送 /start 命令，带上自定义参数
            if 'tg://' in url:
                # 提取机器人用户名
                bot_username = url.split('domain=')[1].split('&')[0]
                # 提取命令和参数
                command = 'start'
                parameter = url.split('start=')[1]
            else:
                # 提取机器人用户名
                bot_username = url.split('/')[-1].split('?')[0]
                # 提取命令和参数
                query_string = url.split('?')[1]
                command, parameter = query_string.split('=')
            bot_links = self.checkbox["bot_links"]

            if bot_links.get(parameter):
                link = bot_links.get(parameter)
                return link
            else:
                # print(11111,bot_username,f'/{command} {parameter}')
                await self.client.send_message(bot_username, f'/{command} {parameter}')
                # 等待一段时间以便消息到达
                await asyncio.sleep(2)
                # 获取最近的消息
                messages = await self.client.get_messages(bot_username, limit=1)  # 获取最近1条消息
                # print(f'消息内容: {messages[0].message}')
                message = messages[0].message
                links = re.findall(r'(https?://[^\s]+)', message)
                if links:
                    link = links[0]
                    bot_links[parameter] = link
                    self.checkbox["bot_links"] = bot_links
        except Exception as e:
            print(f'TG_Bot error: {e}')
        return link
    async def reverse_async_iter(self, async_iter, limit):
        # 使用 deque 存储消息，方便从尾部添加
        buffer = deque(maxlen=limit)

        # 将消息填充到 buffer 中
        async for message in async_iter:
            buffer.append(message)

        # 从 buffer 的尾部开始逆序迭代
        for message in reversed(buffer):
            yield message
    async def delete_messages_in_time_range(self, chat_name, start_time_str, end_time_str):
        """
        删除指定聊天中在指定时间范围内的消息
        :param chat_name: 聊天名称或ID
        :param start_time_str: 开始时间字符串，格式为 "YYYY-MM-DD HH:MM"
        :param end_time_str: 结束时间字符串，格式为 "YYYY-MM-DD HH:MM"
        """
        # 中国时区偏移量（UTC+8）
        china_timezone_offset = timedelta(hours=8)
        china_timezone = timezone(china_timezone_offset)
        # 将字符串时间解析为带有时区信息的 datetime 对象
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M").replace(tzinfo=china_timezone)
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M").replace(tzinfo=china_timezone)
        # 获取聊天实体
        chat = await self.client.get_entity(chat_name)
        # 遍历消息
        async for message in self.client.iter_messages(chat):
            # 将消息时间转换为中国时区
            message_china_time = message.date.astimezone(china_timezone)
            # 判断消息是否在目标时间范围内
            if start_time <= message_china_time <= end_time:
                # print(f"删除消息：{message.text} (时间：{message_china_time})")
                await message.delete()  # 删除消息
    async def clear_main(self, start_time, end_time):
        await self.delete_messages_in_time_range(self.forward_to_channel, start_time, end_time)
    def clear(self):
        start_time = "2025-01-08 23:55"
        end_time = "2025-01-09 08:00"
        with self.client.start():
            self.client.loop.run_until_complete(self.clear_main(start_time, end_time))
    def categorize_urls(self,urls):
        """
        将 URL 按云盘厂商和磁力链接分类并存储到字典中
        """
        # 定义分类规则
        categories = {
            "magnet": ["magnet"],  # 磁力链接
            "ed2k": ["ed2k"], # ed2k
            "uc": ["drive.uc.cn"],  # UC
            "mobile": ["caiyun.139.com"],  # 移动
            "tianyi": ["cloud.189.cn"],  # 天翼
            "quark": ["pan.quark.cn"],  # 夸克
            "115": ["115cdn.com","115.com", "anxia.com"],  # 115
            "aliyun": ["alipan.com", "aliyundrive.com"],  # 阿里云
            "pikpak": ["mypikpak.com"],
            "baidu": ["pan.baidu.com"],
            "123": ['123684.com','123685.com','123912.com','123pan.com','123pan.cn','123592.com'],
            "others": []  # 其他
        }
        # 初始化结果字典
        result = {category: [] for category in categories}
        # 遍历 URL 列表
        for url in urls:
            # 处理磁力链接
            if url.startswith("magnet:"):
                result["magnet"].append(url)
                continue
            # ed2k
            elif url.startswith("ed2k:"):
                result["ed2k"].append(url)
                continue
            # 解析 URL
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc.lower()  # 获取域名并转换为小写
            # 判断 URL 类型
            categorized = False
            for category, domains in categories.items():
                if any(pattern in domain for pattern in domains):
                    result[category].append(url)
                    categorized = True
                    break
            # 如果未分类，放入 "others"
            if not categorized:
                result["others"].append(url)
        return result
    async def deduplicate_links(self,links=[]):
        """
        删除聊天中重复链接的旧消息，只保留最新的消息
        """
        # 将 links 列表转换为集合，方便快速查找
        target_links = set(self.checkbox['links']) if not links else links
        if not target_links:
            return 
        chats = [self.forward_to_channel]
        if self.channel_match:
            for rule in self.channel_match:
                chats.append(rule['target'])
        for chat_name in chats:
            # 已经存在的link
            links_exist = set()
            # 用于批量删除的消息ID列表
            messages_to_delete = []
            # 获取聊天实体
            chat = await self.client.get_entity(chat_name)
            # 遍历消息
            messages = self.client.iter_messages(chat)
            async for message in messages:
                if message.message:
                    # 提取消息中的链接
                    links_in_message = re.findall(self.pattern, message.message, re.VERBOSE)
                    if not links_in_message:
                        continue  # 如果消息中没有链接，跳过
                    link = links_in_message[0]
                    # 检查消息中的链接是否在目标链接列表中
                    if link in target_links:  # 只处理目标链接
                        if link in links_exist:
                            messages_to_delete.append(message.id)
                        else:
                            links_exist.add(link)
            # 批量删除旧消息
            if messages_to_delete:
                print(f"【{chat_name}】删除 {len(messages_to_delete)} 条历史重复消息")
                await self.client.delete_messages(chat, messages_to_delete)
    async def checkhistory(self):
        '''
        检索历史消息用于过滤去重
        '''
        links = []
        sizes = []
        if os.path.exists(self.history):
            with open(self.history, 'r', encoding='utf-8') as f:
                self.checkbox = json.loads(f.read())
                if self.checkbox.get('today') == datetime.now().strftime("%Y-%m-%d"):
                    links = self.checkbox['links']
                    sizes = self.checkbox['sizes']
                else:
                    self.checkbox['links'] = []
                    self.checkbox['sizes'] = []
                    self.checkbox["bot_links"] = {}
                    self.checkbox["today_count"] = 0
                self.today_count = self.checkbox.get('today_count') if self.checkbox.get('today_count') else self.checknum
        self.checknum = self.checknum if self.today_count < self.checknum else self.today_count
        chat = await self.client.get_entity(self.forward_to_channel)
        messages = self.client.iter_messages(chat, limit=self.checknum)
        async for message in messages:
            # 视频类型对比大小
            if hasattr(message.document, 'mime_type'):
                sizes.append(message.document.size)
            # 匹配出链接
            if message.message:
                matches = re.findall(self.pattern, message.message, re.VERBOSE)
                if matches:
                    links.append(matches[0])
        links = list(set(links))
        sizes = list(set(sizes))
        return links,sizes
    async def copy_and_send_message(self, source_chat, target_chat, message_id, text=''):
        """
        复制消息内容并发送新消息
        :param source_chat: 源聊天（可以是用户名、ID 或输入实体）
        :param target_chat: 目标聊天（可以是用户名、ID 或输入实体）
        :param message_id: 要复制的消息 ID
        """
        try:
            # 获取原始消息
            message = await self.client.get_messages(source_chat, ids=message_id)
            if not message:
                print("未找到消息")
                return

            # 发送新消息（复制原始消息内容和媒体文件）
            await self.client.send_message(
                target_chat,
                text,  # 复制消息文本
                file=message.media  # 复制消息的媒体文件
            )
            # print("消息复制并发送成功")
        except Exception as e:
            print(f"操作失败: {e}")
    async def forward_messages(self, chat_name, limit, hlinks, hsizes, reply=False, reply_limit=None):
        global total
        links = hlinks
        sizes = hsizes
        F = False
        print(f'当前监控频道【{chat_name}】，本次检测最近【{len(links)}】条历史资源进行去重')
        try:
            chat = None
            if 'https://t.me/' in chat_name:
                invite_hash = chat_name.split("/")[-1].lstrip("+")
                try:
                    invite = await self.client(CheckChatInviteRequest(invite_hash))
                    chat = invite.chat
                except Exception as e:
                    print(f"检查邀请链接失败: {e}")
            else:
                chat = await self.client.get_entity(chat_name)
                F = chat.noforwards
            messages = self.client.iter_messages(chat, limit=limit, reverse=False)
            async for message in self.reverse_async_iter(messages, limit=limit):
                # print('bbb', message)
                if self.only_today:
                    # 将消息时间转换为中国时区
                    message_china_time = message.date + self.china_timezone_offset
                    # 判断消息日期是否是当天
                    if message_china_time.date() != self.today:
                        continue
                self.random_wait(200, 1000)
                if message.media:
                    # 视频
                    if hasattr(message.document, 'mime_type') and self.contains(message.document.mime_type,'video') and self.nocontains(message.message, self.exclude):
                        size = message.document.size
                        text = message.message
                        if message.message:
                            jumpLinks = await self.redirect_url(message)
                            if jumpLinks and self.hyperlink_text:
                                categorized_urls = self.categorize_urls(jumpLinks)
                                # 遍历每个分类
                                for category, keywords in hyperlink_text.items():
                                    # 获取该分类的第一个 URL（如果有）
                                    if categorized_urls.get(category):
                                        url = categorized_urls[category][0]  # 使用第一个 URL
                                    else:
                                        continue  # 如果没有 URL，跳过
                                    # 遍历关键词并替换
                                    for keyword in keywords:
                                        if keyword in text:
                                            text = text.replace(keyword, url)
                        if size not in sizes:
                            await self.copy_and_send_message(chat_name,self.forward_to_channel,message.id,text)
                            sizes.append(size)
                            total += 1
                        else:
                            print(f'视频已经存在，size: {size}')
                    # 图文(匹配关键词)
                    elif self.contains(message.message, self.include) and message.message and self.nocontains(message.message, self.exclude):
                        jumpLinks = await self.redirect_url(message)
                        if not jumpLinks and self.contains(message.message, ['💡 评论区评论']):
                            jumpLinks = await self.send_reply(message,chat_name)
                        matches = re.findall(self.pattern, message.message, re.VERBOSE) if self.contains(message.message, self.urls_kw) else []
                        if matches or jumpLinks:
                            link = jumpLinks[0] if jumpLinks else matches[0]
                            if link not in links:
                                await self.dispatch_channel(message, jumpLinks, F)
                                total += 1
                                links.append(link)
                            else:
                                print(f'链接已存在，link: {link}')
                    # 资源被放到评论中，图文(不含关键词)
                    if (self.check_replies or reply) and message.message:
                        replies = await self.get_all_replies(chat_name,message)
                        replies = replies[-reply_limit:] if reply_limit else replies[-self.replies_limit:]
                        for r in replies:
                            jumpLinks = await self.redirect_url(r)
                            matches = re.findall(self.pattern, r.message, re.VERBOSE) if self.contains(r.message, self.urls_kw) else []
                            if matches or jumpLinks:
                                link = jumpLinks[0] if jumpLinks else matches[0]
                                if link not in links:
                                    await self.dispatch_channel(r, jumpLinks, F)
                                    total += 1
                                    links.append(link)
                                else:
                                    print(f'链接已存在，link: {link}')
                # 纯文本消息
                elif message.message:
                    if self.contains(message.message, self.include) and self.nocontains(message.message, self.exclude):
                        jumpLinks = await self.redirect_url(message)
                        if not jumpLinks and self.contains(message.message, ['💡 评论区评论']):
                            jumpLinks = await self.send_reply(message,chat_name)
                        matches = re.findall(self.pattern, message.message, re.VERBOSE) if self.contains(message.message, self.urls_kw) else []
                        if matches or jumpLinks:
                            link = jumpLinks[0] if jumpLinks else matches[0]
                            if link not in links:
                                await self.dispatch_channel(message, jumpLinks)
                                total += 1
                                links.append(link)
                            else:
                                print(f'链接已存在，link: {link}')
            print(f"从 {chat_name} 转发资源 成功: {total}")
            return list(set(links)), list(set(sizes))
        except Exception as e:
            print(f"从 {chat_name} 转发资源 失败: {e}")
    async def main(self):
        reply = False
        reply_limit = None
        start_time = time.time()
        links,sizes = await self.checkhistory()
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
        for chat_name in self.channels_groups_monitor:
            limit = self.limit
            if '|' in chat_name:
                limit = chat_name.split('|')[1]
                chat_name = chat_name.split('|')[0]
                if 'reply_' in limit:
                    reply = True
                    reply_limit = int(limit.split('_')[1])
                    limit = int(limit.split('_')[2]) if len(limit.split('_'))==3 else self.limit
                limit = int(limit)

            global total
            total = 0
            try:
                links, sizes = await self.forward_messages(chat_name, limit, links, sizes, reply, reply_limit)
            except Exception as e:
                continue
        await self.send_daily_forwarded_count()
        with open(self.history, 'w+', encoding='utf-8') as f:
            self.checkbox['links'] = list(set(links))[-self.checkbox["today_count"]:]
            self.checkbox['sizes'] = list(set(sizes))[-self.checkbox["today_count"]:]
            self.checkbox['today'] = datetime.now().strftime("%Y-%m-%d")
            f.write(json.dumps(self.checkbox))
        # 调用函数，删除重复链接的旧消息
        if os.path.exists(self.download_folder):
            shutil.rmtree(self.download_folder)
        await self.deduplicate_links()
        await self.client.disconnect()
        end_time = time.time()
        print(f'耗时: {end_time - start_time} 秒')
    def run(self):
        with self.client.start():
            if self.try_join:
                self.client.loop.run_until_complete(self.join_channels())
            self.client.loop.run_until_complete(self.main())

    async def join_channels(self):
        for channel in channels_groups_monitor:
            if '|' in channel:
                channel = channel.split('|')[0]
            if 'https://t.me/' in channel:
                # 提取邀请链接中的 hash
                invite_hash = channel.split("/")[-1].lstrip("+")
                # 检查邀请链接信息
                try:
                    invite = await self.client(CheckChatInviteRequest(invite_hash))
                except Exception as e:
                    print(f"检查邀请链接失败: {e}")
                    return None
                # 检查是否为 ChatInviteAlready（已加入）
                if isinstance(invite, ChatInviteAlready):
                    chat = invite.chat
                    if isinstance(chat, Channel):
                        channel_id = chat.id
                        full_channel_id = f"-100{channel_id}"  # 私有频道 ID 格式
                        print(f"{channel} 频道名称: {chat.title}, channel_id: {channel_id} 完整 ID: {full_channel_id}")
                        return full_channel_id
                    else:
                        print("chat 对象不是 Channel 类型")
                        return None
                # 未加入频道
                elif isinstance(invite, ChatInvite):
                    if getattr(invite, "channel", False) and getattr(invite, "broadcast", False):
                        print(f"未加入的私有频道，标题: {invite.title}")
                        try:
                            # 加入频道
                            result = await self.client(ImportChatInviteRequest(invite_hash))
                            print(f"加入结果: {result}")

                            # 从加入结果中提取频道信息
                            if hasattr(result, "chats") and result.chats:
                                chat = result.chats[0]  # 第一个 chat 对象是目标频道
                                if isinstance(chat, Channel):
                                    channel_id = chat.id
                                    full_channel_id = f"-100{channel_id}"
                                    print(f"{channel} 频道名称: {chat.title} channel_id: {channel_id} 完整 ID: {full_channel_id}")
                                    return full_channel_id
                                else:
                                    print("加入后未找到 Channel 对象")
                                    return None
                            else:
                                print("加入后未返回频道信息")
                                return None
                        except Exception as e:
                            print(f"加入频道失败: {e}")
                            return None
                    else:
                        print("这不是一个私有频道邀请链接，或无权限")
                        return None
                else:
                    print("尚未加入频道，或返回的不是 ChatInviteAlready")
                    return None
            else:
                try:
                    await self.client(JoinChannelRequest(channel))
                    print(f"成功加入频道/群组: {channel}")
                except Exception as e:
                    print(f"加入频道/群组失败: {channel}, 错误: {e}")

    def run_join(self):
        with self.client.start():
            self.client.loop.run_until_complete(self.join_channels())


if __name__ == '__main__':
    # 使用配置系统
    TGForwarder(config).run()







