"""Bind historical dynamic callback registrations; never launch this observer."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 path=D/'cv3-remaining-resident-v4/timing-v2-preflight-v1/run.lua';s=path.read_text();a0=s.index(' if not strictDmaHooks[key]then');a1=s.index('local pendingReturns,installedReturns=',a0);b0=s.index('local function onReturn');b1=s.index("emu.addMemoryCallback(function()\n if not entered or done or not valid('AudioUpdate')",b0)
 assert'emu.addMemoryCallback'in s[a0:a1]and'emu.addMemoryCallback'in s[b0:b1];assert'emu.removeMemoryCallback'not in s
 findings=[dict(owner='DMA completion registration inside4014 callback',line=s[:a0].count('\n')+1,excerpt=s[a0:a1]),dict(owner='onReturn called inside source/audio/performance callbacks',line=s[:b0].count('\n')+1,excerpt=s[b0:b1])]
 result=dict(passed=True,launch_safe=False,startup_static=False,native_executed=False,historical_script=dict(path=str(path),sha256=sha(path)),findings=findings,bound_builders={str(f.relative_to(ROOT)):sha(f)for f in[ROOT/'tools/audit/cv3_remaining_sfx_native_v7.py',ROOT/'tools/audit/cv3_remaining_sfx_resident_native_v2.py']},required_successor='New startup-registered dispatcher, exact old/new synthetic return/DMA observation equivalence, frozen generated scripts/inputs and native same-input equivalence before budget qualification. Existing native negatives remain immutable; no retry or cadence claim.',tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='findings'},indent=2))
if __name__=='__main__':main()
