import requests
import re
from collections import defaultdict
import time

# -------------------------
# 频道分类（正规区域）
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
                 '乐游', '生活时尚', '都市剧场', '欢笑剧场', '游戏风云', '动漫秀场', '金色学堂', '法治天地', '哒啵赛事', '哒啵电竞', '黑莓电影', '黑莓动画', 
                 '卡酷少儿', '金鹰卡通', '优漫卡通', '哈哈炫动', '嘉佳卡通', 'iHOT爱喜剧', 'iHOT爱科幻', 'iHOT爱院线', 'iHOT爱悬疑',
                 'iHOT爱历史', 'iHOT爱谍战', 'iHOT爱旅行', 'iHOT爱幼教', 'iHOT爱玩具', 'iHOT爱体育', 'iHOT爱赛车', 'iHOT爱浪漫', 'iHOT爱奇谈',
                 'iHOT爱科学', 'iHOT爱动漫', '东北热剧', '中国功夫', '动作电影', '军事评论', '军旅剧场', '魅力潇湘',
                 '古装剧场', '家庭剧场', '惊悚悬疑', '明星大片', '欢乐剧场', '海外剧场', '潮妈辣婆', '爱情喜剧',
                 '炫舞未来', '精品体育', '精品大剧', '精品纪录', '精品萌宠', '超级体育', '超级电影', '怡伴健康',
                 '超级电视剧', '超级综艺', '金牌综艺', '武搏世界', '农业致富'],
    "山西频道": ['山西卫视', '山西黄河HD', '山西经济与科技HD', '山西影视HD', '山西社会与法治HD', '山西文体生活HD'],
}

# -------------------------
# 频道映射（别名 -> 规范名）
# -------------------------
CHANNEL_MAPPING = {
    "CCTV1": ["CCTV-1", "CCTV-1 HD", "CCTV-1 综合", "CCTV1 HD", "CCTV 1", "CCTV-1 高清"],
    "CCTV2": ["CCTV-2", "CCTV-2 HD", "CCTV-2 财经", "CCTV2 HD", "CCTV 2", "CCTV-2 高清"],
    "CCTV3": ["CCTV-3", "CCTV-3 HD", "CCTV-3 综艺", "CCTV3 HD", "CCTV 3", "CCTV-3 高清"],
    "CCTV4": ["CCTV-4", "CCTV-4 HD", "CCTV4a", "CCTV4A", "CCTV-4 中文国际", "CCTV4 高清"],
    "CCTV4欧洲": ["CCTV-4欧洲", "CCTV-4欧洲 HD", "CCTV-4 欧洲", "CCTV4o", "CCTV4O", "CCTV-4 中文欧洲", "CCTV4中文欧洲"],
    "CCTV4美洲": ["CCTV-4美洲", "CCTV-4美洲 HD", "CCTV-4 美洲", "CCTV4m", "CCTV4M", "CCTV-4 中文美洲", "CCTV4中文美洲"],
    "CCTV5": ["CCTV-5", "CCTV-5 HD", "CCTV-5 体育", "CCTV5 HD", "CCTV 5", "CCTV-5 高清"],
    "CCTV5+": ["CCTV-5+", "CCTV-5+ HD", "CCTV-5+ 体育赛事", "CCTV5+ HD", "CCTV 5+"],
    "CCTV6": ["CCTV-6", "CCTV-6 HD", "CCTV-6 电影", "CCTV6 HD", "CCTV 6"],
    "CCTV7": ["CCTV-7", "CCTV-7 HD", "CCTV-7 国防军事", "CCTV7 HD", "CCTV 7"],
    "CCTV8": ["CCTV-8", "CCTV-8 HD", "CCTV-8 电视剧", "CCTV8 HD", "CCTV 8"],
    "CCTV9": ["CCTV-9", "CCTV-9 HD", "CCTV-9 纪录", "CCTV9 HD", "CCTV 9"],
    "CCTV10": ["CCTV-10", "CCTV-10 HD", "CCTV-10 科教", "CCTV10 HD", "CCTV 10"],
    "CCTV11": ["CCTV-11", "CCTV-11 HD", "CCTV-11 戏曲", "CCTV11 HD", "CCTV 11"],
    "CCTV12": ["CCTV-12", "CCTV-12 HD", "CCTV-12 社会与法", "CCTV12 HD", "CCTV 12"],
    "CCTV13": ["CCTV-13", "CCTV-13 HD", "CCTV-13 新闻", "CCTV13 HD", "CCTV 13"],
    "CCTV14": ["CCTV-14", "CCTV-14 HD", "CCTV-14 少儿", "CCTV14 HD", "CCTV 14"],
    "CCTV15": ["CCTV-15", "CCTV-15 HD", "CCTV-15 音乐", "CCTV15 HD", "CCTV 15"],
    "CCTV16": ["CCTV-16", "CCTV-16 HD", "CCTV-16 奥林匹克", "CCTV16 4K", "CCTV16奥林匹克 4K"],
    "CCTV17": ["CCTV-17", "CCTV-17 HD", "CCTV-17 农业农村", "CCTV17 HD", "CCTV 17"],
    "湖南卫视": ["湖南卫视高清", "湖南卫视 HD", "湖南卫视HD", "湖南卫视 高清"],
    "浙江卫视": ["浙江卫视高清", "浙江卫视 HD", "浙江卫视HD", "浙江卫视 高清"],
    "江苏卫视": ["江苏卫视高清", "江苏卫视 HD", "江苏卫视HD", "江苏卫视 高清"],
    "东方卫视": ["东方卫视高清", "东方卫视 HD", "东方卫视HD", "东方卫视 高清"],
    "北京卫视": ["北京卫视高清", "北京卫视 HD", "北京卫视HD", "北京卫视 高清"],
    # 其他映射保持不变...
}

