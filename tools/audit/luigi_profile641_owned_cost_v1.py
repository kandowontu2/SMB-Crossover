"""Finite exact-CPU full-PlayerCtrl cost facts, old731 versus private641; no native."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from check_tmnt_render_oa import load,address
from verify_native_relocation import NesMPU
from luigi_mario_profile731_cpu_v1 import full,state,PARENT,CURRENT,BASE
from mario_luigi731_coefficients_v1 import seed_vx
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
NEW=D/'luigi-mario-profile731-v3/candidate.nes'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,q):assert not p.exists();p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')


def run(q,bits):
    q.set('SavedJoypadBits',bits);b=q.b;m=q.m
    # Same exact Arena.invoke entry/return contract; add read-only cycle counters.
    m.page(1,1);q.set('CurrentBank',129);m.writes=[]
    c=NesMPU(memory=m,pc=address(b,'PlayerCtrlRoutine'));c.a=c.x=c.y=0;c.p=0x30;c.sp=0xfd;c.stPushWord(0x5aff)
    names=['PlayerCtrlRoutine','PlayerMovementSubs','LuigiNativePrepare','LuigiNativeTraction',
           'CrossoverMarioMovement','LuigiSourceMovementBridge','LuigiSourceDryMovement']
    entries={}
    for name in names:
        if name not in b['syms']:continue
        s=b['syms'][name];seg=b['segs'][s['seg']];bank=(int(seg['ooffs'],0)-16)//8192
        entries[(bank,address(b,name))]=name
    active=[];calls=[];bankcycles={};minimum=255
    for _ in range(100000):
        while active and c.pc==active[-1]['return_pc'] and c.sp==active[-1]['return_SP']:
            z=active.pop();z['inclusive_cycles']=c.processorCycles-z.pop('start');calls.append(z)
        if c.pc==0x5b00:break
        bank=m.banks[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1
        name=entries.get((bank,c.pc))
        if name:
            lo=m[0x100+((c.sp+1)&255)];hi=m[0x100+((c.sp+2)&255)]
            active.append(dict(name=name,entry_pc=c.pc,bank=bank,entry_SP=c.sp,
                               return_pc=((hi<<8)+lo+1)&65535,return_SP=(c.sp+2)&255,start=c.processorCycles))
        before=c.processorCycles;minimum=min(minimum,c.sp);c.step()
        bankcycles[bank]=bankcycles.get(bank,0)+c.processorCycles-before
    else:raise AssertionError(('CPU timeout',hex(c.pc)))
    assert c.sp==0xfd and not active
    assert q.get('SelectedCharacter')==8 and q.get('MarioVariant')==1 and q.get('PlayerStatus')==1
    result=dict(cycles=c.processorCycles,instructions=sum(1 for _ in []),minimum_SP=minimum,
                complete_call_AXYP=[c.a,c.x,c.y,c.p],final_banks=list(m.banks),state=state(q,1),
                bank_execution_cycles=bankcycles,actual_entry_return_costs=calls)
    result.pop('instructions')
    return result


def seed(bundle,mode,kind):
    q=full(bundle,mode,1)
    if kind!='cold':
        run(q,0);q.put(PreviousA_B_Buttons=0,FrameCounter=1)
    if kind in ['coast','reverse','run','run-jump']:
        seed_vx(q,8 if bundle['raw']==load_old_raw else 0,2.5)
    if kind=='walk':
        seed_vx(q,8 if bundle['raw']==load_old_raw else 0,1.0)
    if kind=='release':
        q.put(Player_State=1,Player_Y_Speed=252,Player_Y_MoveForce=128,
              Player_Y_Position=155,VerticalForce=32,VerticalForceDown=112,
              JumpOrigin_Y_Position=176,DiffToHaltJump=1,PreviousA_B_Buttons=128,
              MmFrictionYActive=1)
        q.array('MmVY',[0,128,252])
    if kind=='landing':
        q.put(Player_State=2,Player_Y_Speed=2,Player_Y_MoveForce=0,
              Player_Y_Position=174,VerticalForce=112,VerticalForceDown=112)
        q.array('MmVY',[0,0,2])
    return q


load_old_raw=None
def main():
    global load_old_raw
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert sha(BASE)==PARENT and sha(NEW)==CURRENT
    a.output.mkdir(parents=True,exist_ok=False);old,new=load(BASE),load(NEW);load_old_raw=old['raw']
    cases=[]
    for mode in [0,1]:
        for kind,bits in [('cold',0),('idle',0),('walk',1),('run',65),('coast',0),('reverse',2),('jump',128),('run-jump',193),('release',0),('landing',0)]:
            result=[]
            for b in [old,new]:result.append(run(seed(b,mode,kind),bits))
            assert all(z['cycles']==sum(z['bank_execution_cycles'].values()) for z in result)
            assert all(z['actual_entry_return_costs'][-1]['name']=='PlayerCtrlRoutine' for z in result)
            if kind=='landing':assert all(z['state']['y']==176 and z['state']['state']==0 for z in result)
            cases.append(dict(mode=mode,kind=kind,input=bits,old731=result[0],new641=result[1],
                              new_minus_old_cycles=result[1]['cycles']-result[0]['cycles']))
    put(a.output/'full-PlayerCtrl-costs.json',dict(passed=True,cases=cases,
        source_states='Legal isolated assembled full-caller inputs: dry Super Luigi, synthetic legal flat floor and fixed camera; each warmed with its own actual empty caller except cold. Native/source velocities seeded in their genuine formats.',
        model='Untimed CPU model, all actual called routines execute; no IRQ/NMI/PPU/DMC/native cadence. Cost differences include intended movement outcome/branch differences, not equal-state ABI assertions.'))
    inputs=[Path(__file__),BASE,BASE.with_suffix('.dbg'),NEW,NEW.with_suffix('.dbg'),ROOT/'tools/audit/luigi_mario_profile731_cpu_v1.py',ROOT/'tools/audit/mario_luigi731_coefficients_v1.py',ROOT/'tools/audit/check_tmnt_render_oa.py',ROOT/'tools/audit/verify_native_relocation.py',ROOT/'tools/audit/robots_weapon_cpu_v1.py',a.output/'full-PlayerCtrl-costs.json']
    bindings={str(f):sha(f) for f in inputs}
    put(a.output/'proof.json',dict(passed=True,source_CPU_only=True,native_executed=False,ROM_sha256=CURRENT,parent_ROM_sha256=PARENT,
                                  actual_full_PlayerCtrl_pairs=len(cases),modes=[0,1],bindings=bindings,
                                  minimum_delta_cycles=min(z['new_minus_old_cycles']for z in cases),maximum_delta_cycles=max(z['new_minus_old_cycles']for z in cases),
                                  foreign_zero_cost_is_separate_existing_fact=True,no_free_or_cadence_claim=True))
    print(json.dumps([dict(mode=z['mode'],kind=z['kind'],old=z['old731']['cycles'],new=z['new641']['cycles'],delta=z['new_minus_old_cycles'])for z in cases],indent=2))


if __name__=='__main__':main()
