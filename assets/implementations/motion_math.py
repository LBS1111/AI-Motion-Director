"""Original motion primitives. Time-based, no framework dependency."""
import math


def clamp(value, low=0.0, high=1.0):
    return min(high, max(low, value))


def smootherstep(t):
    t = clamp(t)
    return t * t * t * (t * (t * 6 - 15) + 10)


def progress(seconds, start, duration):
    if duration <= 0:
        raise ValueError("duration must be positive")
    return smootherstep((seconds - start) / duration)


def lerp(start, end, amount):
    return start + (end - start) * amount


def hermite(position0, velocity0, position1, velocity1, seconds, duration):
    """Endpoint velocities are units/second, not normalized curve slopes."""
    if duration <= 0:
        raise ValueError("duration must be positive")
    t = clamp(seconds / duration)
    return (2*t**3-3*t**2+1)*position0 + (t**3-2*t**2+t)*duration*velocity0 + (-2*t**3+3*t**2)*position1 + (t**3-t**2)*duration*velocity1


def damped_step(seconds, frequency=2.0, damping=0.8):
    """Unit step, zero initial velocity; underdamped or critical damping only."""
    if frequency <= 0 or not 0 < damping <= 1:
        raise ValueError("frequency>0 and 0<damping<=1 required")
    t = max(0, seconds)
    w = 2 * math.pi * frequency
    if damping == 1:
        return 1 - math.exp(-w*t) * (1 + w*t)
    wd = w * math.sqrt(1-damping*damping)
    return 1 - math.exp(-damping*w*t) * (math.cos(wd*t) + damping*w/wd * math.sin(wd*t))
