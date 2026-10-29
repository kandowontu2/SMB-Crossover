"""Finite actual-original versus compiled Gimmick source projection controls."""
from pathlib import Path
import hashlib,json,sys
import gimmick_source_audit_v1 as G
R=G.R;O=R/'build/gimmick-component-v2';sys.path.insert(0,str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import Memory,address
from verify_native_relocation import NesMPU
def load():
 parent=scoped_load(R/'build/pit-retold-host-v3/candidate.nes');leaf=scoped_load(O/'leaf.bin')
 raw=bytearray(parent['raw']);banks={'GIMMICK_CORE':24,'GIMMICK_MOVE':122,'GIMMICK_COLD':75,'GIMMICK_ART':73}
 for s in leaf['segs'].values():
  name=s['name'].strip('"')
  if name not in banks:continue
  start=int(s['start'],0);size=int(s['size'],0);p=int(s['ooffs'],0)
  at=16+banks[name]*8192+(start&8191);raw[at:at+size]=leaf['raw'][p:p+size]
 candidate=O/'candidate.nes'
 if candidate.exists():
  at=16+1048576+816*1024;raw[at:at+4096]=(R/'chr/characters/gimmick-source-v2.chr').read_bytes()
  actual=scoped_load(candidate)
  assert actual['raw']==bytes(raw),'Full candidate must equal current compiled sections over immutable parent'
  return actual
 b=dict(parent);b['raw']=bytes(raw);b['syms']=dict(parent['syms']);b['syms'].update(leaf['syms'])
 return b
B=load();PROJ=json.loads((O/'projection.json').read_text());ALIASES={int(k):v for k,v in PROJ['aliases'].items()}
def run(m,pc,stop=0x5b00,a=0,x=0,y=0,p=0x30):
 c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,0xfd;c.stPushWord(0x5aff)
 m.writes=[];c.visited=set()
 for i in range(25000):
  if c.pc in [stop,0x5b00]:return c
  assert m[c.pc]!=0,('unexpected BRK',hex(c.pc));c.visited.add(c.pc);c.step()
 raise AssertionError(('bound',hex(pc),hex(c.pc)))
def port(src,bank=24):
 m=Memory(B);m.page(1,bank);m.page(2,73)
 m[address(B,'CurrentBank')]=bank|128;m[address(B,'CurrentBankC')]=73|128
 m[address(B,'SelectedCharacter')]=26
 for a,n in ALIASES.items():m[address(B,n)]=src[a]
 m[address(B,'GmCueCount')]=src[0x5a]
 for i in range(4):m[address(B,'GmCues')+i]=src[0x56+i]
 return m
def compare(src,m,tag,skip=(),inventory_jump=False):
 relocated={}
 if inventory_jump:
  original=src[2]+256*src[3]
  assert original in [0x804a,0x804d,0x807f,0x808b],('actual native dispatcher target',hex(original))
  target=address(B,'GmN30_%04X'%original)
  relocated={1:(address(B,'GmN30_803F')+2)>>8,2:target&255,3:target>>8}
  assert src[1]==0x80,'Original inline-return pointer high byte'
 for a,n in ALIASES.items():
  if a in set(skip)|{6,7}:continue
  #06/07 are explicitly replaced original-room pointers; the port calls real
  #host block addressing instead. They are not source gameplay state.
  expected=relocated.get(a,src[a])
  assert expected==m[address(B,n)],(tag,hex(a),n,expected,m[address(B,n)])
 assert src[0x5a]==m[address(B,'GmCueCount')],(tag,'queue count')
 assert bytes(src[0x56:0x5a])==bytes(m[address(B,'GmCues'):address(B,'GmCues')+4]),(tag,'ordered cue image')
def call_input(src,m,mask,fresh=None):
 src[0xf5]=mask&~src[0xf7]if fresh is None else fresh;src[0xf7]=mask
 m[address(B,'SavedJoypadBits')]=mask;m[address(B,'GmFresh')]=src[0xf5]
 a=run(src,0x8000,0x82ec);b=run(m,address(B,'GmN30_8000'),address(B,'GmN30_82EC'))
 compare(src,m,('input',mask),inventory_jump=0xf319 in a.visited);return a,b
def main():
 assert not(O/'handoff.json').exists(),'frozen output'
 rows=[];calls=0
 try:
  for ground in [False,True]:
   for mask in [0,1,2,3]:
    src=G.hero();m=port(src);cost=[]
    for tick in range(32):
     src[0x9a]=0;src[0xa4]=6;m[address(B,'GmRam009A')]=0;m[address(B,'GmRam00A4')]=6
     a,b=call_input(src,m,mask);cost.append([a.processorCycles,b.processorCycles]);calls+=1
     m.page(1,122);m[address(B,'CurrentBank')]=250
     a=run(src,0xf689 if ground else 0xf6f3,0xf72f)
     b=run(m,address(B,'GmN31_F689'if ground else'GmN31_F6F3'),address(B,'GmN31_F72F'))
     compare(src,m,('motion',ground,mask,tick));assert(a.a,a.x,a.y,a.p)==(b.a,b.x,b.y,b.p),('integrator flags',ground,mask,tick)
     calls+=1;m.page(1,24);m[address(B,'CurrentBank')]=152
     src[0xed]=(src[0xed]+1)&255;m[address(B,'GmClock')]=src[0xed]
    rows.append(dict(kind='horizontal',ground=ground,held=mask,updates=32,cycles=cost))
  for hold in [1,4,12,32]:
   src=G.hero();m=port(src)
   for tick in range(30):
    src[0x36e]=128 if tick==0 else 0;m[address(B,'GmRam036E')]=src[0x36e]
    call_input(src,m,128 if tick<hold else 0);calls+=1
    m.page(1,122);m[address(B,'CurrentBank')]=250
    a=run(src,0xf6f3,0xf72f);b=run(m,address(B,'GmN31_F6F3'),address(B,'GmN31_F72F'))
    compare(src,m,('jump',hold,tick));assert(a.a,a.x,a.y,a.p)==(b.a,b.x,b.y,b.p)
    calls+=1;m.page(1,24);m[address(B,'CurrentBank')]=152
    src[0xed]=(src[0xed]+1)&255;m[address(B,'GmClock')]=src[0xed]
   rows.append(dict(kind='variable jump',hold=hold,updates=30))
  for held in [1,32,33,42,60]:
   for face in [0,1]:
    src=G.hero();src[0x30a]=face;src[0xcc]=16;m=port(src)
    for tick in range(held):call_input(src,m,64);calls+=1
    call_input(src,m,0);calls+=1
    rows.append(dict(kind='charge/release',held=held,facing=face,status=src[0x91],VX=src[0xcd],VY=src[0xc3]))
  for item in [0,1,2,3]:
   src=G.hero();src[0x36]=item;src[0x39]=1;src[0x346]=1;m=port(src)
   call_input(src,m,0x48);calls+=1
   rows.append(dict(kind='actual inventory dispatcher',item=item,remaining=src[0x39],HP=src[0x346],star_kind=src[0x351]))
  for kind in range(3):
   states=[1,2,0x80,0x9d,0xa0,0xa9,0xd0]+([0xd1]if kind!=1 else[])
   for state in states:
    for phase in [0,1,14]:
     src=G.Original(29)
     for at,v in {0x90:1,0x91:state,0x351:kind,0xb8:5,0xb9:5,0xa4:6,0xa5:6,0xae:128,0xaf:128,
      0xcd:40,0xc3:48,0x397:48,0x3a1:40,0xed:phase}.items():src[at]=v
     m=port(src)
     entry=[0x8023,0x8171,0x82ab][kind];stop=[0x815c,0x5b00,0x845e][kind]
     a=run(src,entry,stop);b=run(m,address(B,'GmN29_%04X'%entry),address(B,'GmN29_%04X'%stop)if stop!=0x5b00 else 0x5b00)
     compare(src,m,('star',kind,state,phase));calls+=1
     assert (a.a,a.x,a.y,a.p)==(b.a,b.x,b.y,b.p),('star AXYP',kind,state,phase,(a.a,a.x,a.y,a.p),(b.a,b.x,b.y,b.p))
     assert (a.pc==stop)==(b.pc==(address(B,'GmN29_%04X'%stop)if stop!=0x5b00 else 0x5b00))
     if src[0x92]:
      at=address(B,'GmEffects');packed=m[at:at+4]
      assert packed==[src[0xb0],src[0xba],src[0x9c],src[0xa6]&15],('actual B4 allocation',kind,state,phase,packed)
      assert m[address(B,'GmSpawnIndex')]==0
      assert src[0x352]==0xb4 and src[0xc4]==src[0xce]==src[0x384]==0
     rows.append(dict(kind='star source fragment',star_kind=kind,state=state,NMI_phase=phase,
      original_cycles=a.processorCycles,compiled_cycles=b.processorCycles,
      original_stop=hex(a.pc),compiled_stop=hex(b.pc),native_B4_allocated=bool(src[0x92])))
  proof=dict(status='COMPILED_KERNEL_PARTIAL_PASS',source_original=G.bind(G.ROM),leaf=G.bind(O/'leaf.bin'),actual_candidate=G.bind(O/'candidate.nes')if (O/'candidate.nes').exists()else None,calls=calls,cases=rows,
   scope='Original input/control pre-terrain, original selected normal/ice-free motion integration, all3 source star kinds charge/active/expiry/scripted fragments and actual B4 producer. Original room pointers06/07 are explicit replaced boundary outputs. Inline code pointers are validated through exact relocated labels, not compared as equal numeric addresses. No compiled host terrain/render/wholeMain/NMI/IRQ/native claim.',
   manual_clock='Typed source ED and projected GmClock advanced identically once per test update. Real NMI endpoint is separate; this is not native clock wiring.')
  (O/'kernel-controls.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(status=proof['status'],calls=calls)))
 except Exception as e:
  path=O/'kernel-first-failure.json'
  if not path.exists():path.write_text(json.dumps(dict(status='FALSE',error=repr(e),completed_calls=calls,leaf=G.bind(O/'leaf.bin')),indent=2)+'\n')
  raise
if __name__=='__main__':main()
