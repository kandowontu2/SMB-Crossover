"""Retest relinked native-only leaves, without claiming a Main/owner exists."""
import json,types,zipfile
from pathlib import Path
import measure_dkjr_native_link_1102_v5 as P
import prepare_dkjr_native_world_1102_v3 as W
R=P.R;O=P.O


def main():
 checkpoint=R/'docs/qa/checkpoints/2026-11-02/dkjr-native-world-v3';manifest=json.loads((checkpoint/'manifest.json').read_text())
 path=R/'tools/audit/check_dkjr_native_world_1102_v3.py';assert W.P.sha(path.read_bytes())==manifest['files'][path.relative_to(R).as_posix()]['SHA256']
 src=path.read_text();src=src.replace('import prepare_dkjr_native_world_1102_v3 as P','')
 start=src.index(' # Reuse the frozen donor test');end=src.index(' lab={',start);src=src[:start]+src[end:]
 old="json.loads((O/'native-world-v3-source-CPU.json').read_text())['CPU_cases']";assert src.count(old)==1;src=src.replace(old,'0')
 for old,new in[('native-world-v3.lbl','native-link-v5.lbl'),('native-world-v3.bin','native-link-v5.bin'),('native-world-v3.s','native-link-v5.s'),('native-world-v3-layout.json','native-link-v5-layout.json'),('native-world-v3-CPU.json','native-link-v5-CPU.json')]:src=src.replace(old,new)
 proxy=types.SimpleNamespace(R=R,O=O,P=W.P,PIN=W.PIN,CURRENT=W.CURRENT,__file__=P.__file__)
 env={'__name__':'relinked_dkjr_world','__file__':__file__,'P':proxy};exec(compile(src,__file__,'exec'),env);env['main']()
 # Actual native primitive/carry/life tests have no original-level geometry
 # fallback in the native-only ABI. Keep source-world definition explicit.
 path=R/'tools/audit/check_dkjr_native_carry_1102_v4.py';src=path.read_text().replace('import prepare_dkjr_native_carry_1102_v4 as P','')
 src=src.replace("call(m,'DkjrUseOriginalGeometry')","call(m,'DkjrNativeWorldEnable')")
 start=src.index(' terminal_epochs=[]');end=src.index(' lost_lives=[]',start);src=src[:start]+src[end:]
 for old,new in[('native-carry-v4.bin','native-link-v5.bin'),('native-carry-v4.s','native-link-v5.s'),('native-carry-v4-layout.json','native-link-v5-layout.json'),('native-carry-v4-CPU.json','native-link-v5-carry-CPU.json')]:src=src.replace(old,new)
 src=src.replace('remaining_imports=10','remaining_imports=5')
 proxy=types.SimpleNamespace(R=R,O=O,P=W,__file__=P.__file__)
 env={'__name__':'relinked_dkjr_carry','__file__':__file__,'P':proxy};exec(compile(src,__file__,'exec'),env);env['main']()
 world=json.loads((O/'native-link-v5-CPU.json').read_text());carry=json.loads((O/'native-link-v5-carry-CPU.json').read_text());assert world['passed']and carry['passed']and world['component_SHA256']==carry['component_SHA256']
 result=dict(passed=True,native_Main_implemented=False,native_owner_admitted=False,ROM_written=False,component_SHA256=world['component_SHA256'],native_query_cases=world['native_query_cases'],control_cases=world['controller_original_and_native_cases'],local_source_service_cases=world['local_source_service_cases'],coordinate_cases=world['coordinate_cases'],native_primitive_checks=carry['checks'],remaining_actual_actor_imports=5,scope='Relinked native-only terrain/control/anchor/carry/landing/life leaves pass. Removed donor Frame/old level geometry/stage-enemy dispatcher are NOT claimed functional; the actual native Main/contact/fruit/phase/render/owner APIs are still required.',bindings={p.relative_to(R).as_posix():W.P.sha(p.read_bytes())for p in[Path(__file__),Path(P.__file__),path,O/'native-link-v5-CPU.json',O/'native-link-v5-carry-CPU.json',O/'native-link-v5-layout.json']})
 (O/'native-link-v5-proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,native_Main_implemented=False,native_query_cases=result['native_query_cases'],component_SHA256=result['component_SHA256'],remaining_actual_actor_imports=5)))


if __name__=='__main__':main()
