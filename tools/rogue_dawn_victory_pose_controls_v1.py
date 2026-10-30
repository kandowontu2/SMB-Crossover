"""Actual source art/OAM and unchanged movement-state proof for victory draw."""
from pathlib import Path
import itertools
import json
import sys
import traceback

R = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R/'tools'), str(R/'tools/audit')]
import rogue_dawn_flagpole_controls_v1 as base
import rogue_dawn_host_body_controls_v1 as body
from check_tmnt_render_oa import location
from verify_native_relocation import NesMPU

v, q, get, put, address = base.v, base.q, base.get, base.put, base.address
P = R/'build/rogue-dawn-flagpole-v1'
O = R/'build/rogue-dawn-victory-pose-v4'


def state(m):
    return bytes(m[0x5c00:0x5c80]), bytes(m[0x5fb0:0x5fb8])


def graphics(bundle, engine, frame, facing, alt=0):
    m = base.fixture(bundle)
    put(m, GameEngineSubroutine=engine, RdAnimFrame=frame, RdFacing=facing,
        RdSourceAltPalette=alt, RdColorRequest=0)
    c, z = q.invoke(m, 'RdBodyGraphics')
    output = {n:get(m,n) for n in ['ObjectMetasprite','SmChrBank','CurrentCHRBank','X5ChrMode','X5WideChrActive']}
    output['pointer'] = get(m,'SmPosePtr')+256*get(m,'SmPosePtr',1)
    return m, c, z, output


