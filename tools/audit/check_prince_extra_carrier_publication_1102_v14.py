"""Reexecute actual current publication/IRQ transitions for page291 only."""
from pathlib import Path
from types import SimpleNamespace
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools/reference')]
import compile_prince_host_lifecycle_1102_v12 as L
O=L.O


def main():
 p=R/'tools/audit/check_prince_chr_publication_1102_v1.py';text=p.read_text()
 text=text.replace('import audit_prince_pool_1102_v1 as A','A=PROVIDED')
 text=text.replace("env=dict(__file__=str(original)","source=source.replace('publication-CPU-controls.json','extra291-publication-v14.json')\n env=dict(__file__=str(original)")
 text=text.replace("(O/'publication-CPU-controls.json')","(O/'extra291-publication-v14.json')")
 text=text.replace('including all42 proposed pages','including the single proposed291 page')
 adapter=SimpleNamespace(R=R,O=O,ROM=L.BASE,SHA=L.PIN,POOL=[291],sha=lambda x:hashlib.sha256(Path(x).read_bytes()).hexdigest())
 env=dict(__file__=str(p),__name__='prince_extra291_publication',PROVIDED=adapter);exec(compile(text,str(p),'exec'),env);env['main']()
 file=O/'extra291-publication-v14.json';q=json.loads(file.read_text());q['extra_carrier_wrapper_SHA256']=adapter.sha(Path(__file__));q['source_consumer_proof']='extra-carrier-291-v14.json';file.write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps({k:v for k,v in q.items()if k in ['passed','current_ROM_sha256','proposed_pages','actual_typed_setter_instruction_cuts','actual_native_Mario_menu_clear_restore_cuts','real_NMI_returns','no_proposed_page_published']}))


if __name__=='__main__':main()
