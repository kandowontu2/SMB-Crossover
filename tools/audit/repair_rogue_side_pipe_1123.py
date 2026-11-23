"""Restore Rogue's missing ordinary sideways-pipe transaction, in memory.

Focused CPU fixtures disclose their geometry setup. They are not natural
acquisition or Mesen evidence. The retained earned-route controller is untouched.
"""

from hashlib import sha256
import json
from pathlib import Path
import re
from unittest.mock import patch

from py65.assembler import Assembler

import run_rogue_screw_native_1122 as Route
import inspect_rogue_missile_targets_cb95_1116 as Engine


PARENT = '59e1a591d5ea31d62dafa9332990598b74b5b0852194ef7cc7ad22788196b723'
CANDIDATE = '1319c2ef0032e86af897df63cca682a61d35d8da7b96205fe974b5d316805196'
BANK = 95
FIRST_PC, SECOND_PC = 0xAFF7, 0xBEEB
FIRST = bytes.fromhex(
    'ac3e058898051ed010a038208b95c91cf00bc91fd00320ee9cad0e5c604cebbe')
SECOND = bytes.fromhex('c8208b95c91ff0034c10b04c0db0')
LEGACY_UNQUALIFIED = '36dc96b630a3cac9a35d0a03a0c1c4c05bace6eac7fd1d51d973424c69566a66'
# Runs under RdNonSolidBG's existing AX/Y and six-private-cell save. The
# initial upper probe is the native standing right query (+14,+8). A legal
# grounded Morph body is seven pixels lower; this query then sees the same
# lower1F tile as its native ball query. Upper1C requires the real lower1F.
# These are ordinary sideways-pipe semantics only, not a physical resolver.
HOOK_OLD = bytes.fromhex('ad0e5c290fc906904bc90ab047')
HOOK_NEW = bytes.fromhex('20f7af')
ROM = Route.ROM
N, W = Engine.N, Route.Base.W


def H(data):
    return sha256(data).hexdigest()


def file_at(pc):
    return 16+BANK*8192+(pc&8191)


def bundle(raw):
    assert H(raw) == PARENT
    return Route.bundle(raw)[2]


def spans(raw):
    assert H(raw) == PARENT
    bank = raw[16+BANK*8192:16+(BANK+1)*8192]
    matches = [m.start() for m in re.finditer(re.escape(HOOK_OLD), bank)]
    assert len(matches) == 1
    hook = 16+BANK*8192+matches[0]
    assert hook == file_at(0xBF5F), hex(0xA000+matches[0])
    assert raw[file_at(FIRST_PC):file_at(FIRST_PC)+33] == b'\xff'*33
    assert raw[file_at(SECOND_PC):file_at(SECOND_PC)+15] == b'\xea'*15
    return ((hook, raw[hook:hook+3], HOOK_NEW),
            (file_at(FIRST_PC), b'\xff'*len(FIRST), FIRST),
            (file_at(SECOND_PC), b'\xea'*len(SECOND), SECOND))


def _compose(raw):
    image = bytearray(raw)
    for at, old, new in spans(raw):
        assert image[at:at+len(old)] == old and len(old) == len(new)
        image[at:at+len(new)] = new
    return bytes(image)


def compose(raw):
    result = _compose(raw)
    assert CANDIDATE and H(result) == CANDIDATE
    return result


def restore_pipe_bytes(raw):
    """Undo the three owned spans. The caller authenticates the full ROM."""
    restored = bytearray(raw)
    # These addresses/preimages are fixed by the authenticated parent spans.
    for pc, old, new in ((0xBF5F, HOOK_OLD[:3], HOOK_NEW),
                         (FIRST_PC, b'\xff'*len(FIRST), FIRST),
                         (SECOND_PC, b'\xea'*len(SECOND), SECOND)):
        at = file_at(pc)
        assert restored[at:at+len(new)] == new
        restored[at:at+len(new)] = old
    return bytes(restored)


def inverse(raw):
    assert CANDIDATE and H(raw) == CANDIDATE
    restored = restore_pipe_bytes(raw)
    assert H(restored) == PARENT and compose(restored) == raw
    return restored


