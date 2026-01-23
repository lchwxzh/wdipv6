import requests
import re
from collections import defaultdict
import time
import random

# -------------------------
# 添加User-Agent和代理支持
# -------------------------
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# -------------------------
# 频道分类（更新版）
# -------------------------
CHANNEL_CATEGORIES = {
    "央视频道": ['CCTV1', 'CCTV2', 'CCTV3', 'CCTV4', 'CCTV4欧洲', 'CCTV4美洲', 'CCTV5', 'CCTV5+', 'CCTV6', 'CCTV7', 'CCTV8', 'CCTV9',
                 'CCTV10', 'CCTV11', 'CCTV12', 'CCTV13', 'CCTV14', 'CCTV15', 'CCTV16', 'CCTV17', '兵器科技', '风云音乐', '风云足球',
                 '风云剧场', '怀旧剧场', '第一剧场', '女性时尚', '世界地理', '央视台球', '高尔夫网球', '央视文化精品', '卫生健康', '电视指南'],
    "卫视频道": ['湖南卫视', '浙江卫视', '江苏卫视', '东方卫视', '深圳卫视', '北京卫视', '广东卫视', '广西卫视', '东南卫视', '海南卫视',
                 '河北卫视', '河南卫视', '湖北卫视', '江西卫视', '四川卫视', '重庆卫视', '贵州卫视', '云南卫视', '天津卫视', '安徽卫视',
                 '山东卫视', '辽宁卫视', '黑龙江卫视', '吉林卫视', '内蒙古卫视', '宁夏卫视', '山西卫视', '陕西卫视', '甘肃卫视',
                 '青海卫视', '新疆卫视', '西藏卫视', '三沙卫视', '厦门卫视', '兵团卫视', '延边卫视', '安多卫视', '康巴卫视', '农林卫视', '山东教育',
                 'CETV1', 'CETV2', 'CETV3', 'CETV4', '早期教育'],
    "数字频道": ['CHC动作电影', 'CHC家庭影院', 'CHC影迷电影', '淘电影', '淘精彩', '淘剧场', '淘4K', '淘娱乐', '淘Baby', '萌宠TV', '北京纪实科教', '重温经典',
                 '星空卫视', 'CHANNEL[V]', '凤凰中文', '凤凰资讯', '凤凰香港', '凤凰电影', '求索纪录', '求索科学', '求索生活', '求索动物',
                 '睛彩青少', '睛彩竞技', '睛彩篮球', '睛彩广场舞', '金鹰纪实', '快乐垂钓', '茶频道', '天元围棋', '魅力足球', '五星体育', '劲爆体育',
                 '乐游', '生活时尚', '都市剧场', '欢笑剧场', '游戏风云', '动漫秀场', '金色学堂', '法治天地', '哒啎赛事', '哒啎电竞', '黑莓电影', '黑莓动画', 
                 '卡酷少儿', '金鹰卡通', '优漫卡通', '哈哈炫动', '嘉佳卡通', 'iHOT爱喜剧', 'iHOT爱科幻', 'iHOT爱院线', 'iHOT爱悬疑',
                 'iHOT爱历史', 'iHOT爱谍战', 'iHOT爱旅行', 'iHOT爱幼教', 'iHOT爱玩具', 'iHOT爱体育', 'iHOT爱赛车', 'iHOT爱浪漫', 'iHOT爱奇谈',
                 'iHOT爱科学', 'iHOT爱动漫', '东北热剧', '中国功夫', '动作电影', '军事评论', '军旅剧场', '魅力潇湘',
                 '古装剧场', '家庭剧场', '惊悚悬疑', '明星大片', '欢乐剧场', '海外剧场', '潮妈辣婆', '爱情喜剧',
                 '炫舞未来', '精品体育', '精品大剧', '精品纪录', '精品萌宠', '超级体育', '超级电影', '怡伴健康',
                 '超级电视剧', '超级综艺', '金牌综艺', '武搏世界', '农业致富'],
    "山西频道": ['山西卫视', '山西黄河HD', '山西经济与科技HD', '山西影视HD', '山西社会与法治HD', '山西文体生活HD'],
}

