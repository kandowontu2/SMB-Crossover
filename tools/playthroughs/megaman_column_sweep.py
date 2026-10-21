"""Bounded controller discovery at MM's genuine2-2 coral landing.

Uses an owned copy of the frozen generic branch core. No emulated writes;
opaque states are same-ROM discovery only. A winner is independently replayed
from cold boot and compared with every saved RAM byte before root reuse.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import run_mesen
from roster_branch_root import bind_root


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lua(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value) if isinstance(value, int) else json.dumps(value)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom", type=Path, required=True)
    p.add_argument("--prefix", type=Path, required=True)
    p.add_argument("--root-poll", type=int, required=True)
    p.add_argument("--tag", required=True)
    p.add_argument("--timeout", type=int, default=600)
    a = p.parse_args()
    out = ROOT / "build/roster-through-2-2/search" / a.tag
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(out)
    out.mkdir(parents=True, exist_ok=True)
    prefix = out / "prefix.csv"
    shutil.copyfile(a.prefix, prefix)
    polls = [int(v.split(",")[0]) for v in prefix.read_text().splitlines()
             if v.split(",")[0].isdigit()]
    assert max(polls) >= a.root_poll + 8, "Retain a genuine tail for delayed root capture"
    source = ROOT / "tools/playthroughs/roster_branch_search.lua"
    text = source.read_text()
    start = text.index("  local action=actions[actionIndex]\n")
    end = text.index("\n else mask=lastMask end", start)
    replacement = """  local back,prep,hold,fire=actions[actionIndex]:match('^C(%d+)_(%d+)_(%d+)_(%d+)$')
  back,prep,hold,fire=tonumber(back),tonumber(prep),tonumber(hold),tonumber(fire)
  assert(back and prep and hold and fire,'Known bounded controller plan')
  if trialAge<back then mask=2
  elseif trialAge<back+prep then mask=1
  elseif trialAge<back+prep+hold then mask=129
  else mask=1 end
  if fire==1 and trialAge>=back+prep and trialAge%8<3 then mask=mask|64 end"""
    core = out / "column-sweep-core.lua"
    owned = text[:start] + replacement + text[end:]
    root_check = "  local state=emu.createSavestate()"
    assert owned.count(root_check) == 1
    owned = owned.replace(root_check, """  assert(r('SelectedCharacter')==1 and r('Player_State')==0 and r('Player_Y_Position')==112,'Actual MM coral-top support')
  assert((r('SavedJoypadBits')&128)==0 and (r('A_B_Buttons')&128)==0,'No queued launch before the controller sweep')
""" + root_check)
    keep = "   nextBeam[#nextBeam+1]=pendingNode"
    assert owned.count(keep) == 1
    owned = owned.replace(keep, "   -- One-root finite sweep: retain no descendant state beam.")
    core.write_text(owned)
    verify_core = out / "verify-core.lua"
    shutil.copyfile(ROOT / "tools/playthroughs/roster_branch_verify.lua", verify_core)
    actions = [f"C{back}_{prep}_{hold}_{fire}"
               for back in (0, 2, 4, 6) for prep in (4, 6)
               for hold in range(32, 49) for fire in (0, 1)]
    config = dict(out=out.as_posix()+"/", prefix=prefix.as_posix(),
                  rootPoll=a.root_poll, goalX=2090, goalYMin=0, goalYMax=0,
                  width=1, depth=1, chunk=96, airGoal=False,
                  actions=",".join(actions), spatialLimit=0)
    script = out / ("column-sweep-" + a.tag + ".lua")
    script.write_text("SEARCH={" + ",".join(k+"="+lua(v) for k, v in config.items()) +
                      "}\ndofile("+json.dumps(core.as_posix())+")\n")
    manifest = dict(rom_path=a.rom.resolve().as_posix(), rom_sha256=sha(a.rom),
                    prefix_sha256=sha(prefix), frozen_branch_core_sha256=sha(source),
                    owned_sweep_core_sha256=sha(core), verify_core_sha256=sha(verify_core),
                    plans=len(actions), maximum_trial_frames=96,
                    config=config, discovery_uses_unedited_binary_savestates=True,
                    emulated_memory_or_register_patches=False,
                    explicit_ceiling_column_route=True, branch_coldboot_verified=False)
    mp = out / "manifest.json"
    mp.write_text(json.dumps(manifest, indent=2)+"\n")
    options = ["--nes.ramPowerOnState=AllZeros", "--nes.randomizeCpuPpuAlignment=false",
               "--nes.randomizeMapperPowerOnState=false"]
    result = run_mesen.run(script, a.rom, timeout=a.timeout, emulator_options=options)
    native = ROOT / "build/verification" / f"{a.rom.stem}-{script.stem}.log"
    if native.exists():
        shutil.copyfile(native, out / "search-native.log")
    if result == 0 and (out / "winning-inputs.csv").exists():
        verify = out / ("column-coldboot-verify-" + a.tag + ".lua")
        verify.write_text("BRANCH_VERIFY={out="+json.dumps(out.as_posix()+"/")+
                          ",basename='winning',exportRoot=true}\ndofile("+
                          json.dumps(verify_core.as_posix())+")\n")
        verified = run_mesen.run(verify, a.rom, timeout=a.timeout,
                                emulator_options=options) == 0
        native = ROOT / "build/verification" / f"{a.rom.stem}-{verify.stem}.log"
        if native.exists():
            shutil.copyfile(native, out / "winning-verify-native.log")
        manifest.update(branch_coldboot_verified=verified,
                        winning_inputs_sha256=sha(out / "winning-inputs.csv"))
        if verified:
            manifest["winning_reusable_root"] = bind_root(out, "winning", a.rom, verify_core)
        mp.write_text(json.dumps(manifest, indent=2)+"\n")
        return 0 if verified else 1
    return result


if __name__ == "__main__":
    raise SystemExit(main())
