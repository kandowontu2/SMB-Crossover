"""Run the unchanged H5 actual-handler replay for newly admitted MMC3 captures."""
from pathlib import Path
import hashlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tools/audit/run_sophia49_interrupt_h5_replays_a.py'
OUT = ROOT / 'build/verification/root49o2-sophia-interrupt-h5-replays-b'

def main():
    assert not OUT.exists()
    text = SOURCE.read_text()
    assert "OUT=ROOT/'build/verification/root49o2-sophia-interrupt-h5-replays-a'" in text
    text = text.replace("OUT=ROOT/'build/verification/root49o2-sophia-interrupt-h5-replays-a'",
                        "OUT=ROOT/'build/verification/root49o2-sophia-interrupt-h5-replays-b'")
    old = "[('mmc5','4adcc4dd4fea86b06e7f8e0115c5c2b541f21fbe94177531d514b23b800427af')]"
    assert text.count(old) == 1
    text = text.replace(old,"[('mmc3','4184ac25201b0b3d3e42299a09d1d43c28ce9a20ba0168473ccd00578c7d6a32')]")
    # Preserve the original root driver and its results; save the exact derivative.
    driver = ROOT / 'build/verification/root49o2-sophia-interrupt-h5-mmc3-driver-b.py'
    assert not driver.exists()
    driver.write_text(text, encoding='utf8')
    print('Original driver SHA256',hashlib.sha256(SOURCE.read_bytes()).hexdigest(),flush=True)
    # The original driver infers ROOT from its own path; execute with the original
    # tools/audit filename while keeping the exact new source as a retained file.
    namespace = {'__name__':'__main__','__file__':str(SOURCE)}
    exec(compile(text,str(driver),'exec'),namespace)

if __name__ == '__main__':
    main()
