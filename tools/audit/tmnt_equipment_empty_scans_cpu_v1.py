"""Strict assembled empty-scan renderer differential; no native timing claim."""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load, Memory, address, location
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU
from tmnt_native_storage_driver import ROOT, sha


def setup(b, cfg):
    m = Memory(b)
    entry = cfg.get('entry', 'TnDrawEquipment')
    m.page(1, (location(b, entry) - 16) // 8192)
    m.page(2, 88)
    def put(name, value, i=0): m[address(b, name) + i] = value & 255
    for i in range(256): m[0x200 + i] = (i * 73 + 29) & 255
    for i in range(8): put('R' + str(i), (91 + i * 23) & 255)
    seed = dict(SelectedCharacter=19, OperMode=1, GameEngineSubroutine=8,
                TnVariant=cfg.get('variant', 0), PlayerFacingDir=cfg.get('face', 1),
                Player_X_Position=128, Player_Y_Position=176, Player_PageLoc=0,
                CurrentBank=m.banks[1] | 128, CurrentBankC=216,
                CurrentOAMOffset=cfg.get('offset', 48), GuestOamRotationActive=cfg.get('rotate', 1),
                RgOamRotation=cfg.get('rotation', 0), ScreenLeft_X_Pos=cfg.get('scroll', 0),
                ScreenLeft_PageLoc=cfg.get('camera_page', 0), TnGearSelected=1,
                TnHudSelected=1, TnHudAmmo=cfg.get('hud_ammo', 99),
                VRAM_Buffer1_Offset=cfg.get('queue', 0), SmChrBank=604 & 255)
    seed.update(cfg.get('seed', {}))
    for name, value in seed.items(): put(name, value)
    for i in range(4):
        put('TnHealth', 128, i); put('TnEquipment', cfg.get('equipment', 2), i)
        put('TnAmmo', cfg.get('ammo', 99), i)
    for i in range(cfg.get('enemies', 2)):
        put('Enemy_Flag', 1, i); put('Enemy_ID', 6, i)
    for shot in cfg.get('shots', []):
        i, pose, kind = shot
        for name, value in dict(TnShotKind=kind, TnShotAnim=pose,
                                TnShotFace=cfg.get('face', 1), TnShotX=cfg.get('x', 128),
                                TnShotPage=cfg.get('page', 0), TnShotY=cfg.get('y', 176)).items(): put(name, value, i)
    for i, kind in cfg.get('drops', []):
        for name, value in dict(TnDropKind=kind, TnDropX=cfg.get('x', 128),
                                TnDropPage=cfg.get('page', 0), TnDropY=cfg.get('y', 176)).items(): put(name, value, i)
    for row in cfg.get('pickups', []):
        i, stamp, owner, code, actor, state, flag = row
        for name, value in dict(TnPickupStamp=stamp, InvPickupOwner=owner, InvPickup=code,
                                Enemy_ID=actor, Enemy_State=state, Enemy_Flag=flag,
                                Enemy_X_Position=cfg.get('x', 128), Enemy_PageLoc=cfg.get('page', 0),
                                Enemy_Y_Position=cfg.get('y', 176), Enemy_Y_HighPos=1, Enemy_SprAttrib=32).items(): put(name, value, i)
    if cfg.get('primary'):
        put('TnAttack', 1); put('TnPose', cfg['primary'], 1)
        put('TnSeq', 0x9c, 1); put('TnPhase', 0, 1)
    c = NesMPU(memory=m)
    c.pc, c.a, c.x, c.y, c.p, c.sp = address(b, entry), 85, 3, 7, cfg.get('flags', 0x60), 253
    m[510], m[511] = 255, 126; m.writes = []
    return c, m


def outcome(c, m):
    # Only discarded upper CPU stack is omitted. Full SMC, every ordinary RAM
    # byte, mapper state, ordered OAM and hardware/CHR publications are exact.
    ram = bytes(m[:0x1a0]) + bytes(m[0x200:0x8000])
    return (c.a, c.x, c.y, c.p & 207, c.sp, ram, tuple(m.banks),
            tuple((at, v) for at, v in m.writes if 0x200 <= at < 0x300 or 0x2000 <= at < 0x5c00))


def execute(b, cfg, stop=None):
    c, m = setup(b, cfg)
    trace, scans = [], Counter()
    q = qualified_cache[id(b)]
    hooks = {q['TnDrawEquipment', 'Drop']: 'drop', q['TnDrawEquipment', 'Pickup']: 'pickup'}
    for index in range(30000):
        if c.pc == (stop if stop is not None else 0x7f00): break
        if m.banks[1] == 87:
            if c.pc in hooks: scans[hooks[c.pc]] += 1
            if c.pc >= 0xb020: trace.append((c.pc, c.a, c.x, c.y, c.p, c.sp))
        c.step()
    else: raise AssertionError(('Renderer timeout', cfg, hex(c.pc), m.banks))
    return c, m, scans, trace


qualified_cache = {}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['baseline', 'candidate', 'output']: p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True)
    old, new = load(a.baseline), load(a.candidate)
    for b, path in [(old, a.baseline), (new, a.candidate)]: qualified_cache[id(b)] = qualified(path)
    rows, count = [], 0
    def check(tag, cfg):
        nonlocal count
        c, m, scans, _ = execute(old, cfg)
        d, n, nscans, _ = execute(new, cfg)
        left, right = outcome(c, m), outcome(d, n)
        assert left == right, (tag, cfg, left[:5], right[:5],
            [(hex(i), m[i], n[i]) for i in range(0x8000) if not 0x1a0 <= i < 0x200 and m[i] != n[i]][:20])
        populated = bool(cfg.get('drops') or any(p[1] for p in cfg.get('pickups', [])))
        if populated: assert scans == nscans, (tag, 'Populated scan lost', scans, nscans)
        elif scans: assert not nscans, (tag, 'Empty scans were not skipped', scans, nscans)
        count += 1
        rows.append(dict(tag=tag, cfg=cfg, baseline_cycles=c.processorCycles, candidate_cycles=d.processorCycles,
                         delta=d.processorCycles-c.processorCycles, scan_entries=dict(scans), candidate_scan_entries=dict(nscans)))
    flags = [0x20 | ((i & 3)) | ((i & 4) << 0) | ((i & 8) << 0) | ((i & 16) << 2) | ((i & 32) << 2) for i in range(64)]
    assert len(set(flags)) == 64
    # Every full-world source record, both facings, all relevant edge/rotation
    # and OAM-overflow controls. P is rotated across its full physical domain.
    for pose, face, edge in itertools.product(range(84), [1,2], range(8)):
        x,y,page,off,rotate,rotation = [(128,176,0,48,1,0),(0,0,0,0,0,0),(7,24,0,240,1,4),
            (8,23,0,248,1,128),(255,255,0,252,1,252),(128,176,1,255,1,255),
            (128,0,0,1,0,0),(255,24,255,16,1,128)][edge]
        check('all-world-records', dict(shots=[(2,pose,2)], face=face,x=x,y=y,page=page,offset=off,
              rotate=rotate,rotation=rotation,flags=flags[(pose*16+face*8+edge)%64]))
    for entry, face, primary, flag in itertools.product(['TnDraw','TnDrawDispatch'],[1,2],[0,1,12,24],flags):
        check('real-farcall-continuation',dict(entry=entry,face=face,primary=primary,flags=flag,shots=[(0,73,2),(1,74,2),(2,75,2)],hud_ammo=98))
    for gear,equipment,ammo,queue,enemy_count in itertools.product([0,1],[0,1,2,3,4],[0,1,9,10,99,128,255],[0,77,78,83,255],[0,2,6]):
        check('hud-and-empty-groups',dict(seed={'TnGearSelected':gear},equipment=equipment,ammo=ammo,queue=queue,enemies=enemy_count,hud_ammo=98,
              shots=[(0,73,2)],flags=flags[count%64]))
    for i,kind,edge in itertools.product(range(4),[1,2,3,4],range(3)):
        check('each-nonzero-drop',dict(drops=[(i,kind)],x=[128,7,255][edge],y=[176,24,255][edge],offset=[48,248,255][edge],flags=flags[count%64]))
    for i,stamp,state,owner,code,actor,flag in itertools.product(range(6),[1,4,255],[0,1,2,128],range(2),range(2),range(2),[0,1,255]):
        check('private-stamp-owner-controls',dict(pickups=[(i,stamp,19 if owner else 18,0xb4 if code else 0xb3,0x2e if actor else 6,state,flag)],flags=flags[count%64]))
    for face,offset,rotation in itertools.product([1,2],[0,128,240,248,252,255],[0,4,128,252,255]):
        check('all-populated',dict(face=face,offset=offset,rotation=rotation,drops=[(i,1+i%3) for i in range(4)],
              pickups=[(i,4,19,0xb4,0x2e,128,1) for i in range(6)],shots=[(0,60,3),(1,72,4),(2,75,2)],flags=flags[count%64]))
    for sub,dead in itertools.product([0,7,8,9],[0,1]):
        check('early-controls',dict(seed={'GameEngineSubroutine':sub,'MmDeathFlag':dead}))
    (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
    grouped = {}
    for tag in sorted({r['tag'] for r in rows}):
        rr=[r for r in rows if r['tag']==tag]; ds=[r['delta'] for r in rr]
        grouped[tag]=dict(cases=len(rr),min_delta=min(ds),max_delta=max(ds),total_delta=sum(ds))
    proof=dict(passed=True,source_only=True,native_run=False,baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),cases=count,
        all_source_world_entries=168,full_caller_flags=64,grouped=grouped,full_final_AXYP_SP_RAM_SMC_banks_ordered_OAM_hardware_exact=True,
        omitted_memory_only_discarded_stack='01A0..01FF',populated_scans_exact=True,checker_sha256=sha(Path(__file__)),
        limits='Arranged CPU states, including actual compiled caller continuations. No PPU/DMC DMA clocks or native cadence/recovered-draw claim. Dead A/C before the icon tail are not asserted identical; complete final ABI and every ordinary RAM byte are exact.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof),flush=True)


if __name__=='__main__': main()
