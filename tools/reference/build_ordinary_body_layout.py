"""Generate viewport-safe low-pressure poses; retain original fallback assets.

The frozen plan was independently derived from immutable30 ROM composites.
Normal builds need no reference ROM, SciPy, external source or emulator.
"""
from pathlib import Path
import hashlib,json,re

ROOT=Path(__file__).resolve().parents[2]
def decode(b):return tuple(tuple(((b[(y//8)*16+y%8]>>(7-x))&1)+2*((b[(y//8)*16+y%8+8]>>(7-x))&1)for x in range(8))for y in range(16))
def flip(p,a):return tuple(tuple(reversed(r))if a&64 else r for r in(reversed(p)if a&128 else p))
def composite(parts,bank):
    out={}
    for p in reversed(parts):
        pic=flip(decode(bank[p['tile']//2*32:p['tile']//2*32+32]),p['a'])
        for y,row in enumerate(pic):
            for x,c in enumerate(row):
                if c:out.setdefault((p['x']+x,p['y']+y),(p['a']&3,c))
    return [[x,y,p,c]for(x,y),(p,c)in sorted(out.items())]
def mirrored(parts):return[dict(p,x=8-p['x'],a=p['a']^64)for p in parts]
def source_parts(path,name):
    code=path.read_text();s=re.search(r'^'+re.escape(name)+r':\n(.*?)(?=^[A-Za-z_.]|\Z)',code,re.M|re.S);assert s,name
    return[dict(tile=int(t,16),a=int(a,16),y=int(y),x=int(x))for t,a,y,x in re.findall(r'MetaspriteVramOffset\{\$([0-9a-f]+)\}, \{SPRITE_BANK_0\}, \$([0-9a-f]+), (-?\d+), (-?\d+)',s[1])]
def main():
    folder=ROOT/'chr/characters';original_path=folder/'ordinary-body-layout.json'
    growth_path=folder/'ordinary-body-growth-layout.json';plan_path=growth_path if growth_path.exists()else original_path
    plan=json.loads(plan_path.read_text())
    if growth_path.exists():
        original=json.loads(original_path.read_text());assert plan['growth_parent_plan_sha256']==hashlib.sha256(original_path.read_bytes()).hexdigest()
        assert plan['growth_owned_weapon_pairs']==[2,3,4,5]
        for before,after in zip(original['replacements'],plan['replacements']):
            before=dict(before);after=dict(after);a=bytes.fromhex(before.pop('baseline_bank_hex'));b=bytes.fromhex(after.pop('baseline_bank_hex'))
            assert before==after,'Growth successor retains all original body records and pixels'
            owned={2,3,4,5}if before['name']=='RgBILL0_WALK2'else set()
            assert all(a[i*32:(i+1)*32]==b[i*32:(i+1)*32]for i in range(32)if i not in owned),'Growth only allocates four proved weapon pairs' 
    expanded=bytearray((folder/'crossover-expanded.chr').read_bytes());low=bytearray((folder/'crossover-roster-low.chr').read_bytes())
    first=0xd1+len((folder/'crossover-roster-high.chr').read_bytes())//1024
    lines=['; Generated low-pressure poses; original records are retained for viewport fallback.'];report=[]
    for item in plan['replacements']:
        b=item['bank'];baseline=bytes.fromhex(item['baseline_bank_hex']);is_bass=b in(224,225)
        blob,off=(expanded,(b-first)*1024)if is_bass else(low,(b-0x1d)*1024)
        block=bytes(blob[off:off+1024]);assert len(block)==1024
        inc=ROOT/'src'/('bass_metasprites.inc'if is_bass else'bill_metasprites.inc')
        for side in('Left','Right'):
            source=source_parts(inc,item['name']+side)
            assert source==item['old_parts'][side],'Original fallback record must remain exact: '+item['name']+side
            assert composite(source,block)==item['baseline_pixels'][side],'Original fallback pixels remain exact'
        if b==224:
            assert block==baseline,'Common buster/normal Bass bank must remain byte-identical'
            cover=plan['walk1_cover'];pool=[block[:32]]+[bytes.fromhex(c['pattern'])for c in cover]
            private=b''.join(pool)+bytes(1024-len(pool)*32);assert private[:32]==block[:32]
            (folder/'ordinary-bass-walk.chr').write_bytes(private)
            right=[dict(tile=(i+1)*2,a=c['pal']|c['flags'],x=c['x'],y=c['y'])for i,c in enumerate(cover)]
            target=private;label='OrdBassWalk1';segment='XG_BASS_GFX';logical=0x83
        else:
            owned=30 if b==225 else 31
            assert block[:owned*32]+block[(owned+1)*32:]==baseline[:owned*32]+baseline[(owned+1)*32:],'No unrelated pattern may change'
            target=bytearray(block);patch=bytes.fromhex(item['pair_edits'][str(owned)])
            assert target[owned*32:(owned+1)*32]in(bytes(32),patch),'Only a proven spare pair may be allocated'
            target[owned*32:(owned+1)*32]=patch;blob[off:off+1024]=target
            right=item['new_parts']['Right'];label='OrdBassWalk3'if b==225 else'OrdBillWalk2';segment='XG_BASS_GFX'if is_bass else'BILL_GFX';logical=b
        parts={'Right':right,'Left':mirrored(right)}
        lines+=['.pushseg',f'.segment "{segment}"']
        for side in('Left','Right'):
            assert composite(parts[side],target)==item['baseline_pixels'][side],'Final palette symbols and opaque coordinates remain exact'
            lines +=[label+side+':',f'  .byte {len(parts[side])*4}']
            for p in parts[side]:lines.append(f"  .byte MetaspriteVramOffset{{${p['tile']:02x}}}, {{SPRITE_BANK_0}}, ${p['a']:02x}, {p['y']}, {p['x']}")
        lines+=['.popseg'];report.append(dict(name=label,logical_bank=logical,hardware_parts=len(right),chr_sha256=hashlib.sha256(target).hexdigest()))
    (folder/'crossover-expanded.chr').write_bytes(expanded);(folder/'crossover-roster-low.chr').write_bytes(low)
    (ROOT/'src/ordinary_body_layout_art.inc').write_text('\n'.join(lines)+'\n')
    out=ROOT/'build/ordinary-body-layout';out.mkdir(exist_ok=True)
    (out/'manifest.json').write_text(json.dumps(dict(plan_sha256=hashlib.sha256(plan_path.read_bytes()).hexdigest(),poses=report,original_records_unchanged=True,viewport_fallback=True),indent=2)+'\n')
    print('Low-pressure ordinary poses:',report)
if __name__=='__main__':main()
