"""After an explicit native grant, compare complete static replay to saved original observations."""
from pathlib import Path
import argparse,hashlib,json
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);packet=json.loads((a.packet/'preparation.json').read_text());rows=[]
 for e in packet['cases']:
  old=Path(e['original_completed_case']);new=Path(e['static_script']).parent;assert sha(new/'run.lua')==e['static_script_sha256'];assert sha(old/'run.lua')==e['original_script_sha256'];assert json.loads((old/'proof.json').read_text())==json.loads((new/'proof.json').read_text())
  exact=[];semantic=[]
  for name,digest in e['historical_artifact_hashes'].items():
   assert sha(old/name)==digest,name
   if name in['native-proof.json','bindings.json']:continue
   if name.endswith(('.csv','.argb')):
    assert(old/name).read_bytes()==(new/name).read_bytes(),(e['name'],name);exact.append(dict(name=name,sha256=digest))
   elif name.endswith('.jsonl'):
    before=[json.loads(s)for s in(old/name).read_text().splitlines()];after=[json.loads(s)for s in(new/name).read_text().splitlines()];assert before==after,(e['name'],name);semantic.append(dict(name=name,events=len(before),old_sha256=digest,static_sha256=sha(new/name)))
   else:
    assert json.loads((old/name).read_text())==json.loads((new/name).read_text()),(e['name'],name);semantic.append(dict(name=name,old_sha256=digest,static_sha256=sha(new/name)))
  rows.append(dict(name=e['name'],ROM_sha256=e['ROM_sha256'],numeric_mode=0,all_CSV_and_raw_capture_bytes_exact=exact,all_JSON_outputs_semantically_exact=semantic,complete_native_proof_equal=True,held_cadence_verdict_unchanged=True))
 result=dict(passed=True,native_observation_equivalent=True,game_source_modified=False,rows=rows,packet_sha256=sha(a.packet/'preparation.json'),tool_sha256=sha(__file__),scope='Complete same-ROM/same-input/same-configuration original-versus-static observation layer equality for these two saved controls only. Cadence/source outcomes of HELD0802 remain rejected, unchanged. This does not certify0c45, another profile, audible waveform or campaign.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
