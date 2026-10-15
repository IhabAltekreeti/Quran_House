import argparse
import json
import sys

from .errors import IntegrityError, MediaError, RenderError


def main(argv=None):
    p = argparse.ArgumentParser(prog="python -m quranhouse", description="Generate a verified Quran short video")
    p.add_argument("--surah", type=int, required=True)
    p.add_argument("--from", dest="ayah_from", type=int, required=True)
    p.add_argument("--to", dest="ayah_to", type=int)
    p.add_argument("--reciter", type=int, default=7, help="Quran.com recitation id (default 7)")
    p.add_argument("--translation", type=int, default=20, help="Quran.com translation id (default 20)")
    p.add_argument("--output-dir", default="output")
    a = p.parse_args(argv)
    from .pipeline import generate
    try:
        final, manifest = generate(a.surah, a.ayah_from, a.ayah_to or a.ayah_from, a.reciter,
                                   a.translation, a.output_dir)
    except (IntegrityError, MediaError, RenderError) as e:
        print(f"GENERATION ABORTED ({type(e).__name__}): {e}", file=sys.stderr)
        return 2
    print(json.dumps({"output": final, "verified": manifest["verified"]}, ensure_ascii=False))
    return 0 if manifest["verified"] else 3


if __name__ == "__main__":
    sys.exit(main())
