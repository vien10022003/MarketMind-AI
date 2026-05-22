"""
Image Generator Module - Stage C
Calls the GenTextToImage API to generate images from prompts.
Supports single and batch generation with fallback for offline API.
API URL is fetched from Firebase Realtime Database with health checks.
"""

import os
import requests
from typing import Optional, List
from rich import print as rprint

# Firebase Realtime Database URL for image API configuration
FIREBASE_IMAGE_API_URL = "https://vienvipvail-default-rtdb.firebaseio.com/api-graduation-image.json"

# Cache for API URL to avoid repeated Firebase calls
_cached_image_api_url: Optional[str] = None


def fetch_image_api_from_firebase() -> Optional[str]:
    """
    Fetch image API URL from Firebase Realtime Database.
    Validates the API by checking its /health endpoint.
    
    Returns:
        API URL string if healthy, None otherwise
    """
    global _cached_image_api_url
    
    try:
        rprint("[yellow]🔄 Fetching image API URL from Firebase...[/yellow]")
        response = requests.get(FIREBASE_IMAGE_API_URL, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Firebase returns the value directly or wrapped in a dict
            api_url = data.get("value", "") if isinstance(data, dict) else data
            
            if isinstance(api_url, str) and api_url.strip():
                api_url = api_url.strip()
                # Validate by checking health
                health_url = f"{api_url.rstrip('/')}/health"
                try:
                    health_response = requests.get(health_url, timeout=5)
                    if health_response.status_code == 200:
                        _cached_image_api_url = api_url
                        rprint(f"[green]✅ Image API fetched and verified: {api_url}[/green]")
                        return api_url
                    else:
                        rprint(f"[red]❌ Image API health check failed (HTTP {health_response.status_code})[/red]")
                        return None
                except requests.exceptions.RequestException as e:
                    rprint(f"[red]❌ Image API health check failed: {e}[/red]")
                    return None
            else:
                rprint("[red]❌ Invalid API URL from Firebase[/red]")
                return None
        else:
            rprint(f"[red]❌ Firebase fetch failed (HTTP {response.status_code})[/red]")
            return None
            
    except requests.exceptions.Timeout:
        rprint("[red]❌ Firebase request timeout[/red]")
        return None
    except Exception as e:
        rprint(f"[red]❌ Error fetching from Firebase: {e}[/red]")
        return None


def get_image_api_url() -> str:
    """
    Get image API URL exclusively from Firebase.
    Returns cached URL if available, otherwise attempts to fetch from Firebase.
    """
    global _cached_image_api_url
    if _cached_image_api_url:
        return _cached_image_api_url
        
    fetched_url = fetch_image_api_from_firebase()
    if fetched_url:
        return fetched_url
        
    return ""


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
        print(f"Image API response status: {response.status_code}")
        print(f"Image API response body: {response.text}")
        if response.status_code == 200:
            print(f"Image API response json: {response.json()}")
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
