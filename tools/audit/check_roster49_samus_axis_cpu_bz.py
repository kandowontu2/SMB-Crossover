"""Check the compiled axis decision against previous-head fixed-point geometry."""
from pathlib import Path
import hashlib,importlib.util,json,random,statistics
R=Path(__file__).resolve().parents[2];V=R/'build/verification';G=V/'root49-samus-head-axis-g6'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
at=lambda a:a if a<0x800 else a-0x6000+0x800
def main():
 out=G/'axis-cpu-bz.json';assert not out.exists()
 model=V/'agent49-samus-bill-arsenal-a/palette_native_model_cu.py'
 sp=importlib.util.spec_from_file_location('samus_axis_cpu',model);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 groups=[]
 for mp in ['mmc3','mmc5']:
  old=m.q.Image(R/f'build/checkpoints/roster-audit-v49-freeze-render-fast-f/smb-crossover-{mp}.nes')
  new=m.q.Image(G/f'source/build/smb-crossover-{mp}.nes');A=new.ram
  def put(r,n,v,i=0):r[at(A[n]+i)]=v%256
  def putq(r,n,v,count=3):
   for i in range(count):put(r,n,v//256**i,i)
  def init():
   r=bytearray(10240);r[0x1d1]=255;r[0x1d2]=223
   put(r,'SelectedCharacter',2);put(r,'CurrentBank',11);put(r,'GameEngineSubroutine',8)
   put(r,'Player_Y_HighPos',1);return r
  banks={0x8000:62,0xa000:11,0xc000:13,0xe000:63}
  rng=random.Random(490699);count=0;digest=hashlib.sha256();cost=[]
  for headIndex,adder in [(51,1),(58,7),(65,19)]:
   table=new.hook('BlockBuffer_Y_Adder',delta=headIndex);assert table['bytes'][0]==adder
   for bottom in [48,80,112,160,192,208,240,256]:
    for fraction in [0,1,32767,32768,65535]:
     for vy in [-1,-32768,-65536,-163840,-273067,-360448]:
      # Put the previous head just above/on/below each cell boundary.
      for offset in [-65536,-1,0,1,65535]:
       previous=(bottom-adder)*65536+offset
       current=previous+vy
       y=current//65536
       if not 32<=y<=206:continue
       # Independent fractional cases use the same geometric threshold with
       # several low-word borrows; this is not a rounded native-speed oracle.
       current=(y<<16)|fraction;previous=current-vy
       for tile in [105,0xc2]:
        r=init();put(r,'R2',bottom-48);put(r,'R3',tile)
        put(r,'Player_Y_Position',y);put(r,'Player_Y_Speed',vy//65536)
        putq(r,'MmYFraction',fraction,2);putq(r,'MmVY',vy)
        expected=(tile==105 and previous+adder*65536>=bottom*65536)
        z=m.execute(new,r,[tile,0,headIndex,rng.randrange(256)&0xcf,0xd0],banks,new.hook('SamusHeadAxisProbe')['address'],0xe000,0xd2)
        assert z['regs'][0]==(tile if expected or tile==0xc2 else 0),(mp,bottom,headIndex,y,fraction,vy,expected,z['regs'])
        assert bool(z['regs'][3]&1)==expected and z['regs'][1:3]==[0,headIndex]
        for n in ['Player_Y_Position','Player_Y_HighPos','Player_X_Position','Player_PageLoc','MmYFraction','MmVY']:
         length=3 if n=='MmVY'else 2 if n=='MmYFraction'else 1
         assert all(z['ram'][at(A[n]+i)]==r[at(A[n]+i)]for i in range(length))
        assert z['banks']==banks
        count+=1;digest.update(bytes(z['regs'][:5]));cost.append(z['cycles'])
  empties=[]
  for speed in [0,-1,-4]:
   for x in [1233,1279,255,256]:
    r=init();put(r,'CurrentBank',10);put(r,'Player_X_Position',x);put(r,'Player_PageLoc',x//256)
    put(r,'Player_Y_Position',176);put(r,'Player_Y_Speed',speed)
    bs=dict(banks);bs[0xa000]=10
    a=m.execute(old,r,[0,0,58,0x24,0xd0],bs,old.hook('SamusHeadProbe')['address'],0xe000,0xd2)
    b=m.execute(new,r,[0,0,58,0x24,0xd0],bs,new.hook('SamusHeadProbe')['address'],0xe000,0xd2)
    assert a['regs']==b['regs']and a['banks']==b['banks']
    assert a['ram'][:0x100]==b['ram'][:0x100]and a['ram'][0x200:]==b['ram'][0x200:]
    assert not any(t[2]in [A['CurrentBank'],0x8000,0x8001,0x5115]for t in b['trace'])
    delta=b['cycles']-a['cycles'];assert 0<delta<=40,(mp,x,speed,a['cycles'],b['cycles'])
    empties.append(dict(x=x,speed=speed,F_cycles=a['cycles'],G6_cycles=b['cycles'],added=delta))
  groups.append(dict(mapper=mp,geometric_components=count,decision_digest=digest.hexdigest(),leaf_cycles=[min(cost),statistics.median(cost),max(cost)],empty_native_full_head_cases=empties,
    scope='Compiled CPU components, no injected interrupts/DMA stalls. Independent unbounded Q16 previous-head/cell-bottom inequality, coin retention, return A/X/Y/C, player state untouched. Empty whole-head output is identical outside stack call bytes and uses no mapper writes. Not an ordinary route or full original HitTester corner-axis proof.'))
 report=dict(status='PASS_G6_COMPILED_SOURCE_AXIS_DECISION_AND_LOCAL_EMPTY_HEAD_ABI',script_sha256=sha(__file__),model_sha256=sha(model),build_review_sha256=sha(G/'build-review.json'),groups=groups,
   cold_work_scope='Only nonempty head samples call the cold bank. Listed actual empty-head instruction-cycle deltas include branch page crossings, rather than assuming a fixed delta per sample. No whole-game FPS improvement claim.',main_changed=False,goal_complete=False)
 out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],sha(out),[(q['mapper'],q['geometric_components'])for q in groups],flush=True)
if __name__=='__main__':main()
