"""Additive first arena vector-global mismatch diagnosis; no pass assertion."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import contra_force_p1_restore_arena_api_vectors_v1 as X
A,V,T,C,U=X.A,X.V,X.T,X.C,X.U;O=R/'build/contra-force-p1-restore-vector-diagnostic-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();base=V.scene();T.put(base,SmFreezeLastBlue=193,SmFreezePalettePending=128,SmFreezeTurn=1,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,Sprite0HitDetectFlag=0,NmiDisable=255,ReloadCHRBank=0);base[T.address(T.B,'VRAM_Buffer1')]=0
 m=A.arena(C.clone(base));c=X.start(m);e=A.arena(C.clone(base));ec=X.start(e);expected=T.finish(e,ec)
 while not(m.rawtags[1]==219 and 40960<=c.pc<41027):c.step()
 rows=[]
 for kind in['NMI','IRQ']:
  z,d=U.clone(m,c);A.arena(z);before=[int(x)for x in z[:32768]];z[21028]=128;beforeISR=[int(x)for x in z[:32768]];proof=U.interrupt(z,d,kind,keep_ppu=False);afterISR=[int(x)for x in z[:32768]];actual=T.finish(z,d)
  delta=[dict(address=i,expected=e[i],actual=z[i],before_test=before[i],before_ISR=beforeISR[i],after_ISR=afterISR[i])for i in range(32768)if not 256<=i<=480 and i not in list(range(2016,2023))+[2026,32762]and e[i]!=z[i]]
  rows.append(dict(kind=kind,PC=c.pc,AXYP=actual['AXYP'],expected_AXYP=expected['AXYP'],deltas=delta,**proof))
 q=dict(diagnostic_only=True,qualified=False,native=False,actual_cartridge=False,rows=rows,bindings={str(p.resolve()):sha(p)for p in[Path(__file__),Path(X.__file__),R/'build/contra-force-p1-restore-arena-api-vectors-v1/controls.json',A.A/'proof.json']});p=O/'diagnostic.json';p.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),rows=rows)),flush=True)
if __name__=='__main__':main()
