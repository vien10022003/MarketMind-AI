"""
Discord Publisher Module - Stage C
Format and post content to Discord via webhook.
Builds on the existing discord_advertising.py patterns but uses env-based webhook URL.
"""

import os
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional, Generator
from rich import print as rprint

from .data_models_c import ExecutionResult, CampaignLog, StageCInput
from .image_generator import generate_image, check_image_api_health


def get_webhook_url() -> str:
    """Get Discord webhook URL from environment."""
    return os.getenv("DISCORD_WEBHOOK_URL", os.getenv("WEBHOOK_URL", ""))


def format_discord_embed(
    title: str,
    caption: str,
    image_url: Optional[str] = None,
    color: int = 0x5865F2,
    pillar: str = "",
    content_type: str = "",
    day: int = 0,
) -> dict:
    """
    Format a Discord embed payload from a content brief.
    
    Returns:
        Complete webhook payload dict ready to POST
    """
    embed = {
        "title": title,
        "description": caption,
        "color": color,
        "footer": {
            "text": f"MarketMind AI • {pillar} • Day {day}",
            "icon_url": "https://cdn-icons-png.flaticon.com/512/10232/10232557.png",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if image_url:
        embed["image"] = {"url": image_url}

    # Add content type as a field
    if content_type:
        embed["fields"] = [
            {"name": "📂 Loại nội dung", "value": content_type, "inline": True},
        ]

    payload = {
        "username": "🚀 MarketMind AI",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/4712/4712109.png",
        "embeds": [embed],
    }

    return payload


def post_to_discord(payload: dict, webhook_url: Optional[str] = None) -> bool:
    """
    Post a formatted payload to Discord via webhook.
    
    Returns:
        True if successful (HTTP 204), False otherwise
    """
    url = webhook_url or get_webhook_url()
    if not url:
        rprint("[red]❌ DISCORD_WEBHOOK_URL not configured[/red]")
        return False

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 204:
            rprint("[green]✅ Discord post sent successfully[/green]")
            return True
        else:
            rprint(f"[red]❌ Discord error {response.status_code}: {response.text[:200]}[/red]")
            return False
    except requests.exceptions.RequestException as e:
        rprint(f"[red]❌ Discord connection error: {e}[/red]")
        return False


def run_stage_c_pipeline(stage_c_input: StageCInput) -> Generator[dict, None, None]:
    """
    Run Stage C campaign execution as a generator for streaming.
    For each approved brief: generate image → format embed → post to Discord → log result.
    """
    briefs = stage_c_input.approved_briefs
    webhook_url = stage_c_input.webhook_url or get_webhook_url()
    image_api_url = stage_c_input.image_api_url or os.getenv("IMAGE_API_URL", "")
    skip_images = stage_c_input.skip_image_generation

    if not briefs:
        yield {"status": "error", "message": "❌ Không có content brief nào được phê duyệt."}
        return

    if not webhook_url:
        yield {"status": "error", "message": "❌ DISCORD_WEBHOOK_URL chưa được cấu hình trong .env"}
        return

    yield {
        "status": "stage_c_starting",
        "message": f"🚀 Bắt đầu thực thi chiến dịch: {len(briefs)} bài đăng",
    }

    # Check image API availability
    image_api_available = False
    if not skip_images and image_api_url:
        image_api_available = check_image_api_health(image_api_url)
        if image_api_available:
            yield {"status": "progress", "message": "✅ Image API sẵn sàng"}
        else:
            yield {"status": "progress", "message": "⚠️ Image API không khả dụng, bỏ qua tạo ảnh"}
    elif skip_images:
        yield {"status": "progress", "message": "ℹ️ Bỏ qua tạo ảnh theo yêu cầu"}

    results: List[ExecutionResult] = []
    total_posted = 0
    total_failed = 0

    for idx, brief_data in enumerate(briefs, 1):
        brief_id = brief_data.get("id", f"brief-{idx}")
        brief_title = brief_data.get("title", f"Bài đăng {idx}")

        yield {
            "status": "brief_executing",
            "message": f"📝 [{idx}/{len(briefs)}] Đang xử lý: {brief_title}",
            "brief_index": idx,
        }

        image_url = None
        image_skipped = True

        # Step 1: Generate image (if available)
        if image_api_available and not skip_images:
            image_prompt = brief_data.get("image_prompt", "")
            if image_prompt:
                yield {
                    "status": "image_generating",
                    "message": f"🎨 Đang tạo ảnh cho: {brief_title}",
                    "brief_index": idx,
                }
                image_url = generate_image(image_prompt, image_api_url)
                image_skipped = False
                if image_url:
                    yield {
                        "status": "image_generated",
                        "message": f"✅ Ảnh đã tạo: {image_url[:60]}...",
                        "brief_index": idx,
                        "image_url": image_url,
                    }
                else:
                    yield {
                        "status": "progress",
                        "message": f"⚠️ Không tạo được ảnh, tiếp tục đăng không ảnh",
                        "brief_index": idx,
                    }

        # Step 2: Format Discord embed
        payload = format_discord_embed(
            title=brief_title,
            caption=brief_data.get("caption", ""),
            image_url=image_url,
            color=brief_data.get("embed_color", 0x5865F2),
            pillar=brief_data.get("pillar", ""),
            content_type=brief_data.get("content_type", ""),
            day=brief_data.get("scheduled_day", idx),
        )

        # Step 3: Post to Discord
        yield {
            "status": "discord_posting",
            "message": f"📤 Đang đăng lên Discord: {brief_title}",
            "brief_index": idx,
        }

        success = post_to_discord(payload, webhook_url)

        exec_result = ExecutionResult(
            brief_id=brief_id,
            brief_title=brief_title,
            status="success" if success else "failed",
            image_url=image_url,
            image_skipped=image_skipped,
            discord_sent=success,
            error=None if success else "Discord post failed",
        )
        results.append(exec_result)

        if success:
            total_posted += 1
            yield {
                "status": "discord_posted",
                "message": f"✅ [{idx}/{len(briefs)}] Đã đăng: {brief_title}",
                "brief_index": idx,
                "result": exec_result.model_dump(),
            }
        else:
            total_failed += 1
            yield {
                "status": "discord_post_failed",
                "message": f"❌ [{idx}/{len(briefs)}] Thất bại: {brief_title}",
                "brief_index": idx,
                "result": exec_result.model_dump(),
            }

    # Build campaign log
    import uuid
    campaign_log = CampaignLog(
        campaign_id=str(uuid.uuid4())[:8],
        mongodb_stage_a_id=stage_c_input.mongodb_stage_a_id,
        results=results,
        total_briefs=len(briefs),
        total_posted=total_posted,
        total_failed=total_failed,
        total_skipped=len(briefs) - total_posted - total_failed,
        completed_at=datetime.now().isoformat(),
    )

    yield {
        "status": "stage_c_completed",
        "message": f"🎉 Chiến dịch hoàn tất! {total_posted}/{len(briefs)} bài đã đăng thành công.",
        "campaign_log": campaign_log.model_dump(),
    }
