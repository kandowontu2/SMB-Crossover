"""Finite emitted Hot target/ABI, import, cached-carrier and mirror closure."""
from pathlib import Path
import hashlib,itertools,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
from check_tmnt_render_oa import address,location
P=R/'build/thomas-physical-host-1031-v9';J=R/'build/thomas-natural-host-1031-v6';I=R/'build/thomas-private-ingress-1031-v5';O=R/'build/thomas-linked-closure-1031-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
HOT={
 'HotPlayerGraphics':['RlGraphics','KbGraphicsDispatch','CdGraphicsDispatch','LmGraphicsGate','JnGraphicsDispatch','M3GraphicsDispatch','VvGraphicsDispatch','TnGraphics','NrGraphics'],
 'HotNewCharacterDraw':['RlDraw','CdNewDrawDispatch','CdNewDrawDispatch','LmDrawGate','JnDrawDispatch','M3NewDrawDispatch','VvDrawDispatch','TnDraw','NrDraw']}
def endpoint(m,name,p):
 c=H.start(m,name,a=0x59,x=0x5a,y=0xc7,p=p);smc=address(m.bundle,'FarcallJmpTarget_SMC');first=True
 for n in range(800):
  if c.pc==smc:
   if not first:return(c.a,c.x,c.y,c.p,c.sp,m.rawtags[1],m[smc+1]|m[smc+2]<<8),c.processorCycles
   first=False
  assert m[c.pc]!=0,(name,hex(c.pc));c.step()
 raise AssertionError(('hot endpoint bound',name))