def metadata(raw):
    result = compose(raw)
    rows = spans(raw)
    owned = {i for at, old, _ in rows for i in range(at, at+len(old))}
    changed = {i for i, (a, b) in enumerate(zip(raw, result, strict=True)) if a != b}
    assert changed <= owned and inverse(result) == raw
    legacy=bytearray(raw)
    legacy_first=bytes.fromhex('a4338898051ed010a038208b95c91cf00bc91fd00320ee9cad0e5c604cebbe')
    legacy_second=bytes.fromhex('c8208b95c91ff0034c0fb04c0cb0')
    for pc,code in ((0xBF5F,HOOK_NEW),(FIRST_PC,legacy_first),(SECOND_PC,legacy_second)):
        legacy[file_at(pc):file_at(pc)+len(code)]=code
    assert H(legacy)==LEGACY_UNQUALIFIED
    return dict(parent_SHA256=PARENT, candidate_SHA256=CANDIDATE,
                owned_bytes=len(owned), changed_bytes=len(changed),
                unchanged_outside_owned_spans=True, exact_inverse=True,
                prior_unqualified_proposal=dict(SHA256=LEGACY_UNQUALIFIED,
                    reproducible_exactly_in_memory=True,
                    rejected_reason='Symbolic assembly detects moving-direction33 instead of actual PlayerFacingDir053E; no candidate CPU PASS'),
                ROM_files_written=0, RAM_allocated=0, native=False,
                spans=[dict(offset=at, before=old.hex(), after=new.hex())
                       for at, old, new in rows])


def rebind(m, raw):
    m.bundle = dict(m.bundle, raw=raw)
    for window, tag in enumerate(tuple(m.rawtags)):
        if tag&128:
            m.raw_page(window, tag)
    return m


def put(m, **values):
    for name, value in values.items():
        m[W.address(m.bundle, name)] = value