# 其他映射保持不变...
# 为了保持代码简洁，这里省略了完整的映射表，你可以保留原有的CHANNEL_MAPPING

# -------------------------
# 正则表达式
# -------------------------
ipv6_regex = r"https?://\[[0-9a-fA-F:]+\]"
ipv4_regex = r"https?://[^\s]+"

def normalize_channel_name(name: str) -> str:
    """根据别名映射表统一频道名称"""
    name = re.sub(r'\s+', ' ', name.strip())  # 去除多余空格
    for standard, aliases in CHANNEL_MAPPING.items():
        if name == standard:
            return standard
        for alias in aliases:
            if alias.lower() == name.lower():
                return standard
    return name

def is_invalid_url(url: str) -> bool:
    """检查是否为无效 URL"""
    invalid_patterns = [
        r"http://\[[a-fA-F0-9:]+\](?::\d+)?/ottrrs\.hl\.chinamobile\.com/.+/.+",
        r"http://\[2409:8087:1a01:df::7005\]/.*",
        r".*\.m3u8?$",  # 排除m3u8链接（可选）
    ]
    
    for pattern in invalid_patterns:
        if re.match(pattern, url):
            return True
    return False

# -------------------------
# 抓取 URL
# -------------------------
def fetch_lines(url: str, max_retries=3):
    """下载并分行返回内容，支持重试"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for retry in range(max_retries):
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.encoding = resp.apparent_encoding or 'utf-8'
            if resp.status_code == 200:
                return resp.text.splitlines()
            else:
                print(f"⚠️  HTTP {resp.status_code} 从 {url}")
        except Exception as e:
            print(f"❌ 获取失败 {url} (尝试 {retry+1}/{max_retries}): {e}")
            if retry < max_retries - 1:
                time.sleep(2)  # 重试前等待
    return []

# -------------------------
# 解析 M3U / TXT
# -------------------------
def parse_lines(lines):
    """解析 M3U 或 TXT 内容，返回 {频道名: [url列表]}"""
    channels_dict = defaultdict(list)
    current_name = None
    group_title = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # M3U #EXTINF 格式
        if line.startswith("#EXTINF"):
            current_name = None
            group_title = None
            
            # 提取频道名
            if "," in line:
                current_name = line.split(",")[-1].strip()
            
            # 尝试从属性中提取 group-title
            match = re.search(r'group-title="([^"]+)"', line)
            if match:
                group_title = match.group(1)
            
            # 尝试提取 tvg-name
            match = re.search(r'tvg-name="([^"]+)"', line)
            if match and not current_name:
                current_name = match.group(1)
        
        # 如果是URL行且我们有频道名
        elif current_name and (line.startswith("http://") or line.startswith("https://")):
            url = line.split("$")[0].strip()  # 去掉 $ 后缀
            
            # 检查URL有效性
            if not is_invalid_url(url):
                # 优先使用tvg-name，否则使用频道名
                norm_name = normalize_channel_name(current_name)
                if norm_name:
                    channels_dict[norm_name].append({
                        'url': url,
                        'group': group_title
                    })
            current_name = None
            group_title = None
        
        # TXT 频道名,URL 格式
        elif "," in line and not line.startswith("#"):
            parts = line.split(",", 1)
            if len(parts) == 2:
                ch_name, url = parts[0].strip(), parts[1].strip()
                url = url.split("$")[0].strip()
                if not is_invalid_url(url):
                    norm_name = normalize_channel_name(ch_name)
                    if norm_name:
                        channels_dict[norm_name].append({
                            'url': url,
                            'group': None
                        })

    return channels_dict

# -------------------------
# 去重和排序URL
# -------------------------
def deduplicate_urls(url_list):
    """去重URL，保留顺序"""
    seen = set()
    unique_urls = []
    for item in url_list:
        url = item['url']
        if url not in seen:
            seen.add(url)
            unique_urls.append(item)
    return unique_urls

# -------------------------
# 生成 M3U 文件
# -------------------------
def create_m3u_file(all_channels, filename="ipv6.m3u"):
    """生成带分类的 M3U 文件，一频道多源连续写"""
    channel_count = 0
    url_count = 0
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write('#EXTM3U x-tvg-url="https://kakaxi-1.github.io/IPTV/epg.xml"\n\n')
        
        for group, channel_list in CHANNEL_CATEGORIES.items():
            for ch in channel_list:
                if ch in all_channels and all_channels[ch]:
                    # 去重 URL，保留顺序
                    unique_urls = deduplicate_urls(all_channels[ch])
                    
                    if unique_urls:
                        logo = f"https://kakaxi-1.github.io/IPTV/LOGO/{ch}.png"
                        f.write(f'#EXTINF:-1 tvg-id="{ch}" tvg-name="{ch}" tvg-logo="{logo}" group-title="{group}",{ch}\n')
                        for item in unique_urls:
                            f.write(f"{item['url']}\n")
                        f.write("\n")
                        
                        channel_count += 1
                        url_count += len(unique_urls)
    
    return channel_count, url_count

# -------------------------
# 添加备用源
# -------------------------
def get_backup_sources():
    """返回备用源列表"""
    return [
        "https://raw.githubusercontent.com/kakaxi-1/IPTV/main/ipv6.m3u",
        "https://raw.githubusercontent.com/YanG-1989/m3u/main/China.m3u",
        "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
        "https://raw.githubusercontent.com/guptaharsh1997/IPTV/main/playlist.m3u",
        # 可以添加更多源
    ]

# -------------------------
# 主函数
# -------------------------
def main():
    print("🔄 开始抓取IPTV源...")
    
    all_channels = defaultdict(list)
    sources = get_backup_sources()
    
    for idx, url in enumerate(sources, 1):
        print(f"\n📡 正在处理源 {idx}/{len(sources)}: {url}")
        lines = fetch_lines(url)
        if lines:
            parsed = parse_lines(lines)
            found_count = len(parsed)
            for ch, urls_list in parsed.items():
                all_channels[ch].extend(urls_list)
            print(f"   ✅ 找到 {found_count} 个频道")
        else:
            print("   ⚠️  未获取到数据")
    
    # 生成文件
    print("\n📝 正在生成M3U文件...")
    channel_count, url_count = create_m3u_file(all_channels, "ipv6_merged.m3u")
    
    print(f"\n✅ 完成！")
    print(f"   频道总数: {channel_count}")
    print(f"   源总数: {url_count}")
    print(f"   文件已保存为: ipv6_merged.m3u")
    
    # 显示部分频道统计
    print(f"\n📊 频道分类统计:")
    for group, channels in CHANNEL_CATEGORIES.items():
        count = sum(1 for ch in channels if ch in all_channels and all_channels[ch])
        if count > 0:
            print(f"   {group}: {count}/{len(channels)}")

if __name__ == "__main__":
    main()


