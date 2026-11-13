import time
from strawberry_cli.core.timer import CountdownTimer


def test_timer_initial_state():
    timer = CountdownTimer(duration_seconds=7.0, total_blocks=7)
    assert timer.duration_seconds == 7.0
    assert timer.remaining == 7.0
    assert not timer.is_expired


def test_timer_countdown_and_bar():
    timer = CountdownTimer(duration_seconds=5.0, total_blocks=5)
    timer.start()

    bar = timer.render_bar(colored=False)
    assert bar.startswith("[█████]")
    assert "5s" in bar

    time.sleep(1.05)
    bar_after = timer.render_bar(colored=False)
    assert "4s" in bar_after or "3s" in bar_after
    assert "░" in bar_after


def test_timer_expiration():
    timer = CountdownTimer(duration_seconds=0.1, total_blocks=5)
    timer.start()
    time.sleep(0.15)
    assert timer.is_expired
    assert timer.remaining == 0.0
    assert timer.remaining_seconds_int == 0