def tile(m, x, y, value):
    name = 'Block_Buffer_2' if (x//256)&1 else 'Block_Buffer_1'
    m[W.address(m.bundle, name)+(x&255)//16+(y-32)//16*16] = value


def fixture(seed, raw, *, x=2643, y=129, state=0, face=1, top=0x1c,
            bottom=0x1f, page=1, engine=8):
    m = rebind(N.fork(seed), raw)
    put(m, WorldNumber=0, LevelNumber=1, AreaType=2,
        Player_X_Position=x&255, Player_PageLoc=x//256,
        Player_Y_Position=y, Player_Y_HighPos=page,
        Player_State=state, PlayerFacingDir=face,
        RdX=(x+8)&255, RdRoomHi=(x+8)//256, RdY=(y+16)&255,
        RdRadiusX=4, RdRadiusY=8 if y==136 else 15,
        RdAction=3 if y==136 else 1, RdGravity=0 if state==0 else 1,
        GameEngineSubroutine=engine, ScreenLeft_PageLoc=9, ScreenRight_PageLoc=11,
        Player_SprAttrib=0, Square1SoundQueue=0, ChangeAreaTimer=0)
    for name in ('Block_Buffer_1', 'Block_Buffer_2'):
        at = W.address(m.bundle, name)
        m[at:at+208] = bytes(208)
    tile(m, 2656, 128, top)
    tile(m, 2656, 144, bottom)
    for xx in range(2592, 2721, 16):
        tile(m, xx, 160, 0x61)
    return m


def invoke(m, name, cut=None, **registers):
    trace = []
    interrupts=[]
    previous = N.NesMPU
    class CPU(previous):
        def step(self):
            if self.pc>=0x8000:
                key=(self.pc, self.memory.rawtags[(self.pc-0x8000)//8192]&127)
                if key not in trace:
                    trace.append(key)
                if cut and key==cut[:2] and not interrupts:
                    snapshot=(self.pc,self.sp,self.a,self.x,self.y,self.p&0xef,
                              tuple(self.memory.rawtags),bytes(self.memory[0x15a:0x17b]),
                              bytes(self.memory[0x5c00:0x5c80]))
                    if cut[2]=='NMI':
                        self.nmi()
                    else:
                        self.stPushWord(self.pc)
                        self.stPush(self.p&~self.BREAK|self.UNUSED)
                        self.p|=self.INTERRUPT
                        self.pc=W.address(self.memory.bundle,'IrqScrollSplit')
                    low=self.sp
                    for _ in range(50000):
                        previous.step(self);low=min(low,self.sp)
                        if (self.pc,self.sp)==snapshot[:2]:
                            break
                    else:
                        raise AssertionError(('Bounded real interrupt',cut,hex(self.pc)))
                    after=(self.pc,self.sp,self.a,self.x,self.y,self.p&0xef,
                           tuple(self.memory.rawtags),bytes(self.memory[0x15a:0x17b]),
                           bytes(self.memory[0x5c00:0x5c80]))
                    assert after==snapshot,('Interrupt context',cut,snapshot,after)
                    interrupts.append(dict(kind=cut[2],PC=cut[0],bank=cut[1],minimum_SP=low,
                                           registers_maps_SMC_private_image_exact=True))
            return super().step()
    with patch.object(N, 'NesMPU', CPU):
        cpu = N.invoke(m, name, **registers)
    if cut:
        assert len(interrupts)==1,('Unreached interrupt seam',name,cut)
        cpu['interrupt']=interrupts[0]
    return cpu, trace


def inspect_parent(raw):
    b = bundle(raw)
    seed = Route.cold(raw)
    m = fixture(seed, raw)
    probes = []
    for index in (56, 57):
        c, _ = invoke(m, 'BlockBufferColli_Side', y=index)
        probes.append(dict(index=index, x=2657, y=129+(8 if index==56 else 24), tile=c['A']))
    assert [row['tile'] for row in probes] == [0x1c, 0x1f], probes
    q = fixture(seed, raw)
    old, trace = invoke(q, 'RdNonSolidBG')
    assert N.get(q, 'GameEngineSubroutine') == 8
    assert (W.address(b, 'PipeDwnS'), 126) not in trace
    native = fixture(seed, raw)
    result, native_trace = invoke(native, 'CheckSideMTiles', a=0x1f)
    assert N.get(native, 'GameEngineSubroutine') == 2
    assert (W.address(b, 'PipeDwnS'), 126) in native_trace
    return seed, dict(parent_SHA256=PARENT, probes=probes,
                     parent_semantic_missing=True, unchanged_native_handler_enters=True,
                     native_engine=N.get(native, 'GameEngineSubroutine'),
                     native_timer=N.get(native, 'ChangeAreaTimer'),
                     native_sound=N.get(native, 'Square1SoundQueue'),
                     fixture_scope='Captured legal pose/observed native metatiles are component setups; no natural route claim.')


def assembly_proof(b):
    def z(name):
        value=W.address(b,name)
        return '$%02X'%value if value<256 else '$%04X'%value
    assembler=Assembler(N.NesMPU())
    def code(pc, lines):
        out=bytearray()
        for line in lines:
            part=assembler.assemble(line,pc+len(out))
            out.extend(part)
        return bytes(out)
    first=[
        'LDY '+z('PlayerFacingDir'),'DEY','TYA','ORA '+z('Player_State'),
        'BNE $B010','LDY #$38','JSR '+z('BlockBufferColli_Side'),
        'CMP #$1C','BEQ $B014','CMP #$1F','BNE $B010',
        'JSR '+z('PipeDwnS'),'LDA '+z('RdX'),'RTS','JMP $BEEB']
    second=['INY','JSR '+z('BlockBufferColli_Side'),'CMP #$1F',
            'BEQ $BEF6','JMP $B010','JMP $B00D']
    assert code(FIRST_PC,first)==FIRST,code(FIRST_PC,first).hex()
    assert code(SECOND_PC,second)==SECOND,code(SECOND_PC,second).hex()
    assert len(FIRST)==32 and len(SECOND)==14
    assert W.address(b,'RdNonSolidBG')==0xBF32
    assert W.address(b,'BlockBufferColli_Side')==0x958B
    assert W.address(b,'PipeDwnS')==0x9CEE
    return dict(exact_assembled_bytes=True, hook_PC=0xBF5F,
                helper_PCs=[FIRST_PC,SECOND_PC], helper_bytes=[32,14])


def closure(raw,b):
    regions=((FIRST_PC,FIRST_PC+33),(SECOND_PC,SECOND_PC+15))
    bank=raw[16+BANK*8192:16+(BANK+1)*8192]
    calls=[]
    for at in range(len(bank)-2):
        if bank[at] not in (0x20,0x4c):
            continue
        target=bank[at+1]+256*bank[at+2]
        if any(lo<=target<hi for lo,hi in regions):
            calls.append((0xa000+at,target))
    assert not calls, calls
    typed=[]
    for lo,hi in regions:
        for target in range(lo,hi):
            token=bytes((target&255,target>>8,128+BANK))
            typed.extend((m.start(),target)for m in re.finditer(re.escape(token),raw[16:16+128*8192]))
    assert not typed,typed
    labels=[]
    for name, symbol in b['syms'].items():
        try:
            at=W.location(b,name)
        except KeyError:
            continue
        if (at-16)//8192==BANK and any(lo<=W.address(b,name)<hi for lo,hi in regions):
            labels.append(name)
    # An end marker is not an executable public entry or an indexed table.
    assert all(name.endswith('End')for name in labels),labels
    return dict(original_direct_calls_to_padding=calls,original_typed_descriptors_to_padding=typed,
                padding_labels=labels,old_box_tail_and_fixed_death_descriptors_untouched=True)


def critical(m):
    names=('SelectedCharacter','RdVariant','Player_X_Position','Player_PageLoc',
           'Player_Y_Position','Player_Y_HighPos','Player_State','PlayerFacingDir',
           'RdX','RdRoomHi','RdY','RdAction','RdVY','RdVX','RdGravity',
           'RdHealthLo','RdHealthHi','RdGear','RdTanks','RdMissiles','RdMaxMissiles',
           'NumberofLives','GameEngineSubroutine','Player_SprAttrib','Square1SoundQueue',
           'ChangeAreaTimer','ScrollLock','EventMusicQueue','FlagpoleSoundQueue',
           'FlagpoleCollisionYPos')
    return {name:N.get(m,name)for name in names}


def proof(raw):
    seed, result=inspect_parent(raw)
    b=bundle(raw)
    image=compose(raw)
    result.update(metadata=metadata(raw),assembly=assembly_proof(b),closure=closure(raw,b),
                  positives=[],negatives=[],flagpole=[],foreign=[],cold=[],whole_player=[],interrupts=[],
                  fixture_scope='Compiled-menu cold seeds; later captured position/terrain/pose and foreign identity setups are explicit CPU component fixtures. No natural acquisition, full stage, Mesen or audible-audio claim.')
    for y in (129,136):
        models=[fixture(seed,q,y=y)for q in(raw,image)]
        before=critical(models[0])
        private=(0x5c31,0x5c32,0x5c33,0x5c35,0x5c36,0x5c37)
        for m in models:
            for i,at in enumerate(private):m[at]=7+i*19
        old,_=invoke(models[0],'RdNonSolidBG',a=54,x=13,y=87,p=0x71)
        cpu,trace=invoke(models[1],'RdNonSolidBG',a=54,x=13,y=87,p=0x71)
        assert N.get(models[0],'GameEngineSubroutine')==8
        assert N.get(models[1],'GameEngineSubroutine')==2
        assert (W.address(b,'PipeDwnS'),126)in trace
        after=critical(models[1])
        changes={name:(value,after[name])for name,value in before.items()if value!=after[name]}
        assert changes==dict(GameEngineSubroutine=(8,2),Player_SprAttrib=(0,32),
                             Square1SoundQueue=(0,16),ChangeAreaTimer=(0,52)),changes
        assert (cpu['X'],cpu['Y'])==(13,87)
        assert [models[1][at]for at in private]==[7+i*19 for i in range(6)]
        assert cpu['minimum_SP']>=128
        result['positives'].append(dict(native_y=y,morph=y==136,changes=changes,
                                        actual_native_owner=True,minimum_SP=cpu['minimum_SP']))
    cases=[dict(state=s)for s in(1,2,3)]+[dict(face=f)for f in(0,2,3)]
    cases += [dict(top=t,bottom=u)for t,u in((0,0),(0x51,0x1f),(0x1c,0),(0x1c,0x51),(0x6b,0x6c))]
    cases += [dict(x=2639),dict(page=0),dict(page=2)]
    for case in cases:
        models=[fixture(seed,q,**case)for q in(raw,image)]
        rows=[invoke(m,'RdNonSolidBG',a=54,x=13,y=87,p=0x71)[0]for m in models]
        assert critical(models[0])==critical(models[1]),case
        assert N.get(models[1],'GameEngineSubroutine')==8,case
        assert [(q['X'],q['Y'],q['P']&0xef)for q in rows][0]==[(q['X'],q['Y'],q['P']&0xef)for q in rows][1],case
        result['negatives'].append(case)
    for center,cy,t in((344,128,0x25),(344,121,0x24),(600,128,0x25)):
        models=[]
        for q in(raw,image):
            m=fixture(seed,q,x=center-8,y=cy-16)
            put(m,LevelNumber=0,AreaType=1,ScreenLeft_PageLoc=0,ScreenRight_PageLoc=2)
            tile(m,center&~15,128,t)
            models.append(m)
        rows=[invoke(m,'RdNonSolidBG',a=54,x=13,y=87,p=0x71)[0]for m in models]
        assert critical(models[0])==critical(models[1])
        assert N.get(models[1],'GameEngineSubroutine')==4
        result['flagpole'].append(dict(center=center,source_y=cy,tile=t,
                                       native_transaction_exact=True))
    for char,var in((0,0),(8,0),(2,0),(2,2),(3,0),(3,1),(43,0),(43,1)):
        models=[fixture(seed,q,top=0,bottom=0)for q in(raw,image)]
        for m in models:put(m,SelectedCharacter=char,RdVariant=var)
        rows=[invoke(m,'RdNativeBGGate',a=54,x=13,y=87,p=0x71)[0]for m in models]
        assert critical(models[0])==critical(models[1]),(char,var)
        assert rows[0]==rows[1],(char,var,rows)
        result['foreign'].append(dict(raw=char,variant=var,whole_gate_CPU_and_outcome_exact=True))
    for q in(raw,image):
        expected=bundle(raw)
        values=Route.bundle(raw)[:2]+(dict(expected,raw=q),)
        with patch.object(Route.Previous,'bundle',lambda image:values if image is q else (_ for _ in ()).throw(AssertionError('Wrong cold image'))):
            m=Route.Previous.cold(q)
        assert m.bundle['raw']is q
        assert [N.get(m,name)for name in('SelectedCharacter','RdVariant','NumberofLives')]==[2,1,2]
        for _ in range(8):
            m.controller_pad=0
            Engine.Frames.frame(m,whole_pass=True)
        assert N.get(m,'GameEngineSubroutine')==8 and N.get(m,'NumberofLives')==2
        result['cold'].append(dict(image_SHA256=H(q),compiled_menu=True,neutral_completed_Mains=8,
                                   x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
                                   y=N.get(m,'Player_Y_Position')))
    for pose in(129,136):
        models=[fixture(seed,q,y=pose)for q in(raw,image)]
        for m in models:
            put(m,SavedJoypadBits=1,Left_Right_Buttons=1,A_B_Buttons=0,PreviousA_B_Buttons=0,
                RdHeld=1,RdFresh=0,RdVX=16,Player_X_Speed=16,NmiDisable=255)
            for slot in range(6):m[W.address(b,'Enemy_Flag')+slot]=0
        rows=[invoke(m,'PlayerCtrlRoutine',a=54,x=13,y=87,p=0x71)for m in models]
        assert N.get(models[0],'GameEngineSubroutine')==8,(pose,critical(models[0]))
        assert N.get(models[1],'GameEngineSubroutine')==2,(pose,critical(models[1]))
        assert (W.address(b,'PipeDwnS'),126)in rows[1][1]
        before,after=critical(models[0]),critical(models[1])
        for name in('RdHealthLo','RdHealthHi','RdGear','RdTanks','RdMissiles','RdMaxMissiles','NumberofLives'):
            assert before[name]==after[name],(pose,name)
        result['whole_player'].append(dict(native_y=pose,old_engine=8,new_engine=2,
            actual_movement_then_BG=True,minimum_SP=rows[1][0]['minimum_SP']))
    for pc,bank in((FIRST_PC,95),(SECOND_PC,95),(W.address(b,'BlockBufferColli_Side'),126),
                   (W.address(b,'PipeDwnS'),126)):
        for kind in('IRQ','NMI'):
            m=fixture(seed,image)
            put(m,NmiDisable=255)
            cpu,_=invoke(m,'RdNonSolidBG',cut=(pc,bank,kind),a=54,x=13,y=87,p=0x71)
            assert N.get(m,'GameEngineSubroutine')==2
            assert cpu['interrupt']['minimum_SP']>=128
            result['interrupts'].append(cpu['interrupt'])
    result.update(passed=True,outputs=0,native=False)
    result['receipt_SHA256']=H(json.dumps(result,sort_keys=True,separators=(',',':')).encode())
    return result


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inspect', action='store_true')
    a=p.parse_args()
    installed=ROM.read_bytes()
    raw=installed
    if H(raw)!=PARENT:
        import compose_sonic_current_auth_epoch_1122 as Epoch
        raw=Epoch.inverse(raw)
        assert H(raw)==PARENT
    def deny(*args, **kwargs):
        raise AssertionError('Source pipe proof attempted files or process launch')
    with patch.object(Path,'write_bytes',deny), patch.object(Path,'write_text',deny), patch('subprocess.Popen',deny):
        if a.inspect:
            _,result=inspect_parent(raw)
        else:
            result=proof(raw)
        result['input_SHA256']=H(installed)
        result.pop('receipt_SHA256',None)
        result['receipt_SHA256']=H(json.dumps(result,sort_keys=True,separators=(',',':')).encode())
    print('ROGUE_SIDE_PIPE '+json.dumps(result,sort_keys=True,separators=(',',':')),flush=True)


if __name__=='__main__':
    main()
