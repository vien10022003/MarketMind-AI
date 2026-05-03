import os
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Lấy Webhook URL từ env
# WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
WEBHOOK_URL = "https://discord.com/api/webhooks/1497549073966960723/iy-9ZG0NN_XOSVeLjZhvY53B-VxluZUqxAWJedCI-OgrmLcjEjWB4hxuA2_Y_6BbF3Cg"

def send_ad_to_discord(
    title: str,
    description: str,
    username: str = "🚀 MarketMind AI",
    avatar_url: str = "https://cdn-icons-png.flaticon.com/512/4712/4712109.png",
    content: str = "",
    thumbnail_url: str = "",
    image_url: str = "",
    color: int = 0x5865F2,
    fields: Optional[List[Dict]] = None,
    buttons: Optional[List[Dict]] = None
) -> bool:
    """
    Gửi quảng cáo lên Discord qua Webhook
    
    Args:
        title: Tiêu đề chính của embed
        description: Mô tả chi tiết
        username: Tên bot hiển thị trên Discord
        avatar_url: URL avatar của bot
        content: Nội dung text phía trên embed
        thumbnail_url: URL hình thumbnail (góc phải)
        image_url: URL hình banner (toàn bộ chiều ngang)
        color: Màu hex của embed (mặc định Discord Blurple)
        fields: Danh sách các trường thông tin dạng bảng
                Ví dụ: [{"name": "Field 1", "value": "Value 1", "inline": True}]
        buttons: Danh sách các nút bấm
                Ví dụ: [{"label": "Click", "url": "https://...", "emoji": "🎁"}]
    
    Returns:
        bool: True nếu gửi thành công, False nếu thất bại
    """
    
    if not WEBHOOK_URL:
        print("❌ Lỗi: DISCORD_WEBHOOK_URL chưa được set trong env")
        return False
    
    # Chuẩn bị fields mặc định nếu không được cung cấp
    if fields is None:
        fields = []
    
    # Chuẩn bị components (buttons) nếu được cung cấp
    components = []
    if buttons:
        button_components = []
        for btn in buttons:
            button_obj = {
                "type": 2,  # Button type
                "style": 5,  # Link button style
                "label": btn.get("label", "Click"),
                "url": btn.get("url", "https://example.com"),
            }
            if "emoji" in btn:
                button_obj["emoji"] = {"name": btn["emoji"]}
            button_components.append(button_obj)
        
        if button_components:
            components.append({
                "type": 1,  # Action Row
                "components": button_components
            })
    
    # Chuẩn bị embed
    embed = {
        "title": title,
        "description": description,
        "url": "",
        "color": color,
        "fields": fields,
        "footer": {
            "text": "MarketMind AI - Powered by Advanced Analysis",
            "icon_url": "https://cdn-icons-png.flaticon.com/512/10232/10232557.png"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Thêm thumbnail nếu được cung cấp
    if thumbnail_url:
        embed["thumbnail"] = {"url": thumbnail_url}
    
    # Thêm image nếu được cung cấp
    if image_url:
        embed["image"] = {"url": image_url}
    
    # Chuẩn bị payload
    ad_payload = {
        "username": username,
        "avatar_url": avatar_url,
        "content": content,
        "embeds": [embed]
    }
    
    # Thêm components nếu có
    if components:
        ad_payload["components"] = components
    
    # Gửi request
    try:
        response = requests.post(WEBHOOK_URL, json=ad_payload, timeout=10)
        
        if response.status_code == 204:
            print("✅ Gửi quảng cáo lên Discord thành công!")
            return True
        else:
            print(f"❌ Lỗi {response.status_code}: {response.text}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi kết nối: {e}")
        return False


def send_product_ad(
    product_name: str,
    description: str,
    price_text: str,
    setup_time: str,
    bonus_text: str,
    trial_link: str = "https://example.com/trial",
    demo_link: str = "https://example.com/demo",
    image_url: str = ""
) -> bool:
    """
    Gửi quảng cáo sản phẩm với template chuẩn
    
    Args:
        product_name: Tên sản phẩm
        description: Mô tả sản phẩm
        price_text: Thông tin giá dùng thử
        setup_time: Thời gian setup
        bonus_text: Thông tin bonus/quà tặng
        trial_link: Link dùng thử
        demo_link: Link xem demo
        image_url: URL hình banner (tùy chọn)
    
    Returns:
        bool: True nếu gửi thành công
    """
    
    fields = [
        {
            "name": "💰 Giá dùng thử",
            "value": price_text,
            "inline": True
        },
        {
            "name": "⚡ Thời gian setup",
            "value": setup_time,
            "inline": True
        },
        {
            "name": "🎁 Quà tặng đặc biệt",
            "value": bonus_text,
            "inline": False
        }
    ]
    
    buttons = [
        {
            "label": "🎁 Dùng thử miễn phí",
            "url": trial_link,
            "emoji": "🎁"
        },
        {
            "label": "📺 Xem demo video",
            "url": demo_link,
            "emoji": "▶️"
        }
    ]
    
    return send_ad_to_discord(
        title=f"🤖 {product_name}",
        description=description,
        content=f"🎯 **RA MẮT: {product_name.upper()}** 🎯\n\n✨ *Giải pháp tối ưu cho nhu cầu của bạn* ✨",
        thumbnail_url="https://cdn-icons-png.flaticon.com/512/4712/4712109.png",
        image_url=image_url,
        fields=fields,
        buttons=buttons
    )


if __name__ == "__main__":
    # Test với dữ liệu mẫu
    print("🚀 Test gửi quảng cáo...")
    
    success = send_product_ad(
        product_name="AI Content Pro",
        description="**Giải pháp all-in-one cho:** Content Creator • Marketer • Seller • Blogger\n\n✅ **Tính năng nổi bật:**\n• 📝 Tạo bài viết chuẩn SEO trong 30 giây\n• 🎨 Gợi ý hình ảnh + caption đồng bộ\n• 📊 Phân tích đối thủ & trend tự động\n• 🌐 Hỗ trợ 20+ ngôn ngữ",
        price_text="✅ **MIỄN PHÍ** 7 ngày\n❌ Không cần thẻ tín dụng",
        setup_time="🚀 **Dưới 2 phút**\nKhông cần kỹ thuật",
        bonus_text="📦 E-book + Template + Support 1-1\n*(Trị giá $97 — Miễn phí hôm nay)*",
        image_url="https://cdn-media.sforum.vn/storage/app/media/ctvseo_MH/%E1%BA%A3nh%20%C4%91%E1%BA%B9p%20%C4%91%C3%A0%20n%E1%BA%B5ng/anh-dep-da-nang-thumb.jpg"
    )
    
    if success:
        print("✅ Test thành công!")
    else:
        print("❌ Test thất bại. Kiểm tra DISCORD_WEBHOOK_URL trong .env")
