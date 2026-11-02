"""Link measured source/native leaves privately and price exact cold storage."""
from pathlib import Path
import hashlib,json
import recover_prince_core_1101_v1 as B
R,O=B.R,B.O


def main():
 receipts={n:json.loads((O/n).read_text())for n in ['contact-CPU.json','contact-sequence-CPU.json','contact-point-CPU.json','host-render-CPU.json']}
 assert all(q['passed']for q in receipts.values())
 lab=B.P.T.labels(O/'contact-core.lbl');core=bytearray((O/'contact-core.bin').read_bytes())
 point=(O/'contact-point.bin').read_bytes();draw=(O/'host-render.bin').read_bytes()
 pointproof=receipts['contact-point-CPU.json'];drawproof=receipts['host-render-CPU.json']
 lo,hi=pointproof['code_half_open'];assert lo==lab['PpCoreEnd']and hi<=lab['PpScripts']
 assert not any(core[lo-0xa000:hi-0xa000]);core[lo-0xa000:hi-0xa000]=point
 assert drawproof['code_half_open']==[0xa000+len(core),0xa000+len(core)+len(draw)]
 core.extend(draw);assert 0xa000+len(core)<=0xbfe0
 file=O/'host-private.bin';file.write_bytes(core)
 spans=[dict(name='qualified_original_contact_core',half_open=[0xa000,lab['PpCoreEnd']],bytes=lab['PpCoreEnd']-0xa000),dict(name='qualified_native_point',half_open=[lo,hi],bytes=len(point)),dict(name='original_scripts_and_tables',half_open=[lab['PpScripts'],drawproof['code_half_open'][0]],bytes=drawproof['code_half_open'][0]-lab['PpScripts']),dict(name='qualified_native_render',half_open=drawproof['code_half_open'],bytes=len(draw))]
 layout=dict(passed=True,private_proposal_only=True,host_ROM_created=False,environment_callbacks_bound=False,source_image_bytes=len(core),image_half_open=[0xa000,0xa000+len(core)],source_declared_alignment_spare=[hi,lab['PpScripts']],source_alignment_spare_bytes=lab['PpScripts']-hi,tail_spare_bytes=0xbfe0-0xa000-len(core),total_remaining_live_code_bytes=lab['PpScripts']-hi+0xbfe0-0xa000-len(core),regions=spans,SHA256=hashlib.sha256(core).hexdigest(),source_state_native_packet_half_open=[0xc200,0xc235],scope='Original controls/animation/fullpostcontact/ledge/HP plus real native point and renderer leaves fit the same conditional bank. World material/coordinate bindings, update/camera/health/combat hooks and owner/IRQ admission remain incomplete. Environment vectors still identify explicit fixture services and are not callable on host.')
 (O/'host-private-layout.json').write_text(json.dumps(layout,indent=2)+'\n')
 p=R/'tools/audit/measure_prince_lossless_storage_1102_v1.py';s=p.read_text()
 changes={'prince-core.bin':'host-private.bin',"'lzss.":"'host-lzss.",'lossless-storage-cost.json':'host-lossless-storage-cost.json','(0xc800 if dest==0xa000 else 0x9000)':'(0xc500 if dest==0xa000 else 0x9000)'}
 for old,new in changes.items():assert old in s,old;s=s.replace(old,new)
 env=dict(__file__=str(p),__name__='prince_measured_host_storage');exec(compile(s,str(p),'exec'),env);env['main']()
 out=O/'host-lossless-storage-cost.json';q=json.loads(out.read_text())
 q['private_layout']=layout
 q['wrapper_SHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 q['cold_state_lifetime']='Decoder C000..C0B4 and compressed tail C200..C332 exist only before source initialization/authentication. Return from both decodes, then zero the full C000..C800 state before live init/header publication. Native packet C200..C235 is written only by later live drawing.'
 out.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(layout))


if __name__=='__main__':main()
