"""Execute old/new native elevator manager; compare Goku and rejection paths."""
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_hogan_current_bounded_v1 as M
from prepare_ff_current_component_v2 import qualified
O=R/'build/karnov-native-platform-1101-v1'

def main():
    paths=[R/'build/kirby-approach-owner-1101-v3/candidate.nes',O/'candidate.nes']
    bundles=[qualified(p) for p in paths];bases=[M.fresh(b) for b in bundles]
    cases=0;minimum=255
    for char,mode,xpos,invalid,full in itertools.product([0,10,24,35],range(2),[680,856],range(5),range(2)):
        pair=[]
        for base in bases:
            m=M.fork(base)
            M.put(m,SelectedCharacter=char,GameEngineSubroutine=8,GamePauseStatus=0,TimerControl=0,
                  WorldNumber=0,LevelNumber=0,AreaType=1,AreaAddrsLOffset=5,
                  HpValid=1,HpCount=0,HpArea=37,HpKey=0,HpCharacter=char,
                  HpMode=mode,CrossoverBehaviorVersion=mode,HpSupport=0,HpActorSlot=0,
                  Player_PageLoc=xpos//256,Player_X_Position=xpos%256,
                  ScreenLeft_PageLoc=2,ScreenLeft_X_Pos=88)
            for i in range(6):m[M.address(m.bundle,'Enemy_Flag')+i]=full
            if invalid: M.put(m,**[{},{'HpValid':0},{'HpCharacter':99},{'TimerControl':1},{'HpArea':1}][invalid])
            result=M.invoke(m,'DpPlatformTick',a=91,x=177,y=66,p=0x71)
            minimum=min(minimum,result['minimum_SP'])
            state=bytes(m[:0x100])+bytes(m[0x200:0x800])+bytes(m[0x6000:0x8000])
            pair.append((tuple(result[k] for k in ['A','X','Y','P']),state,tuple(m.rawtags)))
        assert pair[0]==pair[1],(char,mode,xpos,invalid,full)
        cases+=1
    q=dict(passed=True,CPU_only=True,native=False,candidate_sha256=hashlib.sha256(paths[1].read_bytes()).hexdigest(),
           unchanged_Goku_and_foreign_manager_cases=cases,minimum_standalone_SP=minimum,
           scope='Actual native manager, full/empty actor slots, both modes, two placements and invalid scene/cache/frozen states. CPU stack contents excluded because internal return PCs move. Does not establish Main ISR safety or full-stage completion.')
    (O/'manager-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))

if __name__=='__main__':main()
