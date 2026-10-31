from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_thomas_natural_cold_1031_v1 as N
H=N.H;C=N.C
b=H.C.qualified(N.J/'candidate.nes');m=C.fresh(b,0);H.put(m,CrossoverMenuIndex=10,FmAlts=64,SelectedCharacter=0)
for name in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:N.invoke(m,name)
H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0);N.invoke(m,'GameMenuRoutine');N.invoke(m,'PauseRoutine',a=0)
for i in range(1000):
 if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:break
 H.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
 N.invoke(m,'GameLoop');C.A.consume(m)
m.ram[2][0x8c]=0 # Explicit diagnostic counterfactual: omitted donor boss, NOT product/readiness evidence.
rows=[]
for i in range(16):
 H.put(m,SavedJoypadBits=1,SavedJoypad1Bits=1,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=1,Up_Down_Buttons=0,NmiDisable=255)
 z=N.invoke(m,'GameLoop');C.A.consume(m)
 row=dict(age=i,X=z['X'],frame=H.get(m,'FrameCounter'),fields={hex(a):m.ram[2][a]for a in[0x12,0x14,0x15,0x20,0x21,0x23,0x55,0x62,0x64,0x65,0x66,0x67,0x68,0x69,0x6a,0x73,0x74,0x94,0xd4,0xe5,0x36e,0x36f,0x38f,0x800,0x803,0x807]})
 rows.append(row);print(row,flush=True)
O=R/'build/thomas-natural-walk-diagnostic-1031-v2';O.mkdir();(O/'review.json').write_text(json.dumps(rows,indent=2)+'\n')
