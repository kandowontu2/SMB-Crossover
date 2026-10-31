"""Actual SFC worker-frame forwarding and retirement before foreign writes."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import wwf_hogan_runtime_controls_v3 as V
from ff_wram_host_isr_v4 import clone
from wwf_first_hogan_owner_isr_v1 import interrupt
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
H=V.H;T=V.T;J=R/'build/wwf-hogan-natural-source-v15/joint';O=R/'build/wwf-hogan-foreign-scene-controls-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def invoke(m,n,p=0x79,hook=None):
 c=H.start(m,n,a=85,x=7,y=91,p=p);c,lo=H.finish(m,c,hook);assert c.sp==224
 return c,lo
def main():
 assert not O.exists();O.mkdir();q=dict(passed=False,native=False,rows=[],vectors=[])
 try:
  b=T.qualified(J/'candidate.nes');V.J=J
  seed=T.make(b)
  for bank in[2,3]:seed.ram[bank][0x1fe0:0x1ff0]=bytes(16)
  cases=[(raw,0x79)for raw in range(34)if raw!=29]+[(0,0x30|(i&15)|((i&48)<<2))for i in range(64)]
  for raw,p in cases:
   pair=[];mins=[]
   for name in ['BwScene','WfScene']:
    m,_=clone(seed,NesMPU(memory=seed));H.put(m,SelectedCharacter=raw,FmAlts=0,FmGroups=0)
    c,low=invoke(m,name,p)
    pair.append(((c.a,c.x,c.y,c.p,c.sp),[bytes(a)for a in m.ram],bytes(m[0x15a:0x17b]),bytes(m[3:11]),m.rawtags[:],bytes(m[0x200:0x800])))
    mins.append(low)
   assert pair[0]==pair[1],('Genuine native scene output/frame',raw,p,[a[0]for a in pair])
   q['rows'].append(dict(raw=raw,P=p,minimum_SP=mins))
  # Pin the actual worker return origin BEFORE the source drops two bytes.
  m,_=clone(seed,NesMPU(memory=seed));H.put(m,SelectedCharacter=0);shots=[];seen=set();origin=[]
  def watch(mem,cpu,step):
   if cpu.pc==address(b,'WfScene'):
    ret=mem[0x101+cpu.sp]+256*mem[0x102+cpu.sp]
    assert ret==address(b,'FarcallJmpTarget_SMC')+2
    origin.append(dict(SP=cpu.sp,return_word=ret,expected_source_JSR_return=address(b,'FarcallJmpTarget_SMC')+2))
   raw=mem.rawtags[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else -1
   if raw==224 and address(b,'WfSceneForeignReturn')<=cpu.pc<address(b,'WfDetachRuntime'):
    key=cpu.pc
    if key not in seen:seen.add(key);shots.append((key,*clone(mem,cpu)))
  invoke(m,'WfScene',hook=watch);assert len(origin)==1 and shots
  for pc,s,c in shots:
   for context in ['normal','lag','paused']:
    for kind in ['NMI','IRQ']:
     if kind=='IRQ'and c.p&4:continue
     z,d=clone(s,c);H.put(z,NmiDisable=255 if context=='lag'else 0,GamePauseStatus=int(context=='paused'))
     low=interrupt(z,d,kind);H.finish(z,d)
     assert d.sp==224 and z.rawtags[1]==H.get(z,'CurrentBank')and z.rawtags[2]==H.get(z,'CurrentBankC')
     q['vectors'].append(dict(PC=pc,context=context,kind=kind,minimum_SP=low))
  q.update(passed=True,candidate=sha(J/'candidate.nes'),actual_scene_pairs=len(q['rows']),entry_origin=origin,original_native_AXYP_SP_RAM_SMC33_R0_7_maps_exact=True,scope='New WWF wrapper forwards foreign scenes through the genuine original SFC frame. Foreign live constructor stack never retains the extra WWF19-byte save. Actual InitScreen is the sole source importer; arbitrary direct WfScene calls are not an API.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(V.__file__),J/'candidate.nes',J/'candidate.dbg',J.parent/'source-stage.json']}
  (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q.get(k)for k in['passed','candidate','actual_scene_pairs','error']}))
if __name__=='__main__':main()