# -------------------------
# 增强的频道映射
# -------------------------
CHANNEL_MAPPING = {
    "CCTV1": ["CCTV-1", "CCTV-1 HD", "CCTV-1 综合", "CCTV1 HD", "CCTV1高清", "CCTV-1高清", "中央一套"],
    "CCTV2": ["CCTV-2", "CCTV-2 HD", "CCTV-2 财经", "CCTV2 HD", "CCTV2高清", "中央二套"],
    "CCTV3": ["CCTV-3", "CCTV-3 HD", "CCTV-3 综艺", "CCTV3 HD", "CCTV3高清", "中央三套"],
    "CCTV4": ["CCTV-4", "CCTV-4 HD", "CCTV4a", "CCTV4A", "CCTV-4 中文国际", "CCTV4 HD", "中央四套"],
    "CCTV5": ["CCTV-5", "CCTV-5 HD", "CCTV-5 体育", "CCTV5 HD", "CCTV5高清", "中央五套"],
    "CCTV5+": ["CCTV-5+", "CCTV-5+ HD", "CCTV-5+ 体育赛事", "CCTV5+ HD"],
    "CCTV6": ["CCTV-6", "CCTV-6 HD", "CCTV-6 电影", "CCTV6 HD", "中央六套"],
    "CCTV7": ["CCTV-7", "CCTV-7 HD", "CCTV-7 国防军事", "CCTV7 HD", "中央七套"],
    "CCTV8": ["CCTV-8", "CCTV-8 HD", "CCTV-8 电视剧", "CCTV8 HD", "中央八套"],
    "CCTV9": ["CCTV-9", "CCTV-9 HD", "CCTV-9 纪录", "CCTV9 HD"],
    "CCTV10": ["CCTV-10", "CCTV-10 HD", "CCTV-10 科教", "CCTV10 HD", "中央十套"],
    "CCTV11": ["CCTV-11", "CCTV-11 HD", "CCTV-11 戏曲", "CCTV11 HD"],
    "CCTV12": ["CCTV-12", "CCTV-12 HD", "CCTV-12 社会与法", "CCTV12 HD"],
    "CCTV13": ["CCTV-13", "CCTV-13 HD", "CCTV-13 新闻", "CCTV13 HD", "新闻频道"],
    "CCTV14": ["CCTV-14", "CCTV-14 HD", "CCTV-14 少儿", "CCTV14 HD", "少儿频道"],
    "CCTV15": ["CCTV-15", "CCTV-15 HD", "CCTV-15 音乐", "CCTV15 HD", "音乐频道"],
    "CCTV16": ["CCTV-16", "CCTV-16 HD", "CCTV-16 奥林匹克", "CCTV16 4K", "CCTV16奥林匹克 4K", "CCTV16 HD", "奥林匹克频道"],
    "CCTV17": ["CCTV-17", "CCTV-17 HD", "CCTV-17 农业农村", "CCTV17 HD", "农业农村频道"],
    # 添加更多映射...
}

# -------------------------
# 改进的正则表达式
# -------------------------
ipv6_regex = r"http://\[[0-9a-fA-F:]+\](?::\d+)?/.+"  # 增强的IPv6匹配
m3u_channel_regex = r'tvg-name="([^"]+)"'

def normalize_channel_name(name: str) -> str:
    """根据别名映射表统一频道名称"""
    # 先清理常见的前缀后缀
    name = name.strip()
    name = re.sub(r'\(.*?\)', '', name)  # 移除括号内容
    name = re.sub(r'\s*HD\s*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*高清\s*$', '', name)
    name = re.sub(r'\s*4K\s*$', '', name, flags=re.IGNORECASE)
    
    for standard, aliases in CHANNEL_MAPPING.items():
        if name.lower() == standard.lower():
            return standard
        for alias in aliases:
            if name.lower() == alias.lower():
                return standard
    return name

def is_invalid_url(url: str) -> bool:
    """检查是否为无效 URL"""
    invalid_patterns = [
        r"ottrrs\.hl\.chinamobile\.com",  # 黑龙江移动
        r"2409:8087:1a01:df::7005",  # 特定IPv6地址
        r"\.m3u8?$",  # m3u8链接（如果需要过滤）
    ]
    
    for pattern in invalid_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    return False

# -------------------------
# 改进的抓取函数
# -------------------------
def fetch_lines(url: str, retry=3):
    """下载并分行返回内容，支持重试"""
    for attempt in range(retry):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.encoding = "utf-8"
            
            if resp.status_code == 200:
                return resp.text.splitlines()
            else:
                print(f"⚠️ 请求失败 {url}: HTTP {resp.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ 超时 {url}，尝试 {attempt + 1}/{retry}")
        except requests.exceptions.ConnectionError:
            print(f"🔌 连接错误 {url}，尝试 {attempt + 1}/{retry}")
        except Exception as e:
            print(f"❌ 错误 {url}: {e}")
        
        if attempt < retry - 1:
            time.sleep(random.uniform(1, 3))  # 随机等待
    
    return []

