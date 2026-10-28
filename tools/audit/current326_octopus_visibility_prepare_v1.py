"""Prepare one passive current326 Octopus replay. Does not launch an emulator."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import re

import current_roster_compact_11_v1 as route

ROOT = route.ROOT
EXPECTED = '32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
BASE = ROOT/'build/verification/compact-326942-octopus-easy-v1'
OUT = ROOT/'build/verification/compact-326942-octopus-visibility-v1'
MODULE = Path(__file__).with_suffix('.lua').with_name('current326_octopus_visibility_probe_v1.lua')
SCALARS = '''SelectedCharacter VvVariant CrossoverBehaviorVersion WorldNumber LevelNumber GameEngineSubroutine
Player_X_Position Player_PageLoc Player_Y_Position Player_Y_HighPos ScreenLeft_X_Pos ScreenLeft_PageLoc
Player_State PlayerFacingDir Player_SprAttrib ObjectMetasprite ObjectVerticalFlip FrameCounter PlayerStatus
VvHurt GuestHurtKind GuestHurtTicks GuestInvulTicks GuestHurtVisible InjuryTimer MmDeathFlag
PnBigStage PnBigTimerHi PnBigTimerLo PnAutoMode PnAutoIndex PnSkin PnAux PnPool PnDrawFrame PnMissing
SmFreezeRenderState RgOamPlayerStart RgOamRotation RgOamFirst RgOamUsed GuestOamRotationActive
SmChrBank PlayerChrBank PlayerOutlinesOff CurrentOAMOffset CurrentBank CurrentBankC ReloadCHRBank RlOutlineBypass'''.split()


def digest(path):
    return route.sha(path)


def prepare():
    assert not OUT.exists(), 'Fresh isolated output only; never replace a ready or native outcome'
    old = json.loads((BASE/'ready.json').read_text())
    assert old['ROM_sha256'] == EXPECTED
    assert json.loads((BASE/'result.json').read_text())['passed']
    assert all(digest(p) == h for p, h in old['bindings'].items()), 'Original actual inputs changed'
    rom = ROOT/'build/zelda2_easy_glove.nes'
    raw, syms, addr, loc, hook = route.linked(rom)
    assert digest(rom) == EXPECTED
    names = set(SCALARS + ['R0','R1','PnFrame','PnDrawFlags','PnContact','SmPosePtr','OutlinePoseBuffer'])
    assert not(names-syms.keys()), ('No fabricated RAM aliases', names-syms.keys())
    ram = {n: addr(n) for n in sorted(names)}
    assert addr('R1') == addr('R0')+1
    assert addr('PnFrame')-addr('PnDrawFlags') == 28
    assert addr('PnPalette')-addr('PnFrame') == 28
    for n, at in ram.items():
        assert at < 0x2000 or 0x5c00 <= at < 0x8000, ('Actual RAM only',n,at)
    # Body is the LAST real JSR DrawMetasprite inside DrawAll. Bind its true
    # post-return PC, not an assumed final RTS in a callee with multiple exits.
    draw_at, draw_pc = loc('DrawAllMetasprites'), addr('DrawAllMetasprites')
    draw = raw[draw_at:draw_at+int(syms['DrawAllMetasprites']['size'],0)]
    needle = b'\x20'+addr('DrawMetasprite').to_bytes(2,'little')
    calls = [i for i in range(len(draw)) if draw[i:i+3] == needle]
    assert len(calls) == 3
    ret = calls[-1]+3
    assert draw[ret:ret+3] == b'\xad'+addr('GuestOamRotationActive').to_bytes(2,'little')
    assert raw[loc('RosterOamReady')] == 0x60
    # Actual reservation starts by reading SmPosePtr; body is skipped only by
    # the actual zero ObjectMetasprite branch. No alternate publication added.
    assert raw[loc('RosterProjectileOamReady'):loc('RosterProjectileOamReady')+3] == b'\xad'+addr('SmPosePtr').to_bytes(2,'little')
    assert b'\xa0\x00\xbe'+addr('ObjectMetasprite').to_bytes(2,'little')+b'\xf0' in draw[calls[-1]-70:calls[-1]]
    freeze_at=loc('SamusFreezeDrawAll')
    assert raw[freeze_at:freeze_at+3] == b'\xad'+addr('SmFreezeRenderState').to_bytes(2,'little')
    branch=raw[freeze_at+4]
    assert raw[freeze_at+5:freeze_at+8] == b'\x20'+draw_pc.to_bytes(2,'little')
    assert raw[freeze_at+5+branch:freeze_at+8+branch] == b'\x4c'+draw_pc.to_bytes(2,'little')
    hooks=copy.deepcopy(old['config']['hooks'])
    for key in ('nmi','nmi_return','irq','irq_return'):
        hooks[key]['always']=True  # Depth must include entry outside the window.
    for key,name in [('draw','DrawAllMetasprites'),('reservation','RosterProjectileOamReady'),
                     ('draw_ready','RosterOamReady'),('body','DrawMetasprite'),
                     ('pointer','HpNativePointerEnd'),('renderer','MetaspriteRenderLoop')]:
        hooks[key]=hook(name)
    reservation_copy = (b'\xad'+addr('SmPosePtr').to_bytes(2,'little')+bytes([0x85,addr('R0')])+
                        b'\xad'+(addr('SmPosePtr')+1).to_bytes(2,'little')+bytes([0x85,addr('R1')]))
    assert len(reservation_copy)==10 and raw[loc('RosterProjectileOamReady'):loc('RosterProjectileOamReady')+10]==reservation_copy
    hooks['reservation']=hook('RosterProjectileOamReady',offset=10)
    assert hooks['reservation']['bytes']==[0xa0,0,0xb1], 'After genuine pointer copy, before actual header read'
    hooks['body_return']=dict(name='actual DrawAll body JSR continuation',pc=draw_pc+ret,
        bank=(draw_at-16)//8192,bytes=list(draw[ret:ret+3]))
    source=MODULE.read_text()
    assert not re.search(r'\bemu\.(?:write\w*|setState|setInput|loadSavestate|reset|stop)\s*\(',source)
    assert 'removeMemoryCallback' not in source
    assert len(re.findall(r'\n hook\(C\.hooks\.',source)) == 14
    assert len(re.findall(r'\n memory\(',source)) == 5
    assert source.count('emu.addEventCallback(') == 2
    assert source.count('emu.addMemoryCallback(') == 1  # Wrapped registration only, used at startup.
    # Finite ownership negatives: same PC without the matching actual SP or
    # return word, bank, or interrupt depth must never qualify body completion.
    def owns(sp,word,bank,depth):
        return sp == 240 and word+1 == hooks['body_return']['pc'] and bank == 4 and depth == 0
    word=hooks['body_return']['pc']-1
    owner_controls=[owns(240,word,4,0),not owns(238,word,4,0),not owns(240,word+1,4,0),
                    not owns(240,word,12,0),not owns(240,word,4,1)]
    assert all(owner_controls)
    route.prepare(argparse.Namespace(rom=rom,output=OUT,frames=8000,expected_sha256=EXPECTED,
        identity='octopus',mode='easy',policy=Path(old['config']['policy']),replay=BASE/'inputs.csv'))
    ready_path=OUT/'ready.json';ready=json.loads(ready_path.read_text())
    cfg=ready['config'];before=old['config']
    allowed={'out','prefix','replay'}
    assert {k:v for k,v in cfg.items()if k not in allowed} == {k:v for k,v in before.items()if k not in allowed}
    probe=dict(ram=ram,scalars=SCALARS,hooks=hooks,first=3256,last=3266,row_cap=512,byte_cap=1_000_000)
    run=OUT/'run.lua';original=run.read_text()
    tail='dofile('+route.lua(route.SCRIPT.as_posix())+')\n'
    assert original.endswith(tail)
    addition='ROSTER_CONFIG.bass_close=dofile('+route.lua(MODULE.as_posix())+')(ROSTER_CONFIG.prefix,'+route.lua(probe)+')\n'
    run.write_text(original[:-len(tail)]+addition+tail,encoding='utf-8')
    assert run.read_text().replace(addition,'') == original
    controls=dict(passed=True,source_only=True,actual_body_call_pc=draw_pc+calls[-1],actual_body_return_hook=hooks['body_return'],
        call_bytes=needle.hex(),freeze_zero_tail_jmp_verified=True,rotated_final_rts_verified=True,
        expected_startup_callbacks=21,exec_callbacks=14,bus_callbacks=5,event_callbacks=2,
        callback_registration_runtime=False,owner_positive_negative_controls=len(owner_controls),
        actual_RAM_aliases=len(ram),source_arrays_length=28,
        Lua_runtime_control='No standalone Lua5.4 interpreter survives; no download/extraction/native was attempted. Actual Lua execution remains the forthcoming bounded Mesen run.',
        boundary_limits='Window may begin after a prior owner. Null earlier publication is retained; no synthetic epoch is supplied. RTS hooks are entry points, body hook is actual caller after RTS.')
    controls_path=OUT/'source-controls.json';controls_path.write_text(json.dumps(controls,indent=2)+'\n')
    deps={MODULE,Path(__file__).resolve(),controls_path,BASE/'ready.json',BASE/'result.json',BASE/'inputs.csv',
          BASE/'trace.csv',BASE/'events.jsonl',BASE/'captures.nesppuv1',BASE/'captures-index.jsonl',BASE/'review.json',
          ROOT/'src/metasprite_engine.s',ROOT/'src/parodius_render.s',ROOT/'src/parodius_adapter.s',ROOT/'src/roll_fast_render.s'}
    ready['bindings'].update({str(p):digest(p) for p in deps})
    ready['bindings'][str(run)]=digest(run)
    ready['passive_probe']=dict(config=probe,controls=str(controls_path),
        baseline=str(BASE),exact_replay=True,unchanged_shared_harness_sha256=digest(route.SCRIPT),
        baseline_decoded_full_sha256=json.loads((BASE/'review.json').read_text())['container']['decoded_full_sha256'],
        compare_after_run=['inputs.csv byteexact','trace.csv byteexact','events.jsonl byteexact','decoded full PPU stream SHA256 exact'],
        baseline_selected_epochs=[245,467,480,498,3604,4801],
        maximum_selected_epochs_new_run=8,proposed_additional_epochs=[3261,3263],
        source_probe_file='octopus-visibility.jsonl',source_probe_max_bytes=1_000_000,
        physical_attributes='Compare physical OAM attributes E3; preserve source/raw DMA writes unmasked.',
        intended_mutation='Host-only observer result metadata and one journal. No game/controller/config/guard change.',
        limitations=['No PPU pattern-fetch trace or background reconstruction. CHR IDs are actual mapper-state readbacks.',
                    'Source body before/after and actual store sequence need completed DMA linkage before any displayed-body claim.',
                    'No new native grant, screenshots or visual verdict from source readiness.'])
    ready_path.write_text(json.dumps(ready,indent=2)+'\n')
    command=OUT/'command.json';command.write_text(json.dumps(dict(command=ready['command'],launch=False),indent=2)+'\n')
    assert all(digest(p)==h for p,h in ready['bindings'].items())
    print(json.dumps(dict(prepared=True,native_run=False,ready=str(ready_path),ready_sha256=digest(ready_path),
                         bindings=len(ready['bindings']),command_file=str(command),command_sha256=digest(command)),indent=2))


if __name__=='__main__':
    prepare()
