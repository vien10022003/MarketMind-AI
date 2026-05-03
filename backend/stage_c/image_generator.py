"""
Image Generator Module - Stage C
Calls the GenTextToImage API to generate images from prompts.
Supports single and batch generation with fallback for offline API.
"""

import os
import requests
from typing import Optional, List
from rich import print as rprint


def get_image_api_url() -> str:
    """Get image API URL from environment."""
    return os.getenv("IMAGE_API_URL", "")


def generate_image(
    prompt: str,
    api_url: Optional[str] = None,
    num_inference_steps: int = 50,
    timeout: int = 120,
) -> Optional[str]:
    """
    Generate a single image from text prompt.
    
    Args:
        prompt: Text prompt for image generation
        api_url: Override API URL (defaults to IMAGE_API_URL env)
        num_inference_steps: Quality setting (20-100)
        timeout: Request timeout in seconds
    
    Returns:
        Image URL string or None if failed
    """
    url = api_url or get_image_api_url()
    if not url:
        rprint("[yellow]⚠️ IMAGE_API_URL not set, skipping image generation[/yellow]")
        return None

    endpoint = f"{url.rstrip('/')}/generate-image"

    try:
        rprint(f"[yellow]🎨 Generating image: {prompt[:60]}...[/yellow]")
        response = requests.post(
            endpoint,
            json={
                "prompt": prompt,
                "num_inference_steps": num_inference_steps,
            },
            timeout=timeout,
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                image_url = data.get("image_url", "")
                rprint(f"[green]✅ Image generated: {image_url[:60]}...[/green]")
                return image_url
            else:
                rprint(f"[red]❌ Image API error: {data.get('error', 'Unknown')}[/red]")
                return None
        else:
            rprint(f"[red]❌ Image API HTTP {response.status_code}[/red]")
            return None

    except requests.exceptions.ConnectionError:
        rprint("[yellow]⚠️ Image API offline, skipping[/yellow]")
        return None
    except requests.exceptions.Timeout:
        rprint("[yellow]⚠️ Image API timeout, skipping[/yellow]")
        return None
    except Exception as e:
        rprint(f"[red]❌ Image generation error: {e}[/red]")
        return None


def generate_batch_images(
    prompts: List[str],
    api_url: Optional[str] = None,
    num_inference_steps: int = 50,
    timeout: int = 300,
) -> List[Optional[str]]:
    """
    Generate multiple images. Falls back to sequential if batch endpoint fails.
    
    Args:
        prompts: List of text prompts
        api_url: Override API URL
        num_inference_steps: Quality setting
        timeout: Request timeout
    
    Returns:
        List of image URLs (None for failed ones)
    """
    url = api_url or get_image_api_url()
    if not url:
        rprint("[yellow]⚠️ IMAGE_API_URL not set, skipping all images[/yellow]")
        return [None] * len(prompts)

    # Try batch endpoint first
    endpoint = f"{url.rstrip('/')}/generate-batch"
    try:
        response = requests.post(
            endpoint,
            json={
                "prompts": prompts,
                "num_inference_steps": num_inference_steps,
            },
            timeout=timeout,
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                images = data.get("images", [])
                return [img.get("image_url") for img in images]
    except Exception:
        rprint("[yellow]⚠️ Batch endpoint failed, falling back to sequential[/yellow]")

    # Fallback: generate one by one
    results = []
    for prompt in prompts:
        img_url = generate_image(prompt, api_url, num_inference_steps)
        results.append(img_url)
    return results


def check_image_api_health(api_url: Optional[str] = None) -> bool:
    """Check if the image generation API is available."""
    url = api_url or get_image_api_url()
    if not url:
        return False
    try:
        response = requests.get(f"{url.rstrip('/')}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False