# -------------------------
# 改进的解析函数
# -------------------------
def parse_lines(lines):
    """解析 M3U 或 TXT 内容，返回 {频道名: [url列表]}"""
    channels_dict = defaultdict(list)
    current_name = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith("#EXTM3U"):
            continue
        
        # M3U #EXTINF 格式
        if line.startswith("#EXTINF"):
            # 提取频道名
            name_match = re.search(m3u_channel_regex, line)
            if name_match:
                current_name = name_match.group(1)
            elif "," in line:
                current_name = line.split(",", 1)[-1].strip()
            
            # 获取URL
            if current_name and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not next_line.startswith("#"):
                    url = next_line.split("#")[0].split("$")[0].strip()
                    if re.match(ipv6_regex, url) and not is_invalid_url(url):
                        norm_name = normalize_channel_name(current_name)
                        if norm_name:  # 确保名称不为空
                            channels_dict[norm_name].append(url)
            
            current_name = None
        
        # TXT 格式: 频道名,URL
        elif "," in line and "://" in line:
            try:
                parts = line.split(",", 1)
                if len(parts) == 2:
                    ch_name, url = parts[0].strip(), parts[1].strip()
                    url = url.split("#")[0].split("$")[0].strip()
                    
                    if re.match(ipv6_regex, url) and not is_invalid_url(url):
                        norm_name = normalize_channel_name(ch_name)
                        if norm_name:
                            channels_dict[norm_name].append(url)
            except:
                continue
    
    return channels_dict

# -------------------------
# 生成M3U文件
# -------------------------
def create_m3u_file(all_channels, filename="ipv6.m3u"):
    """生成带分类的 M3U 文件"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write('#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml"\n')
        f.write('#EXTM3U url-tvg="http://epg.51zmt.top:8000/e.xml"\n\n')
        
        channel_count = 0
        url_count = 0
        
        for group, channel_list in CHANNEL_CATEGORIES.items():
            for ch in channel_list:
                if ch in all_channels and all_channels[ch]:
                    unique_urls = list(dict.fromkeys(all_channels[ch]))
                    logo = f"https://live.fanmingming.com/tv/{ch}.png"
                    
                    f.write(f'#EXTINF:-1 tvg-id="{ch}" tvg-name="{ch}" tvg-logo="{logo}" group-title="{group}",{ch}\n')
                    for url in unique_urls:
                        f.write(f"{url}\n")
                        url_count += 1
                    
                    channel_count += 1
        
        print(f"📊 统计: {channel_count}个频道，{url_count}个直播源")
        return channel_count

# -------------------------
# 主函数
# -------------------------
def main():
    # 可用的IPv6直播源列表（可以添加更多）
    urls = [
        "https://raw.githubusercontent.com/kakaxi-1/IPTV/main/ipv6.m3u",
        "https://raw.githubusercontent.com/SPX372928/MyIPTV/master/直播源/ipv6.txt",
        "https://raw.githubusercontent.com/YanG-1989/m3u/main/Gather.m3u",
        "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    ]
    
    all_channels = defaultdict(list)
    
    print("🌐 开始抓取直播源...")
    for i, url in enumerate(urls, 1):
        print(f"\n📡 正在处理源 {i}/{len(urls)}: {url}")
        lines = fetch_lines(url)
        if lines:
            parsed = parse_lines(lines)
            for ch, urls_list in parsed.items():
                all_channels[ch].extend(urls_list)
            print(f"   ✅ 获取到 {len(parsed)} 个频道")
        else:
            print(f"   ❌ 无法获取内容")
    
    # 去重并过滤
    for ch in list(all_channels.keys()):
        unique_urls = list(dict.fromkeys(all_channels[ch]))
        # 过滤掉无效URL
        valid_urls = [url for url in unique_urls if not is_invalid_url(url)]
        if valid_urls:
            all_channels[ch] = valid_urls
        else:
            del all_channels[ch]
    
    # 生成文件
    channel_count = create_m3u_file(all_channels)
    
    if channel_count > 0:
        print(f"\n🎉 已成功生成 ipv6.m3u，包含 {channel_count} 个频道")
        print("📁 文件已保存为: ipv6.m3u")
    else:
        print("\n⚠️  没有获取到有效的直播源，请检查网络连接或源地址")

if __name__ == "__main__":
    main()
