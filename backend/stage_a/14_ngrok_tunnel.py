"""
Ngrok Tunnel Module
Expose Flask server to public internet
"""

import os
from pyngrok import ngrok
from werkzeug.serving import WSGIRequestHandler
from rich import print as rprint


def setup_ngrok_tunnel(port: int = 5000) -> str:
    """
    Setup ngrok tunnel to expose Flask server
    
    Args:
        port: Flask server port (default 5000)
    
    Returns:
        Public URL from ngrok
    """
    # Get ngrok auth token
    ngrok_auth_token = os.getenv("NGROK_AUTH_TOKEN")
    if ngrok_auth_token:
        ngrok.set_auth_token(ngrok_auth_token)
    else:
        rprint("[yellow]⚠️ NGROK_AUTH_TOKEN not found in .env[/yellow]")

    # Set server timeout
    WSGIRequestHandler.timeout = 3600  # 1 hour

    # Create tunnel
    try:
        public_url = ngrok.connect(port, bind_tls=True)
        rprint(f"[bold green]✅ NGROK TUNNEL CREATED[/bold green]")
        rprint(f"[bold green]  Public URL: {public_url}[/bold green]")
        rprint(f"[bold green]  Endpoint: {public_url}/api/research/stage_a[/bold green]")
        return str(public_url)
    except Exception as e:
        rprint(f"[red]✗ Failed to create ngrok tunnel: {e}[/red]")
        return None


def run_server(app, host: str = "0.0.0.0", port: int = 5000, use_ngrok: bool = True):
    """
    Run Flask server with optional ngrok tunnel
    
    Args:
        app: Flask application
        host: Host address
        port: Port number
        use_ngrok: Whether to setup ngrok tunnel
    """
    if use_ngrok:
        public_url = setup_ngrok_tunnel(port)
        if not public_url:
            rprint("[yellow]Proceeding without ngrok tunnel[/yellow]")

    rprint(f"[yellow]Starting Flask server on {host}:{port}[/yellow]")
    app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    from .13_flask_api import create_app
    
    app = create_app()
    run_server(app, use_ngrok=True)
