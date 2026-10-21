"""Retain GC's profiler rejection and bind its exact RAM-resident farcall return."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    gc = R / 'tools/audit/continue_easy49_bass_profile_gc.py'
    core = R / 'tools/audit/ordinary_roster_profile49.lua'
    fixed = V / 'root49-el-bass-profile-gd-core.lua'
    old = " assert(q.bank>=0,'Only actual ROM callers are timed')"
    new = """ if q.bank<0 then
  local smc=assert(C.smc_return,'Explicit RAM farcall return binding')
  assert(pc==smc.address,'Unclassified caller '..n..' pc='..pc..' sp='..e.sp)
  for j,v in ipairs(smc.bytes)do
   assert(guard[j]==v,'Literal compiled farcall return8 '..n)
  end
 end"""
    text = core.read_text()
    assert text.count(old) == 1
    assert not fixed.exists()
    fixed.write_text(text.replace(old, new))
    driver = V / 'root49-el-bass-profile-gd-driver.py'
    assert not driver.exists()
    source = gc.read_text().replace('root49-el-bass-profile-gc', 'root49-el-bass-profile-gd')
    source = source.replace('root49gc-bass-live', 'root49gd-bass-live')
    source = source.replace("core = R / 'tools/audit/ordinary_roster_profile49.lua'",
        "core = V / 'root49-el-bass-profile-gd-core.lua'")
    anchor = "    out.mkdir(exist_ok=False)"
    assert source.count(anchor) == 1
    addition = """    smc = next(s for s in im.segs.values() if s['name'] == 'SMCCODE')
    raw = im.raw[smc['ooffs']:smc['ooffs']+smc['size']]
    # Original compiled MMC3 FarCallCommon: its sole JSR is byte25, and
    # the return at+28 begins STA SafereturnA / LDA#47 / STA BankShadow.
    assert smc['start'] == 341 and smc['size'] == 49
    assert raw[25] == 0x20 and raw[28:36] == bytes.fromhex('8d8401a9478d4601')
    cfg['smc_return'] = dict(address=smc['start']+28, bytes=list(raw[28:36]),
        owning_segment=smc, source_sha256=sha(R/'src/mmc3.s'))
"""
    source = source.replace(anchor, addition + anchor)
    driver.write_text(source)
    negative = R / 'build/roster-through-2-2/root49gc-bass-live-9-v0-mmc3/manifest.json'
    assert json.loads(negative.read_text()).get('result') is None
    report = dict(status='PREPARED_EXACT_RAM_FARCALL_RETURN_BINDING',
        script_sha256=sha(__file__), parent_driver_sha256=sha(gc),
        retained_GC_instrumentation_negative_sha256=sha(negative),
        original_core_sha256=sha(core), corrected_core_sha256=sha(fixed),
        corrected_driver_sha256=sha(driver), runtime_changes=False,
        correction='Accept only the exact compiled FarCallCommon RAM return address369 with literal eight bytes; all other non-ROM callers remain errors. Same verified GB input tape and FW controller.')
    (V / 'root49-el-bass-profile-gd-preparation.json').write_text(json.dumps(report, indent=2)+'\n')
    raise SystemExit(subprocess.run([sys.executable, str(driver)], cwd=R).returncode)


if __name__ == '__main__':
    main()