def draw_complete(m, frame, face):
    """Current integrated DrawAll: only the genuine shot-slot scratch changes."""
    b = m.bundle
    body.vis(m)
    put(m,RdAnimFrame=frame,RdFacing=face,PlayerFacingDir=face+1,Player_SprAttrib=0,
        CurrentOAMOffset=0,Player_X_Position=120,Player_Y_Position=144,Player_PageLoc=0,
        ScreenLeft_X_Pos=0,Player_Y_HighPos=1,DisableScreenFlag=0)
    for i in range(0,256,4): m[address(b,'Sprite_Data')+i]=248
    # Include the actual visibility predecessor; F7 used to skip RdBodyGraphics.
    q.invoke(m,'PlayerGfxHandler')
    before = state(m)
    consumed, scratch_writes = [], []
    start=location(b,'RdWxDraw')
    needle=bytes([0x8e])+address(b,'RdSlot').to_bytes(2,'little')
    code=b['raw'][start:start+180]
    assert code.count(needle)==1
    slot_pc=address(b,'RdWxDraw')+code.index(needle)
    original=NesMPU.step
    def step(c):
        bank=m.banks[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1
        if c.pc==address(b,'HpNativePointerEnd') and bank==4 and c.y==0:
            ptr=get(m,'R0')+256*get(m,'R1')
            consumed.append(dict(C=m.banks[2],pointer=ptr,header=m[ptr],SP=c.sp))
        previous=get(m,'RdSlot')
        pc=c.pc
        original(c)
        if get(m,'RdSlot')!=previous:
            assert pc==slot_pc and bank==121, ('unexpected source scratch writer',pc,bank)
            scratch_writes.append(dict(PC=pc,bank=bank,value=get(m,'RdSlot')))
    NesMPU.step=step
    try:
        c,_=q.invoke(m,'PlayerOAMReservation')
        put(m,CurrentOAMOffset=c.a)
        q.invoke(m,'DrawAllMetasprites')
    finally:
        NesMPU.step=original
    expected=bytearray(before[0]); expected[address(b,'RdSlot')-0x5c00]=0xf0
    assert state(m)==(bytes(expected),before[1]), 'Full source state, except typed slot iterator, must remain unchanged'
    assert [z['value']for z in scratch_writes]==[0xd0,0xe0,0xf0]
    return consumed,scratch_writes


def main():
    assert not (O/'controls.json').exists()
    build = json.loads((O/'build.json').read_text())
    for z in build['bindings']:
        assert v.ref.binding(z['path']) == z, z['path']
    old, b = v.scoped_load(P/'candidate.nes'), v.scoped_load(O/'candidate.nes')
    frames = [i for i in range(106) if b['raw'][location(b,'RdBodyIndex0')+i] != 255]
    frames += [106, 247, 255]
    proof = dict(passed=False, source_CPU_only=True, native_run=False, checks={})
    checks = proof['checks']
    try:
        rows = []
        for engine, frame, face, alt in itertools.product(range(12),frames,[0,1],[0,1]):
            a, ca, za, out_a = graphics(old,engine,frame,face,alt)
            m, c, z, out = graphics(b,engine,frame,face,alt)
            assert state(m) == state(a), ('source state',engine,frame,face,alt)
            if engine in [4,5] and not alt:
                ref, _, _, expected = graphics(old,engine,8,face)
                assert out == expected, ('authentic standing',engine,frame,face,out,expected)
                assert out['ObjectMetasprite'] == address(b,'METASPRITE_SAMUS_BODY')
            else:
                assert out == out_a and base.application(m) == base.application(a), ('foreign phase',engine,frame,face,alt)
            rows.append(dict(engine=engine,source_frame=frame,facing=face,unsupported_palette=alt,
                             source_context_unchanged=True,CPU=z['CPU'],minimum_SP=z['minimum_SP']))
        checks['all_supported_and_empty_source_frames_phases_faces_palette_contract'] = rows
        print('source state/art matrix PASS',len(rows),flush=True)
        # Actual full native DrawAll consumers, preserving all source state.
        rows = []
        for engine, frame, face in itertools.product([4,5],[3,8,12,35,247],[0,1]):
            output=[]
            for bundle, selected in [(old,8),(b,frame)]:
                m=base.fixture(bundle)
                put(m,GameEngineSubroutine=engine,RdColorRequest=0)
                consumed,scratch=draw_complete(m,selected,face)
                pixels,record=body.decoded_body(m,8,face)
                output.append((pixels,record,consumed,scratch))
            assert output[0][:2] == output[1][:2]
            assert output[1][2] and all(z['C']==94 for z in output[1][2])
            rows.append(dict(engine=engine,source_frame=frame,facing=face,
                             exact_authentic_opaque_pixels=len(output[1][0]),
                             genuine_pointer_consumers=output[1][2],typed_slot_iterator_writes=output[1][3]))
        checks['20_complete_DrawAll_authentic_standing_OAM_pixels_source_context'] = rows
        print('20 actual DrawAll consumers PASS',flush=True)
        rows=[]
        for mode,keys in itertools.product([0,1],[0,1,128,129,64]):
            pair=[]
            for bundle in [old,b]:
                m=base.side.base.ready(bundle,mode)
                put(m,SavedJoypadBits=keys)
                c,z=q.mainstep(m);n=q.wake(m)
                pair.append((base.registers(c),base.application(m),q.physical(m),z['CPU'],n['CPU']))
            assert pair[0][:3]==pair[1][:3] and pair[0][4]==pair[1][4],('real Main',mode,keys)
            rows.append(dict(mode=mode,keys=keys,Main_CPU_delta=pair[1][3]-pair[0][3],NMI_CPU_delta=pair[1][4]-pair[0][4]))
        checks['10_complete_active_Rogue_Main_NMI_exact_state_registers'] = rows
        rows=[]
        for char,mode in itertools.product(range(24),[0,1]):
            pair=[]
            for bundle in [old,b]:
                m=q.make(bundle,mode)
                put(m,SelectedCharacter=char,RdVariant=0,SavedJoypadBits=1)
                c,z=q.mainstep(m);n=q.wake(m)
                pair.append((base.registers(c),base.application(m),q.physical(m),z['CPU'],n['CPU']))
            assert pair[0][:3]==pair[1][:3] and pair[0][4]==pair[1][4],('foreign full Main',char,mode)
            rows.append(dict(character=char,mode=mode,application_registers_maps_NMI_exact=True,
                             Main_CPU_delta=pair[1][3]-pair[0][3]))
        checks['48_foreign_complete_Main_NMI_exact_application_and_NMI_cost'] = rows
        rows=[]
        for engine,kind in itertools.product([4,5,8],['NMI','IRQ']):
            m=base.fixture(b)
            put(m,GameEngineSubroutine=engine,RdAnimFrame=247,NmiDisable=255)
            c,z=q.invoke(m,'RdBodyGraphics',cut=(address(b,'RdVictoryPublishChr'),95,kind))
            assert z['minimum_SP']>=128
            rows.append(dict(engine=engine,interrupt=kind,minimum_SP=z['minimum_SP'],proof=q.summary(z['interrupt'])))
        checks['6_actual_vector_ISR_body_publication_seams'] = rows
        proof.update(passed=True,ROM=v.ref.binding(O/'candidate.nes'),
                     bindings=[v.ref.binding(p) for p in [Path(__file__),O/'build.json',O/'candidate.nes',
                         O/'candidate.dbg',O/'candidate.lbl',R/'tools/rogue_dawn_flagpole_controls_v1.py',
                         R/'tools/rogue_dawn_host_body_controls_v1.py']],
                     limits=['Source/art/full-caller CPU evidence; displayed victory sequence still requires exact-candidate native review.',
                             'Automatic castle motion uses a standing pose as an explicit SMB adaptation; no original Rogue castle sequence exists.'])
    except Exception as e:
        proof.update(error=repr(e),traceback=traceback.format_exc())
        i=1
        while (O/f'controls-negative-{i}.json').exists(): i+=1
        (O/f'controls-negative-{i}.json').write_text(json.dumps(proof,indent=2)+'\n')
        raise
    (O/'controls.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=True,counts={k:len(v)for k,v in checks.items()})))


if __name__ == '__main__':
    main()
