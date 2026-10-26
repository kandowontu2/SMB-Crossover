"""Source-only real-wrapper, foreign ABI and IRQ controls for private Luigi dry profile."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/audit'))
from mario_luigi731_coefficients_v1 import make, seed_vx, coord, q24
from robots_weapon_cpu_v1 import Arena
from check_tmnt_render_oa import load, address, location
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU
from luigi_flower731_rg_prepare_v1 import trace_call

D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE = D / 'mm-proto-clean-menu-candidates-v1/clean-menu-irq/candidate.nes'
PARENT = '731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
CURRENT = '641460e2646806c03fb98cf84f8a8c2e8de99c74dac8c5876c50f05ef1eb512c'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p, q):
    assert not p.exists(), p
    p.write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')


def app(m):
    g = next(g for g in m.bundle['segs'].values() if g.get('name') == '"SMCCODE"')
    lo = int(g['start'], 0);hi = lo + int(g['size'], 0)
    return bytes(m[:0x100]) + bytes(m[lo:hi]) + bytes(m[0x200:0x800]) + bytes(m[0x5c00:0x8000])
def result(q, cpu):return cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,app(q.m),tuple(q.m.banks)
def full(b, mode=0, power=1):
    q = make(b, 8, mode)
    q.put(MarioVariant=1, PlayerStatus=power, OperMode_Task=3, GameEngineSubroutine=8,
          Player_Rel_XPos=96, Player_Pos_ForScroll=96, ScreenLeft_PageLoc=1,
          ScreenLeft_X_Pos=0, ScreenRight_PageLoc=1, ScreenRight_X_Pos=255, ScrollLock=1)
    for name in ['Block_Buffer_1','Block_Buffer_2']:
        for i in range(0xb0, 0xd0):q.set(name, 0x54, i)
    return q
def tick(q, bits):
    q.set('SavedJoypadBits', bits);c, _ = q.invoke('PlayerCtrlRoutine')
    q.set('PreviousA_B_Buttons', bits & 192)
    q.set('FrameCounter', (q.get('FrameCounter') + 1) & 255)
    if q.get('RunningTimer'):q.set('RunningTimer', q.get('RunningTimer') - 1)
    return c
def state(q, i):return dict(update=i, x=coord(q,'X'), y=coord(q,'Y')-256, state=q.get('Player_State'),
    vx=q24(q,'MmVX'), vy=q24(q,'MmVY'), camera=q.get('ScreenLeft_PageLoc')*256+q.get('ScreenLeft_X_Pos'),
    crouch=q.get('CrouchingFlag'), native_vx=q.get('Player_X_Speed'), native_vy=q.get('Player_Y_Speed'),
    character=q.get('SelectedCharacter'), power=q.get('PlayerStatus'))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert sha(BASE)==PARENT and sha(a.candidate)==CURRENT
    a.output.mkdir(parents=True,exist_ok=False);old,new=load(BASE),load(a.candidate)
    qb,qn=qualified(BASE),qualified(a.candidate)
    differences={str(k):[v,qn.get(k)] for k,v in qb.items() if qn.get(k)!=v}
    expected={str(('LuigiNativeTraction','Brake')),str(('LuigiNativeTraction','Leftward')),str(('_FARCALL_COUNT',))}
    assert set(differences)==expected,differences
    assert qn[('_FARCALL_COUNT',)]==qb[('_FARCALL_COUNT',)]+22
    put(a.output/'symbols.json',dict(retained=len(qb)-3,actual_changes=differences,
        genuine_private_relocation='Only old internal Brake/Leftward labels are removed; new source-owned body has real relocated labels. Old public traction entry/span/foreign prefix/Done RTS remain. Farcall count is metadata.'))
    foreign=[]
    for char,mode,bits in itertools.product([x for x in range(20) if x!=8],[0,1],[0,1,0xc1]):
        q=make(old,char,mode);r=make(new,char,mode)
        for z in [q,r]:z.put(SavedJoypadBits=bits,A_B_Buttons=bits&192,Left_Right_Buttons=bits&3)
        c,_=q.invoke('PlayerMovementSubs');d,_=r.invoke('PlayerMovementSubs')
        assert result(q,c)==result(r,d),(char,mode,bits)
        assert c.processorCycles==d.processorCycles,(char,mode,bits,'foreign cost')
        foreign.append(dict(character=char,mode=mode,input=bits,cycles=c.processorCycles))
    put(a.output/'foreign-complete-movement.json',dict(passed=True,cases=foreign,full_AXYP_SP_RAM_SMC_banks_exact=True,cycle_delta=0))

    wrappers=[]
    for mode,power,bits in itertools.product([0,1],range(3),[0,1,2,3,4,5,6,128,132,193]):
        q=full(new,mode,power);tick(q,bits);z=state(q,1)
        assert q.get('SelectedCharacter')==8 and q.get('MarioVariant')==1 and q.get('PlayerStatus')==power
        assert q.get('PlayerSize')==int(power==0)
        if bits in [5,6]:
            assert q.get('Left_Right_Buttons')==q.get('Up_Down_Buttons')==0
            assert z['crouch']==(4 if power else 0)
        if bits in [128,132]:assert z['y']<176 and z['state']==1
        else:assert z['y']==176 and z['state']==0
        wrappers.append(dict(mode=mode,power=power,input=bits,result=z))
    put(a.output/'actual-PlayerCtrl-inputs.json',dict(passed=True,cases=wrappers,actual_wrapper=True))

    chains=[]
    for mode,kind in itertools.product([0,1],['hold-jump','release-jump','reversal','wall','pipe','ledge','landing','head','scroll']):
        q=full(new,mode);q.set('MarioSourceActive',1)
        if kind in ['wall','pipe']:
            q.put(Player_X_Position=114,Player_Rel_XPos=114,Player_Pos_ForScroll=114);seed_vx(q,0,2.5)
            for row in [0x80,0x90,0xa0]:q.set('Block_Buffer_2',0x10 if kind=='pipe' else 0x54,row+8)
        if kind=='ledge':
            q.set('Player_X_Position',118);seed_vx(q,0,2.5)
            for row in [0xb0,0xc0]:
                for col in range(8,16):q.set('Block_Buffer_2',0,row+col)
        if kind=='landing':q.put(Player_Y_Position=150,Player_State=2,Player_Y_Speed=2);q.array('MmVY',[0,0,2])
        if kind=='head':
            q.put(Player_Y_Position=162,Player_State=1,Player_Y_Speed=251);q.array('MmVY',[0,0,251])
            for col in [6,7]:q.set('Block_Buffer_2',0x54,0x70+col)
        if kind=='scroll':
            q.put(Player_X_Position=144,Player_Rel_XPos=144,Player_Pos_ForScroll=144,ScrollLock=0);seed_vx(q,0,2.5)
        if kind=='reversal':seed_vx(q,0,2.5)
        path=[]
        limit=75 if kind in ['hold-jump','release-jump'] else 12 if kind=='ledge' else 25
        for age in range(limit):
            bits=128 if kind=='hold-jump' or (kind=='release-jump' and age<8) else 2 if kind=='reversal' else 0 if kind in ['landing','head','release-jump'] else 65
            tick(q,bits);path.append(state(q,age+1))
            assert q.get('SelectedCharacter')==8 and q.get('MarioVariant')==1 and q.get('PlayerStatus')==1
            assert q.get('GameEngineSubroutine')==8
        if kind in ['hold-jump','release-jump','landing','head']:
            assert path[-1]['y']==176 and path[-1]['state']==0 and path[-1]['vy']==0,(mode,kind,path[-1])
        if kind in ['wall','pipe']:assert max(z['x'] for z in path)<=371 and path[-1]['x']==370
        if kind=='ledge':assert any(z['state']==2 and z['y']>176 for z in path)
        if kind=='head':assert any(0<z['native_vy']<128 for z in path) and min(z['y'] for z in path)>=144
        if kind=='scroll':
            assert path[-1]['camera']>256
            assert len({z['x']-z['camera'] for z in path})==1
        if kind=='reversal':assert path[-1]['vx']<0
        chains.append(dict(mode=mode,kind=kind,path=path))
    put(a.output/'actual-PlayerCtrl-collision-history.json',dict(passed=True,cases=chains,
        explicit_synthetic_block_buffers=True,terrain_imports_real=True,real_landing_caller=True,
        not_native_traversal=True,main_bookkeeping='Only controller history, FrameCounter and RunningTimer bookkeeping between actual PlayerCtrl calls.'))

    identity=[]
    for power,held,prev in [(1,64,0),(2,0,0),(2,64,64),(2,64,0)]:
        calls=[]
        for bundle in [old,new]:
            q=full(bundle,0,power);q.put(SavedJoypadBits=held,A_B_Buttons=held,PreviousA_B_Buttons=prev,RgPreviousButtons=prev)
            events=trace_call(q,'ProcFireball_Bubble');calls.append((app(q.m),tuple(q.m.banks),events))
        assert calls[0]==calls[1]
        identity.append(dict(power=power,held=held,previous=prev,actual_source_stores=calls[0][2]))
    poses=[]
    for power,pose in itertools.product(range(3),[0,1,4,7]):
        both=[]
        for bundle in [old,new]:
            q=full(bundle,0,power);q.put(RgPose=pose,PlayerFacingDir=1,GuestPowerupActive=0);c,_=q.invoke('ExpandedPose');both.append(result(q,c))
        assert both[0]==both[1]
        poses.append(dict(power=power,pose=pose))
    put(a.output/'identity-weapon-art-controls.json',dict(passed=True,actual_weapon_calls=identity,actual_pose_calls=poses,
        complete_final_state_and_code_art_exact=True,no_palette_changes=True))

    # Same unchanged compiled mapper IRQ executes at every newly reached instruction.
    seen=set();hw=set();minimum=255
    nseg=next(g for g in new['segs'].values() if g.get('name')=='"X5_PROFILES"')
    oldseg=next(g for g in old['segs'].values() if g.get('name')=='"X5_PROFILES"')
    start=int(nseg['start'],0)+int(oldseg['size'],0);end=int(nseg['start'],0)+int(nseg['size'],0)
    spans=[(78,start,end),(1,address(new,'LuigiNativeTraction'),address(new,'LuigiNativeTraction')+84)]
    for kind in ['jump','brake','release','native-fallback']:
        q=full(new,1);q.set('MarioSourceActive',1)
        if kind=='brake':seed_vx(q,0,2.5)
        if kind=='release':q.put(Player_State=1,Player_Y_Speed=252,MmFrictionYActive=1);q.array('MmVY',[0,128,252])
        if kind=='native-fallback':q.set('JumpspringAnimCtrl',1)
        q.put(SavedJoypadBits=128 if kind=='jump' else 0)
        sym=new['syms']['PlayerCtrlRoutine'];q.m.page(1,1);q.set('CurrentBank',129)
        c=NesMPU(memory=q.m,pc=address(new,'PlayerCtrlRoutine'));c.sp=0xfd;c.p=0x30;c.stPushWord(0x5aff)
        for _ in range(100000):
            if c.pc==0x5b00:break
            bank=q.m.banks[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1;key=(bank,c.pc)
            if any(bank==k and lo<=c.pc<hi for k,lo,hi in spans) and key not in seen:
                assert not c.p&4;seen.add(key)
                before=(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,app(q.m),tuple(q.m.banks))
                q.m[0x5204]=128;mark=len(q.m.writes);c.irq();assert c.pc==0x8000
                for __ in range(400):
                    if c.pc==before[0] and c.sp==before[5]:break
                    minimum=min(minimum,c.sp);c.step()
                else:raise AssertionError(('IRQ failed RTI',key))
                assert (c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,app(q.m),tuple(q.m.banks))==before,('IRQ caller mutation',key)
                hw.update(at for at,v in q.m.writes[mark:] if 0x2000<=at<0x5c00)
            c.step()
        else:raise AssertionError('IRQ-injected wrapper timeout')
        assert c.sp==0xfd and q.get('SelectedCharacter')==8
    assert seen and hw and hw<=set([0x2005,0x2006,0x5128,0x5130]),hw
    put(a.output/'actual-IRQ-controls.json',dict(passed=True,actual_IRQ_RTI_injections=len(seen),minimum_SP=minimum,
        hardware_store_addresses=sorted(hw),reached_boundaries=[dict(bank=k,PC=v) for k,v in sorted(seen)],
        exact_resumed_AXYP_SP_appRAM_fiveSMC_banks=True,scope='Actual compiled IRQ/vector/RTI in an untimed CPU memory model; explicit pending flag. No NMI/PPU/DMA/DMC timing/native certification.'))
    bindings={str(p):sha(p) for p in [Path(__file__),a.candidate,a.candidate.with_suffix('.dbg'),BASE,BASE.with_suffix('.dbg')]}
    for p in a.output.iterdir():bindings[str(p)]=sha(p)
    put(a.output/'proof.json',dict(passed=True,native_executed=False,adopted=False,ROM_sha256=CURRENT,parent_ROM_sha256=PARENT,
        retained_qualified_symbols=len(qb)-3,foreign_complete_movement_cases=len(foreign),foreign_cycle_delta=0,
        full_PlayerCtrl_input_cases=len(wrappers),full_PlayerCtrl_history_collision_cases=len(chains),
        actual_item_weapon_cases=len(identity),actual_pose_cases=len(poses),actual_IRQ_injections=len(seen),
        unchanged_water_climb_spring_stomp_small_gap_policy=True,bindings=bindings,
        limits='Finite source/CPU components. No native run, cadence, PPU visibility, audio waveform, full level, natural pickups or full physics parity. Native-source handoffs not changed.'))
    print(json.dumps({k:v for k,v in json.loads((a.output/'proof.json').read_text()).items() if k!='bindings'},indent=2))


if __name__=='__main__':main()
