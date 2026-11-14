"""Current Kirby shell preservation and normal-controls CPU encounter audit."""
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch
import zipfile

import check_kirby_inhale_safety_1113 as Existing
import check_ff_white_mushroom_current_1110 as W
import check_bub_current_budget_1113 as Frames
from check_ff_stdout_controller_source_1110 import LuaRuntime

R=Path(__file__).resolve().parents[2]
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PINS={'fa66fa915d91ed125cf947b5c15d517c2919c62941378e10d62b0fdf184cdaae',
      '421379021e775e6e03357c0aa11d4cab04008452f94bc9e8938f0662cc0c979f'}
SOURCE=R/'tools/playthroughs/kirby_current_green_stdout_1110_v5.lua'
SOURCE_SHA='730a40160788c5fa41b3bf8b931bfd14834bb463ae75a04b18f07f12e0d2ff20'
CHECKPOINT=R/'docs/qa/checkpoints/2026-11-01/kirby-owner-nightly-v2/source.zip'
CHECKPOINT_SHA='e465b2c73a0e0ce9a36f55ad3cac648bdf2ec6b1e198c8763974be419688c847'
N=W.N


def controller(raw):
    assert sha256(raw).hexdigest()in PINS and sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    text=SOURCE.read_text(encoding='utf-8')
    # Same authentication update already used by delivered1112 green-route:
    # the capture-frame helper changed these five bytes, not the shell route.
    at=Existing.Old.Wide.offset(0xa31a)
    assert raw[at:at+5]==bytes.fromhex('a9018d0c5c')
    first,body=text.split('\n',1)
    text=first+'\nC.hooks.erased.bytes={'+','.join(map(str,raw[at:at+5]))+'}\n'+body
    marker='local menuDone,finished,lastA=false,false,false'
    assert text.count(marker)==1
    text=text.replace(marker,'local menuDone,finished,lastA=true,false,false',1)
    LuaRuntime().compile(text)
    assert not any(v in text for v in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw):
    assert sha256(raw).hexdigest()in PINS
    b=Existing.bundle(raw)
    assert sha256(CHECKPOINT.read_bytes()).hexdigest()==CHECKPOINT_SHA
    with zipfile.ZipFile(CHECKPOINT)as z:owner=z.read('kirby-owner/kirby_weapons.s').decode()
    assert 'Native kicked shells use $30/$d0 in4.4, exactly3px/update.'in owner
    assert 'cmp #32'in owner and 'jsr KbShellEnemyContact'in owner
    text=controller(raw)
    lua=LuaRuntime(unpack_returned_tuples=True)
    config=lua.execute(SOURCE.read_text().split('\n',1)[0]+'\nreturn C')
    hook_checks={}
    for name,h in config.hooks.items():
        values=bytes(v for _,v in sorted(h.bytes.items()))
        if name=='erased':values=bytes.fromhex('a9018d0c5c')
        assert raw[16+h.offset:16+h.offset+len(values)]==values,(name,'Exact retained native observer preimage')
        hook_checks[name]=dict(pc=h.pc,PRG_offset=h.offset,bytes=values.hex())
    at=W.location(b,'KickedShellXSpdData')
    assert raw[at:at+2]==bytes.fromhex('30d0')
    return b,text,dict(ROM_SHA256=sha256(raw).hexdigest(),Kirby_PRG74_SHA256=Existing.KIRBY_BANK_SHA,
        exact1113_Kirby_bank_and_capture_return_source_recomposition=True,
        retained_source_controller_SHA256=SOURCE_SHA,CPU_frontend_adapter_SHA256=sha256(text.encode()).hexdigest(),
        original_owner_checkpoint_SHA256=CHECKPOINT_SHA,
        native_kicked_shell_speed_data='30d0, signed4.4 equals +/-3 pixels per native update',
        native_hook_preimages=hook_checks,known_repairs_already_delivered=True,
        source_src_kirby_weapons_s_is_historical_not_installed_authority=True,
        game_ROM_writes=0,outputs=0,Mesen_run=False)


def cold(raw):
    # Established current native menu arena; real Start/parser/constructor.
    # No actor, terrain, position, health, ability, copy, shot or flag seeds.
    b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,12)
    assert W.UI.menu_name(m)[0]=='KIRBY'and N.get(m,'SelectedCharacter')==13
    assert N.get(m,'KbVariant')==N.get(m,'CrossoverBehaviorVersion')==0
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for tick in range(700):
        if tuple(N.get(m,k)for k in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'KbHealth')==6 and N.get(m,'NumberofLives')==2
            assert N.get(m,'KbCopy')==N.get(m,'KbMouth')==N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Current Kirby menu/Start/constructor bound')


