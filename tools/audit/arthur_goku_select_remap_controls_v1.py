"""Real remapped menu/Select/Start flags, pending guard, and cold constructors.

No native process. The408a ancestor's genuine SMB2 black-backdrop native
negative remains an inherited publication hold; this tool does not relabel
that as a remap defect or claim hardware palette success.
"""
from pathlib import Path
import collections,json,traceback
import arthur_quick_functional_admission_v1 as A
import prepare_functional_roster_visuals58_v1 as B

R=B.R;P=R/'build/functional-roster-coherent62-v4/joint';N=R/'build/arthur-goku-select-remap-v3/joint'
O=N.parent;T=A.T;FLAGS=A.FLAGS
VARS=['FmAlts','FmGroups','MarioVariant','RlVariant','RdVariant','ProtoVariant','DwVariant','Smb2Class']

def val(m,n):return m.get(n)if n in m.lab else None
def menu(path,slot,v=0):
 m=A.fresh(path,slot);A.call(m,'MenuResolveCharacter');A.call(m,'QueueSelection')
 for _ in range(v):A.button(m,32)
 return m

def main():
 out=O/'menu-controls.json';assert not out.exists();d=dict(passed=False,native=False);rows=[]
 try:
  # Every existing individual remains reachable. Old Goku23 is now genuine
  # Select1 behind Arthur31; all other slots and Select orders are exact.
  for slot,count in enumerate(A.COUNTS):
   for variant in range(count):
    dest=(31,1)if slot==23 else(slot,variant)
    pair=[menu(P,slot,variant),menu(N,*dest)]
    rr=[A.call(m,'FmPending')[0]for m in pair]
    assert bool(rr[0]['P']&1)==bool(rr[1]['P']&1)
    assert pair[0].get('SelectedCharacter')==pair[1].get('SelectedCharacter'),(slot,variant,dest)
    packets=[[q for q in A.commands(m)if q['address']==0x2328]for m in pair]
    assert packets[0]==packets[1],('existing full name',slot,variant,dest,packets)
    for key in [16,128]:
     zz=[A.start_boundary(T.fork(m),key,0xf9)for m in pair]
     assert zz[0]==zz[1],('real Start/A AXYP/SP',slot,variant,dest,key,zz)
    rows.append(dict(prior=[slot,variant],current=dest,raw=pair[1].get('SelectedCharacter'),pending=bool(rr[1]['P']&1),actual_names_equal=True))
  bt=menu(N,23);r=A.call(bt,'FmPending')[0]
  assert r['P']&1 and bt.get('SelectedCharacter')==0
  for key in[16,128]:assert not A.start_boundary(T.fork(bt),key,0xf9)['launch']
  name=[q for q in A.commands(bt)if q['address']==0x2328]
  assert name[0]['data']==[36,36,63]+[ord(c)-55 for c in 'BATTLETOADS']+[36,36]
  A.call(bt,'DrawSelectionPreview');oam=list(bt.ram[0x200:0x210]);assert all(oam[j]for j in[0,4,8,12])
  # Real table resolver, every slot/live64flags and every selected bit7.
  resolver=[];templates=[T.bus(path)for path in[P,N]]
  for slot in range(32):
   for bits in[0,128,255]:
    for p in FLAGS:
     mm=[T.fork(m)for m in templates]
     for m in mm:m.set('FmAlts',bits)
     z=[A.S.execute(m,'NrMenuCharacter',A=0x83,X=slot,Y=0xc7,P=p)[0]for m in mm]
     expected=33 if slot==23 else 24 if slot==31 and bits&128 else A.RAW[slot]
     assert(z[1]['A'],z[1]['X'],z[1]['Y'])==(expected,slot,0xc7)
     assert z[1]['P']&~0x82==z[0]['P']&~0x82,('resolver CVDI',slot,bits,p,z)
     if slot not in[23,31]:assert z[0]==z[1]
     resolver.append([slot,bits,p])
  # Exact Start bit policy across ALL256bytes/all64flags. Its output is
  # the source contract: only31 retains80, only9 retains20, others clear.
  start=[]
  for slot in range(32):
   for bits in range(256):
    # Every byte; allflags additionally on each extremal legal mask case.
    flags=FLAGS if bits in[0,32,128,255]else[0xf9]
    for p in flags:
     m=T.fork(templates[1]);m.set('FmAlts',bits);m.set('FmGroups',255)
     z=A.S.execute(m,'FmStartFlags',A=0x83,X=slot,Y=0xc7,P=p)[0]
     expected=bits&(128 if slot==31 else 32 if slot==9 else 0)
     assert(m.get('FmAlts'),m.get('FmGroups'))==(expected,0)
     assert(z['A'],z['X'],z['Y'])==(0,slot,0xc7)
     assert z['P']&~0x82==p&~0x82 and z['P']&0x82==2,('Start flags',slot,bits,p,z)
     start.append([slot,bits,p])
  # Actual foreign Select callers across all64flags. All source R0 scratch
  # effects are judged at their real complete menu caller, not invented ABI.
  toggle=[]
  for slot,count in enumerate(A.COUNTS):
   if slot in[23,31]:continue
   for variant in range(count):
    base=[menu(path,slot,variant)for path in[P,N]]
    for p in FLAGS:
     mm=[T.fork(m)for m in base]
     for m in mm:
      A.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
     zz=[A.S.execute(m,'CrossoverMenuInput',A=0x83,X=0x5a,Y=0xc7,P=p)[0]for m in mm]
     assert zz[0]==zz[1],('foreign real Select AXYP',slot,variant,p,zz)
     assert [val(mm[0],n)for n in VARS]==[val(mm[1],n)for n in VARS],('foreign variants',slot,variant,p)
     assert mm[0].ram[:0x100]==mm[1].ram[:0x100],('complete menu ZP',slot,variant,p)
     assert A.commands(mm[0])==A.commands(mm[1]),('foreign real menu packet',slot,variant,p)
     toggle.append([slot,variant,p])
  # Actual Ar -> Goku -> Ar Select calls choose original source name/body.
  own=menu(N,31);cycle=[]
  for index,raw in enumerate([32,24,32]):
   if index:A.button(own,32)
   assert own.get('SelectedCharacter')==raw
   z=A.call(own,'DrawSelectionPreview')
   if raw==24:assert own.get('DpRenderIndex')==1
   cycle.append(dict(index=index,raw=raw,FmAlts=own.get('FmAlts'),OAMoffset=own.get('CurrentOAMOffset'),CPU=z[1]))
  # Full genuine Start/Fresh source return, not explicit constructor calls.
  fresh=[]
  for slot,variant in[(31,0),(31,1)]:
   m=menu(N,slot,variant);calls=collections.Counter();names=['IcGlobalInit','SunnyGlobalInit','QwBoot','ArGenConstruct','DpAdmissionFresh','CmHostFresh']
   points={(m.bank(n)|128,m.lab[n]):n for n in names}
   def observe(c):
    if c.pc>=0x8000:
     key=(m.tags[(c.pc-0x8000)//8192],c.pc)
     if key in points:calls[points[key]]+=1
   A.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverContinue=0)
   z=A.S.execute(m,'CrossoverMenuInput',hook=observe)
   assert m.get('SelectedCharacter')==(32 if variant==0 else 24)and m.get('CrossoverMenuState')==0
   assert calls['IcGlobalInit']==1 and calls['SunnyGlobalInit']==1 and calls['QwBoot']==1
   assert calls['ArGenConstruct']==(variant==0)and calls['DpAdmissionFresh']==(variant==1)
   fresh.append(dict(variant=variant,raw=m.get('SelectedCharacter'),calls=dict(calls),returned=z[0],minimumSP=z[2]))
  d.update(passed=True,preserved_existing_individuals=len(rows),ready=sum(not r['pending']for r in rows),new_generic_pending_Battletoads_profiles=1,existing_rows=rows,Nr_resolver_allflags_cases=len(resolver),Start_all256bytes_and64flags_cases=len(start),foreign_complete_Select_allflags_cases=len(toggle),Ar_Goku_Ar_cycle=cycle,actual_Start_post_Ic_Fresh=fresh,header_CHR_payloads_unchanged=True,inherited_publication_hold='408a native SMB2 full P0 transparent header aliases overworld backdrop; root owns frozen palette/eye successor. No remap native/admission claim.',native_music_scope='Original Goku/Arthur audio and physics modules are byteexact outside menu66/76/Nr124. This is routing preservation, not a new original-game music completion claim.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc())
 d['bindings']={str(p.resolve()):B.sha(p)for p in[Path(__file__),P/'candidate.nes',P/'candidate.dbg',N/'candidate.nes',N/'candidate.dbg',O/'source-stage.json']}
 B.write(out,json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items()if k not in['bindings','existing_rows','traceback']}));assert d['passed'],d.get('error')

if __name__=='__main__':main()
