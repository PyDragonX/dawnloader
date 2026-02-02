import os
import yt_dlp
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
from rich.table import Table
from rich.prompt import Prompt

# Initialize Console
console = Console()

class Dawnloader:
    def __init__(self):
        self.version = "2.5.0-Pro"
        self.github_user = "PyDragonX"
        self.github_link = f"https://github.com/{self.github_user}/"
        
        # Path Management (Linux/Termux)
        self.save_dir = '/sdcard/Download/Dawnloader' if os.path.exists('/sdcard') else './Downloads'
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir, exist_ok=True)

    def print_banner(self):
        # Added 'r' before the string to fix SyntaxWarning (invalid escape sequence)
        ascii_art = r"""
    ____                         __                 __            
   / __ \____ _      ____  / /___  ____ _____  / /__  _____
  / / / / __ `/ | /| / / __ \/ / __ \/ __ `/ __  / _ \/ ___/
 / /_/ / /_/ /| |/ |/ / / / / / /_/ / /_/ / /_/ /  __/ /    
/_____/\__,_/ |__/|__/_/ /_/_/\____/\__,_/\__,_/\___/_/     
        """
        console.print(Panel(
            f"[bold cyan]{ascii_art}[/bold cyan]\n"
            f"[bold magenta]Owner:[/bold magenta] [link={self.github_link}]{self.github_user}[/link] | "
            f"[bold green]Version:[/bold green] {self.version}\n"
            f"[dim]{self.github_link}[/dim]",
            title="💎 [bold white]The Ultimate Media Engine[/bold white] 💎",
            border_style="blue",
            padding=(1, 2)
        ))

    def fetch_info(self, query):
        """Search and fetch video details"""
        is_url = query.startswith(("http", "www"))
        search_engine = f"ytsearch1:{query}" if not is_url else query
        
        with console.status("[bold yellow]⚡ Searching...", spinner="bouncingBall"):
            ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': False}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(search_engine, download=False)
                    if 'entries' in info:
                        return info['entries'][0]
                    return info
                except Exception as e:
                    console.print(f"[bold red]❌ Error:[/bold red] {e}")
                    return None

    def get_download_options(self, mode):
        """Configure yt-dlp options"""
        base_opts = {
            'outtmpl': f'{self.save_dir}/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'writethumbnail': True,
            'addmetadata': True,
        }

        if mode == "1": # Video
            base_opts.update({
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
            })
        elif mode == "2": # Audio
            base_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }, {'key': 'FFmpegMetadata'}],
            })
        return base_opts

    def run_download(self, url, opts):
        """Download logic with progress bar"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=None, style="white", complete_style="bold cyan"),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("🚀 Downloading...", total=100)

            def progress_hook(d):
                if d['status'] == 'downloading':
                    try:
                        p = d.get('_percent_str', '0%').replace('%', '').strip()
                        progress.update(task, completed=float(p))
                    except: pass
                elif d['status'] == 'finished':
                    progress.update(task, completed=100, description="🔥 Finalizing...")

            opts['progress_hooks'] = [progress_hook]
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

    def run(self): # Unified function name to fix AttributeError
        self.print_banner()
        while True:
            console.print(f"\n[bold white]📍 Path:[/bold white] [yellow]{self.save_dir}[/yellow]")
            user_input = Prompt.ask("[bold green]📥 Link or Search Name[/bold green] (or 'q' to quit)")

            if user_input.lower() in ['q', 'quit', 'exit']:
                console.print(f"[bold red]👋 Goodbye! Visit: {self.github_link}[/bold red]")
                break

            video = self.fetch_info(user_input)
            if not video: continue

            # UI Display
            info_table = Table(show_header=False, border_style="dim")
            info_table.add_row("[bold cyan]Title[/bold cyan]", video.get('title'))
            info_table.add_row("[bold cyan]Channel[/bold cyan]", video.get('uploader'))
            console.print(Panel(info_table, title="🔍 Found", border_style="cyan"))

            menu = Table(show_header=True, header_style="bold magenta", expand=True)
            menu.add_column("Key", justify="center")
            menu.add_column("Format")
            menu.add_row("1", "🎬 Video (MP4)")
            menu.add_row("2", "🎶 Audio (MP3 320kbps)")
            console.print(menu)

            mode = Prompt.ask("Select Mode", choices=["1", "2"], default="1")
            
            try:
                download_opts = self.get_download_options(mode)
                self.run_download(video.get('webpage_url'), download_opts)
                console.print(f"\n[bold green]✅ DONE![/bold green] File: [yellow]{self.save_dir}[/yellow]")
            except Exception as e:
                console.print(f"[bold red]❌ Error:[/bold red] {e}")

if __name__ == "__main__":
    try:
        app = Dawnloader()
        app.run() # Fixed: Now matches the function name
    except KeyboardInterrupt:
        console.print("\n[bold red]Closed.[/bold red]")
