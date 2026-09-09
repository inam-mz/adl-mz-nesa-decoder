"""
NESA sample files for the documentation capture harness.

The core mock FTP server (adl/docs/screenshots/capture/mock-ftp/server.py)
runs this after writing its own TOA5 samples, with SAMPLE_ROOT, SAMPLE_TZ and
SAMPLE_HOURS in the environment.

One file per day, matched by the station link's File Pattern under
*Pattern Only* (this decoder does no date narrowing of its own):

    /data/nesa/NESA_MAPUTO_<YYYYMMDD>.txt

Line shape, per plugins/.../decoders/nesa_mz.py:

    S,<recordID>,<HH>,<MM>,<SS>,<DD>,<MM>,<YYYY>,<id1>,<id2>,<value>,...,#

Each id1;id2 triplet becomes one key in the decoded record, which is what an
operator types as the File Variable Name. The pairs below are the ones the
fixture maps, so the demo connection stores values rather than decoding into
nothing.

The timestamp carries no timezone; ADL reads it in the station's timezone,
which is why the fixture sets Africa/Maputo.

Nothing here is real data: values are a smooth diurnal cycle plus noise.
"""

import math
import os
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

ROOT = os.environ.get("SAMPLE_ROOT", "/srv/ftp")
TZ = ZoneInfo(os.environ.get("SAMPLE_TZ", "Africa/Maputo"))
DAYS = int(os.environ.get("NESA_SAMPLE_DAYS", "2"))
STEP_MINUTES = int(os.environ.get("NESA_STEP_MINUTES", "15"))


def line(moment, record_id):
    rng = random.Random(f"nesa-{moment:%Y%m%d%H%M}")
    hour = moment.hour + moment.minute / 60
    diurnal = math.sin((hour - 9) / 24 * 2 * math.pi)

    temp = 24 + 6 * diurnal + rng.uniform(-0.4, 0.4)
    rh = 72 - 20 * diurnal + rng.uniform(-2, 2)
    press = 1010 + 1.8 * math.sin(hour / 12 * math.pi) + rng.uniform(-0.3, 0.3)
    rain = rng.choice([0.0, 0.0, 0.0, 0.2, 0.8]) if 15 <= hour <= 18 else 0.0
    wind = max(0.0, 2.8 + 2.0 * diurnal + rng.uniform(-0.7, 0.7))
    wdir = (140 + 35 * diurnal + rng.uniform(-15, 15)) % 360
    solar = max(0.0, 880 * math.sin((hour - 6) / 12 * math.pi)) if 6 <= hour <= 18 else 0.0

    triplets = [
        ("1", "2", f"{temp:.1f}"),
        ("1", "3", f"{rh:.1f}"),
        ("2", "1", f"{press:.1f}"),
        ("3", "1", f"{rain:.1f}"),
        ("4", "1", f"{wind:.1f}"),
        ("4", "2", f"{wdir:.0f}"),
        ("5", "1", f"{solar:.1f}"),
    ]

    parts = [
        "S", f"{record_id:06d}",
        f"{moment:%H}", f"{moment:%M}", f"{moment:%S}",
        f"{moment:%d}", f"{moment:%m}", f"{moment:%Y}",
    ]
    for id1, id2, value in triplets:
        parts += [id1, id2, value]
    parts.append("#")
    return ",".join(parts)


def main():
    now = datetime.now(TZ).replace(second=0, microsecond=0)
    now -= timedelta(minutes=now.minute % STEP_MINUTES)
    directory = os.path.join(ROOT, "data", "nesa")
    os.makedirs(directory, exist_ok=True)

    per_day = {}
    steps = DAYS * 24 * 60 // STEP_MINUTES
    for i in range(steps + 1):
        moment = now - timedelta(minutes=STEP_MINUTES * (steps - i))
        per_day.setdefault(moment.date(), []).append(moment)

    for day, moments in per_day.items():
        path = os.path.join(directory, f"NESA_MAPUTO_{day:%Y%m%d}.txt")
        with open(path, "w", newline="") as f:
            f.write("\n".join(line(m, i + 1) for i, m in enumerate(moments)) + "\n")

    print(f"[mock-ftp] generated {len(per_day)} NESA day file(s) up to "
          f"{now:%Y-%m-%d %H:%M} {TZ.key}", flush=True)


if __name__ == "__main__":
    main()
