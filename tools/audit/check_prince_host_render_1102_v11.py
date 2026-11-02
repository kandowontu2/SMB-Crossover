"""Compact-geometry successor of frozen actual renderer/IRQ qualification."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools/reference')]
import recover_prince_core_1101_v1 as B
O=B.O


def main():
 p=R/'tools/audit/check_prince_host_render_1102_v1.py';text=p.read_text()
 changes={"src=R/'tools/reference/prince_host_render_1102_v1.s'":"src=O/'host-render-compact-v11.s'","'host-render":"'host-render-v11","prince-pose-packets.bin":"prince-pose-packets-v11.bin","geometry={0x4bc,0x4c3,0x6f1,0x70f}":"geometry={0x88,0x4bc,0x4c3,0x6f1,0x70f}","g=pose['source_projection_geometry'];assert":"g=pose['source_projection_geometry'];assert m[0xc088]==g['native_06F1_minus_anchor_y'];assert"}
 for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
 text=text.replace('host-render-v11-compact-v11.s','host-render-compact-v11.s')
 env=dict(__file__=str(p),__name__='prince_compact_geometry_renderer');exec(compile(text,str(p),'exec'),env);env['main']()
 file=O/'host-render-v11-CPU.json';q=json.loads(file.read_text());q['successor_wrapper_SHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();q['compact_geometry_source_proof']='geometry-codec-v11.json';q['owned_cached_source_delta']=0xc088
 file.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
