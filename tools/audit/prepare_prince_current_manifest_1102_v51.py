"""Granted battle v47 memory-only composition over actual22d099 nightly."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_cold_worker_1102_v19 as A
import prepare_prince_successor_manifest_1102_v26 as M
O=M.O
BASE=R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes'
PIN='22d09909bf952ef007d1582589dc869073262784bf38b92d2c7b206ce3c45b19'
sha=lambda b:hashlib.sha256(b).hexdigest()


def bundle():
 parent,_,old_patches,event=M.bundle();raw=BASE.read_bytes();assert sha(raw)==PIN
 current=dict(parent,raw=raw);lab=json.loads((O/'native-labels-v42.json').read_text())
 text=(O/'public-selector-v24.s').read_text();old=A.L.P.T.labels(O/'public-private-v24.lbl')['PpNativeRoute'];needle=f'PpNativeRoute=${old:04x}';assert text.count(needle)==1;text=text.replace(needle,f'PpNativeRoute=${lab["PpNativeRoute"]:04x}')
 selector,slab=A.assemble('current-selector-v51',text,(O/'public-selector-v24.cfg').read_text());assert len(selector)==(O/'public-selector-v24.bin').stat().st_size
 # Cookie binds complete actual live code and backing, never selected RAM
 # state or an outcome. All old Ex/BB/Sh cookie bytes remain source-exact.
 payload=(O/'cold-pool-v44.bin').read_bytes();cookie=bytes([0xa7,38,2])+hashlib.sha256((O/'native-runtime-v42.bin').read_bytes()+(O/'native-metadata-v42.bin').read_bytes()+(O/'native-state_code-v18.bin').read_bytes()+payload).digest()[:13]
 text=(O/'owner-third-v23.s').read_text();needle='PrNativeRetire=$dbba';assert text.count(needle)==1;text=text.replace(needle,f'PrNativeRetire=${lab["PpNativeRetire"]:04x}')
 oldcookie=text[text.index('PrCookie:\n')+len('PrCookie:\n'):text.index('\nPrExtraEnd:')];assert oldcookie.startswith('.byte ')and len(bytes.fromhex(oldcookie.replace('.byte ','').replace('$','').replace(',','')))==16;text=text.replace(oldcookie,'.byte '+','.join(f'${v:02x}'for v in cookie))
 cfg=(O/'owner-third-v23.cfg').read_text().replace('owner-third-extra-v23.bin','current-owner-extra-v51.bin')
 owner,olab=A.assemble('current-owner-v51',text,cfg);extra=(O/'current-owner-extra-v51.bin').read_bytes();assert len(owner)==531 and len(extra)==(O/'owner-third-extra-v23.bin').stat().st_size
 # Assert exact only-source-authorized resident rebindings versus v30.
 oldselector=(O/'public-selector-v24.bin').read_bytes();sdiff=[i for i,(a,z)in enumerate(zip(oldselector,selector))if a!=z];assert len(sdiff)==2
 oldowner=(O/'owner-third-v23.bin').read_bytes();oldextra=(O/'owner-third-extra-v23.bin').read_bytes();assert owner==oldowner
 diff=[i for i,(a,z)in enumerate(zip(oldextra,extra))if a!=z];ret=olab['PrRetire'];cookie_at=olab['PrCookie'];calls=[i for i in range(len(oldextra)-2)if oldextra[i:i+3]==bytes.fromhex('20badb')];assert len(calls)==1
 allowed={calls[0]+1,calls[0]+2}|set(range(cookie_at-0xab72,cookie_at-0xab72+16));assert set(diff)<=allowed and extra[calls[0]+1:calls[0]+3]==lab['PpNativeRetire'].to_bytes(2,'little')
 post=bytearray(raw);patches=[]
 replacements={(65,0xa740):selector,(65,0xae00):owner,(65,0xab72):extra}
 for patch in old_patches:
  if 'physical_PRG'not in patch:continue
  at=patch['file_offset'];pre=bytes.fromhex(patch['old_hex']);assert raw[at:at+len(pre)]==pre,('Current shared preimage drift',patch['role'],at)
  bank=patch['physical_PRG'];cpu=patch['CPU_half_open'][0];blob=replacements.get((bank,cpu),bytes.fromhex(patch['new_hex']));assert len(blob)==len(pre)
  post[at:at+len(blob)]=blob;patches.append(dict(physical_PRG=bank,CPU_half_open=[cpu,cpu+len(blob)],file_offset=at,bytes=len(blob),old_hex=pre.hex(),new_hex=blob.hex(),old_SHA256=sha(pre),new_SHA256=sha(blob),role=patch['role']))
 for i,page in enumerate(M.POOL+[514]):
  blob=payload[i*1024:(i+1)*1024]
  if not blob:continue
  at=1048592+1024*page;pre=raw[at:at+len(blob)];assert pre==parent['raw'][at:at+len(blob)],('Current granted carrier drift',page)
  post[at:at+len(blob)]=blob;patches.append(dict(physical_CHR=page,file_offset=at,bytes=len(blob),old_hex=pre.hex(),new_hex=blob.hex(),old_SHA256=sha(pre),new_SHA256=sha(blob),role='Existing44 granted Prince source/art/code carriers',source_offset=i*1024))
 # Every cumulative/root menu/Thomas difference relative to613b is retained
 # and explicitly disjoint from every new write, including equal-value spans.
 inherited={i for i,(a,z)in enumerate(zip(parent['raw'],raw))if a!=z};written={i for p in patches for i in range(p['file_offset'],p['file_offset']+p['bytes'])};assert not inherited&written,('Current inherited delta overlap',len(inherited&written))
 for at,length in event:assert post[at:at+length]==raw[at:at+length]
 changed={i for i,(a,z)in enumerate(zip(raw,post))if a!=z};assert changed<=written and len(post)==len(raw)
 return current,dict(current,raw=bytes(post)),patches,dict(cookie=cookie.hex(),selector_two_operand_offsets=sdiff,manager_531bytes_unchanged=True,manager_extra_changed_offsets=diff,current_inherited_bytes_retained=len(inherited),all55_Bub_event_spans_retained=event,new_changed_bytes=len(changed),old_native_route=old,new_native_route=lab['PpNativeRoute'],old_retire=0xdbba,new_retire=lab['PpNativeRetire'],source_code_audio_v49_not_included=True,production_menu_admission_changed=False)


def main():
 base,new,patches,details=bundle();q=dict(status='PRIVATE_SOURCE_COMPOSITION_MANIFEST_NO_NATIVE_ADMISSION',ROM_written=False,installed=False,base=BASE.relative_to(R).as_posix(),base_SHA256=PIN,expected_memory_only_SHA256=sha(new['raw']),patches=patches,details=details,qualified_inputs='Frozen v47 original battle,6050B metadata,44254B payload and grantedv46 execution only. Ungranted proposedC780 v49 code is excluded.',required='Actual current22d099 full shared manager/header/fresh/scene/foreign/ISR qualification of exact rebound labels/cookie. Remaining collision policies/native play are not admitted. Root owns Mesen/install queue.',bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in [Path(__file__),BASE,O/'current-selector-v51.bin',O/'current-owner-v51.bin',O/'current-owner-extra-v51.bin',O/'native-runtime-v42.bin',O/'native-metadata-v42.bin',O/'cold-pool-v44.bin',O/'native-link-CPU-v43.json',O/'cold-link-CPU-v45.json',R/'docs/qa/allocations/prince-battle-lifetime-1102-v46.json',R/'docs/qa/allocations/prince-shared-successor-1102-v30.json']})
 (O/'current-manifest-v51.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['patches','bindings']}))


if __name__=='__main__':main()
