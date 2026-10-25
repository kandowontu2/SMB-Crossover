"""Execute the complete camera/movement finish before and after admission."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load
from check_tmnt_front_gates_oc import run


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom);rows=[]
    for char,variant,scenario,flags in itertools.product(range(20),range(4),range(8),[0x30,0x71,0x39,0xee]):
        seed={'SelectedCharacter':char,'TnVariant':variant,'RlVariant':variant,'Cv3Variant':variant,
              'Z2Variant':variant,'VvVariant':variant,'OperMode':1,'GameEngineSubroutine':8,
              'NumberofLives':3,'Player_X_Position':128 if scenario!=7 else 250,'Player_PageLoc':1,
              'Player_Y_Position':176 if scenario!=6 else 24,'Player_Y_HighPos':1,
              'ScreenLeft_X_Pos':113,'ScreenLeft_PageLoc':1,'PlayerFacingDir':1 if scenario&1 else 2,
              'SavedJoypadBits':[0,0x81,0x42,0x24,0x11,0x61,0x40,0x82][scenario],
              'FrameCounter':50,'TnMarker':0xc9 if scenario!=0 else 0,'TnLife':3 if scenario!=1 else 4,
              'TnClock':scenario&1,'TnInputFrame':49,'TnSeq':0x80,'TnJumpStage':8,
              'TnPose':9,'TnHurt':3 if scenario==2 else 0,'TnFood':2,
              'Player_State':0 if scenario<4 else 1,'SwimmingFlag':1 if scenario==5 else 0,
              'CrossoverBehaviorVersion':scenario&1,('TnHealth',variant):128}
        x=run(old,'X5NewMovementFinish','X5NewMovementFinish',seed,flags)
        y=run(new,'X5NewMovementFinish','X5NewMovementFinish',seed,flags)
        assert x[:5]==y[:5],(char,variant,scenario,flags,x[0],y[0],
            [(hex(i),x[1][i],y[1][i])for i in range(0x8000)if x[1][i]!=y[1][i]][:16],x[4],y[4])
        rows.append(dict(character=char,variant=variant,scenario=scenario,flags=flags,old_cycles=x[5],new_cycles=y[5]))
    native=[r['old_cycles']-r['new_cycles']for r in rows if r['character']==19]
    legacy=[r['new_cycles']-r['old_cycles']for r in rows if r['character']!=19]
    q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
           cases=len(rows),native_cycles_saved=[min(native),max(native)],legacy_cycles_added=[min(legacy),max(legacy)],
           scope='Complete linked X5NewMovementFinish with pre-step camera sample and outgoing flags preserved. All20 internal IDs, four variants, eight input/initialization/life/hurt/cadence/water/page-edge arrangements and four flag states. Exact A/X/Y/meaningfulP/SP, application RAM outside discarded stack/SMC/safecall scratch, ordered OAM/non-banking hardware and final physical banks. Seeded CPU components; native route and IRQ checks separate.')
    (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
