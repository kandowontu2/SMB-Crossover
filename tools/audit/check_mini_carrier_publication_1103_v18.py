"""Replay existing typed setter/menu/lag publication protocol for962..968."""
from pathlib import Path
from types import SimpleNamespace
import contextlib,io,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import measure_mini_private_owner_1103_v15 as M
O=M.O


def main():
    audit=json.loads((O/'carrier-audit-v16.json').read_text());assert audit['passed']
    script=R/'tools/audit/check_prince_chr_publication_1102_v1.py';source=script.read_text()
    source=source.replace('import audit_prince_pool_1102_v1 as A','A=PROVIDED')
    source=source.replace('build/prince-actor-1101-v1','build/mini-mario-owner-1103-v15')
    source=source.replace(" env=dict(__file__=str(original)"," source=source.replace('publication-CPU-controls.json','publication-CPU-v18.json').replace('range(1,38)','range(1,42)')\n env=dict(__file__=str(original)")
    source=source.replace("O/'publication-CPU-controls.json'","O/'publication-CPU-v18.json'")
    adapter=SimpleNamespace(R=R,O=O,ROM=M.BASE,SHA=M.PIN,POOL=M.CODE+[M.META,M.ART],sha=lambda p:M.sha(Path(p).read_bytes()))
    env=dict(__file__=str(script),__name__='mini_existing_publication',PROVIDED=adapter)
    exec(compile(source,str(script),'exec'),env)
    with contextlib.redirect_stdout(io.StringIO()):env['main']()
    path=O/'publication-CPU-v18.json';q=json.loads(path.read_text());assert q['passed']and q['no_proposed_page_published']
    q['bindings'].update({p.relative_to(R).as_posix():M.sha(p.read_bytes())for p in [Path(__file__),script,M.BASE,O/'carrier-audit-v16.json']})
    q['scope']='Exact80d3 existing typed setter/nativeMario menu clear/restore and old-qualified real lagNMI/RTI instruction cuts for sevenMini-reserved pages. Guardinput41 is not Mini gameplay admission. Audio child remains explicitreturn port. No final Mini/NMI/clock qualification or Mesen/native claim.'
    path.write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in ['passed','current_ROM_sha256','actual_typed_setter_instruction_cuts','actual_native_Mario_menu_clear_restore_cuts','real_NMI_returns','no_proposed_page_published','proposed_pages']}))


if __name__=='__main__':main()
