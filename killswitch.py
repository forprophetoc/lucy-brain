"""Kill switch for live sends. Presence of the STOP file = armed (no transmission).
   python killswitch.py arm | disarm | status
"""
import sys
import pathlib

STOP = pathlib.Path(__file__).parent / "STOP"


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "arm":
        STOP.write_text("armed")
        print("kill switch ARMED (STOP present) — live sends blocked")
    elif cmd == "disarm":
        if STOP.exists():
            STOP.unlink()
        print("kill switch DISARMED (STOP absent) — live sends allowed")
    else:
        print("kill switch:", "ARMED" if STOP.exists() else "DISARMED")


if __name__ == "__main__":
    main()
