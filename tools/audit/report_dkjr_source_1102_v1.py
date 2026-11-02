"""Compact bound source report and one original-art preview; no host changes."""
from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools/reference')]
import dkjr_original_cpu_1102_v1 as D
import prepare_dkjr_component_1102_v1 as P
from PIL import Image,ImageDraw
O=P.O
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    cpu=json.loads((O/'CPU.json').read_text());layout=json.loads((O/'component-layout.json').read_text())
    assert cpu['passed'] and cpu['code_sha256']==layout['code_sha256']==sha(O/'component.bin')
    art=json.loads((O/'body-poses.json').read_text());chr_data=(O/'body.chr').read_bytes()
    assert len(chr_data)==1728 and layout['component_bytes']==len((O/'component.bin').read_bytes())
    colors={15:(0,0,0),48:(252,252,252),6:(108,6,0),54:(252,176,176),42:(76,208,32),22:(180,48,0),23:(228,92,16),55:(252,216,120)}
    image=Image.new('RGB',(528,240),(24,32,40));draw=ImageDraw.Draw(image)
    draw.text((8,4),'ORIGINAL DK JR / all body frames, paired 8x16',(240,240,240))
    for i,p in enumerate(art['poses']):
        col=i%6;row=i//6;x0=8+col*86;y0=24+row*50
        draw.text((x0,y0),f"{p['base']:02X} / {p['render_mode']}",(220,220,220))
        for cell in p['cells']:
            for yy in range(16):
                tile=cell['tile']+yy//8;at=tile*16+(yy&7)
                for xx in range(8):
                    sx=7-xx if cell['attr']&64 else xx
                    value=(chr_data[at]>>(7-sx)&1)|((chr_data[at+8]>>(7-sx)&1)<<1)
                    if value:
                        x=x0+(cell['x']+xx)*2;y=y0+14+yy*2
                        draw.rectangle((x,y,x+1,y+1),fill=colors[art['palette'][value]])
    image.save(O/'body-preview.png')
    source_files=[R/'tools/reference/dkjr_original_cpu_1102_v1.py',
                  R/'tools/audit/recover_dkjr_source_1102_v1.py',
                  R/'tools/audit/prepare_dkjr_component_1102_v1.py',
                  R/'tools/audit/check_dkjr_component_1102_v1.py',Path(__file__),
                  R/'docs/qa/dkjr-readiness-1102-v1.md']
    outputs=['component.s','component.cfg','component.bin','component.lbl','component-layout.json',
             'CPU.json','body.chr','body-poses.json','body-preview.png']
    q=dict(status='PRIVATE_ORIGINAL_SOURCE_COMPONENT_REVIEW_READY',donor=str(D.DONOR),donor_sha256=D.SHA,
           source_files={p.relative_to(R).as_posix():sha(p)for p in source_files},
           outputs={name:sha(O/name)for name in outputs},
           original_instruction_bytes=layout['original_instruction_bytes'],original_instructions=layout['original_instructions'],
           component_bytes=layout['component_bytes'],private_original_state_bytes=2048,body_CHR_bytes=1408,total_CHR_bytes=1728,
           body_8x16_sprites=4,fruit_8x16_sprites=2,hit_8x16_sprites=1,
           source_palettes=art['source_sprite_palettes'],CPU_cases=cpu['CPU_cases'],natural_NMI_frames=cpu['natural_NMI_frames'],
           body_pixel_comparisons=cpu['pixel_comparisons'],jump=cpu['jump'],vine=cpu['unblocked_vine_kinematics'],
           measurement_only_code_origin=0xa000,measurement_only_state_origin=0xc000,
           unbound_imports='Each import is a local self-JMP. Donor differential substitutes independent original services, never a host implementation.',
           host_resource_grant=False,host_glue_measured=False,menu_admission=False,native_run=False,installed=False,helpers_added=False,
           next_requirements=['Review source/import contracts and actual host resource allocation before integration.',
             'Implement native terrain/vine/fruit/enemy/lifecycle adapters and full owner authentication/retirement/CHR/menu ingress.',
             'Prove writable-code indirect operand safety at actual NMI/IRQ cuts and native service ABI.',
             'Native original controls, graphics, contacts and 1-1 traversal; 15px jump cannot independently clear native 32/48/64px pipes.'],
           commands=['python -B tools/audit/run_bounded_build_v1.py --resume --output build/dkjr-source-1102-v1 --timeout 180 -- python -B '+p.relative_to(R).as_posix()for p in source_files[2:]if p.suffix=='.py'])
    (O/'source-report.json').write_text(json.dumps(q,indent=2)+'\n')
    files=[p for p in O.rglob('*')if p.is_file()];size=sum(p.stat().st_size for p in files)
    assert size<32_000_000 and len(files)<=128,(size,len(files))
    print(json.dumps(dict(status=q['status'],component_bytes=q['component_bytes'],CHR_bytes=1728,CPU_cases=q['CPU_cases'],output_bytes=size,output_files=len(files))))
if __name__=='__main__':main()
