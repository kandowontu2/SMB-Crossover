"""Exact memory-only proposal over613b, preserving every Bubv9 event byte."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools/reference')]
import measure_prince_owner_routes_1102_v23 as A
import compile_prince_host_lifecycle_1102_v12 as L
from link_pit_rygar_sophia_audit_cpu import scoped_load
O=A.O;POOL=[341,343,345,347,349,351,353,355,357,359,361,365,369,373,377,381,383,385,387,389,391,393,544,545,605,607,609,611,613,615,617,619,621,623,625,627,690,691,692,693,695,795,291]
sha=lambda x:hashlib.sha256(x).hexdigest()


def bundle():
 current=scoped_load(A.BASE);assert sha(current['raw'])==A.PIN
 # The root native packet intentionally ships a compact71-symbol DBG.
 # Existing native addresses use the full1966 linked source symbol map; all
 # common symbols present in the compact current map must agree exactly.
 native=scoped_load(L.BASE)
 for name,sym in current['syms'].items():
  if name in native['syms']:assert int(sym['val'],0)==int(native['syms'][name]['val'],0),('Native symbol drift',name)
 base=dict(native,raw=current['raw']);raw=bytearray(base['raw']);patches=[]
 def patch(bank,pc,blob,role,source):
  at=16+bank*8192+(pc&8191);old=bytes(raw[at:at+len(blob)]);raw[at:at+len(blob)]=blob;patches.append(dict(physical_PRG=bank,CPU_half_open=[pc,pc+len(blob)],file_offset=at,bytes=len(blob),old_hex=old.hex(),new_hex=blob.hex(),old_SHA256=sha(old),new_SHA256=sha(blob),role=role,source=source))
 for bank,pc,name,role in [(65,0xa740,'public-selector-v24.bin','Shared bounded Sh/Ex/BB/Prince family/service selector'),(65,0xaaf7,'shared-frame-v22.bin','Source-factored common AXYP/Cmap/5SMC/result transport'),(65,0xab72,'owner-third-extra-v23.bin','Authenticated typed cold/Prince retirement/cookie in reclaimed98B tail'),(65,0xae00,'owner-third-v23.bin','Three-owner bounded selector and source-funded pointer tables; fixed531B'),(65,0xb013,'public-scene-v24.bin','Exact19B original scene span, bounded37..39 own branch'),(65,0xb031,'public-foreign-v24.bin','Foreign UI unchanged except source-relocated two operands'),(79,0xa707,'public-router-v24.bin','Source-granted native router47of48, legalraw38 routes Ex family'),(79,0xbfb0,'public-router-tail-v24.bin','Source-granted router tail29of29; other legal owners retained')]:patch(bank,pc,(O/name).read_bytes(),role,'build/prince-actor-1101-v1/'+name)
 descriptor=bytes([2,0,8,0xd0,617&255,617>>8,619&255,619>>8]);patch(123,0xbf93,descriptor,'Typed two-row bootstrap descriptor in granted Mac source-declared pad','common-cold-1102-v1.json, proposed third descriptor8of18 spare')
 payload=(O/'cold-pool-v25.bin').read_bytes();assert len(payload)<=len(POOL)*1024
 for i,page in enumerate(POOL):
  part=payload[1024*i:1024*(i+1)];at=1048592+1024*page;pre=bytes(raw[at:at+len(part)]);raw[at:at+len(part)]=part;patches.append(dict(physical_CHR=page,file_offset=at,bytes=len(part),old_hex=pre.hex(),new_hex=part.hex(),old_SHA256=sha(pre),new_SHA256=sha(part),role='Granted Prince carrier code/art scatter',source='build/prince-actor-1101-v1/cold-pool-v25.bin',source_offset=i*1024))
 # A private composition must retain all55 actual v9 changes, including
 # source original-pop vector, genuine callback and21B owner gate extent.
 v9=R/'docs/qa/checkpoints/2026-11-02/bubble-native-event-v9/proposal.json';event=json.loads(v9.read_text());event_spans=[]
 for p in event['patches']:
  at=p.get('offset',p.get('file_offset'));post=bytes.fromhex(p.get('new',p.get('new_hex','')));assert at is not None and post
  assert base['raw'][at:at+len(post)]==post and raw[at:at+len(post)]==post,('Bubv9 event changed',at);event_spans.append([at,len(post)])
 changes={i for i,(a,z)in enumerate(zip(base['raw'],raw))if a!=z};covered={i for p in patches for i in range(p['file_offset'],p['file_offset']+p['bytes'])};assert changes<=covered
 return base,dict(base,raw=bytes(raw)),patches,event_spans


def main():
 old,new,patches,event=bundle();root=O/'successor-proposal-v26.json';q=dict(status='PROPOSAL_ONLY_NOT_GRANTED',ROM_written=False,shared_sources_written=False,installed=False,base_ROM=A.BASE.relative_to(R).as_posix(),base_SHA256=A.PIN,expected_memory_only_successor_SHA256=sha(new['raw']),patches=patches,actual_changed_bytes=sum(a!=z for a,z in zip(old['raw'],new['raw'])),all_Bub_v9_event_spans_preserved=event,all_other_bytes_exact=True,menu_admission_changed=False,resident_funding=dict(source_frame_factor=141,third_owner_extra=92,public_selector_growth=21,remaining=28,PRG79_existing77B_used=76,scene_existing19B_used=19,common_descriptor8B_uses_existing18B_spare=True),private_fit=json.loads((O/'public-routes-measurement-v24.json').read_text()),qualification=dict(frame_CPU='shared-frame-CPU-v22.json',frame_readers='shared-frame-consumers-v22.json',negative_preserved='frame-negative-v22.json',source_stream_decoder='cold-successor-v25.json',required=['Full actual613b three-owner manager/foreign/header/ISR differential.','C09E service-tag original world SavedY direct/write-before-read/ISR lifetime proof.','Actual typed common-worker→Prince cold decode/auth publication/fresh+scene CPU.','Private fresh/reset public rows/code-state preservation CPU.','Production palette/native collision profile/health/hurt/combat and source-visible menu remain unbound; no admission.']),scope='Exact memory-only all-preimage successor proposal, preserving cumulative613b plus all55 v9 event changes. No ROM artifact, native run, installation, resource grant or shared source mutation.',bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in [Path(__file__),A.BASE,O/'owner-third-v23.bin',O/'owner-third-extra-v23.bin',O/'public-selector-v24.bin',O/'shared-frame-v22.bin',O/'public-scene-v24.bin',O/'public-foreign-v24.bin',O/'public-router-v24.bin',O/'public-router-tail-v24.bin',O/'cold-pool-v25.bin',O/'shared-frame-CPU-v22.json',O/'shared-frame-consumers-v22.json',O/'frame-negative-v22.json',O/'cold-successor-v25.json',R/'docs/qa/checkpoints/2026-11-02/bubble-native-event-v9/proposal.json']})
 root.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['patches','private_fit','bindings','qualification']}))


if __name__=='__main__':main()