def main():
 assert not O.exists();O.mkdir(parents=True);q=dict(passed=False,native=False)
 try:
  stage=json.loads((J/'source-stage.json').read_text())
  for p,h in stage['bindings'].items():assert sha(p)==h,p
  bs=[H.C.qualified(p/'candidate.nes')for p in[P,J]];moves=json.loads((I/'moved-symbols.json').read_text());targetnames=set(json.loads((I/'moved-import-consumers.json').read_text())[str(I/'main.o')])|{'HuNativeWorldPalette','HuPlayerSubs'}
  rows=[];pairs=0
  for name,targets in HOT.items():
   emitted=[]
   for i,target in enumerate(targets):
    off=[location(bs[1],name+'::'+n)+i for n in ['Lo','Hi','Bank']]
    actual=[bs[1]['raw'][k]for k in off];expected=[address(bs[1],target)&255,address(bs[1],target)>>8,((location(bs[1],target)-16)//8192)|128]
    assert actual==expected,(name,i,target,actual,expected);emitted.append(dict(index=i,export=target,emitted=actual))
   base=[L.make(b)for b in bs]
   def check(raw,roll,alt,p):
    nonlocal pairs
    results=[]
    for m in base:
     H.put(m,SelectedCharacter=raw,RlVariant=roll,FmAlts=alt);m.writes.clear();results.append(endpoint(m,name,p)[0])
    a,z=results
    if raw==10 and alt&68==64:
     target='NrGraphics'if name=='HotPlayerGraphics'else'NrDraw'
     assert z[:5]==a[:5] and z[5:]==(((location(bs[1],target)-16)//8192)|128,address(bs[1],target))
    else:assert a==z,('same original Hot child/AXYP/SP/bank',name,raw,roll,alt,p,a,z)
    app=lambda m:[(a,v)for a,v in m.writes if not(0x100<=a<0x200 or 0x15a<=a<0x17b or a in[0x5115,0x5116])]
    assert app(base[0])==app(base[1]),('same original Hot application writes',name,raw,roll,alt,p)
    pairs+=1
   for raw,p in itertools.product(range(256),[48,255]):check(raw,0,0,p)
   for raw,roll,alt in[(0,0,0),(9,0,0),(9,1,0),(9,0,32),(10,0,0),(10,0,4),(10,0,64),(10,0,68)]+[(i,0,0)for i in range(13,21)]:
    for f in range(64):check(raw,roll,alt,L.flags(f))
   rows.append(dict(entry=name,original_nine_targets=emitted))
  print('Thomas linked nine-target Hot tables/allraw/allflags child ABI PASS',pairs,flush=True)
  inputs=[Path(p)for p in json.loads((J/'final-link.json').read_text())['command']if str(p).endswith('.o')];imports={};cc=R/'tools/Windows/cc65/bin/od65.exe'
  for p in inputs:
   text=subprocess.run([str(cc),'--dump-imports',str(p)],capture_output=True,text=True,check=True).stdout
   found=sorted(set(re.findall(r'Name:\s*"([^"]+)"',text))&targetnames)
   if found:imports[str(p)]=found
  assert str(J/'bt-api.o')in imports and imports[str(J/'bt-api.o')]==['HuNativeWorldPalette']
  assert str(J/'union.o')in map(str,inputs) and str(J/'main.o')in imports
  side=[]
  for path in sorted((P/'sideoutputs').glob('*.bin')):
   child=J/'sideoutputs'/path.name;a=path.read_bytes();z=child.read_bytes();changes=[i for i,(x,y)in enumerate(zip(a,z))if x!=y]
   if path.name.startswith('01-'):
    at=address(bs[1],'BtNativeWorldPalette')-0xa000
    assert changes==[at+6] and a[at+6]==address(bs[0],'HuNativeWorldPalette')&255 and z[at+6]==address(bs[1],'HuNativeWorldPalette')&255,('sole cached imported operand',changes,at)
    assert z==(J/'source/bt/stream.bin').read_bytes()
    cookie=(J/'source/bt/cookie.bin').read_bytes();assert cookie[4:]==hashlib.sha256(z).digest()[:12]
    cp=location(bs[1],'BtCookie');assert bs[1]['raw'][cp:cp+16]==cookie
    stream=next(g for g in bs[1]['segs'].values()if g['name']=='"BT_STREAM"');pos=int(stream['ooffs'],0)
    assert bs[1]['raw'][pos:pos+8192]==z
   else:assert not changes,('retained foreign cached payload changed',path.name,changes)
   side.append(dict(name=path.name,changed_offsets=changes,parent_sha256=sha(path),child_sha256=sha(child)))
  # Raw little-endian coincidences are retained as data/opcode pairs, never
  # globally rewritten. No retained image contains direct JSR/JMP(oldHu).
  coincidences=[]
  for path in sorted((J/'sideoutputs').glob('*.bin')):
   data=path.read_bytes()
   for name in sorted(targetnames):
    value=int(moves[name]['old'],16).to_bytes(2,'little')
    for at in range(1,len(data)-1):
     if data[at:at+2]!=value:continue
     assert data[at-1]not in[0x20,0x4c,0x6c],('old direct control target',path.name,name,at)
     coincidences.append(dict(image=path.name,name=name,offset=at,context=data[max(0,at-5):at+5].hex(' '),classification='Retained data-state access or opcode/immediate boundary, not an imported A79 control target. Genuine imports enumerated from every actual final object.'))
  # Real source.incbin mirror assembly must consume this same final127, with
  # declared donor DMC regions and the original CV3 manager as exceptions.
  fixed=bs[1]['raw'][16+127*8192:16+128*8192];assert fixed==(J/'source/fixed127.bin').read_bytes()
  dmc=(J/'source/dmc-clones.s').read_text();assert str((J/'source/fixed127.bin').as_posix())in dmc
  for bank,ranges in[(119,[(0,4416),(5697,5760),(6721,6784),(7681,8192)]),(120,[(0,4416),(5489,5504),(6145,6208),(6465,6528),(7681,8192)]),(125,[(0,0x1140),(0x1581,0x15c0),(0x1681,0x1af7),(0x1b8a,8192)])]:
   image=bs[1]['raw'][16+bank*8192:16+(bank+1)*8192]
   for lo,hi in ranges:assert image[lo:hi]==fixed[lo:hi],('same-final127 mirror',bank,lo,hi)
  q.update(passed=True,actual_Hot_allraw_allflags_pairs=pairs,emitted_original_Hot_targets=rows,actual_final_object_count=len(inputs),moved_import_consumers=imports,cached_sideimage_closure=side,old_numeric_data_coincidences=coincidences,same_final127_mirrors=[119,120,125],limitations=['Finite typed target/import/source-carrier closure; no global replacement of numerical coincidences','Real complete foreign callback behavior independently compared in five genuine cold/Main cohorts','Current a126 lineage only; root a441/campaign/other later source composition still separate'])
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p):sha(p)for p in[Path(__file__),Path(L.__file__),Path(H.__file__),J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'final-link.json',I/'moved-symbols.json',I/'moved-import-consumers.json']}
 dump(O/'controls.json',q);print(json.dumps({k:v for k,v in q.items()if k not in['bindings','emitted_original_Hot_targets','moved_import_consumers','cached_sideimage_closure','old_numeric_data_coincidences','traceback']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
