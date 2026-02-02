import os
import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, Static, Label, Select, TabbedContent, TabPane, Log
from textual.containers import Container, Horizontal, Vertical
from textual import on, work
import yt_dlp

class DawnloaderApp(App):
    TITLE = "Dawnloader Pro"
    SUB_TITLE = "The Ultimate Media Engine by PyDragonX"
    
    # CSS لتنسيق الواجهة بشكل فخم
    CSS = """
    Screen { background: #0f172a; }
    #main_container { padding: 1; align: center middle; }
    .logo { color: cyan; text-align: center; text-style: bold; margin-bottom: 1; }
    TabPane { padding: 1; }
    Input { border: tall magenta; margin-bottom: 1; }
    Button { width: 100%; margin: 1 0; }
    .status_ok { color: green; text-style: bold; }
    .status_error { color: red; }
    Log { height: 10; border: solid gray; margin-top: 1; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main_container"):
            yield Static(r"""
    ____                         __                 __            
   / __ \____ _      ____  / /___  ____ _____  / /__  _____
  / / / / __ `/ | /| / / __ \/ / __ \/ __ `/ __  / _ \/ ___/
 / /_/ / /_/ /| |/ |/ / / / / / /_/ / /_/ / /_/ /  __/ /    
/_____/\__,_/ |__/|__/_/ /_/_/\____/\__,_/\__,_/\___/_/     
            """, classes="logo")

            with TabbedContent():
                with TabPane("📥 Download", id="download_tab"):
                    yield Label("🔗 URL or Search Query:")
                    yield Input(placeholder="Enter link or video name...", id="url_input")
                    
                    yield Label("⚙️ Format:")
                    yield Select([("Video + Audio", "vid"), ("Audio Only (MP3)", "aud")], value="vid", id="mode_select")
                    
                    with Horizontal():
                        yield Button("🚀 Start Download", variant="success", id="start_btn")
                        yield Button("🧹 Clear", variant="default", id="clear_btn")
                    
                    yield Label("", id="status_msg")
                    yield Log(id="process_log")

                with TabPane("📜 History", id="history_tab"):
                    yield Label("Recent Downloads:")
                    yield Log(id="history_log")

                with TabPane("⚙️ Settings", id="settings_tab"):
                    yield Label(f"📂 Save Path: {self.get_save_path()}")
                    yield Button("🔄 Update Download Engine (yt-dlp)", variant="primary", id="update_btn")
                    yield Button("❌ Exit Application", variant="error", id="exit_btn")
        yield Footer()

    def get_save_path(self):
        path = '/sdcard/Download/Dawnloader' if os.path.exists('/sdcard') else os.path.expanduser('~/Downloads/Dawnloader')
        os.makedirs(path, exist_ok=True)
        return path

    @on(Button.Pressed, "#exit_btn")
    def action_exit(self):
        self.exit()

    @on(Button.Pressed, "#clear_btn")
    def action_clear(self):
        self.query_one("#url_input", Input).value = ""
        self.query_one("#status_msg", Label).update("")

    @on(Button.Pressed, "#update_btn")
    @work(thread=True)
    def update_engine(self):
        self.query_one("#process_log", Log).write_line("Updating yt-dlp...")
        os.system("pip install -U yt-dlp")
        self.notify("Engine Updated Successfully!", title="System Update")

    @on(Button.Pressed, "#start_btn")
    def handle_download(self):
        query = self.query_one("#url_input", Input).value
        mode = self.query_one("#mode_select", Select).value
        if not query:
            self.notify("Please enter something to download!", severity="error")
            return
        
        self.query_one("#status_msg", Label).update("[yellow]Processing...[/yellow]")
        self.run_download(query, mode)

    @work(thread=True)
    def run_download(self, query, mode):
        log = self.query_one("#process_log", Log)
        history = self.query_one("#history_log", Log)
        save_path = self.get_save_path()
        
        is_url = query.startswith(("http", "www"))
        final_query = query if is_url else f"ytsearch1:{query}"

        ydl_opts = {
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'logger': MyLogger(log),
            'progress_hooks': [lambda d: self.update_status(d)],
        }

        if mode == "vid":
            ydl_opts.update({'format': 'bestvideo+bestaudio/best', 'merge_output_format': 'mp4'})
        else:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}]
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(final_query, download=True)
                title = info.get('title', 'Video') if is_url else info['entries'][0]['title']
                self.call_from_thread(self.notify, f"Finished: {title}", title="Download Complete")
                history.write_line(f"✅ {title}")
                self.query_one("#status_msg", Label).update("[green]Download Finished![/green]")
        except Exception as e:
            log.write_line(f"Error: {e}")
            self.query_one("#status_msg", Label).update("[red]Download Failed![/red]")

    def update_status(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%')
            self.query_one("#status_msg", Label).update(f"[cyan]Downloading: {p}[/cyan]")

class MyLogger:
    def __init__(self, log_widget): self.log_widget = log_widget
    def debug(self, msg): self.log_widget.write_line(msg)
    def warning(self, msg): self.log_widget.write_line(f"⚠️ {msg}")
    def error(self, msg): self.log_widget.write_line(f"❌ {msg}")

if __name__ == "__main__":
    DawnloaderApp().run()
