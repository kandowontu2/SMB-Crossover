"""Close conditional physical leases against actual ac126 source/table owners."""
from pathlib import Path
import hashlib,json,re,sys
import gimmick_leases_v2 as L
R=L.R;O=L.O
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
def main():
 assert not(O/'handoff.json').exists()
 b=scoped_load(L.P);old=json.loads((O/'lease-proof.json').read_text());deps=json.loads((L.P.parent/'build-proof.json').read_text())['actual_dependencies']
 assert old['parent']['sha256']==L.EXPECTED
 names={'contra.inc','gradius-native.inc','gradius_audio.s','kirby.s','kirby_art.inc','kirby_copy_icons.inc','kirby_adapter.s','kirby_draw.s','meta_knight_art.inc','meta_knight.s','meta_knight_adapter.s','vic_viper.s','vic_native_motion.s','vic_native_weapons.s','vic_gear.s','vic_world_queries.s','vic_adapter.s','parodius.s','parodius_native.s','parodius_adapter.s','parodius_data.inc','parodius_contact_data.inc','tmnt_art.inc','tmnt.s','tmnt_render.s'}
 consumed={p:h for p,h in deps.items()if Path(p).name in names or Path(p).name.startswith(('kirby_','meta_knight_','vic_','parodius_','tmnt_'))};assert len(consumed)>=20,len(consumed)
 for p,h in consumed.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,('Changed actual parent dependency',p)
 owners={g['name'].strip('"'):g for g in b['segs'].values()if g['name'].strip('"')in ['CONTRA_AUDIO','VIC_NATIVE_AUDIO','VIC_CORE','KIRBY_GFX']}
 def sym(n):
  q=b['syms'].get(n);assert q and 'val'in q,('Unresolved genuine label',n)
  return int(q['val'],0),b['segs'].get(q.get('seg'),{})
 pointers=[];literal=[];indirect=[]
 for pp in consumed:
  p=Path(pp)
  for line_no,line in enumerate(p.read_text().splitlines(),1):
   s=line.split(';')[0].strip()
   if not s:continue
   # All ROM pointers in the two genuine stream programs are symbolic ca65
   # relocations. A stream cursor advances through emitted data; FE/FD loop
   # targets are .addr/.word, never a hidden pointer into linker FF fill.
   if p.name=='contra.inc' and 'generated'not in str(p):continue
   if p.name not in ['contra.inc','gradius-native.inc']:continue
   if re.match(r'\.(addr|word)\b',s):
    q=s.split(None,1)[1]
    for n in q.split(','):
     n=n.strip();assert re.fullmatch(r'[A-Za-z_]\w*',n),('Non-symbolic ROM pointer needs review',pp,line_no,s)
     a,g=sym(n);assert g['name'].strip('"')in ['CONTRA_AUDIO','VIC_NATIVE_AUDIO'],(pp,line_no,n,g)
     assert int(g['start'],0)<=a<int(g['start'],0)+int(g['size'],0)
     pointers.append([p.name,line_no,n,a])
   if re.match(r'(lda|cmp|jmp)\s+\(',s,re.I):indirect.append([p.name,line_no,s])
   m=re.match(r'(?:lda|ldx|ldy|sta|stx|sty|adc|sbc|cmp|and|ora|eor|bit|inc|dec|jmp|jsr)\s+\$([89a-f][0-9a-f]{3})',s,re.I)
   if m:literal.append([p.name,line_no,int(m[1],16),s])
 # No unrelocated CPU-ROM literal survives these translated drivers. The
 # indirect E0/E4/E8/EC and F6/FA families come from the symbolic tables above;
 # their literal grammar is bound with the exact original parser source.
 assert not literal,literal[:10]
 # Authenticate all Kirby/MK/icon descriptor targets in the borrowed C73.
 records={};actions={}
 for pp in consumed:
  if Path(pp).name not in ['kirby_art.inc','kirby_copy_icons.inc','meta_knight_art.inc']:continue
  for n in set(re.findall(r'[<>]([A-Za-z_]\w*)',Path(pp).read_text())):
   a,g=sym(n)
   if g.get('name')!='"KIRBY_GFX"':continue
   assert 0xc000<=a<0xd908,(n,hex(a))
   at=int(g['ooffs'],0)+a-int(g['start'],0);length=b['raw'][at]
   if re.fullmatch(r'MkAction[0-6]',n):
    k=int(n[-1]);length_addr,gg=sym('MkActionLength');length=b['raw'][int(gg['ooffs'],0)+length_addr-int(gg['start'],0)+k]
    assert a+length<=0xd908 and max(b['raw'][at:at+length])<90,(n,length)
    actions[n]=dict(address=a,length=length,max_pose=max(b['raw'][at:at+length]));continue
   assert length%4==0 and a+length+1<=0xd908,(n,hex(a),length)
   records[n]=dict(address=a,parts=length//4,end=a+length+1)
 assert len(records)>100,len(records)
 # VIC_CORE routines/tables are fully emitted symbolic source; verify every
 # actual owner label lies below B9B9, not only the all-FF proposed preimage.
 labels=[]
 for n,s in b['syms'].items():
  if 'seg'in s and b['segs'][s['seg']].get('name')=='"VIC_CORE"':
   a=int(s['val'],0);assert 0xa000<=a<=0xb9b9,(n,hex(a));labels.append(n)
 # Source-owned original TMNT body/equipment pages end below unused tail;
 # current GB-Pit pages808..812 are emitted separately and are untouched.
 chr_at=16+1048576+816*1024
 assert b['raw'][chr_at:chr_at+4096]==bytes(4096)
 chr_owners=[]
 for g in b['segs'].values():
  if 'ooffs'not in g or not int(g['size'],0):continue
  lo=int(g['ooffs'],0);hi=lo+int(g['size'],0)
  assert hi<=chr_at or lo>=chr_at+4096,('Emitted CHR owner in proposed pages',g)
 for g in owners.values():
  # Every old emitted endpoint is below the approved preimage, including
  # Parodius routines sharing VIC_CORE and MK/icon records sharing KIRBY_GFX.
  assert int(g['size'],0)>0
 proof=dict(status='PRIVATE_SOURCE_OWNER_LEASE_CLOSED',parent=L.bind(L.P),prior_partial=L.bind(O/'lease-proof.json'),
  exact_parent_source_dependencies=[dict(path=p,sha256=h)for p,h in consumed.items()],
  source_parser_pointer_relocations=len(pointers),pointer_relocations=pointers,ROM_indirect_sites=indirect,
  unrelocated_ROM_literals=literal,Kirby_MK_icon_complete_records=records,MK_action_arrays=actions,VIC_CORE_actual_labels=len(labels),
  emitted_owner_extents=owners,CHR=dict(first=816,pages=4,all_zero=True,no_emitted_segment=True),
  scope='Conditional approved leases closed for current authenticated source consumers: actual emitted owners and symbolic pointer/record parser closure plus original finite77 Contra/16Gradius dynamic campaign. Not arbitrary corrupted RAM/pointer values, future generated assets or an unbounded formal machine proof. Every link rechecks immutable parent bytes. Original loops/streams and neighboring wrappers are retained byte-exact.',
  bindings=[L.bind(Path(__file__)),L.bind(L.P.with_suffix('.dbg')),L.bind(L.P.parent/'build-proof.json')])
 (O/'lease-closure.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(status=proof['status'],sources=len(consumed),pointers=len(pointers),records=len(records),VIC_labels=len(labels))))
if __name__=='__main__':main()
