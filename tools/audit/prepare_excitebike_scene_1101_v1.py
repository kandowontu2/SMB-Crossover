"""Fit the own/foreign cold scene in existing Ex grants; no new ROM written."""
from pathlib import Path
import json,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_excitebike_dispatch_1101_v1 import O,sha,labels,save
from prepare_excitebike_host_1101_v1 import BASE,PIN
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address

def main():
    b=scoped_load(BASE);assert sha(BASE)==PIN
    source=(O/'dispatch.s').read_text()+'\nExPriorScene=$ac1d\nExPriorMenuResolve=$ad88\n'
    source+=''.join(f'{n}=${address(b,n):04x}\n'for n in ['CrossoverMenuIndex','FmAlts'])
    source+='.include "excitebike_scene_1101_v1.inc"\n.include "excitebike_menu_1101_v1.inc"\n'
    (O/'scene.s').write_text(source)
    cfg=(O/'dispatch.cfg').read_text().replace('SEGMENTS{','MEMORY{G:start=$a7e9,size=$11,file="'+(O/'scene-gate.bin').as_posix()+'";S:start=$b062,size=$15,file="'+(O/'scene-own.bin').as_posix()+'";MG:start=$a7fa,size=6,file="'+(O/'menu-gate.bin').as_posix()+'";MB:start=$b077,size=21,file="'+(O/'menu-body.bin').as_posix()+'";MD:start=$b0fb,size=10,file="'+(O/'menu-done.bin').as_posix()+'";}SEGMENTS{')
    # Reuse already-qualified byte-identical loader/body/veneer outputs.
    cfg=cfg.replace('EX_VENEERS:load=V,type=ro;','EX_VENEERS:load=V,type=ro;EX_SCENE_GATE:load=G,type=ro;EX_SCENE_OWN:load=S,type=ro;EX_MENU_GATE:load=MG,type=ro;EX_MENU_BODY:load=MB,type=ro;EX_MENU_DONE:load=MD,type=ro;')
    (O/'scene.cfg').write_text(cfg);cc=R/'tools/Windows/cc65/bin'
    before={name:sha(O/name)for name in ['dispatch-loader.bin','dispatch-body.bin','dispatch-veneers.bin']}
    for cmd in [[cc/'ca65.exe','-I',R/'tools/reference','-I',O,'--bin-include-dir',O,O/'scene.s','-o',O/'scene.o'],
                [cc/'ld65.exe','-C',O/'scene.cfg',O/'scene.o','-o',O/'scene-unused.bin','-Ln',O/'scene.lbl']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    assert before=={name:sha(O/name)for name in before}
    gate=(O/'scene-gate.bin').read_bytes();own=(O/'scene-own.bin').read_bytes();lab=labels(O/'scene.lbl')
    assert len(gate)==17 and len(own)==21 and len((O/'dispatch-loader.bin').read_bytes())==556
    q=dict(passed=True,ROM_written=False,scene_gate_half_open=[0xa7e9,0xa7e9+len(gate)],
           own_scene_half_open=[0xb062,0xb062+len(own)],scene_bytes=len(gate)+len(own),
           menu_gate_half_open=[0xa7fa,0xa800],menu_body_half_open=[0xb077,0xb08c],menu_done_half_open=[0xb0fb,0xb100],
           reset_half_open=[0xb100,0xb105],private_menu_bytes=32,ROM_reset_bytes=5,
           existing_Ex_grant_only=True,Shinobi_bytes_modified=0,foreign_scene=0xac1d,
           loader_funding_bytes=96,loader_funding='Guards15B +sharedpublisher11B +contiguousselector17B +completeheaderpublishloop26B +same-latch/addressSTY4B +boundedORA1B +publishcounter1B +privateC-onlyheaderleaf21B. Upper reset/dummyread/Y0/allcopyverify retained; bank2headerbyte0 isfinalcommit.',
           native=False,installed=False,menu_unlock=False,
           scope='Assembled split coldscene/menu/reset, byte-identical existing transport. No InitScreen/sharedrouter hook or candidate ROM changed.',
           bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),R/'tools/reference/excitebike_scene_1101_v1.inc',R/'tools/reference/excitebike_menu_1101_v1.inc',O/'scene-gate.bin',O/'scene-own.bin',O/'menu-gate.bin',O/'menu-body.bin',O/'menu-done.bin',O/'scene.lbl',O/'dispatch-assembly.json']})
    save('scene-assembly.json',q);print(json.dumps(q))

if __name__=='__main__':main()
