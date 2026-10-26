"""Independent source/physical DMA and full HUD RGB checks for saved b0 menu."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from PIL import Image, ImageDraw

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=lambda p:[json.loads(l) for l in Path(p).open(encoding='utf-8')]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ['native','run','output']:ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    proof=json.loads((a.native/'proof.json').read_text(encoding='utf-8'))
    assert proof['passed'] and proof['ROM_sha256']=='b0c152fa0c588a7df28171e1c673a8db31e2769c5e9114768742e328f1134a99'
    bindings=json.loads((a.native/'manifest.json').read_text(encoding='utf-8'))
    assert sha(a.native/'manifest.json')==proof['manifest_sha256']
    for p,h in bindings.items():assert sha(p)==h,p
    comparisons=json.loads((a.native/'all1651-RGB-comparison.json').read_text(encoding='utf-8'))
    parent=Path(comparisons[0]['historical']).parent
    for n in ['inputs.csv','trace.csv','completed-loop-motion.csv']:
        assert (a.run/n).read_bytes()==(parent/n).read_bytes(),n
    def rgb(p):
        raw=np.frombuffer(Path(p).read_bytes(),dtype=np.uint8).reshape(240,256,4)
        return raw[:,:,[2,1,0]]
    raw=(a.run/'candidate.nes').read_bytes()
    oldraw=(parent/'candidate.nes').read_bytes()
    frames={z['finished']['frame']:z['start'] for z in rows(a.run/'hud-frames.jsonl')}
    oldframes={z['finished']['frame']:z['start'] for z in rows(parent/'hud-frames.jsonl')}
    shifts=np.arange(7,-1,-1)
    def indices(rom,s):
        bar=np.empty((8,224),dtype=np.uint8)
        for column,tile in enumerate(s['labels']):
            offset=1048592+s['chr'][8+tile//64]*1024+(tile%64)*16
            data=np.frombuffer(rom[offset:offset+16],dtype=np.uint8)
            px=((data[:8,None]>>shifts)&1)|(((data[8:,None]>>shifts)&1)<<1)
            palette=(s['attrs'][(column+2)//4]>>((column+2)&2))&3
            colors=np.asarray(s['palette'][palette*4:palette*4+4],dtype=np.uint8)&63
            bar[:,column*8:column*8+8]=np.where(px==0,s['palette'][0]&63,colors[px])
        return bar
    oldbar=rgb(parent/'frame-000548.argb')[8:16,16:240]
    ci=indices(oldraw,oldframes[548]);calibration={}
    for color in np.unique(ci):
        colors=np.unique(oldbar[ci==color],axis=0);assert len(colors)==1
        calibration[int(color)]=colors[0]
    checked=0
    for pair in rows(a.run/'hud-lease-frames.jsonl'):
        n=pair['ppu']['frame'];s=frames[n];assert pair['ppu']==s['ppu']
        ci=indices(raw,s);expected=np.empty((8,224,3),dtype=np.uint8)
        for color in np.unique(ci):expected[ci==color]=calibration[int(color)]
        actual=rgb(a.run/f'frame-{n:06d}.argb')[8:16,16:240]
        assert np.array_equal(actual,expected),n
        checked+=1792
    unique=set()
    for row in rows(a.run/'oam-bus.jsonl'):
        if row['kind']!='4014-complete-after-postDMA-LDA':continue
        assert row['completed_2004_writes']==256 and row['hardware']==row['source']
        assert len(row['source'])==256 and row['mask']&24==0
        assert row['dma_id'] not in unique;unique.add(row['dma_id'])
    assert len(unique)==1000 and checked==2254336
    differences=[]
    for row in comparisons:
        x,y=rgb(row['historical']),rgb(row['current']);mask=np.any(x!=y,axis=2)
        ys,xs=np.where(mask)
        if len(xs):differences.append(dict(frame=row['frame'],pixels=int(mask.sum()),bbox=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]))
    assert len(comparisons)==1651 and len(differences)==8
    sheet=Image.new('RGB',(1024,1040),'#202020');draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(differences):
        for k,(label,folder) in enumerate([('3cee',parent),('b0',a.run)]):
            col=i%4;line=(i//4)*2+k;pos=(col*256,line*260)
            draw.text(pos,f"{label} {row['frame']}",fill='white')
            sheet.paste(Image.fromarray(rgb(folder/f"frame-{row['frame']:06d}.argb")),(pos[0],pos[1]+20))
    sheet.save(a.output/'eight-changed-menu-frames.png')
    q=dict(passed=True,native_run=True,adopted=False,ROM_sha256=proof['ROM_sha256'],bindings_verified=len(bindings),
           all_inputs_trace_completed_motion_byte_exact=True,independent_full_HUD_RGB_pixels=checked,HUD_RGB_mismatches=0,
           independent_unique_full256_hardware_transfers=len(unique),actual_all_frame_pairs=1651,changed_frames=differences,
           independent_palette_calibration='Only immutable3cee frame548 plus its ROM/recorded palette; never new b0 output.',
           source_proof_sha256=sha(a.native/'proof.json'),tool_sha256=sha(__file__),
           limits='One actual Easy Octopus menu1800 control. Other3 HUD variants have source references, not all physical meter states. Visual sample review separate. Crowded bodies and campaign/Buffer2 overlap remain open.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(q,indent=2))

if __name__=='__main__':main()
