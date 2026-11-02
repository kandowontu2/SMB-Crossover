"""Emit only the CPU-qualified exact wall delta and unchanged native packets."""
from pathlib import Path
import hashlib,json,re
import check_arthur_side_clamp_1101_v8 as C
from prepare_selected_native_packet_v1 import prepare
P=C.P;O=P.O


def main():
 receipts=[]
 for name in ['CPU.json','callers-CPU.json']:
  q=json.loads((O/name).read_text());assert q['passed'];receipts.append(q)
  for path,h in q['bindings'].items():assert P.sha(P.R/path)==h,path
 old,new=C.bundle();rom=O/'candidate.nes';digest=hashlib.sha256(new['raw']).hexdigest()
 assert all(q['proposed_candidate_sha256']==digest for q in receipts)
 at=C.location(old,'SamusStopAtWallBanked');delta=[i for i,(a,z)in enumerate(zip(old['raw'],new['raw']))if a!=z]
 assert delta and all(at<=i<at+215 for i in delta)
 # Replace only the actual procedure's local label records, retaining public
 # entries and all other owners' linked source/symbol records byte-for-byte.
 labels={n:int(a,16)for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'new-wall.lbl').read_text(),re.M)}
 scope=old['syms']['SamusStopAtWallBanked::Page']['scope'];seg=old['syms']['SamusStopAtWallBanked']['seg']
 lines=P.BASE.with_suffix('.dbg').read_text().splitlines();remaining=[];maxid=0
 for line in lines:
  if line.startswith('sym\t'):
   d=dict(v.split('=',1)for v in line[4:].split(',')if'='in v);maxid=max(maxid,int(d['id']))
   if d.get('scope')==scope:continue
  remaining.append(line)
 for name,pc in labels.items():
  if name=='SamusStopAtWallBanked':continue
  maxid+=1;remaining.append(f'sym\tid={maxid},name="{name}",addrsize=absolute,scope={scope},val=0x{pc:04X},seg={seg},type=lab')
 rom.write_bytes(new['raw']);rom.with_suffix('.dbg').write_text('\n'.join(remaining)+'\n')
 # Existing LBL locals are unscoped and ambiguous across physical banks.
 # Add genuine scoped aliases rather than deleting another owner's names.
 text=P.BASE.with_suffix('.lbl').read_text()
 text+='\n'+''.join(f'al {pc:06X} .SamusStopAtWallBanked::{n}\n'for n,pc in labels.items()if n!='SamusStopAtWallBanked')
 rom.with_suffix('.lbl').write_text(text)
 b=C.scoped_load(rom);assert C.address(b,'SamusStopAtWallBanked::NativeGuest')==0xa29d and C.address(b,'SamusStopAtWallBanked::Page')==labels['Page']
 for n,s in old['syms'].items():
  if s.get('scope')!=scope and(s.get('scope')=='1'or'::'in n):assert C.address(b,n)==C.address(old,n),(n,'External label moved')
 q=dict(prepared=True,installed=False,native=False,ROM_sha256=digest,base_sha256=P.SHA,changed_ROM_bytes=len(delta),only_physical_PRG_bank=10,owned_CPU_half_open=['A290','A367'],owned_file_half_open=[at,at+215],all_other_ROM_bytes_exact=True,no_new_PRG_CHR_RAM=True,no_external_or_NativeGuest_entry_moved=True,delta=[dict(file_offset=i,old=old['raw'][i],new=new['raw'][i])for i in delta],bindings={str(p.relative_to(P.R)):P.sha(p)for p in [Path(__file__),rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),O/'CPU.json',O/'callers-CPU.json',P.SOURCE]})
 (O/'candidate.json').write_text(json.dumps(q,indent=2)+'\n')
 for name,ref,timeout,scope in [
  ('flower',P.R/'build/arthur-natural-flower-1101-v6/native2/controller.lua',150,'Unchanged controller-earned firstflower route and source torch pickup from v30 negative; no memory seeds/helpers. Native pending.'),
  ('full11',P.R/'build/arthur-death-1101-v4/full11-stairs/controller.lua',240,'Unchanged qualified Arthur full1-1 stair controller, all4pipes/3gaps toactual1-2 without life loss. No memory seeds/helpers. Native pending.')]:
  prepare(O/name,rom,ref.read_text(),[Path(__file__),ref,O/'candidate.json'],expected=digest,timeout=timeout,scope=scope,allow_interactive=True)
 print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','delta']}))


if __name__=='__main__':main()
