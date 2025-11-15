"""
UI utilities for terminal-based interface.
"""

import os
import sys
import time
from typing import Optional


class Color:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Regular colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'

    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'


class UI:
    """Terminal UI helper class."""

    def __init__(self):
        self.width = self._get_terminal_width()

    def _get_terminal_width(self) -> int:
        """Get terminal width."""
        try:
            return os.get_terminal_size().columns
        except OSError:
            return 80

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name != 'nt' else 'cls')

    def print_banner(self):
        """Print application banner."""
        banner = f"""
{Color.CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              🤖  MULTI-AGENT CLI SYSTEM  🤖                  ║
║                                                              ║
║          Powered by Google Gemini & File Search              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Color.RESET}
"""
        print(banner)

    def print_header(self, text: str):
        """Print a section header."""
        print(f"\n{Color.BOLD}{Color.BLUE}═══ {text} ═══{Color.RESET}\n")

    def print_success(self, text: str):
        """Print success message."""
        print(f"{Color.GREEN}✓{Color.RESET} {text}")

    def print_error(self, text: str):
        """Print error message."""
        print(f"{Color.RED}✗{Color.RESET} {text}", file=sys.stderr)

    def print_warning(self, text: str):
        """Print warning message."""
        print(f"{Color.YELLOW}⚠{Color.RESET} {text}")

    def print_info(self, text: str):
        """Print info message."""
        print(f"{Color.CYAN}ℹ{Color.RESET} {text}")

    def print_step(self, text: str):
        """Print a step in progress."""
        print(f"{Color.MAGENTA}►{Color.RESET} {text}")

    def get_input(self, prompt: str, default: Optional[str] = None) -> str:
        """Get user input with optional default value."""
        if default:
            prompt_text = f"{Color.CYAN}?{Color.RESET} {prompt} [{default}]: "
        else:
            prompt_text = f"{Color.CYAN}?{Color.RESET} {prompt}: "

        user_input = input(prompt_text).strip()
        return user_input if user_input else (default or "")

    def confirm(self, prompt: str, default: bool = True) -> bool:
        """Get yes/no confirmation from user."""
        default_str = "Y/n" if default else "y/N"
        response = self.get_input(f"{prompt} ({default_str})", "y" if default else "n")
        return response.lower() in ['y', 'yes'] if response else default

    def pause(self, seconds: float = 1):
        """Pause for specified seconds."""
        time.sleep(seconds)

    def show_spinner(self, text: str):
        """Show a loading spinner (placeholder for now)."""
        print(f"{Color.YELLOW}⏳{Color.RESET} {text}...")

    def print_divider(self, char: str = "─"):
        """Print a horizontal divider."""
        print(f"{Color.GRAY}{char * self.width}{Color.RESET}")
