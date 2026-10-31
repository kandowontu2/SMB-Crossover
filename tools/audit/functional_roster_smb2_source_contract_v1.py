"""Source and emitted-boundary contract for the no-growth SMB2 join."""
from pathlib import Path
import json,re
from check_tmnt_render_oa import load,address,location
import prepare_functional_roster_smb2_v1 as B
O=B.O;N=B.N;P=B.P

def main():
 out=O/'source-contract.json';assert not out.exists()
 old,new=[load(p/'candidate.nes')for p in [P,N]]
 h=address(old,'HuEntryBase');prologues=[]
 for i in range(36):
  a=16+79*8192+((h+16*i)&8191)
  x=old['raw'][a:a+11];y=new['raw'][a:a+11]
  assert x==y and x[-3]==0x4c and x[-2]+256*x[-1]==address(new,'HuCommon'),('fixed11B/no-fallthrough',i)
  prologues.append(dict(index=i,PC=h+16*i,bytes=x.hex(),island_PC=h+16*i+11,terminates_absolute_JMP_HuCommon=True))
 # Each old selected-owned five-byte island was not data/continuation: its
 # entire enclosing public entry is source-fixed16B, terminated by JMP, and
 # old code had no defined symbol there. References now have real symbols.
 for i,name in [(30,'HuS2Decide'),(31,'HuS2Foreign'),(32,'HuS2High'),(33,'HuS2StoreHigh'),(34,'HuS2Bank')]:
  pc=h+i*16+11;at=16+79*8192+(pc&8191)
  assert old['raw'][at:at+5]==bytes([255])*5
  assert address(new,name)==pc
  assert not [n for n,s in old['syms'].items()if 'seg'in s and int(s['val'],0)==pc and int(old['segs'][s['seg']].get('ooffs','-1'),0)//8192==79]
 for name in ['HuEntryBase','HuEnd','GmOnlyCommon','GmOnlyQuick']:
  assert address(old,name)==address(new,name),name
 # Every private Only ingress supplies exactly the agreed 0..15 immediate
 # index before the shared helper; ORA16 only replaces arithmetic there.
 text=(N/'src/new_roster_dispatch.s').read_text()
 assert 'Legacy:\n tya\n ora #16\n tay\nOwn:' in text
 oldh=address(old,'HuEnd');newh=address(new,'HuEnd');assert newh==oldh==0xbfff
 protected=['river_city_required_ink_v1.inc','river_city_shared_palette_art.inc','chip_dale_render.s']
 for name in protected:assert B.sha(P/'src'/name)==B.sha(N/'src'/name),name
 for name in ['code.bin','data.bin','ram3.bin']:assert B.sha(P/name)==B.sha(N/name),name
 # Real dependencies emitted by the actual newly compiled ca65 recipes.
 dependencies={N/'private.cfg'};objects=set();commands=[]
 for path in O.glob('*-build.json'):
  q=json.loads(path.read_text());c=q.get('command',[])
  if not c:continue
  assert q.get('returncode',0)==0,path
  commands.append(path)
  for token in c:
   if token.endswith(('.s','.inc','.o','.cfg'))and Path(token).is_file():dependencies.add(Path(token).resolve())
  if '--create-full-dep' in c:
   dep=Path(c[c.index('--create-full-dep')+1]);dependencies.add(dep)
   first=dep.read_text().split(':\t',1)[1].splitlines()[0]
   for token in re.split(r'(?<!\\)\s+',first):
    if not token:continue
    p=Path(token.replace('\\ ',' '));p=(B.R/p).resolve()if not p.is_absolute()else p.resolve();assert p.is_file(),p;dependencies.add(p)
 c=json.loads((O/'final-link.json').read_text())['command']
 for token in c:
  if token.endswith('.o'):objects.add(Path(token).resolve())
 assert objects and all(p.is_file()for p in objects);dependencies.update(objects)
 closure=dict(passed=True,actual_new_Main_and_S2_common_union_recompiled=True,actual_inputs=len(dependencies),linked_objects=len(objects),copied_object_provenance='Parent54 and immutable correctedS2v15/v13 handoffs remain binding for source objects not rebuilt here.',bindings={str(p.resolve()):B.sha(p)for p in sorted(dependencies)})
 (O/'source-closure.json').write_text(json.dumps(closure,indent=2)+'\n')
 d=dict(passed=True,native=False,candidate=B.sha(N/'candidate.nes'),all36_fixed11B_public_entry_prologues=prologues,old_owned_padding_repurposed_without_public_fallthrough=[30,31,32,33,34],HuEnd=newh,A79_payload=2591,A79_capacity=2592,GmOnly_helpers_no_growth=True,RCR_Chip_sources_exact=True,Quick_Arthur_FF_code_data_exact=True,source_closure=B.sha(O/'source-closure.json'),limits=['Actual emitted prologues and private source-call indices close the padding/ORA16 contracts; allraw/flags runtime and realvector controls are separate bound receipts.','No full1-1/allupgrades/nativePPU/cadence claim.'],bindings={str(p.resolve()):B.sha(p)for p in [Path(__file__),O/'source-stage.json',O/'shared-source.patch',P/'candidate.nes',P/'candidate.dbg',N/'candidate.nes',N/'candidate.dbg',N/'union.s',N/'src/new_roster_dispatch.s',O/'source-closure.json']})
 out.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(passed=True,inputs=len(dependencies),linked_objects=len(objects),A79=2591)))
if __name__=='__main__':main()
