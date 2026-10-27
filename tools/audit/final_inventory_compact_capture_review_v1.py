"""Bounded stdlib decoder/static checks; honestly report unavailable Lua tests."""
from pathlib import Path
import argparse,copy,csv,difflib,hashlib,json,random,struct,tempfile
from final_inventory_compact_capture_v1 import FRAME_BYTES,MAGIC,HEADER,MODULE,adapt_script,adapt_collector,collect_full_ppu,read_virtual,verify,word_fnv
from capture_budget import RUN_BYTES,RUN_FILES
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def bind(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))
def repeated(word,count):
 assert count>0;out=[]
 while count:
  n=min(count,128);out.append(bytes([127+n])+struct.pack('<I',word));count-=n
 return b''.join(out)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();a.output.mkdir(parents=True);codec=[];neg=[]
 # Entire synthetic model is temporary and <2MB; no real capture is moved,
 # restored, copied or exported. Only hashes/counts survive this test.
 with tempfile.TemporaryDirectory(prefix='compact-decoder-source-')as folder:
  out=Path(folder);container=out/'captures.nesppuv1';idx=out/'captures-index.jsonl';fullidx=out/'actual-ppu-index.csv';rows=[];raws=[];sequence=0;full=0;at=16
  solid=struct.pack('<I',0xff102030)*(FRAME_BYTES//4);noise=random.Random(731).randbytes(FRAME_BYTES)
  with container.open('wb')as f:
   f.write(MAGIC)
   def record(kind,raw,mode,payload,name):
    nonlocal sequence,full,at
    sequence+=1
    if kind==1:full+=1;raws.append(raw)
    stamp=dict(ppu_frame=full,scanline=240,dot=0,cpu_cycle=full*29780)
    meta=dict(name=name,stamp=stamp,decoded_bytes=len(raw),full_ordinal=full if kind==1 else 0);mb=json.dumps(meta).encode();check=word_fnv(raw);head=HEADER.pack(kind,mode,0,sequence,len(mb),len(payload),check);f.write(head+mb+payload)
    rows.append(dict(type='record',record=sequence,offset=at,bytes=len(head+mb+payload),kind=kind,mode=mode,name=name,decoded_bytes=len(raw),stamp=stamp,full_ordinal=meta['full_ordinal'],word_fnv1a32=check));at+=len(head+mb+payload)
   record(1,solid,1,repeated(0xff102030,FRAME_BYTES//4),'actual-ppu.argb')
   rows.append(dict(type='alias',name='case-one.argb',record=1,decoded_bytes=FRAME_BYTES,stamp=rows[-1]['stamp']))
   record(1,noise,0,noise,'actual-ppu.argb');record(1,noise,2,repeated(0,FRAME_BYTES//4),'actual-ppu.argb')
   for i in range(300):rows.append(dict(type='alias',name=f'gallery-{i:03d}.argb',record=3,decoded_bytes=FRAME_BYTES,stamp=rows[-1]['stamp']))
   blob=bytes(range(256))*4;record(3,blob,0,blob,'diagnostic-CHR-0242.bin')
  idx.write_text(''.join(json.dumps(q)+'\n'for q in rows));fullidx.write_text('ordinal,ppu_frame,scanline,dot,cpu_cycle,phase,updates,mode,tier\n'+''.join(f'{i},{i},240,0,{i*29780},synthetic,{i},1,1\n'for i in range(1,4)))
  result=verify(container,idx,fullidx);assert result['decoded_full_sha256']==hashlib.sha256(b''.join(raws)).hexdigest()and result['named_aliases']==301
  assert read_virtual(container,idx,'case-one.argb')==solid and read_virtual(container,idx,'gallery-299.argb')==noise and read_virtual(container,idx,'diagnostic-CHR-0242.bin')==blob
  (out/'ppu-capture-native-result.json').write_text(json.dumps(dict(passed=True,actual_mode_readback=1,original_done_seen=True,frames=3,bytes=3*FRAME_BYTES)))
  names=[q['name'][:-5]for q in rows if q['type']=='alias'];events=[dict(kind='ppu-frame-captured',data=dict(name=n))for n in names];(out/'events.jsonl').write_text(''.join(json.dumps(q)+'\n'for q in events));assert collect_full_ppu(out)['passed']
  codec=[dict(mode=0,raw_bytes=FRAME_BYTES,encoded_bytes=FRAME_BYTES),dict(mode=1,raw_bytes=FRAME_BYTES,encoded_bytes=len(repeated(0xff102030,FRAME_BYTES//4))),dict(mode=2,raw_bytes=FRAME_BYTES,encoded_bytes=len(repeated(0,FRAME_BYTES//4)))]
  original_bytes=container.read_bytes();original_index=idx.read_text()
  def reject(name,change):
   change()
   try:collect_full_ppu(out);ok=False
   except Exception:ok=True
   assert ok,name;neg.append(dict(name=name,rejected=True));container.write_bytes(original_bytes);idx.write_text(original_index);(out/'events.jsonl').write_text(''.join(json.dumps(q)+'\n'for q in events))
  reject('truncated-record',lambda:container.write_bytes(original_bytes[:-1]))
  reject('changed-pixel-bit',lambda:container.write_bytes(original_bytes[:-1]+bytes([original_bytes[-1]^1])))
  reject('wrong-record-sequence',lambda:container.write_bytes(original_bytes[:20]+struct.pack('<I',99)+original_bytes[24:]))
  reject('missing-physical-index',lambda:idx.write_text(''.join(json.dumps(q)+'\n'for q in rows if not(q['type']=='record'and q['record']==1))))
  bad=copy.deepcopy(rows);bad[1]['record']=999;reject('wrong-alias-target',lambda:idx.write_text(''.join(json.dumps(q)+'\n'for q in bad)))
  bad=copy.deepcopy(rows);bad[0]['stamp']['ppu_frame']=999;reject('wrong-source-stamp',lambda:idx.write_text(''.join(json.dumps(q)+'\n'for q in bad)))
  reject('missing-named-alias',lambda:idx.write_text(''.join(json.dumps(q)+'\n'for q in rows if q.get('name')!='gallery-299.argb')))
  reject('missing-native-capture-event',lambda:(out/'events.jsonl').write_text(''.join(json.dumps(q)+'\n'for q in events[:-1])))
  synthetic=dict(raw_decoded_bytes=result['decoded_full_bytes'],raw_SHA256=result['decoded_full_sha256'],container_bytes=result['container_bytes'],container_SHA256=result['container_sha256'],aliases=result['named_aliases'],record_modes=[q['mode']for q in rows if q['type']=='record'],temporary_files_only=True,retained_binary_files=0)
 original='FINAL_ITEM_PROGRESSIVE={}\n'+(R/'tools/audit/final_item_abilities_failure.lua').read_text()+'\n'+(R/'tools/audit/final_item_matrix_progressive.lua').read_text()+'\n'+(R/'tools/audit/final_item_abilities_pit731_ppu_v1.lua').read_text();after,insert=adapt_script(original);assert after.replace(insert,'',1)==original
 module=MODULE.read_text();assert all(n not in module for n in['emu.','addMemoryCallback','addEventCallback','setInput'])
 hostpath=R/'tools/audit/final_megaproto_common_proto_ce635_context_run_v1.py';host=hostpath.read_text();adapted,delta=adapt_collector(host);(a.output/'collector-only.patch').write_text(''.join(difflib.unified_diff(host.splitlines(True),adapted.splitlines(True),fromfile='qualified-Proto-context-runner',tofile='only-full-PPU-container-reader')))
 (a.output/'script-io-only.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),after.splitlines(True),fromfile='unchanged-source-fragments',tofile='I-O-only-prefix-adapter')))
 put(a.output/'owned-obsolete-inventory.json',dict(read_only=True,no_packing_or_deletion=True,no_root_zip_assumed=True,active_inputs_excluded=True,candidates=[dict(path=str(D/n),exists=(D/n).exists(),reason='Owned failed/superseded prototype only; if still present, ROOT must independently confirm inactive before any lossless packing.')for n in['currentce635-inventory-default-defer-candidate-v1','currentce635-inventory-default-defer-candidate-v2','currentce635-inventory-default-defer-candidate-v3','currentce635-inventory-default-defer-cpu-v1','currentce635-inventory-default-defer-cpu-v2','currentce635-inventory-default-defer-cpu-v3','currentce635-inventory-default-defer-cpu-v4','currentce635-inventory-default-defer-source-freeze-v1']],not_to_pack_as_obsolete=['ROOT current source/build/default','surviving handoff receipts','one chosen reusable portable Mesen/settings627 runtime','any active candidate or granted fixture'],missing_inputs_not_recreated=['b645 candidate/source-v4','old Proto context/diagnostic readies','pinned Lua54/lupa dependency']))
 report=R/'docs/qa/final-inventory-compact-capture-2026-10-26.txt';report.write_text('Compact native capture adapter, source only / Lua validation held\n\nNo emulator or game/runtime/source copies. No archive packing/deletion and no missing source restoration. b645 and old native readies disappeared independently; ROOT reports no real packing ZIP. The pinned Lua54/lupa path and local Lua executables are unavailable, so actual Lua codec/callback execution remains UNRUN, not passed. The optional controls tool is ready to run only when a sanctioned existing Lua dependency is available. No native grant follows from this packet.\n\nAdapter design: prepend one I/O-only shim, leaving every original callback, controller, mechanics, failure assertion and capture event body byte-exact. No emulated writes, inputs or callback registrations added. io.open for the single fullPPU .argb stream, named .argb and diagnosticCHR blobs is redirected into ONE NESPPU01 container plus one index. Normal logs/JSON/PPU index still use original io.open. ARGB is lossless pixel RLE or XOR-RLE with raw fallback, periodic keyframes and source-buffer word checksums. Equal named captures reference the current full frame only after exact raw-byte equality; different named/failure images retain their own pixels. Reused names keep all index events and latest-name lookup matches old overwrite semantics. Failure output is flushed before the unchanged assertion raises. No per-frame or named .argb files/CHR blobs or PNGs are created.\n\nStorage bounds: container <=1.5GB,25000 records, index <=50000 bounded4096B rows. Central capture_budget.py remains authoritative for total2GB/64files and global archive/free-space limits; native pipeline must keep it strict. Adapter creates zero screenshots; later review must select at most8 and cannot re-expand every frame. Current reader supports streaming integrity/virtual captures without any image export. Container compression cost is host work; no NES cadence/FPS assertion.\n\nExecuted stdlib source checks: three synthetic full frames, raw/RLE/XOR-RLE,301 aliases and oneCHR blob decode to exact original bytes/hash with all indices; eight truncation/pixel/sequence/index/alias/event negatives reject. Source body reverse-normalizes exactly; only fullPPU host file reading changes and all original frame/mode/count/order predicates remain, plus complete ordered named-capture/event closure. This proves the Python format/collector and static adapter boundary, NOT execution of the Lua encoder or current74 native callbacks. All original strict DMA/E3/deadline/bank/CHR/IRQ/stack/mechanics predicates remain outside the adapter unchanged.\n\nOnly the small checkpoint/text/source patch is retained; synthetic binary files are deleted with the owned temporary test directory. Existing obsolete owned prototype paths are listed read-only with current existence; none are packed or removed. No all-871 binding/candidate/native readiness claim while those inputs are missing.\n',encoding='utf-8')
 refs=[Path(__file__),MODULE,R/'tools/audit/final_inventory_compact_capture_v1.py',R/'tools/audit/final_inventory_compact_capture_controls_v1.py',R/'tools/audit/capture_budget.py',hostpath,R/'tools/audit/final_item_abilities_failure.lua',R/'tools/audit/final_item_matrix_progressive.lua',R/'tools/audit/final_item_abilities_pit731_ppu_v1.lua',report]+[q for q in a.output.iterdir()if q.is_file()]
 put(a.output/'manifest.json',dict(bindings=[bind(q)for q in refs]));put(a.output/'proof.json',dict(passed=False,source_review_complete=True,source_only=True,native_run=False,Python_decoder_and_collector_controls_passed=True,synthetic=synthetic,codec_cases=codec,negative_controls=neg,static_script_reverse_exact=True,static_collector_other_predicates_exact=True,Lua_encoder_and_74callback_execution='UNRUN: pinned Lua/lupa dependency and original prepared fixture are absent',no_inputs_restored=True,no_source_runtime_clones=True,one_lossless_container_planned=True,maximum_run_files=RUN_FILES,maximum_run_bytes=RUN_BYTES,maximum_screenshots=8,screenshots_created=0,manifest_sha256=sha(a.output/'manifest.json'),native_readiness=False,native_grant=False))
 print(json.dumps(dict(proof=str(a.output/'proof.json'),proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),Lua_status='UNRUN/missing dependency',native_run=False,retained_binary_files=0),indent=2))
if __name__=='__main__':main()
