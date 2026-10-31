"""Actual vector cuts at the new no-growth S2 transport islands.

Stops before each genuine service worker; active S2 audio/body source-vector
coverage is bound separately. No callback intercept or cartridge rewrite.
"""
from pathlib import Path
import json,traceback
import prepare_functional_roster_smb2_v1 as B
import current_quick_transport_controls_v4 as T
C=T.C;S=T.S;O=B.O/'dispatch-isr-v1';N=B.N

def start(m,name,raw,alt,p):
 m.set('SelectedCharacter',raw);m.set('FmAlts',alt);m.set('RdVariant',0)
 A=raw if name in ['NrAdder','NrBox'] else 0x83
 m.ram[m.lab['SafecallA_SMC']+1]=A
 m.ram[m.lab['FarcallJmpTarget_SMC']+1]=m.lab[name]&255;m.ram[m.lab['FarcallJmpTarget_SMC']+2]=m.lab[name]>>8
 m.ram[0x1fe]=0xfe;m.ram[0x1ff]=0x7f
 c=C.H.N.NesMPU(memory=m,pc=m.lab['FarCallCommon']);c.a=m.bank(name)|128;c.x=90;c.y=199;c.p=p;c.sp=253
 return c

def walk(m,c,hook=None):
 seen=0;hu=m.lab['HuEntryBase'];low=c.sp
 for age in range(4000):
  low=min(low,c.sp);m.pc=c.pc
  if hook:hook(age,c)
  if c.pc==0x7fff:return dict(returned=True,registers=[c.a,c.x,c.y,c.p,c.sp],minimumSP=low)
  if c.pc==m.lab['FarcallJmpTarget_SMC']:
   dest=m[m.lab['FarcallJmpTarget_SMC']+1]+256*m[m.lab['FarcallJmpTarget_SMC']+2]
   if seen and not hu<=dest<hu+36*16:return dict(dest=dest,tag=m.tags[1],registers=[c.a,c.x,c.y,c.p,c.sp],minimumSP=low)
   seen+=1
  assert m[c.pc],('genuine transport BRK',hex(c.pc),m.tags)
  c.step()
 raise AssertionError(('bounded transport',hex(c.pc),m.tags))

def main():
 assert not O.exists();O.mkdir();d=dict(passed=False,native=False,candidate=B.sha(N/'candidate.nes'));rows=[]
 C.O=N;C.CODE=(N/'code.bin').read_bytes();C.DATA=(N/'data.bin').read_bytes()
 try:
  base=C.Bus()
  for name,val in [('OperMode',1),('GameEngineSubroutine',8),('FamilyMainCommit',1),('GuestAudioCharacter',0)]:base.set(name,val)
  paths=[('NrMovement',25,0),('NrAdder',25,0),('GmFreshGate',25,0),('GmUiGate',25,0),('HuWeaponTail',25,0),('NrMovement',9,32),('GmFreshGate',9,32),('NrMovement',32,0),('GmFreshGate',22,0),('GmUiGate',0,0),('NrMovement',2,0)]
  for name,raw,alt in paths:
   m=S.clone(base);c=start(m,name,raw,alt,0x71);cuts=[];seen=set()
   def observe(age,c):
    tag=m.tags[(c.pc-32768)//8192] if c.pc>=32768 else -1
    key=(tag,c.pc);op=bytes(m[c.pc:c.pc+3]);hu=m.lab['HuEntryBase']
    own=(tag==207 and hu<=c.pc<hu+36*16) or (tag==252 and m.lab['GmOnlyCommon']<=c.pc<m.lab['GmOnlyCommon']+55)
    if key not in seen and (own or 0x15a<=c.pc<0x17b or op in [b'\x8d\x15\x51',b'\x8d\x16\x51']):seen.add(key);cuts.append((age,c.pc,tag))
   reference=walk(m,c,observe)
   for age,pc,tag in cuts:
    for lag in [0,255]:
     for kind in ['NMI','IRQ']:
      q=S.clone(base);q.set('NmiDisable',lag);cc=start(q,name,raw,alt,0x71);proof=[]
      def inject(n,cc):
       if n!=age:return
       assert cc.pc==pc
       if kind=='IRQ' and cc.p&cc.INTERRUPT:return
       proof.append(C.interrupt_at(q,cc,kind))
      actual=walk(q,cc,inject)
      assert actual==reference,('post-vector genuine endpoint',name,raw,pc,lag,kind,reference,actual)
      if proof:rows.append(dict(name=name,raw=raw,alts=alt,age=age,PC=pc,tag=tag,lag=lag,**proof[0]))
  d.update(passed=True,real_vectors=len(rows),rows=rows,scope='Exact current normal/lag NMI and unmasked IRQ at every reached new A79/Only transport instruction, actual33SMC and mapper-store seams; exact endpoint registers/SP/targets/maps and unchanged code/cache. Active source audio/body lifecycle vectors are a separate natural-current receipt.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc(),completed_vectors=len(rows))
 d['bindings']={str(Path(p).resolve()):B.sha(p)for p in [__file__,T.__file__,C.__file__,N/'candidate.nes',N/'candidate.dbg',B.O/'source-stage.json']}
 (O/'result.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items()if k not in ['rows','bindings','traceback']}));assert d['passed'],d.get('error')
if __name__=='__main__':main()
