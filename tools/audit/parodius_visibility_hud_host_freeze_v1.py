"""Freeze the second native-host AV without changing any original run files."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--emulator',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 failed=a.parent/'hud-scroll-native-remaining-v1';leaf=failed/'twinbee-easy/baseline-early';raw=json.loads((leaf/'proof.json').read_text());assert raw['emulator_exit']==0xc0000005 and not raw['passed'];assert not(leaf/'native-result.json').exists()
 command="Get-WinEvent -FilterHashtable @{LogName='Application';Id=1000;StartTime=[datetime]'2026-10-25T20:32:00';EndTime=[datetime]'2026-10-25T20:36:00'} | Where-Object RecordId -EQ 122057 | ForEach-Object { @{TimeCreated=$_.TimeCreated.ToString('o');RecordId=$_.RecordId;Message=$_.Message;XML=$_.ToXml()} } | ConvertTo-Json -Depth 4"
 result=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,check=True);event=json.loads(result.stdout);assert '0x000000000012f820' in event['Message'] and '0xc0000005' in event['Message']
 (a.output/'windows-application-error.json').write_text(json.dumps(event,indent=2)+'\n',encoding='utf-8')
 manifest={str(f.resolve()):dict(sha256=sha(f),bytes=f.stat().st_size)for f in failed.rglob('*')if f.is_file()}
 for f in [a.emulator,a.emulator.with_name('MesenCore.dll'),Path(__file__)]:manifest[str(f.resolve())]=dict(sha256=sha(f),bytes=f.stat().st_size)
 snapshot=a.output/'failed-text-snapshots';snapshot.mkdir()
 for f in leaf.iterdir():
  if f.is_file()and f.suffix not in ['.nes','.dbg','.map','.lbl','.argb']:shutil.copy2(f,snapshot/f.name)
 first=a.parent/'hud-hard-crash-comparison-v2/proof.json';assert first.exists();manifest[str(first.resolve())]=dict(sha256=sha(first),bytes=first.stat().st_size)
 frames=sorted(int(f.stem.removeprefix('frame-'))for f in leaf.glob('frame-*.argb'));bus=[json.loads(s)for s in(leaf/'oam-bus.jsonl').read_text().splitlines()];scroll=[json.loads(s)for s in(leaf/'scroll-events.jsonl').read_text().splitlines()]
 (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
 q=dict(passed=False,classification='HOST_FAILURE_NOT_LUA_ASSERTION',native_completed=False,ROM_sha256=sha(leaf/'candidate.nes'),exception='0xC0000005',fault_RVA='0x12F820',windows_record=122057,application_version='2.2.1.0',DLL_version='0.0.0.0',frames_flushed=frames,last_complete_bus_record=bus[-1],last_complete_scroll_record=scroll[-1],first_AV_prefix_proof=str(first),first_AV_prefix_proof_sha256=sha(first),manifest_sha256=sha(a.output/'manifest.json'),manifest_bindings=len(manifest),remaining_profiles_not_launched=6,bookkeeping='Only first TwinbeeEasy remaining control launched. The original OctopusEasy df515 pilot passed separately. No relabeling, retry or ROM clearance.',limits='Crash can leave buffered CSV tails absent. Runtime callback-vector mutation is a strongly supported host cause, not a native game pass. No new emulation performed.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(manifest),frames=frames)))

if __name__=='__main__':main()
