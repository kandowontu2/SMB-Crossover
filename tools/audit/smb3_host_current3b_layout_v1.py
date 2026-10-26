"""Frozen3b source/PC/art/current-resident-clone ownership and payload placement."""
from pathlib import Path
import argparse,difflib,json,traceback
from smb3_host_current3b_cpu_v1 import D,R,sha,put,FIELDS
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

EXPECTED='7469d9f62af3161c896b844546ead66002bb425ba8b5143692b1c2ae1d9f1219'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);base=D/'root-current-roster-composition-v1'
 try:
  assert sha(a.packet/'candidate.nes')==EXPECTED
  old=scoped_load(base/'candidate.nes');new=scoped_load(a.packet/'candidate.nes');ob=(base/'candidate.nes').read_bytes();nb=(a.packet/'candidate.nes').read_bytes()
  assert ob[:16]==nb[:16] and ob[16+128*8192:]==nb[16+128*8192:]
  oldmanifest=json.loads((base/'source-manifest.json').read_text());newmanifest=json.loads((a.packet/'source-manifest.json').read_text());changed=[];patch=[]
  assert len(oldmanifest)==869 and len(newmanifest)==872 and set(oldmanifest)<=set(newmanifest)
  for n,h in newmanifest.items():
   assert sha(a.packet/'source'/n)==h,n
   if n in oldmanifest:assert sha(base/'source'/n)==oldmanifest[n],n
   if oldmanifest.get(n)==h:continue
   before=(base/'source'/n).read_bytes()if n in oldmanifest else b'';after=(a.packet/'source'/n).read_bytes();row=dict(path=n,parent_sha256=oldmanifest.get(n),candidate_sha256=h)
   if before:
    kind=lambda b:dict(CRLF=b.count(b'\r\n'),bareLF=b.count(b'\n')-b.count(b'\r\n'))
    row['EOL_before']=kind(before);row['EOL_after']=kind(after)
    assert bool(kind(before)['bareLF'])==bool(kind(after)['bareLF']) and bool(kind(before)['CRLF'])==bool(kind(after)['CRLF']),('EOL convention changed',n)
   changed.append(row)
   if Path(n).suffix in ['.s','.inc','.cfg']:patch+=difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/'+n,tofile='b/'+n)
  assert len(changed)==9
  (a.output/'implementation.patch').write_bytes(''.join(patch).encode())
  moved=[];missing=[];retained=0
  for name,s in old['syms'].items():
   if name not in new['syms']:missing.append(name);continue
   before=(s.get('val'),s.get('type'));after=(new['syms'][name].get('val'),new['syms'][name].get('type'))
   if before!=after:
    at=location(old,name);dest=location(new,name);assert at is not None and dest is not None
    originalbank=(at-16)//8192;newbank=(dest-16)//8192
    assert(originalbank,newbank)in[(70,95),(97,95)],('Non-art public symbol moved',name,before,after,originalbank,newbank)
    moved.append(dict(name=name,before=before,after=after,from_bank=originalbank,to_bank=newbank))
   else:retained+=1
  assert not missing and len(moved)==180
  diffs=[]
  for bank in range(128):
   x=ob[16+bank*8192:16+(bank+1)*8192];y=nb[16+bank*8192:16+(bank+1)*8192]
   if x!=y:diffs.append(dict(bank=bank,changed_bytes=sum(v!=w for v,w in zip(x,y))))
  assert[dict(bank=bank,changed_bytes=n)for bank,n in [(5,41),(25,5),(29,1),(38,5106),(69,20),(70,7908),(71,6),(78,4096),(85,5048),(86,4385),(90,3921),(93,3761),(95,5768),(96,2548),(97,7761),(98,3067),(118,4061),(119,2695),(125,2),(126,1),(127,2)]]==diffs
  mirrors=json.loads((a.packet/'candidate.smb3-mirrors.json').read_text());assert mirrors['ROM_sha256']==EXPECTED
  resident=nb[16+127*8192:16+128*8192];aliases=[]
  # Native observer must accept genuine dynamic E aliases, never pretend all
  # resident execution stays in127 while hardware DMC actually owns70/97.
  names=['NonMaskableInterrupt','ContinueNMI','ExitNMI','AudioUpdate','GuestDmcStatus','Cv3DmcOwnerWrite']
  for name in names:
   pc=address(new,name);offset=pc-0xe000;assert 0<=offset<8192
   chunk=resident[offset:offset+16]
   for bank in [70,97,127]:assert nb[16+bank*8192+offset:16+bank*8192+offset+16]==chunk,(name,bank)
   aliases.append(dict(name=name,CPU=pc,physical_E_banks=[70,97,127],first16bytes_hex=chunk.hex()))
  payload=(a.packet/'source/audio/smb3-native/source-payload.bin').read_bytes();placement=[]
  assert len(payload)==36864
  for page,bank in enumerate([78,86,90,93,95,96,98,118,119]):
   data=nb[16+bank*8192+4096:16+(bank+1)*8192];assert data==payload[page*4096:(page+1)*4096];placement.append(dict(page=page,physical_bank=bank,CPU_window='B000..BFFF / D000..DFFF according lease'))
  put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=sha(base/'candidate.nes'),candidate_ROM_sha256=EXPECTED,header_and_all_CHR_literal=True,changed_source_files=changed,complete_source_files=872,all_old_symbols_retained_or_genuine_data_relocated=True,unchanged_old_symbols=retained,genuine_art_symbol_moves=moved,missing_old_symbols=missing,changed_banks=diffs,source_core_span=[address(new,'B3CoreStart'),address(new,'B3CoreEnd')],source_cold_span=[address(new,'B3ColdStart'),address(new,'B3ColdEnd')],core_capacity_remaining=0x1400-(address(new,'B3CoreEnd')-address(new,'B3CoreStart')),cold_capacity_remaining=0x200-(address(new,'B3ColdEnd')-address(new,'B3ColdStart')),resident_native_hook_aliases=aliases,full_authentic_payload_pages=placement,mirror_receipt_sha256=sha(a.packet/'candidate.smb3-mirrors.json'),source_state_reachable_RAM_addresses=FIELDS,implementation_patch_sha256=sha(a.output/'implementation.patch'),checker_sha256=sha(__file__),limits='Source/compiled ownership only. Sixteen-byte hook signatures are readiness bindings, not native entry/return observation. Full regenerated clones are separately bytechecked by the producer outside its declared samples. No physical PPU, DMC fetch clock, waveform, native return/stack/DMA/cadence or live-hook adoption claim.'))
  print(json.dumps(dict(passed=True,changed_source_files=len(changed),symbols_retained=retained,genuine_art_moves=len(moved),changed_banks=len(diffs))))
 except Exception as e:put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
