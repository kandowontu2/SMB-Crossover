"""Differential complete native/legacy UI callers, including hurt history."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_front_gates_oc import run
from check_tmnt_render_oa import load

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom);rows=[]
    for char,variant,mode,scenario,flags in itertools.product(range(20),range(4),range(2),range(4),[0x30,0x71,0x39,0xee]):
        seed=dict(SelectedCharacter=char,TnVariant=variant,Cv3Variant=variant,Z2Variant=variant,RlVariant=variant,
          CrossoverBehaviorVersion=mode,OperMode=1 if scenario!=3 else 0,OperMode_Task=3,
          GameEngineSubroutine=8,Player_Y_HighPos=1,Player_Y_Position=176,PlayerFacingDir=1,
          InvHudActive=1 if scenario==2 else 0,InvPrevious=0x20,InvDirty=254,
          SavedJoypad1Bits=0x23 if scenario==1 else 0,GamePauseStatus=1 if scenario==1 else 0,
          InvRefill=1 if scenario==2 else 0,InvRefillRemain=16,InvRefillTick=2,
          GuestHurtTicks=8 if scenario==3 else 0,GuestHurtKind=char)
        x=run(old,'X5BounceUiDispatch','X5BounceUiDispatch',seed,flags)
        y=run(new,'X5BounceUiDispatch','X5BounceUiDispatch',seed,flags)
        assert x[:5]==y[:5],(char,variant,mode,scenario,flags,x[0],y[0],[(hex(i),x[1][i],y[1][i])for i in range(32768)if x[1][i]!=y[1][i]][:15])
        rows.append(dict(character=char,variant=variant,mode=mode,scenario=scenario,flags=flags,cycles_saved=x[5]-y[5]))
    hurt=0
    for char,kind,ticks,bits,previous,active,dirty,flags in itertools.product([13,14,16,17,19],[0,4,5,10], [0,1,255],[0,0x20,0x23],[0,0x20],[0,1],[0,255],[0x30,0x71]):
        seed=dict(SelectedCharacter=char,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,
          GuestHurtTicks=ticks,GuestHurtKind=kind,SavedJoypad1Bits=bits,InvPrevious=previous,
          InvHudActive=active,InvDirty=dirty,InvFresh=0xa5,ReloadCHRBank=255)
        x=run(old,'X5BounceUiDispatch','X5BounceUiDispatch',seed,flags);y=run(new,'X5BounceUiDispatch','X5BounceUiDispatch',seed,flags)
        assert x[:5]==y[:5],('hurt',seed,flags,x[0],y[0]);hurt+=1
    q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
      outer_cases=len(rows),hurt_history_boundary_cases=hurt,scope='Actual full UI/lifecycle caller. Exact A/X/Y/meaningfulP/SP, application RAM excluding discarded stack and existing farcall scratch, ordered OAM/non-banking hardware writes and final banks. Seeded units, not item delivery or campaign proof.')
    (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q),flush=True)
if __name__=='__main__':main()
