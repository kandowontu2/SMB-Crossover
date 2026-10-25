"""Read-only exact-color repacking trial bound to the current installed CHR."""
from pathlib import Path
import argparse,hashlib,json,sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/reference'))
from parodius_sprite_packing import layers_from_parts,compose_packed,peak
from roll_sprite_packing import pack_layers
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
    manifest=ROOT/'reference/parodius-nes/art/packed/manifest.json';q=json.loads(manifest.read_text());chrpath=ROOT/'chr/characters/parodius.chr'
    raw=chrpath.read_bytes();assert sha(chrpath)==q['CHR_sha256']
    rom=a.rom.read_bytes();prg=(rom[4]+((rom[9]&15)<<8))*16384
    assert rom[16+prg+q['first_chr']*1024:16+prg+q['first_chr']*1024+len(raw)]==raw
    cases=[]
    for pool in q['pools']:
        def pixels(tile):
            at=(pool['body_chr']-q['first_chr'])*1024
            at+=(3072 if tile&1 and tile>=0xc0 else 2048 if tile&1 else 0)+(tile&62)*16
            data=raw[at:at+32];assert len(data)==32
            return [[((data[y//8*16+y%8]>>(7-x))&1)|(((data[y//8*16+y%8+8]>>(7-x))&1)<<1)for x in range(8)]for y in range(16)]
        for frame in pool['body_frames']:
            old=pool['records'][str(frame)];layers=layers_from_parts(old,pixels)
            packed=pack_layers(layers);want={at:(pal,v)for pal,plane in layers.items()for at,v in plane.items()}
            assert compose_packed(packed)==want
            signed=lambda v:v if v<128 else v-256
            before=[(None,attr&3,signed(y),signed(x))for tile,attr,y,x in old]
            cases.append(dict(pool=pool['index'],variant=pool['variant'],phase=pool['phase'],frame=frame,pixels=len(want),
                              old_parts=len(old),new_parts=len(packed),old_peak=peak(before),new_peak=peak(packed)))
    result=dict(passed=True,game_changes=False,native_run=False,goal_complete=False,ROM_sha256=sha(a.rom),
                CHR_sha256=sha(chrpath),manifest_sha256=sha(manifest),tool_sha256=sha(Path(__file__)),cases=cases,
                parts_reduced=sum(r['new_parts']<r['old_parts']for r in cases),peak_reduced=sum(r['new_peak']<r['old_peak']for r in cases),
                scope='Reuses existing palette-plane optimizer on every current generated body pose. Exact visible palette/index composition preserved; CHR bytes equal installed ROM. No source/art mutation or native visibility/optimality claim.')
    (out/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items()if k!='cases'}))


if __name__=='__main__':main()
