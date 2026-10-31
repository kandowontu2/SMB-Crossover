"""Prepare four exact-cart SMB2 firstlooks including sky and red-eye checks.

This creates immutable packets; it never starts Mesen. The source handoff must
already qualify the exact original-art eye-index remap and BG restore.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

OLD = R / 'build/smb2-current-native-firstlook-v3'
UI = R / 'tools/reference/smb2_ui_native_bg_eye_v6.lua'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def lua(value):
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, list):
        return '{' + ','.join(map(lua, value)) + '}'
    if isinstance(value, dict):
        return '{' + ','.join('[' + lua(k) + ']=' + lua(v) for k, v in value.items()) + '}'
    return str(value)


RUN = '''"""Launch only after root grants this exact packet and the global queue."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys
O=Path(__file__).resolve().parent;R=O.parents[2];D=O/'capture'
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from audit import capture_budget as budget
from run_mesen import run
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--launch',action='store_true');a=p.parse_args()
 assert a.launch,'Preparation does not authorize a native launch'
 q=json.loads((O/'ready.json').read_text());assert not(D/'capture-budget.json').exists()
 for name,h in q['bindings'].items():assert sha(name)==h,('readiness drift',name)
 active=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process -Filter \\\"Name like '%Mesen%'\\\" | Select-Object ProcessId,Name | ConvertTo-Json -Compress"],capture_output=True,text=True,check=True).stdout.strip()
 if active:print(json.dumps(dict(launched=False,reason='Existing Mesen left alone',processes=active)));return 3
 cap=q['run_cap_bytes'];budget.RUN_BYTES=cap;budget.PAYLOAD_BYTES=cap-1000000;original=budget.preflight
 def bounded(output,reserved_bytes=cap,reserved_files=64):return original(output,reserved_bytes,reserved_files)
 budget.preflight=bounded;os.environ['SMB_RUN_OUTPUT']=str(D)
 result=run(O/'controller.lua',Path(q['ROM']),timeout=q['host_timeout_seconds'],emulator_options=['--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
 for name,h in q['bindings'].items():assert sha(name)==h,('postrun drift',name)
 (D/'binding.json').write_text(json.dumps(dict(ROM_sha256=q['ROM_sha256'],ready_sha256=sha(O/'ready.json'),exit_code=result,bindings=q['bindings']),indent=2)+'\\n');raise SystemExit(result)
if __name__=='__main__':raise SystemExit(main())
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--handoff', type=Path, required=True)
    parser.add_argument('--expected-source-sha256', required=True)
    parser.add_argument('--joint', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    J = args.joint.resolve()
    SHA = args.expected_sha256
    assert sha(J / 'candidate.nes') == SHA
    assert sha(args.handoff) == args.expected_source_sha256
    handoff = json.loads(args.handoff.read_text(encoding='utf-8'))
    assert handoff['candidate'] == SHA
    for path, digest in handoff['bindings'].items():
        assert sha(path) == digest, ('Source dependency changed', path)
    assert not args.output.exists(), 'Always prepare a new immutable packet'
    out = args.output.resolve()
    out.mkdir()
    bundle = scoped_load(J / 'candidate.nes')
    raw = bundle['raw']
    # The repair changes only eye index2 -> index1 in each page's eye tiles.
    # All other original body bits remain exact, including blank eye pixels.
    old_raw = (R / 'build/functional-roster-smb2-v1/joint/candidate.nes').read_bytes()
    chr_offset = 16 + 128 * 8192
    for page in range(796, 808):
        at = chr_offset + page * 1024
        before = bytearray(old_raw[at:at+1024])
        for tile in range(56, 58) if page < 804 else ():
            offset = tile * 16
            lo, hi = before[offset:offset+8], before[offset+8:offset+16]
            assert not any(lo), 'Original eye mask uses index2 only'
            before[offset:offset+8] = hi
            before[offset+8:offset+16] = bytes(8)
        assert raw[at:at+1024] == before, ('Exact original body plus eye-index remap', page)
    base = (OLD / 'controller.lua').read_text()
    base = base[base.index('-- Cold controller-only'):]

    def replace(old, new):
        nonlocal base
        assert base.count(old) == 1, old
        base = base.replace(old, new)

    replace("local function bank(pc)local a=emu.convertAddress(pc);return a and a.address//8192 or-1 end", "local function bank(pc)local a=emu.convertAddress(pc);return a and a.address//8192 or-1 end\n" + UI.read_text())
    replace("local function shot(n)local f=assert(io.open(OUTPUT..n..'.png','wb'));f:write(emu.takeScreenshot());f:close()end", "local shots=0\nlocal function shot(n)shots=shots+1;assert(shots<=4,'Four PNG bound');local f=assert(io.open(OUTPUT..n..'.png','wb'));f:write(emu.takeScreenshot());f:close();if n=='selected'or n=='lives'then renderedBody(n)end end")
    replace("if done then return end;done=true;shot('endpoint');csv:close();cycles:close()", "if done then return end;done=true;shot('endpoint');csv:close();cycles:close();uiFile:close();if ok then assert(renderedUI.selected and renderedUI.lives,'Visible original source UI verified in both stages')end")
    replace("r('S2NativeCharacter')==0,'Stable ownsource class/ready'", "r('S2NativeCharacter')==P.native_class,'Stable ownsource class/ready'")
    replace("r('S2Variant')==0 and r('S2Ready')==178,'RealreadySMB2Mario'", "r('S2Variant')==P.variant and r('S2Ready')==178,'Real selected SMB2 class ready'")
    replace("r('S2NativeCharacter')==0,'Genuine sourceFresh health/class'", "r('S2NativeCharacter')==P.native_class,'Genuine sourceFresh health/class'")
    replace("  else\n   assert(r('CrossoverMenuState')==2", "  elseif stableUI('selected')then\n   assert(r('CrossoverMenuState')==2")
    replace("if age==80 then shot('lives')end", "if not renderedUI.lives and stableUI('lives')then shot('lives')end")
    replace("assert(r('SelectedCharacter')==P.raw,'Launched ready raw owner');phase='game';age=0", "assert(r('SelectedCharacter')==P.raw,'Launched ready raw owner');assert(renderedUI.lives,'Actual visible lives scene before control');phase='game';age=0")
    replace("frame_completion_histogram=frameHistogram,scope=", "frame_completion_histogram=frameHistogram,actual_UI_DMA_checks=uiChecks,rendered_UI=renderedUI,body_P0_source_exact=true,eye_role_original_red=true,game_background_checks=backgroundChecks,scope=")
    replace("local updates,activeFrames,minSP,lastCPU=0,0,255,0", "local updates,activeFrames,minSP,lastCPU=0,0,255,0\nlocal backgroundChecks=0")
    replace("activeFrames=activeFrames+1;maxX=math.max(maxX,x);apex=math.min(apex,y)", "assert(r('AreaType')==1 and ppu(0x3f00)==0x22 and ppu(0x3f10)==0x22,'Native ground background restored, not black');assert(ppu(0x3f19)==0x16,'Native P2 red eye retained in gameplay');backgroundChecks=backgroundChecks+1\n   activeFrames=activeFrames+1;maxX=math.max(maxX,x);apex=math.min(apex,y)")
    replace("Cold controller menu/lives/idle/walk/jump/land and passive foreground timing; no1-1 clear or60Hz claim.", "Controller-only cold select/lives source body OAM/physicalCHR/PPU pixels, authenticated red-eye role, black lives and restored ground background, idle/walk/jump/land and passive timing. Root must review all four PNGs. No1-1 clear or60Hz claim.")
    known = {m[2]: int(m[1], 16) for line in (J / 'candidate.lbl').read_text().splitlines() if (m := re.fullmatch(r'al ([0-9A-Fa-f]+) \.([\w]+)', line))}
    for name in ['NonMaskableInterrupt', 'IrqScrollSplit']:
        known[name + '_RTI'] = address(bundle, name) + int(bundle['syms'][name]['size']) - 1
    required = set(re.findall(r"r\('([^']+)'\)", base)) | set(re.findall(r'\bL\.([A-Za-z_]\w*)', base)) | {'S2ColdInit', 'S2MainGame', 'S2Movement', 'S2EndFrame', 'S2AudioNativeEntry'}
    supplement = {name: address(bundle, name) for name in sorted(required - set(known))}
    observer = ''.join('L[' + lua(name) + ']=' + str(value) + '\n' for name, value in supplement.items())
    main_return = address(bundle, 'GameLoop') + int(bundle['syms']['GameLoop']['size']) - 1
    shared = [Path(__file__), UI, OLD / 'ready.json', OLD / 'controller.lua', J / 'candidate.nes', J / 'candidate.dbg', J / 'candidate.lbl', J.parent / 'source-stage.json', args.handoff.resolve(), R / 'build/smb2-current-cold-render-v29/handoff.json', R / 'build/smb2-final62-cold-controls-v30/handoff.json', R / 'tools/run_mesen.py', R / 'tools/audit/run_mesen_output_v2.py', R / 'tools/audit/capture_budget.py',R / 'build/smb2-final62-firstlooks-v4/class0/capture/binding.json',R / 'build/smb2-final62-firstlooks-v4/class0/capture/candidate-controller.log',R / 'build/smb2-final62-firstlooks-v4/class0/capture/selected.png',R / 'build/smb2-final62-observer-priority-v1/controls.json']
    rows = []
    for variant, native_class in enumerate([0, 3, 2, 1]):
        folder = out / ('class' + str(variant))
        folder.mkdir()
        (folder / 'capture').mkdir()
        index = (native_class * 2) * 32 + 1
        record_id = raw[location(bundle, 'S2BodyRecord') + index]
        record = raw[location(bundle, 'S2ArtLo') + record_id] + 256 * raw[location(bundle, 'S2ArtHi') + record_id]
        at = 16 + 80 * 8192 + record - 0xc000
        header = raw[at]
        assert header == 20
        parts = [list(raw[i:i + 4]) for i in range(at + 1, at + 1 + header, 4)]
        name_at = location(bundle, 'FmNames') + (10 + variant) * 16
        name = list(raw[name_at:name_at + 16])
        assert 0x2c not in name
        source = dict(rom=(J / 'candidate.nes').as_posix(), chr_offset=chr_offset, page=796 + native_class * 2, p0=[[1, 22, 39], [1, 42, 54], [1, 48, 39], [6, 37, 54]][variant], parts=parts, name=name)
        assert (parts[0][1] & 3) == 2, 'Eye quad uses native P2'
        source_proof = dict(source=source,record_index=index,record_id=record_id,record_CPU=record,original_body_CHR_exact=True,eye_mask_index_remap='2 -> 1; all masks and source opaque pixels retained',original_executed_eye_color=0x16,native_eye_P2_color=0x16)
        (folder / 'ui-source.json').write_text(json.dumps(source_proof, indent=2) + '\n')
        (folder / 'observer-symbol-preflight.json').write_text(json.dumps(dict(passed=True, required_symbols=sorted(required), genuine_DBG_supplement=supplement, resolved={name: supplement.get(name, known.get(name)) for name in sorted(required)}, no_product_RAM_writes=True), indent=2) + '\n')
        prefix = observer + 'COLD_ARGS=' + lua(dict(raw=25, slot=24, variant=variant, native_class=native_class, sha256=SHA, main_return=main_return)) + '\nS2_UI_SOURCE=' + lua(source) + '\n'
        (folder / 'controller.lua').write_text(prefix + base)
        (folder / 'run.py').write_text(RUN)
        inputs = shared + [folder / name for name in ['ui-source.json', 'observer-symbol-preflight.json', 'controller.lua', 'run.py']]
        ready = dict(prepared=True, native_run=False, launch_authorized=False, ROM=str((J / 'candidate.nes').resolve()), ROM_sha256=SHA, variant=variant, native_class=native_class, controller_only=True, no_native_RAM_writes=True, frame_bound=1200, gameplay_frames=220, host_timeout_seconds=60, max_PNG=4, run_cap_bytes=536870912, max_files=64, AllZeros=True, normal_sprite_limit=True, required_root_review=['selected.png', 'lives.png', 'entered.png', 'endpoint.png'], limits=['Source body/eye pixels and complete visible original OAM required. Native black lives and blue ground background must remain correct.', 'No native result or launch grant is conferred by preparation.'], bindings=handoff['bindings'] | {str(path.resolve()): sha(path) for path in inputs})
        (folder / 'ready.json').write_text(json.dumps(ready, indent=2) + '\n')
        rows.append(dict(variant=variant, native_class=native_class, path=str(folder / 'ready.json'), sha256=sha(folder / 'ready.json')))
    (out / 'prepared.json').write_text(json.dumps(dict(prepared=True, native_runs=0, ROM_sha256=SHA, source_handoff=str(args.handoff.resolve()),source_handoff_sha256=sha(args.handoff),serial_root_grant_required=True, packets=rows,authenticated_red_eye_required=True,restored_background_required=True), indent=2) + '\n')
    print(json.dumps(dict(prepared=True, output=str(out), manifest_sha256=sha(out / 'prepared.json'), packets=rows)))


if __name__ == '__main__':
    main()
