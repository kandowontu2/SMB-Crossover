"""Physical Parodius pickups and actual OAM/CHR pixels versus original art."""
from pathlib import Path
import argparse,hashlib,importlib.util,json

ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def pixels(folder,proof,variant):
    source=module('pickup_source_art',ROOT/'tools/reference/export_parodius_art.py')
    checker=module('pickup_composer',ROOT/'tools/audit/check_parodius_packed_art.py')
    raw,_=source.native.source_cpu();poses=source.records(raw,1);chr_data=raw[131088:]
    manifest=json.loads((ROOT/'reference/parodius-nes/art/packed/manifest.json').read_text())
    colors={0x30:0x30,0x28:0x27,0x06:0x16,0x15:0x16,0x08:0x17,0x21:0x21,
            0x03:0x03 if variant in(2,3)else 0x0f,0x38:0x30,0x17:0x17,0x0f:0x0f}
    for frame,p in proof['poses'].items():
        frame=int(frame);pool=manifest['pools'][p['pool']]
        assert p['bank7']==pool['pickup_chr'],'Actual sprite window7 must contain pickup art'
        info=pool['pickup_sources'][str(frame)];override=info['palette_override']
        # Both the native cartridge and SMB store OAM Y one row before its
        # visible scanline. Compare visible pixels, including that hardware+1.
        parts=[(p['x']+8+i['dx'],p['y']+9+i['dy'],i['tile'],
                i['attr']if override is None else(i['attr']&0xc0)|override)for i in poses[info['frame']]['parts']]
        expected=checker.compose(parts,lambda tile:source.pixels(chr_data,tile,[variant,4,11,5,0,0,0,0]),
                                 lambda pal,v:colors[source.PALETTES[pal][v]])
        key=folder/f'pose-{frame}';oam=key.with_name(key.name+'-oam.bin').read_bytes()
        chr=key.with_name(key.name+'-chr.bin').read_bytes();palette=key.with_name(key.name+'-palette.bin').read_bytes()
        actual_parts=[(oam[i+3],oam[i]+1,oam[i+1],oam[i+2])for i in range(0,256,4)
                      if oam[i]<240 and oam[i+1]&1 and oam[i+1]>=0xc1]
        assert max(sum(y<=line<y+16 for _,y,_,_ in actual_parts)for line in range(240))<=8,'Pickup alone exceeds the hardware scanline limit'
        if frame>=251:
            assert len(actual_parts)==len(poses[info['frame']]['parts']),'Native score digits must remain single sprites'
        actual=checker.compose(actual_parts,lambda tile:source.pixels(chr,tile,list(range(8))),
                               lambda pal,v:palette[16+pal*4+v]&63)
        assert actual==expected,(variant,frame,'Actual uploaded pickup sprites differ from source pixels',len(actual),len(expected))
    return len(proof['poses'])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--variants',nargs='+',type=int,default=[1,2,3]);a=p.parse_args()
    rom=a.rom.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    runner=module('pickup_mesen',ROOT/'tools/run_mesen.py');results={}
    prelude=(ROOT/'tests/parodius-integration.lua').read_text().split('local pulses=')[0]
    for variant in a.variants:
        folder=out/str(variant);folder.mkdir(exist_ok=True);script=folder/'pickups.lua'
        script.write_text(f'PN_VARIANT={variant}\n'+prelude+(ROOT/'tests/parodius-pickups.lua').read_text());runner.ROOT=folder
        code=runner.run(script,rom,timeout=60,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
        results[str(variant)]=dict(exit=code,script_sha256=hashlib.sha256(script.read_bytes()).hexdigest())
        if code:raise AssertionError((variant,'Physical pickup arena failed'))
        f=folder/'build/verification';proof=json.loads((f/'pickup-proof.json').read_text())
        results[str(variant)].update(rendered_source_pixel_cases=pixels(f,proof,variant),proof=proof)
        (out/'results.json').write_text(json.dumps(dict(ROM_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),results=results),indent=2)+'\n')
    print('PASS actual pickup sprites and native color/score states',list(results))

if __name__=='__main__':main()
