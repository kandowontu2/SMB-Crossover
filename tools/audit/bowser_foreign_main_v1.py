"""Foreign complete-Main state/ordered writes on the actual new shared source."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import bowser_actual_host_checks_v1 as A
from check_tmnt_render_oa import load,address
T=A.T;H=A.H;C=A.N.C;J=A.J;O=R/'build/bowser-foreign-main-v1';P=R/'build/coherent62-lives-fixes-v1/joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sig(m):
 skip=set(range(256,512))|set(range(0x5100,0x5140))
 return bytes(m[i]for i in range(0x8000)if i not in skip)
def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,native=False,source_CPU=True,rows=[])
 try:
  bundles=[load(x/'candidate.nes')for x in[P,J]]
  for raw,mode,keys in itertools.product([x for x in range(33)if x!=27],range(2),[0,1,129,64]):
   pair=[]
   for b in bundles:
    m=C.fresh(b,0);H.put(m,SelectedCharacter=raw,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,Player_State=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_X_Position=96,Player_PageLoc=0,PlayerFacingDir=1,PlayerStatus=0,TimerControl=0,GamePauseStatus=0,CrossoverBehaviorVersion=mode,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=0,NmiDisable=255,FamilyMainCommit=0,FmAlts=32 if raw==9 else 0,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
    m.writes.clear();m.ram_writes.clear();c=H.start(m,'GameLoop');c,lo=H.finish(m,c)
    ignore=set(range(256,512))|set(range(0x5100,0x5140))
    app=[(a,v)for a,v in m.writes if a not in ignore]
    pair.append(((c.a,c.x,c.y,c.p,c.sp),sig(m),[bytes(x)for x in m.ram],app,m.chr_latches[:],c.processorCycles,lo))
   assert pair[0][:5]==pair[1][:5],('actual foreign Main',raw,mode,keys,pair[0][0],pair[1][0],[(i,x,y)for i,(x,y)in enumerate(zip(pair[0][1],pair[1][1]))if x!=y][:8])
   q['rows'].append([raw,mode,keys,pair[1][5]-pair[0][5],pair[1][6]])
  q.update(passed=True,limits='Legal native controlled scene Main pairs; invalid caches deliberately remain guarded. Actual active source-owner cold controls are separate existing proofs, not requalified native.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(A.__file__),J/'candidate.nes',J/'candidate.dbg',P/'candidate.nes',P/'candidate.dbg']}
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=q['passed'],error=q.get('error'),traceback=q.get('traceback'))));assert q['passed']
if __name__=='__main__':main()
