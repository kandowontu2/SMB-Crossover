"""Finite real-CPU RCR successor/palette/OAM/interrupt contracts; no native claim."""
from pathlib import Path
import hashlib
import itertools
import json
import sys

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from prepare_river_city_controls import fresh, address
from prepare_river_city_assets import POSES, decode
from prepare_river_city_reference import NATIVE, native_pixels
from verify_native_relocation import NesMPU


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    rom = R/'build/river-city-palette-private-v3.nes'
    assert sha(rom) == 'd83fe8ac8aec86b2f5835bab7a7e7dcd32f68d1f83287a1a5dbb4212e59e825b'
    output = R/'build/river-city-palette-runtime-controls-v3.json'
    assert not output.exists()
    bundle = scoped_load(rom)
    base = scoped_load(R/'build/roster-expansion-mac-pipe-corner-v3.nes')
    original = NATIVE.read_bytes()
    chrbase = 16+1048576
    rows, palette, irq = [], [], []
    for variant, face, pose, outlines in itertools.product((0,1), (1,2), range(18), (0,1)):
        q = fresh(bundle, variant)
        q.put(PlayerFacingDir=face, PlayerOutlinesOff=1-outlines,
              OutlineSourceHi=204, OutlineTinyHi=204, CurrentOAMOffset=0)
        q.array('OutlineTinyHi', [204]*4)
        q.array('CurrentCHRBank', [99,100,101,102])
        q.array('X5ChrMode', [129]*4)
        c, _ = q.invoke('RcSetPose', x=pose)
        cycles = c.processorCycles
        ptr = q.get('SmPosePtr')+256*q.get('SmPosePtr',1)
        assert q.get('RcPose') == pose
        if outlines:
            assert ptr == address(bundle, 'OutlinePoseBuffer')
            assert q.get('OutlineSourceHi') == 0
            assert [q.get('OutlineTinyHi',i) for i in range(4)] == [0]*4
        else:
            assert 0xcb80 <= ptr < 0xd9b8
        c, _ = q.invoke('RcPublish')
        cycles += c.processorCycles
        assert [q.get('CurrentCHRBank',i) for i in (2,3)] == [101,102]
        assert [q.get('X5ChrMode',i) for i in (2,3)] == [129,129]
        assert q.get('X5ChrMode') == 130
        if outlines:
            assert q.get('X5ChrMode',1) == 130
        else:
            assert q.get('CurrentCHRBank',1) == 100 and q.get('X5ChrMode',1) == 129
        q.put(ReloadCHRBank=0)
        q.invoke('RcPublish')
        assert q.get('ReloadCHRBank') == 0, 'No unchanged CHR publication'
        q.put(R0=ptr & 255, R1=ptr >> 8, R3=0, R4=96, R5=0,
              R6=96, R7=1, GuestOamRotationActive=0)
        c, _ = q.invoke('MetaspriteRenderLoop')
        cycles += c.processorCycles
        assert c.p & 1
        count = q.get('CurrentOAMOffset')//4
        assert count <= 14
        pixels = {}
        for part in range(count-1,-1,-1):
            tt, aa = q.get('Sprite_Tilenumber',part*4), q.get('Sprite_Attributes',part*4)
            xx, yy = q.get('Sprite_X_Position',part*4)-96, q.get('Sprite_Y_Position',part*4)-96
            window = tt//64
            page = q.get('CurrentCHRBank',window)+256*(q.get('X5ChrMode',window)&3)
            offset = chrbase+page*1024+(tt%64)*16
            pattern = decode(bundle['raw'][offset:offset+32])
            for y in range(16):
                for x in range(8):
                    value = pattern[y][7-x if aa & 64 else x]
                    if value:
                        assert aa & 3 in (0,3)
                        pixels[xx+x,yy+y] = 1 if aa & 3 == 3 else {1:3,2:2,3:4}[value]
        source, _, _ = native_pixels(original, POSES[pose][1], variant, face)
        expected = {p:v for p,v in source.items() if outlines or v != 1}
        assert pixels == expected, (variant,face,pose,outlines)
        rows.append(dict(variant=variant,face=face,pose=pose,outlines=outlines,
                         opaque_pixels=len(pixels),parts=count,cycles=cycles))
    # Exact old world-palette conflict and bounded queue-success acknowledgement.
    q = fresh(base)
    q.put(VRAM_Buffer1_Offset=0)
    q.invoke('RcColors')
    at = address(base,'VRAM_Buffer1')
    assert bytes(q.m[at+6:at+9]) == bytes.fromhex('3f1903')
    for offset, star, power in itertools.product(range(85),(0,1),(0,1)):
        q = fresh(bundle)
        at = address(bundle,'VRAM_Buffer1')
        q.m[at:at+100] = [0xa5]*100
        q.put(VRAM_Buffer1_Offset=offset,StarInvincibleTimer=star,
              GuestPowerupActive=power,RcPalette=0)
        q.invoke('RcQueuePalette')
        accepted = offset < 78 and not (star or power)
        assert q.get('VRAM_Buffer1_Offset') == offset+(6 if accepted else 0)
        assert q.get('RcPalette') == int(accepted)
        if accepted:
            assert bytes(q.m[at+offset:at+offset+7]) == bytes.fromhex('3f110330261100')
        assert bytes(q.m[at:at+offset]) == bytes([0xa5])*offset
        tail = offset+7 if accepted else offset
        assert bytes(q.m[at+tail:at+100]) == bytes([0xa5])*(100-tail)
        palette.append(dict(offset=offset,star=star,transform=power,accepted=accepted))
    # Actual interrupt RTI paths at each reached unique SetPose/Publish boundary.
    for name in ('RcSetPose','RcPublish'):
        q = fresh(bundle,1)
        q.put(PlayerFacingDir=2,PlayerOutlinesOff=0)
        points = set()
        saved = NesMPU.step
        def collect(c):
            if q.m.banks[1] == 81 and 0xa300 <= c.pc < 0xb200:
                points.add(c.pc)
            saved(c)
        NesMPU.step = collect
        try:
            if name == 'RcPublish':
                q.invoke('RcSetPose',x=14)
                points.clear()
            q.invoke(name,x=14)
        finally:
            NesMPU.step = saved
        # Record the complete uninterrupted leaf result, separately from the
        # shadow/hardware disagreement in the two bank-switch instructions.
        def snapshot(q,c):
            fields = ['SmPosePtr','SmPosePtr','SmChrBank','ObjectMetasprite',
                      'CurrentBank','CurrentBankC','CurrentOAMOffset','X5WideChrActive',
                      'ReloadCHRBank','OutlineSourceHi']
            values = [q.get(n,1 if i == 1 else 0) for i,n in enumerate(fields)]
            arrays = [(0x5c00,128), (address(bundle,'OutlinePoseBuffer'),129),
                      (address(bundle,'OutlineTinyHi'),4),
                      (address(bundle,'CurrentCHRBank'),4), (address(bundle,'X5ChrMode'),4)]
            return (c.a,c.x,c.y,c.p&0xcf,c.sp,list(q.m.banks),values,
                    [bytes(q.m[start:start+length]).hex() for start,length in arrays])
        control = fresh(bundle,1)
        control.put(PlayerFacingDir=2,PlayerOutlinesOff=0)
        if name == 'RcPublish':
            control.invoke('RcSetPose',x=14)
        control_cpu,_ = control.invoke(name,x=14)
        expected_final = snapshot(control,control_cpu)
        for point, kind in itertools.product(sorted(points),('NMI','IRQ')):
            q = fresh(bundle,1)
            q.put(PlayerFacingDir=2,PlayerOutlinesOff=0)
            if name == 'RcPublish':
                q.invoke('RcSetPose',x=14)
            fired = [False]
            def step(c):
                if not fired[0] and c.pc == point and q.m.banks[1] == 81:
                    fired[0] = True
                    before = (c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(q.m.banks),
                              q.get('CurrentBank'),q.get('CurrentBankC'))
                    smc = [address(bundle,n)+1 for n in
                           ('NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC')]
                    smc += [address(bundle,'FarcallJmpTarget_SMC')+2]
                    smc_before = [q.m[a] for a in smc]
                    if kind == 'NMI':
                        c.nmi()
                    else:
                        c.stPushWord(c.pc)
                        c.stPush(c.p&~c.BREAK|c.UNUSED)
                        c.p |= c.INTERRUPT
                        c.pc = address(bundle,'IrqScrollSplit')
                    for _ in range(20000):
                        saved(c)
                        if c.pc == before[5] and c.sp == before[4]:
                            break
                    else:
                        raise AssertionError('RTI timeout')
                    after = (c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(q.m.banks),
                             q.get('CurrentBank'),q.get('CurrentBankC'))
                    if name == 'RcSetPose' and kind == 'NMI' and point in (
                            address(bundle,'RcSetPose')+5,address(bundle,'RcSetPose')+7):
                        # Exact macro bytes: LDA#C6; STACurrentBankC;
                        # LDA#C6; STA$5116. The NMI restores the newly published
                        # destination at these two legal transition boundaries.
                        want = list(before)
                        want[6] = list(before[6])
                        want[6][2] = before[8]&127
                        assert tuple(want) == after, (name,point,kind,before,after)
                    else:
                        assert before == after, (name,point,kind,before,after)
                    assert smc_before == [q.m[a] for a in smc]
                saved(c)
            NesMPU.step = step
            try:
                c,_ = q.invoke(name,x=14)
            finally:
                NesMPU.step = saved
            assert fired[0]
            assert snapshot(q,c) == expected_final, ('complete continuation',name,point,kind)
            irq.append(dict(routine=name,PC=point,kind=kind))
    seg = next(x for x in bundle['segs'].values() if x['name'] == '"RIVER_CITY_CORE"')
    paths = [Path(__file__), rom, rom.with_suffix('.dbg'), rom.with_suffix('.lbl'),
             R/'build/roster-expansion-mac-pipe-corner-v3.nes',
             R/'build/roster-expansion-mac-pipe-corner-v3.dbg', NATIVE,
             R/'src/river_city_shared_palette_render.inc', R/'src/river_city_shared_palette_art.inc',
             R/'src/river_city_core.s', R/'src/river_city_combat.s', R/'src/river_city_state.inc',
             R/'chr/characters/river-city-shared-palette.chr',
             R/'build/river-city-palette-runtime-v3-overlay/runtime-build.json']
    proof = dict(passed=True,native_run=False,scope=__doc__,ROM_sha256=sha(rom),
                 complete_native_source_pixel_maps=rows,queue_controls=palette,
                 actual_IRQ_NMI_boundaries=irq,CORE_bytes=int(seg['size'],0),
                 old_world_palette2_write_reproduced=True,
                 bank_transition_scope='At exact RcSetPose+5/+7 NMI restores the newly published C70 shadow before the pending STA5116; full continuation AXYP/SP/owned state/banks matches uninterrupted. Five SMC operands exact at every RTI.',
                 limits=['Finite CPU/source masks and role indices; actual PPU colors/menu/gameplay unqualified.',
                         'All-area black ink hue and full caller/scene/cadence remain integration obligations.'],
                 bindings=[dict(path=str(p),sha256=sha(p)) for p in paths])
    output.write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=True,frames=len(rows),queue_cases=len(palette),
                          interrupt_boundaries=len(irq),CORE_bytes=proof['CORE_bytes'],
                          maximum_cycles=max(x['cycles'] for x in rows))))


if __name__ == '__main__':
    main()
