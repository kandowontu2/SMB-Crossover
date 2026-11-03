"""Proposed full collision image in memory; new execution remains ungranted."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_sunny_rebase_1102_v54 as P
O=P.O;A=P.A;BASE=P.BASE;PIN=P.PIN;sha=P.sha


def bundle():
 base,_,prior,details=P.bundle();raw=base['raw'];labels=json.loads((O/'native-labels-v49.json').read_text())
 source=(O/'current-selector-v51.s').read_text();needle='PpNativeRoute=$df29';assert source.count(needle)==1;source=source.replace(needle,f'PpNativeRoute=${labels["PpNativeRoute"]:04x}')
 selector,_=A.assemble('collision-selector-v59',source,(O/'current-selector-v51.cfg').read_text());oldselector=(O/'current-selector-v51.bin').read_bytes();assert len(selector)==len(oldselector)
 diffs=[i for i,(a,z)in enumerate(zip(oldselector,selector))if a!=z];assert diffs==[145]and selector[145]==labels['PpNativeRoute']&255 and selector[150]==labels['PpNativeRoute']>>8
 payload=(O/'cold-pool-v57.bin').read_bytes();cookie=bytes([0xa7,38,2])+hashlib.sha256((O/'native-runtime-v49.bin').read_bytes()+(O/'native-metadata-v49.bin').read_bytes()+(O/'native-state-v49.bin').read_bytes()+payload).digest()[:13]
 text=(O/'current-owner-v51.s').read_text();assert f'PrNativeRetire=${labels["PpNativeRetire"]:04x}'in text
 at=text.index('PrCookie:\n')+len('PrCookie:\n');end=text.index('\nPrExtraEnd:');oldcookie=text[at:end];text=text[:at]+'.byte '+','.join(f'${v:02x}'for v in cookie)+text[end:]
 cfg=(O/'current-owner-v51.cfg').read_text().replace('current-owner-extra-v51.bin','collision-owner-extra-v59.bin');owner,lab=A.assemble('collision-owner-v59',text,cfg);extra=(O/'collision-owner-extra-v59.bin').read_bytes()
 assert owner==(O/'current-owner-v51.bin').read_bytes();oldextra=(O/'current-owner-extra-v51.bin').read_bytes();ci=lab['PrCookie']-0xab72;assert extra[:ci]==oldextra[:ci]and extra[ci+16:]==oldextra[ci+16:]
 replacements={(65,0xa740):selector,(65,0xae00):owner,(65,0xab72):extra};post=bytearray(raw);patches=[]
 for patch in prior:
  if 'physical_PRG'not in patch:continue
  at=patch['file_offset'];pre=bytes.fromhex(patch['old_hex']);assert raw[at:at+len(pre)]==pre;blob=replacements.get((patch['physical_PRG'],patch['CPU_half_open'][0]),bytes.fromhex(patch['new_hex']));assert len(blob)==len(pre)
  post[at:at+len(blob)]=blob;patches.append(dict(patch,new_hex=blob.hex(),new_SHA256=sha(blob)))
 for i,page in enumerate(P.P.M.POOL+[514]):
  blob=payload[i*1024:(i+1)*1024]
  if not blob:continue
  at=1048592+1024*page;pre=raw[at:at+len(blob)];post[at:at+len(blob)]=blob;patches.append(dict(physical_CHR=page,file_offset=at,bytes=len(blob),old_hex=pre.hex(),new_hex=blob.hex(),old_SHA256=sha(pre),new_SHA256=sha(blob),role='Existing44 granted Prince carriers; new execution proposal only',source_offset=i*1024))
 writes={i for p in patches for i in range(p['file_offset'],p['file_offset']+p['bytes'])}
 for row in details['sunny_five_exact_extents']:
  at=row['file_offset'];blob=bytes.fromhex(row['new_hex']);assert not writes&set(range(at,at+len(blob)))and post[at:at+len(blob)]==blob
 for at,length in details['all55_Bub_event_spans_retained']:assert post[at:at+length]==raw[at:at+length]
 inherited={i for i,(a,z)in enumerate(zip(P.P.M.bundle()[0]['raw'],raw))if a!=z};assert not inherited&writes and len(inherited)==1927
 return base,dict(base,raw=bytes(post)),patches,dict(details,cookie=cookie.hex(),previous_granted_cookie=details['cookie'],selector_two_operand_offsets=diffs,manager_531bytes_unchanged=True,retire_target=labels['PpNativeRetire'],new_native_route=labels['PpNativeRoute'],source_code_audio_v49_not_included=False,execution_extensions_granted=False,new_changed_bytes=sum(a!=z for a,z in zip(raw,post)))


def main():
 base,new,patches,details=bundle();q=dict(passed=True,status='UNGRANTED_EXECUTION_PROPOSAL_ONLY',ROM_written=False,installed=False,base=BASE.relative_to(R).as_posix(),base_SHA256=PIN,expected_memory_only_SHA256=sha(new['raw']),patches=patches,details=details,execution_amendment_required=dict(live_audio=[0xc780,0xc800],cold_staged_PC=[0xc65f,0xc678],dead_renderer=[0xbd3e,0xbd4b],live_metadata=[0xdfa2,0xdfce]),scope='Exact private current16a9 memory manifest for source-derived collision/pickup proposal. Existing44 physical carriers and prior shared selector/manager extents only; no ROM or menu/install writes. New execution lifetimes and current shared/fresh/auth tests require root review. Source original audio production remains typed pending; donor mixer/native music mapping remains incomplete.',bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in [Path(__file__),BASE,P.RECEIPT,O/'sunny-rebase-manifest-v54.json',O/'sunny-services-CPU-v55.json',O/'quiet-audio-code-proposal-v48.json',O/'collision-services-measurement-v49.json',O/'collision-services-CPU-v56.json',O/'cold-link-storage-v57.json',O/'collision-cold-CPU-v58.json',O/'collision-cold-negative-v58.json',O/'cold-pool-v57.bin',O/'collision-selector-v59.bin',O/'collision-owner-v59.bin',O/'collision-owner-extra-v59.bin']})
 (O/'collision-manifest-v59.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['patches','bindings','details']}));print(json.dumps({k:details[k]for k in ['cookie','new_native_route','retire_target','current_inherited_bytes_retained','Sunny_palette_gate_and_local_C_skip_ABI_preserved','new_changed_bytes']}))


if __name__=='__main__':main()
