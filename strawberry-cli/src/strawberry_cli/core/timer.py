"""7-second Countdown Timer with visual progress bar rendering."""

import math
import time
from typing import Optional


class CountdownTimer:
    """Tracks a countdown deadline with a visual ASCII/Unicode progress bar."""

    def __init__(self, duration_seconds: float = 7.0, total_blocks: int = 7):
        self.duration_seconds = max(0.01, duration_seconds)
        self.total_blocks = total_blocks
        self._start_time: Optional[float] = None

    def start(self) -> None:
        """Start or restart the countdown."""
        self._start_time = time.monotonic()

    def reset(self) -> None:
        """Reset the timer to start from the full duration again."""
        self.start()

    @property
    def elapsed(self) -> float:
        """Elapsed time in seconds since start."""
        if self._start_time is None:
            return 0.0
        return max(0.0, time.monotonic() - self._start_time)

    @property
    def remaining(self) -> float:
        """Remaining time in seconds until timeout."""
        if self._start_time is None:
            return self.duration_seconds
        rem = self.duration_seconds - self.elapsed
        return max(0.0, rem)

    @property
    def remaining_seconds_int(self) -> int:
        """Remaining full seconds (rounded up so 0.1s shows as 1s)."""
        rem = self.remaining
        if rem <= 0.0:
            return 0
        return min(int(self.duration_seconds), math.ceil(rem))

    @property
    def is_expired(self) -> bool:
        """Returns True if the countdown has reached zero."""
        return self.remaining <= 0.0

    def render_bar(self, colored: bool = True) -> str:
        """Renders the progress bar, e.g.:

        [███████] 7s
        [██████░] 6s
        ...
        [░░░░░░░] 0s
        """
        secs = self.remaining_seconds_int
        ratio = max(0.0, min(1.0, self.remaining / self.duration_seconds))
        filled_count = int(math.ceil(ratio * self.total_blocks))
        empty_count = self.total_blocks - filled_count

        filled_char = "█"
        empty_char = "░"
        bar = (filled_char * filled_count) + (empty_char * empty_count)

        if not colored:
            return f"[{bar}] {secs}s"

        # ANSI color codes: Red for <=2s, Yellow for 3-4s, Green/Strawberry Red for 5-7s
        if secs <= 2:
            color = "\033[91m"  # Bright Red
        elif secs <= 4:
            color = "\033[93m"  # Bright Yellow
        else:
            color = "\033[92m"  # Bright Green
        reset = "\033[0m"

        return f"{color}[{bar}] {secs}s{reset}"
