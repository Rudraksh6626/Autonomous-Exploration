import math


def _hash2d(x: int, y: int, seed: int) -> int:
    value = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    value ^= value >> 13
    value = (value * 1274126177) & 0xFFFFFFFF
    value ^= value >> 7
    value = (value * 216521695) & 0xFFFFFFFF
    value ^= value >> 17
    return value & 0xFFFFFFFF


def _gradient(hash_value: int) -> tuple[float, float]:
    h = hash_value & 0x3
    if h == 0:
        return (1.0, 1.0)
    if h == 1:
        return (-1.0, 1.0)
    if h == 2:
        return (1.0, -1.0)
    return (-1.0, -1.0)


def _fade(t: float) -> float:
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _value_noise_2d(x: float, y: float, seed: int) -> float:
    x0 = int(math.floor(x))
    y0 = int(math.floor(y))
    x1 = x0 + 1
    y1 = y0 + 1

    xf = x - x0
    yf = y - y0

    n00 = _gradient(_hash2d(x0, y0, seed))
    n10 = _gradient(_hash2d(x1, y0, seed))
    n01 = _gradient(_hash2d(x0, y1, seed))
    n11 = _gradient(_hash2d(x1, y1, seed))

    dot00 = n00[0] * xf + n00[1] * yf
    dot10 = n10[0] * (xf - 1.0) + n10[1] * yf
    dot01 = n01[0] * xf + n01[1] * (yf - 1.0)
    dot11 = n11[0] * (xf - 1.0) + n11[1] * (yf - 1.0)

    u = _fade(xf)
    v = _fade(yf)

    interpolated = _lerp(
        _lerp(dot00, dot10, u),
        _lerp(dot01, dot11, u),
        v,
    )
    return interpolated


def pnoise2(
    x: float,
    y: float,
    octaves: int = 1,
    persistence: float = 0.5,
    lacunarity: float = 2.0,
    repeatx: int = 1024,
    repeaty: int = 1024,
    base: int = 0,
) -> float:
    total = 0.0
    frequency = 1.0
    amplitude = 1.0
    max_amplitude = 0.0

    for _ in range(max(1, octaves)):
        sample_x = x * frequency + base
        sample_y = y * frequency + base
        total += amplitude * _value_noise_2d(sample_x, sample_y, base)
        max_amplitude += amplitude
        amplitude *= persistence
        frequency *= lacunarity

    if max_amplitude == 0.0:
        return 0.0

    return total / max_amplitude


def snoise2(
    x: float,
    y: float,
    octaves: int = 1,
    persistence: float = 0.5,
    lacunarity: float = 2.0,
    base: int = 0,
) -> float:
    return pnoise2(
        x,
        y,
        octaves=octaves,
        persistence=persistence,
        lacunarity=lacunarity,
        base=base,
    )
