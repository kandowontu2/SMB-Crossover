"""Finish frozen successfulee campaigns after explicit adopted-source refresh.

The original v5 preparer/fixture/source proof and preparation negative remain
literal. No source campaigns/native are rerun; only current metadata is ready.
"""
from pathlib import Path
import inspect,json
import current_smb3_final_ee_prepare_v5 as frozen

def main():
 R=frozen.R;B=frozen.B;sha=frozen.sha
 source=B/'current_smb3_final_ee_v5_source.json'
 assert sha(source)=='5b21a30b42b9a15dd630a60b5fc3cd70f254a0245a298ddb8e2344cdf9dfdd60'
 proof=json.loads(source.read_text());assert proof['passed']and not proof['native_run']and proof['complete_GameLoop_calls']==13292
 assert all(sha(Path(p))==h for p,h in proof['bindings'].items())
 assert sha(frozen.ROM)==frozen.EXPECTED
 refresh=dict(path=str(R/'src/smb3_mario_dispatch.s'),historical_pre_adoption_sha256='a35ac65b478494961e68ae5305be5e082f7d4f4931a4ea4f15f820aad7c20c7f',actual_adopted_sha256='d3c4108f6531607fc99436807915b881032b0f0f141de388b514994bf092f546',scope='ROOT adopted exactly the source repair already present in b01/currentee ROM bank90. This is current source-context rebinding, not a guard exception or proof/native retag. Original v4 source context was5a and remains historical.')
 assert sha(Path(refresh['path']))==refresh['actual_adopted_sha256']
 fn=inspect.getsource(frozen.main);start=fn.index(' assert sha(ROM)==EXPECTED;');stop=fn.index(' outputs=[]')
 prefix=""" b=scoped_load(ROM);oldrom=B/'current_smb3_timer.nes';raw=ROM.read_bytes()
 proof=B/'current_smb3_final_ee_v5_source.json';campaigns=json.loads(proof.read_text())['campaigns']
 frame=address(b,'M3Native::PF_STATUE');assert frame==30
 oldfixture=R/'tests/current-smb3-powerups-v4.lua';fixture=R/'tests/current-smb3-powerups-v5.lua';altered=fixture.read_text()
"""
 fn=fn[:start]+prefix+fn[stop:]
 before="assert all(sha(Path(f['path']))==f['sha256']for f in oldready['bindings'])"
 after="assert all((f['sha256']==REFRESH['historical_pre_adoption_sha256'] and sha(Path(f['path']))==REFRESH['actual_adopted_sha256']) if Path(f['path'])==Path(REFRESH['path']) else sha(Path(f['path']))==f['sha256'] for f in oldready['bindings'])"
 assert fn.count(before)==1;fn=fn.replace(before,after)
 assert fn.count('paths|={Path(__file__),oldfixture,fixture,')==1
 fn=fn.replace('paths|={Path(__file__),oldfixture,fixture,','paths|={Path(FINISHER),B/\'current_smb3_final_ee_v5_preparation_negative.json\',Path(__file__),oldfixture,fixture,')
 assert fn.count('parent_readiness_sha256=sha(rp),change=')==1
 fn=fn.replace('parent_readiness_sha256=sha(rp),change=','parent_readiness_sha256=sha(rp),canonical_source_context_refresh=REFRESH,change=')
 assert fn.count('owned_files=[str(Path(__file__)),str(fixture)]')==1
 fn=fn.replace('owned_files=[str(Path(__file__)),str(fixture)]','owned_files=[str(Path(__file__)),str(Path(FINISHER)),str(fixture)]')
 env=dict(vars(frozen));env.update(REFRESH=refresh,FINISHER=str(Path(__file__).resolve()))
 exec(compile(fn,str(Path(__file__))+'::frozen_metadata_finish','exec'),env);env['main']()

if __name__=='__main__':main()
