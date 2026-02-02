import os
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, Static, Label, Select
from textual.containers import Container, Horizontal, Vertical
from textual import on
import yt_dlp

class DawnloaderApp(App):
    """A professional TUI for downloading media."""
    
    TITLE = "Dawnloader v3.0-Pro"
    SUB_TITLE = "The Ultimate Media Engine by PyDragonX"
    CSS = """
    Container {
        align: center middle;
        padding: 1;
    }
    #main_panel {
        width: 80%;
        height: auto;
        border: double cyan;
        padding: 1 2;
        background: $surface;
    }
    .logo {
        content-align: center middle;
        color: cyan;
        margin-bottom: 1;
        text-style: bold;
    }
    Input {
        margin: 1 0;
        border: tall magenta;
    }
    Button {
        width: 100%;
        margin-top: 1;
    }
    #exit_btn {
        background: red;
        color: white;
    }
    .status_label {
        text-align: center;
        margin-top: 1;
        color: yellow;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            with Vertical(id="main_panel"):
                yield Static(r"""
    ____                         __                 __            
   / __ \____ _      ____  / /___  ____ _____  / /__  _____
  / / / / __ `/ | /| / / __ \/ / __ \/ __ `/ __  / _ \/ ___/
 / /_/ / /_/ /| |/ |/ / / / / / /_/ / /_/ / /_/ /  __/ /    
/_____/\__,_/ |__/|__/_/ /_/_/\____/\__,_/\__,_/\___/_/     
                """, classes="logo")
                
                yield Label("🔗 Paste Link or Search Name:")
                yield Input(placeholder="e.g. https://youtube.com/... or Video Name", id="user_input")
                
                yield Label("⚙️ Select Format:")
                yield Select(
                    [("Video (Best Quality)", "1"), ("Audio (MP3 320kbps)", "2")],
                    value="1",
                    id="format_select"
                )
                
                with Horizontal():
                    yield Button("📥 Start Download", variant="success", id="download_btn")
                    yield Button("❌ Exit Tool", variant="error", id="exit_btn")
                
                yield Label("", id="status", classes="status_label")
        yield Footer()

    def get_save_path(self):
        path = '/sdcard/Download/Dawnloader' if os.path.exists('/sdcard') else os.path.expanduser('~/Downloads/Dawnloader')
        os.makedirs(path, exist_ok=True)
        return path

    @on(Button.Pressed, "#exit_btn")
    def quit_app(self):
        self.exit()

    @on(Button.Pressed, "#download_btn")
    def action_download(self):
        user_query = self.query_one("#user_input", Input).value
        mode = self.query_one("#format_select", Select).value
        status = self.query_one("#status", Label)

        if not user_query:
            status.update("⚠️ Please enter a link or name!")
            return

        status.update("🔍 Searching and Processing...")
        self.run_worker(self.process_download(user_query, mode))

    async def process_download(self, query, mode):
        status = self.query_one("#status", Label)
        save_path = self.get_save_path()
        
        is_url = query.startswith(("http", "www"))
        search_query = query if is_url else f"ytsearch1:{query}"

        ydl_opts = {
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }

        if mode == "1":
            ydl_opts.update({'format': 'bestvideo+bestaudio/best', 'merge_output_format': 'mp4'})
        else:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}]
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Running in a thread to keep UI responsive
                info = await self.run_worker(lambda: ydl.extract_info(search_query, download=True), thread=True)
                title = info.get('title', 'Video') if is_url else info['entries'][0]['title']
                status.update(f"✅ Downloaded: {title[:30]}...")
        except Exception as e:
            status.update(f"❌ Error: {str(e)[:50]}")

if __name__ == "__main__":
    app = DawnloaderApp()
    app.run()