def encounter(raw,limit=7500):
    b,text,info=metadata(raw);m=cold(raw)
    lua=LuaRuntime(unpack_returned_tuples=True);callbacks=defaultdict(list);events=defaultdict(list)
    ctx=dict(cpu=None,pc=0,cycles=0,status=None,receipt=None,tick=0)
    counts=Counter();pads=set()
    points={(W.address(b,n),((W.location(b,n)-16)//8192)|128):n
            for n in('GameLoop','KbWeapons','KbWeapons::Move','KbWeapons::EnemyContacts','KbShellEnemyContact')}
    api=lua.table();api.memType=lua.table_from(dict(nesDebug=0,nesWorkRam=1,nesPrgRom=2))
    api.callbackType=lua.table_from(dict(exec=0));api.eventType=lua.table_from(dict(inputPolled=0,endFrame=1))
    def read(at,kind=0):
        if kind==2:return raw[16+at]
        if kind==1:return m.ram[at//8192][at%8192]
        return m[at]
    def mapped(at):
        if at<0x8000:return None
        tag=m.rawtags[(at-0x8000)//8192]
        return lua.table_from(dict(memType=2 if tag&128 else 1,address=(tag&127)*8192+(at&8191)))
    def cpu_state():
        c=ctx['cpu'];s={f'cpu.{n}':getattr(c,n)if c else 0 for n in('pc','sp','a','x','y','p')}
        s['cpu.pc']=ctx['pc'];s['cpu.ps']=s['cpu.p'];s['cpu.cycleCount']=ctx['cycles']
        return lua.table_from(s)
    def input(pad,port):
        assert port==0
        m.controller_pad=sum(v for k,v in(('right',1),('left',2),('down',4),('up',8),('start',16),('select',32),('b',64),('a',128))if pad[k])
        pads.add(m.controller_pad)
    def memory(fn,kind,lo,hi=None):
        assert kind==0
        for at in range(lo,lo+1 if hi is None else hi+1):callbacks[at].append(fn)
    def emit(line):
        if line.startswith('SMB_NATIVE_RECEIPT '):ctx['receipt']=json.loads(line.removeprefix('SMB_NATIVE_RECEIPT '))
    api.read=read;api.convertAddress=mapped;api.getState=cpu_state;api.setInput=input
    api.addMemoryCallback=memory;api.addEventCallback=lambda fn,kind:events[kind].append(fn)
    api.stop=lambda status:ctx.update(status=status)
    lua.globals().emu=api;lua.globals().print=emit
    env={'SMB_STDOUT_ROM_SHA':sha256(raw).hexdigest(),'SMB_TEST_VARIANT':'0'}
    lua.globals().os.getenv=lambda name:env.get(name)
    lua.execute(text)
    native=N.NesMPU
    class Observed(native):
        def step(self):
            ctx['cpu']=self;ctx['pc']=self.pc
            if self.pc>=0x8000:
                name=points.get((self.pc,m.rawtags[(self.pc-0x8000)//8192]))
                if name:counts[name]+=1
            for fn in tuple(callbacks.get(self.pc,())):fn()
            before=self.processorCycles;result=super().step();ctx['cycles']+=self.processorCycles-before
            return result
    with patch.object(N,'NesMPU',Observed):
        for tick in range(limit):
            ctx['tick']=tick
            for fn in tuple(events[0]):fn()
            Frames.frame(m,whole_pass=True)
            for fn in tuple(events[1]):fn()
            if ctx['status']is not None:break
            if tick%500==499:print(json.dumps(dict(progress_Main=tick+1,x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'))),flush=True)
    q=ctx['receipt']or{}
    return dict(passed=ctx['status']==0,metadata=info,source_scheduler_passes=tick+1,
        source_CPU_calls=dict(counts),controller_pad_values=sorted(pads),reason=q.get('reason'),
        genuine_normal_controls=True,actor_terrain_health_copy_shot_position_and_flag_seeds=0,
        frontend='Native menu arena and genuine Start/parser; retained Lua menu coroutine bypassed only in source harness',
        physical_timing_claim=False,embedded_frame_units='source scheduler passes',
        encounter={k:q.get(k)for k in('native_green_koopa','capture','actual_down_swallow','actual_ground_copy_attack',
            'shell_contact','native_defeat_entry','native_defeat_return','terminal','probes','contact_attempts')},
        outputs=0,Mesen_run=False)


if __name__=='__main__':
    raw=ROM.read_bytes();q=encounter(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Current normal-controls shell encounter remains unqualified'
