"""Current instruction-cut publication controls for the proposed DK pages."""
import contextlib,io,json
from pathlib import Path
from types import SimpleNamespace
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O


def main():
    evidence=json.loads((O/'carrier-proposal-v13.json').read_text());assert evidence['passed']and evidence['complete_current_publisher_closure']
    script=R/'tools/audit/check_prince_chr_publication_1102_v1.py';source=script.read_text()
    source=source.replace('import audit_prince_pool_1102_v1 as A','A=PROVIDED')
    source=source.replace('build/prince-actor-1101-v1','build/dkjr-native-source-1102-v2')
    source=source.replace(" env=dict(__file__=str(original)"," source=source.replace('publication-CPU-controls.json','publication-v14-CPU.json').replace('range(1,38)','range(1,41)')\n env=dict(__file__=str(original)")
    source=source.replace("O/'publication-CPU-controls.json'","O/'publication-v14-CPU.json'")
    adapter=SimpleNamespace(R=R,O=O,ROM=A.BASE,SHA=A.PIN,POOL=A.CODE+A.ART,sha=lambda p:A.sha(Path(p).read_bytes()))
    env=dict(__file__=str(script),__name__='dk_current_publication',PROVIDED=adapter)
    exec(compile(source,str(script),'exec'),env)
    with contextlib.redirect_stdout(io.StringIO()):env['main']()
    path=O/'publication-v14-CPU.json';q=json.loads(path.read_text());assert q['passed']and q['no_proposed_page_published']
    q['bindings'].update({p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),script,A.BASE,O/'carrier-proposal-v13.json']})
    q['scope']='Exact current16a9 typed setter/nativeMario menu clear/restore and real lagNMI/RTI instruction cuts for all11 DK-proposed pages. Raw40 is only a guard-input fixture; no newowner/header/menu admission. Audio child remains an explicit existing return port. Not Mesen/raster/native qualification or an allocation.'
    path.write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in ['passed','current_ROM_sha256','actual_typed_setter_instruction_cuts','actual_native_Mario_menu_clear_restore_cuts','real_NMI_returns','no_proposed_page_published','proposed_pages']}))


if __name__=='__main__':main()
