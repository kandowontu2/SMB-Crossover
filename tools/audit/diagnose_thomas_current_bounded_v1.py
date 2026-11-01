"""Trace the first Thomas rightward stall without restoring old fixture graphs."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_hogan_current_bounded_v1 as C
J=R/'build/thomas-natural-host-1031-v6';O=R/'build/thomas-adapter-diagnostic'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists();O.mkdir()
    assert sha(J/'candidate.nes')=='3fe8683284193f311aecde19290ad507f80283cf12c82ce27efea3b64c995527'
    b=C.scoped_load(J/'candidate.nes');m=C.fresh(b)
    C.put(m,CrossoverMenuIndex=10,FmAlts=64,FmGroups=0)
    for n in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:C.invoke(m,n)
    assert C.get(m,'SelectedCharacter')==10 and C.get(m,'FmAlts')&0x44==0x40
    C.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0)
    C.invoke(m,'GameMenuRoutine');C.invoke(m,'PauseRoutine',a=0)
    for setup in range(600):
        if C.get(m,'OperMode_Task')==3 and C.get(m,'GameEngineSubroutine')==8:break
        C.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
        C.invoke(m,'GameLoop');C.consume(m)
    else:raise AssertionError('Native parser bound')
    fields=['Player_X_Position','Player_PageLoc','Player_Rel_XPos','ScreenLeft_X_Pos','ScreenLeft_PageLoc','Player_Pos_ForScroll','Player_X_Scroll','ScrollAmount','Player_X_Speed','SideCollisionTimer']
    rows=[]
    for age in range(180):
        C.put(m,SavedJoypadBits=1,SavedJoypad1Bits=1,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=1,Up_Down_Buttons=0,NmiDisable=255)
        result=C.invoke(m,'GameLoop')
        rows.append(dict(age=age,**{n:C.get(m,n)for n in fields},
                         source={f'{a:02X}':m.ram[2][a]for a in [0x12,0x62,0x64,0x65,0x66,0x94,0xd4,0xe5,0x69]},
                         CPU=result['CPU'],minimum_SP=result['minimum_SP']))
        C.consume(m)
    q=dict(source_CPU=True,native=False,changed_product=False,candidate=sha(J/'candidate.nes'),parser_Main=setup,rows=rows,
           bindings={str(p):sha(p)for p in [Path(__file__),Path(C.__file__),C.model,J/'candidate.nes',J/'candidate.dbg',J/'source-stage.json']},
           scope='Actual native Main and NMI in finite CPU/peripheral model. Controller-byte fixture; no RAM position/state/HP edits after Start.')
    (O/'trace.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(parser_Main=setup,first=rows[0],last=rows[-1])))


if __name__=='__main__':main()
