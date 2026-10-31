"""Updated genuine image fingerprint: copy/readback, rejection and all16 bytes."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import bowser_split_loader_controls_v1 as T
from check_tmnt_render_oa import load
H=T.H;J=R/'build/bowser-playable-jump-v1/joint';O=R/'build/bowser-playable-loader-controls-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,source_CPU=True,native=False)
 try:
  b=load(J/'candidate.nes');m=T.make(b);before=[bytes(x)for x in m.ram[:3]]
  c,lo=T.call(m,'BwLoad');image=bytearray((J/'bowser.bin').read_bytes());image[0x1fe0:0x1ff0]=(J/'bowser/cookie.bin').read_bytes()
  assert c.p&1 and m.ram[3]==image and [bytes(x)for x in m.ram[:3]]==before and m.ppu_reads==16400
  assert m.ram_writes[0]==(3,0x1fe0,0)and m.ram_writes[-1]==(3,0x1fe0,167)
  nr=m.ppu_reads;nw=len(m.ram_writes);T.call(m,'BwLoad');assert m.ppu_reads==nr and len(m.ram_writes)==nw
  for byte in range(16):
   for f in range(64):
    z=T.fork(m);z.ram[3][0x1fe0+byte]^=1;c,_=T.call(z,'BwCheck',p=T.flags(f))
    assert not c.p&1 and(c.a,c.x,c.y,c.sp)==(85,7,91,224)and not z.ram_writes
  for name,values in [('foreign',dict(SelectedCharacter=0)),('FFowner',dict(SelectedCharacter=22)),('title',dict(OperMode=0)),('active',dict(DisableScreenFlag=0)),('mask',dict(Mirror_PPUMASK=30)),('normal',dict(NmiDisable=0)),('notbusy',dict(FamilyMainCommit=0))]:
   z=T.make(b,**values);original=bytes(z.ram[3]);c,_=T.call(z,'BwLoad');assert not c.p&1 and bytes(z.ram[3])==original and z.ppu_reads==0,name
  for name,protection,corrupt in [('locked',[0,0],None),('readback',[2,1],(3,17))]:
   z=T.make(b);z.protection=protection;z.corrupt_at=corrupt;c,_=T.call(z,'BwLoad');assert not c.p&1 and z.ram[3][0x1fe0]!=167,name
  q.update(passed=True,copy_readback_bytes=8192,buffered_reads=16400,valid_first_clear_last_publish=True,warm_no_write=True,cookie_poison_flags=1024,guards=9,minimum_SP=lo)
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(T.__file__),J/'candidate.nes',J/'candidate.dbg',J/'bowser.bin',J/'bowser/cookie.bin']}
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q));assert q['passed']
if __name__=='__main__':main()
