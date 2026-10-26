"""Lossless numeric-object-key reader and separate native event reaggregation. No eval/replay."""
from pathlib import Path
import argparse,hashlib,json
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def normalize(raw):
 out=bytearray();stack=[];edits=[];i=0
 while i<len(raw):
  c=raw[i]
  if c==34:
   start=i;i+=1
   while i<len(raw):
    if raw[i]==92:i+=2;continue
    if raw[i]==34:i+=1;break
    i+=1
   else:raise AssertionError('Unterminated raw string')
   out.extend(raw[start:i]);continue
  if stack and stack[-1][0]==123 and stack[-1][1]and(48<=c<=57 or c==45):
   start=i
   if c==45:i+=1
   while i<len(raw)and 48<=raw[i]<=57:i+=1
   token=raw[start:i];assert token not in[b'',b'-']
   j=i
   while j<len(raw)and raw[j]in b' \r\n\t':j+=1
   assert j<len(raw)and raw[j]==58,'Only integer object-key tokens may normalize'
   edits.append(dict(raw_start=start,raw_end=i,raw_token=token.decode('ascii'),normalized_start=len(out)))
   out.extend(b'"'+token+b'"');continue
  if c in[123,91]:stack.append([c,c==123])
  elif c in[125,93]:assert stack and stack[-1][0]==(123 if c==125 else 91);stack.pop()
  elif c==58:assert stack and stack[-1][0]==123;stack[-1][1]=False
  elif c==44:
   assert stack
   if stack[-1][0]==123:stack[-1][1]=True
  out.append(c);i+=1
 assert not stack
 restored=bytes(out)
 for q in reversed(edits):
  start=q['normalized_start'];size=len(q['raw_token']);assert restored[start:start+size+2]==b'"'+q['raw_token'].encode()+b'"';restored=restored[:start]+restored[start+1:start+size+1]+restored[start+size+2:]
 assert restored==raw,'Token repair must reverse byte-for-byte'
 parsed=json.loads(out);return bytes(out),edits,parsed

def models():
 rows=[]
 for name,raw,want in[('integer_object',b'{4:true}',{'4':True}),('array_numbers',b'[1,2,3]',[1,2,3]),('quoted_key',b'{"4":true}',{'4':True}),('nested_string',b'{4:{9:"{5:yes}, [8:word]"},"t":[8,2]}',{'4':{'9':'{5:yes}, [8:word]'},'t':[8,2]}),('negative_integer_key',b'{-1:3}',{'-1':3})]:
  result,edits,z=normalize(raw);assert z==want;rows.append(dict(name=name,passed=True,edits=len(edits)))
 for name,raw in[('fraction_key',b'{4.5:true}'),('nan_value',b'{"a":NaN}'),('broken_string',b'{4:"x}')]:
  try:
   if name=='nan_value':json.loads(normalize(raw)[0],parse_constant=lambda s:(_ for _ in()).throw(AssertionError(s)))
   else:normalize(raw)
  except Exception:rows.append(dict(name=name,rejected=True));continue
  raise AssertionError(('Unsupported output accepted',name))
 return rows

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--native',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);models_out=models()
 original=json.loads((a.native/'proof.json').read_text());assert original['passed']is False and original['runner_exit']==0 and original['dependencies_unchanged']and not(a.native/'first-failure.json').exists()
 errors=original['analysis']['errors'];assert len(errors)==1 and errors[0].startswith('native B-gallery: Expecting property name enclosed in double quotes:')
 raw=(a.native/'native-bass-gallery.json').read_bytes();normalized,edits,s=normalize(raw);json.loads(normalized,parse_constant=lambda s:(_ for _ in()).throw(AssertionError(s)));assert edits and s['passed']and s['acquisition']is False and len(s['cases'])==16
 (a.output/'native-summary-normalized.json').write_bytes(normalized);put(a.output/'reversible-token-edits.json',dict(original_sha256=sha(a.native/'native-bass-gallery.json'),original_bytes=len(raw),normalized_sha256=sha(a.output/'native-summary-normalized.json'),normalized_bytes=len(normalized),edits=edits,exact_reverse=True,all_values_order_and_noninserted_bytes_unchanged=True))
 events=[json.loads(x)for x in(a.native/'events.jsonl').read_text().splitlines()];cfg=json.loads((a.native/'config.json').read_text());source=(a.native/'run.lua').read_text();assert "current.poolChecked=false;current.emptyChecked=false"in source and "current.emptyChecked=true;capture(q.name..'-exhaust-refusal');change('setup-pool')"in source
 cases=[]
 for i,(q,c)in enumerate(zip(cfg['cases'],s['cases']),1):
  # Lua nil-valued table keys are absent; config JSON null becomes nil at load.
  assert c['q']=={k:v for k,v in q.items()if v is not None}and c['naturalCleanup']and c['poolPassed']and c['selectionCleanup']and c['hits']>0 and c['damageCalls']>0
  assert c['emptyChecked']is False,'Keep the actual per-component reset field, never backfill'
  captures=[x for x in events if x['kind']=='ppu-frame-captured'and x['data']['name']==q['name']+'-exhaust-refusal'];assert len(captures)==1
  transitions=[x for x in events if x['case']==i and x['kind']=='gallery-phase'];ordered=[x['phase']for x in transitions];assert ordered.index('empty')<ordered.index('setup-pool')<ordered.index('pool')<ordered.index('clear-after-pool')
  assert any(x['kind']=='ppu-frame-captured'and x['data']['name']==q['name']+'-selection-cleanup'for x in events)
  cases.append(dict(case=i,name=q['name'],native_raw_emptyChecked=False,reason='Per-component marker reset false at pool setup after successful empty guard/capture; this is not a cumulative-case flag.',actual_exhaust_refusal_capture=captures[0],actual_ordered_transitions=transitions,other_summary_flags_hits_damage_pass=True))
 cap=json.loads((a.native/'ppu-capture-native-result.json').read_text());assert cap['passed']and cap['original_done_seen']and cap['actual_mode_readback']==cfg['mode_value']
 put(a.output/'native-event-reaggregation.json',dict(passed=True,cases=cases,raw_summary_fields_not_rewritten=True,original_serializer_FALSE_preserved=True,scope='Actual exit0/summarypassed/all16native assertion branches and named event chronology; no new emulator run or source/PPU/outcome mutation.'))
 proof=dict(passed=True,interpretation_passed=True,native_execution_passed=True,original_collector_passed=False,original_collector_proof_sha256=sha(a.native/'proof.json'),ROM_sha256=original['ROM_sha256'],actual_numeric_mode=cfg['mode_value'],original_raw_summary_sha256=sha(a.native/'native-bass-gallery.json'),normalized_summary_sha256=sha(a.output/'native-summary-normalized.json'),token_edits_sha256=sha(a.output/'reversible-token-edits.json'),numeric_key_tokens_quoted=len(edits),lossless_reversal_passed=True,event_reaggregation_sha256=sha(a.output/'native-event-reaggregation.json'),models=models_out,source_sha256=sha(a.native/'run.lua'),native_worker_released=True,limits=['Original collectorFALSE remains immutable; formatting and cumulative-marker assumption are separately interpreted.','No field is silently changed to true; actual per-component emptyChecked false preserved in normalized summary.','Independent rawDMA/fullPPU/glyph/selectedimage analysis still required. No native retry/Hard/adoption.'])
 put(a.output/'proof.json',proof);print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),proof=proof),indent=2))
if __name__=='__main__':main()
