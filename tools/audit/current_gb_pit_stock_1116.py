"""GB Pit on explicit current a2/9826/cb95 owners; no old runtime defaults."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
from hashlib import sha256
from collections import Counter
import json
import replay_gb_pit_full11_current_1114 as Historical
import compose_mini_weapon_owner_a2_1116 as Mini
import compose_rogue_missile_9826_1116 as Rogue
import check_bub_current_budget_1113 as Frames

R,ROM,W,N=Historical.R,Historical.ROM,Historical.W,Historical.N
H=lambda b:sha256(b).hexdigest()
PINS={Historical:'8a9d4283522e1e0630e1a22f1ca3648a76fe4971ee3682b23b7bcfb063095b21',
      Mini:'c644e50735327826d2f6de932954d501283ca963b4fc12d8408ae75519750a8c',
      Rogue:'f38d2e2859631b1156ad5805d29a481a89f6e68e77b17a4f509de8af7d19d3a1'}
OWNERS={Mini.PARENT:'a2',Mini.CANDIDATE:'9826',Rogue.CANDIDATE:'cb95'}

@lru_cache(maxsize=1)
def reference(raw):
    assert isinstance(raw,bytes)and H(raw)in OWNERS,'Explicit owning a2/9826/cb95 GB Pit only'
    for module,pin in PINS.items():assert H(Path(module.__file__).read_bytes())==pin
    ref=Rogue.inverse(raw)if H(raw)==Rogue.CANDIDATE else raw
    ref=Mini.inverse(ref)if H(ref)==Mini.CANDIDATE else ref
    assert H(ref)==Mini.PARENT;return ref

def hook(b,name,size=16):
    raw=b['raw'];at=W.location(b,name);pc=W.address(b,name);bank=(at-16)//8192
    return dict(pc=pc,offset=at-16,bank=bank,tag=bank|128,bytes=list(raw[at:at+size]),bank_SHA256=H(raw[16+bank*8192:16+(bank+1)*8192]))

@lru_cache(maxsize=1)
def bindings(raw):
    ref=reference(raw);b=dict(W.Symbols.bundle(),raw=raw)
    names=('SelectedCharacter','PitVariant','CrossoverMenuIndex','CrossoverBehaviorVersion','CheatInvincible','CheatStartLevel',
        'OperMode','OperMode_Task','GameEngineSubroutine','WorldNumber','LevelNumber','AreaNumber','AreaType','AreaPointer',
        'NumberofLives','PlayerStatus','PlayerSize','Player_State','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos',
        'Player_X_Speed','Player_Y_Speed','PlayerFacingDir','Player_MovingDir','Player_CollisionBits','Player1ScoreDisplay',
        'GuestPowerupActive','GuestPowerupAge','GuestPowerupOld','GuestPowerupTarget','GuestLegacyHurt','TimerControl',
        'StarInvincibleTimer','Square2SoundQueue','AreaMusicQueue','RgPose','RgPreviousButtons','GuestHurtTicks','InjuryTimer',
        'XgPitFuel','XgPitFlight','XgPitBlocked','XgPitCrouchHeld','MmVY','MmVX','MmXFraction','MmYFraction','CurrentCHRBank',
        'SmChrBank','X5ChrMode','SavedJoypadBits','A_B_Buttons','PreviousA_B_Buttons','Block_Buffer_1','ScreenLeft_X_Pos','ScreenLeft_PageLoc',
        'Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','PowerUpType',
        'FloateyNum_Control','FloateyNum_Timer','BoundingBox_UL_Corner','EnemyBoundingBoxCoord','ObjectOffset')
    ram={name:W.address(b,name)for name in names}
    wanted=('GameLoop','ExpandedMovement','PitFlightUpdate','PlayerMovementSubs','MarioSourcePowerupCollision','HandlePowerUpCollision',
        'GuestBeginPowerup','GuestPowerupUpdate','EraseEnemyObject','SetupFloateyNumber','FloateyNumbersCore','InjurePlayer')
    hooks={name:hook(b,name)for name in wanted}
    for name in('GbPitPose','GbPitCommon','GbPitMenuNavigate','GbPitQueueName'):
        if name in b['syms']:hooks[name]=hook(b,name)
    for h in hooks.values():assert raw[16+h['offset']:16+h['offset']+len(h['bytes'])]==ref[16+h['offset']:16+h['offset']+len(h['bytes'])]
    banks=sorted({h['bank']for h in hooks.values()})
    graphics=[dict(page=p,file=1048592+p*1024,SHA256=H(raw[1048592+p*1024:1048592+(p+1)*1024]),
        exact_reference=raw[1048592+p*1024:1048592+(p+1)*1024]==ref[1048592+p*1024:1048592+(p+1)*1024])for p in range(808,813)]
    return dict(bundle=b,sha=H(raw),owner_role=OWNERS[H(raw)],name='GB PIT',owner=6,variant=1,slot=6,cycle=1,ram=ram,hooks=hooks,
        full_bank_pins=[dict(bank=k,SHA256=H(raw[16+k*8192:16+(k+1)*8192]))for k in banks],graphics=graphics,
        reference_a2_metadata_only=True,reference_SHA256=H(ref),source_graph_recovery=False)

def state(m):
    names=('SelectedCharacter','PitVariant','PlayerStatus','PlayerSize','NumberofLives','Player_State','GameEngineSubroutine',
        'GuestPowerupActive','GuestPowerupAge','GuestPowerupTarget','TimerControl','XgPitFuel','XgPitFlight','GuestHurtTicks','InjuryTimer')
    return dict({n:N.get(m,n)for n in names},x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'),
        high=N.get(m,'Player_Y_HighPos'),CHR=[m[W.address(m.bundle,'CurrentCHRBank')+i]for i in range(12)],SmChrBank=N.get(m,'SmChrBank'))

def cold(raw,report=False):
    q=bindings(raw);b=q['bundle']
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    cycle=[]
    for pad in(2,2,32):W.UI.key(m,pad);cycle.append(dict(name=W.UI.menu_name(m)[0],slot=N.get(m,'CrossoverMenuIndex'),owner=N.get(m,'SelectedCharacter'),variant=N.get(m,'PitVariant')))
    assert(W.UI.menu_name(m)[0],N.get(m,'CrossoverMenuIndex'),N.get(m,'SelectedCharacter'),N.get(m,'PitVariant'))==('GB PIT',6,6,1)
    assert N.get(m,'CrossoverBehaviorVersion')==N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
    s=W.UI.key(m,16);N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=s['A'],x=s['X'],y=s['Y'],p=s['P']);N.invoke(m,'PauseRoutine',a=0)
    for tick in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        m.controller_pad=0;Frames.frame(m,cold=True)
    else:raise AssertionError('Actual compiled GB Pit constructor bound')
    info=dict(passed=True,actual_CPU_SHA256=H(raw),owner_role=q['owner_role'],compiled_cycle=cycle,parser_passes=tick+1,initial=state(m),
        source_menu_vblank_limit=True,gameplay_seeds=0,outputs=0)
    return(m,info)if report else m

def foundation(raw):
    q=bindings(raw);counts=Counter();pending=[];reads={};base=N.NesMPU
    points={(h['tag'],h['pc']):name for name,h in q['hooks'].items()if name in('GameLoop','ExpandedMovement','PitFlightUpdate')}
    class CPU(base):
        def step(self):
            m=self.memory;tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            while pending and(self.pc,self.sp,tag)==pending[-1][1]:counts[pending.pop()[0]+'_returns']+=1
            name=points.get((tag,self.pc))
            if name:
                counts[name+'_entries']+=1;sp=self.sp;pc=(m[256+((sp+1)&255)]+256*m[256+((sp+2)&255)]+1)&65535
                pending.append((name,(pc,(sp+2)&255,m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1)))
                if name not in reads:
                    h=q['hooks'][name];data=raw[16+h['offset']:16+h['offset']+64];assert bytes(m[self.pc:self.pc+64])==data
                    reads[name]=dict(PC=self.pc,SP=self.sp,tag=tag,bytes=64,SHA256=H(data))
            return super().step()
    m,opening=cold(raw,True)
    with patch.object(N,'NesMPU',CPU):
        for _ in range(16):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    assert m.bundle['raw']is raw and not pending
    assert all(counts[name+'_entries']==counts[name+'_returns']==16 for name in('GameLoop','ExpandedMovement','PitFlightUpdate')),(counts,reads,state(m))
    out=dict(passed=True,ROM_SHA256=H(raw),owner_role=q['owner_role'],cold=opening,neutral16_counts=dict(counts),first_actual_readbacks=reads,
        terminal=state(m),hooks=q['hooks'],full_bank_pins=q['full_bank_pins'],graphics=q['graphics'],
        Pit_symbols={name:dict(PC=W.address(q['bundle'],name),size=q['bundle']['syms'][name].get('size'))for name in q['bundle']['syms']if name.startswith('GbPit')},
        own_runtime='Native expanded movement and ability worker with GB Pit graphics alternate; no private GB CPU packet or synthetic payload cookie claimed',
        item_policy='Source fallthrough routes actor M/F through shared GuestBeginPowerup/60 updates. Must qualify genuine emergence/physical collision/score/resume separately.',
        health_scope='PlayerStatus tier and native lives are observed. No dedicated Pit HP pool or seeded injury test is asserted by neutral foundation.',
        historical82_full_factory_SHA256=PINS[Historical],historical_full_not_replayed=True,outputs=0,Mesen=False,gameplay_seeds=0)
    out['receipt_SHA256']=H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out

if __name__=='__main__':
    raw=ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('GB Pit source foundation attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=foundation(raw)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
