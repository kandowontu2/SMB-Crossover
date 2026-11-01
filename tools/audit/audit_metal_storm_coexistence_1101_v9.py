"""Exact native world art/palette constraints, frozen consumers, no O reads."""
from pathlib import Path
import ast,collections,hashlib,itertools,json,re,sys,zipfile
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
OUT=ROOT/'build/metal-storm-coexistence-1101-v9';V7=ROOT/'build/metal-storm-render-host-1101-v7';V8=ROOT/'build/metal-storm-resource-host-1101-v8'
OLD='1c073196b51b6aaaaac90d1bea925b68807fcaa3055665cf6dd0cc8f7858fe33';NEW='99bf88c8d971f1305f965a21833703c7a11aafa6a24febd9f3bfb7c87ba4bbda'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def value(expr,env):
    expr=re.sub(r'\$([0-9a-f]+)',r'0x\1',expr,flags=re.I)
    n=ast.parse(expr.strip(),mode='eval').body
    def val(n):
        if isinstance(n,ast.Constant):return n.value
        if isinstance(n,ast.Name):return env[n.id]
        if isinstance(n,ast.UnaryOp)and isinstance(n.op,ast.USub):return-val(n.operand)
        if isinstance(n,ast.BinOp):
            a,b=val(n.left),val(n.right)
            if isinstance(n.op,ast.Add):return a+b
            if isinstance(n.op,ast.Sub):return a-b
            if isinstance(n.op,ast.BitOr):return a|b
        raise AssertionError(ast.dump(n))
    return val(n)
def main():
    OUT.mkdir(exist_ok=True);closure=ROOT/'build/karnov-carrier-closure-1101-v4/closure.json';old=json.loads(closure.read_text());used={}
    def source(name):
        p,ref=next((p,r)for p,r in old['sources'].items()if Path(p).name==name);path=Path(p)
        if path.exists()and sha(path)==ref['sha256']:data=path.read_bytes();origin='hash-verified-live'
        else:
            with zipfile.ZipFile(ROOT/'build/_recovery/legacy-sources-2026-10-31.zip')as z:data=z.read('objects/'+ref['sha256'])
            origin='one-exact-indexed-object-in-memory'
        assert hashlib.sha256(data).hexdigest()==ref['sha256'];used[p]=dict(sha256=ref['sha256'],bytes=len(data),origin=origin);return data.decode()
    meta=source('metasprite.s');reset=source('reset.s');constants=source('constants.inc');sprite=source('sprite_render.s');mapper=source('mmc5.s');assert 'CHR_MISC = CHR_SMALLFIRE + $01'in constants
    caller_clauses={name:sprite.split('.proc '+name+'\n',1)[1].split('.endproc',1)[0]for name in ['DrawBlock','DrawPowerUp']}
    assert 'lda #3\n  sta Block_SprAttrib,x'in caller_clauses['DrawBlock']and'lda #1\n      sta Block_SprAttrib,x'in caller_clauses['DrawBlock']
    assert 'and #%00000011'in caller_clauses['DrawPowerUp']and'sta Enemy_SprAttrib,x'in caller_clauses['DrawPowerUp']
    installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');raw=installed.read_bytes();pin=hashlib.sha256(raw).hexdigest();assert pin in[OLD,NEW]
    init_clause=mapper.split('CHRBankInitValues:',1)[1].split('\n\n',2)
    assert '.byte CHR_SMALLMARIO, CHR_MISC, CHR_SPRITES, CHR_SPRITES+1'in mapper and'.byte CHR_SPRITES+2, CHR_SPRITES+3, CHR_SPRITES+4, CHR_SPRITES+5'in mapper
    native_chr_init=[18,20,21,22,23,24,25,26,4,5,6,7];native_chr_init_at=raw.find(bytes(native_chr_init),16,1048592);assert native_chr_init_at>=0
    successor_path=ROOT/'build/karnov-hud-native-1101-v9/hud-controls.json';succ=json.loads(successor_path.read_text());assert succ['passed']and succ['ROM_sha256']==NEW and succ['owners']['parent_ROM_sha256']==OLD and succ['owners']['unchanged_other_owners']
    w=json.loads((V8/'native-witness.json').read_text());physical=bytes.fromhex(next(s['hex']for s in w['spans']if s['name']=='ChrPhysicalMap'));assert max(physical)==246
    assert all(raw[s['offset']:s['offset']+s['size']]==bytes.fromhex(s['hex'])for s in w['spans'])
    palettes={};palette_packets=[]
    for area in['Water','Ground','Underground','Castle']:
        block=reset.split(area+'PaletteData:',1)[1].split('\n\n',1)[0];packet=bytes(int(v,16)for v in re.findall(r'\$([0-9a-f]{2})',block,re.I));assert len(packet)==36 and packet[:3]==bytes([63,0,32])
        at=raw.find(packet,16,1048592);assert at>=16,(area,'native palette bytes absent')
        palettes[area]=[list(packet[3+16+i*4:3+20+i*4])for i in range(4)];palette_packets.append(dict(area=area,file_offset=at,hex=packet.hex()))
    env={f'SPRITE_BANK_{i}':((i%4)*64+(1 if i>=4 else 0))for i in range(8)};env.update(SPR_FLIP_H=0x4000,SPR_FLIP_V=0x8000,SPR_PALETTE_0=0x2000,SPR_PALETTE_1=0x2100,SPR_PALETTE_2=0x2200,SPR_PALETTE_3=0x2300,BOWSER_TILE_SHIFT=0)
    records=[];branches=[];active=True;patterns={}
    text=meta[meta.index('POWERUP_VRAM_OFFSET'):meta.index('.if ::MOUSE_DISPLAY_CURSOR')]
    for line in text.splitlines():
        bare=line.split(';',1)[0].strip()
        if bare.startswith('.if '):branches.append(active);active=active and('MAPPER_MMC5'in bare);continue
        if bare=='.else':active=branches[-1]and not active;continue
        if bare=='.endif':active=branches.pop();continue
        if not active:continue
        m=re.fullmatch(r'(\w+)\s*=\s*(.+)',bare)
        if m:
            try:env[m[1]]=value(m[2],env)
            except(KeyError,SyntaxError,AssertionError):pass
            continue
        m=re.fullmatch(r'MetaspriteBox "(\w+)",\s*"(\w+)",\s*(.+)',bare)
        if not m:continue
        name,pose,args=m.groups();tiles=[value(v,env)for v in args.split(',')];assert 1<=len(tiles)<=4
        def field(suffix,default=0):return env.get(name+'_'+pose+'_'+suffix,env.get(name+'_'+suffix,default))
        bank=field('VRAM_OFFSET');pal=field('PALETTE');xx=field('X_OFFSET');yy=field('Y_OFFSET');packet=bytearray([len(tiles)*4]);cells=[]
        for i,t in enumerate(tiles):
            tile=(t&63)|bank;attr=pal|((t>>8)&255);y=(8+16*(i//2)+yy)&255;x=(xx+8*(i%2))&255;packet.extend([tile,attr,y,x]);slot=(tile&1)*4+((tile&254)*16)//1024;page=physical[20+slot-1]if slot else physical[18];at=1048592+page*1024+((tile&254)*16)%1024;pattern=raw[at:at+32];key=f'{page}:{(tile&254)*16%1024}'
            patterns[key]=pattern.hex();cells.append(dict(tile=tile,attributes=attr,dy=y,dx=x,physical_page=int(page),pattern_key=key,values=sorted({((pattern[(p//8)*16+(p%8)]>>(7-x))&1)+2*((pattern[(p//8)*16+(p%8)+8]>>(7-x))&1)for p in range(16)for x in range(8)}-{0})))
        # Exact actual right-facing descriptor, not a recreation-only fixture.
        at=raw.find(packet,16+4*8192,16+5*8192)
        assert at>=0,(name,pose,packet.hex())
        variants=[1,2]if name in['KOOPA','CHEEP_CHEEP']else range(4)if name=='POWERUP'and pose in['STAR','FIREFLOWER']else[3]if name=='MISC'and pose in['BRICK_GROUND','BRICK_OTHER']else[1,3]if name=='MISC'and pose=='BLOCK'else[0]
        for dynamic in variants:
            records.append(dict(name=name,pose=pose,native_R3=dynamic,descriptor_hex=packet.hex(),file_offset=at,cells=cells))
    # Current firebar producer uses private, immutable worldwindow1 records.
    for index,tile in enumerate([0x40,0x42]):
        packet=bytes([4,tile,2,252,0]);at=raw.find(packet,16,1048592);assert at>=0
        page=int(physical[20]);pos=1048592+page*1024+(tile&63)*16;pattern=raw[pos:pos+32];key=f'{page}:{(tile&63)*16}';patterns[key]=pattern.hex()
        records.append(dict(name='FIREBAR',pose=str(index),native_R3=0,descriptor_hex=packet.hex(),file_offset=at,cells=[dict(tile=tile,attributes=2,dy=252,dx=0,physical_page=page,pattern_key=key,values=sorted({((pattern[(p//8)*16+(p%8)]>>(7-x))&1)+2*((pattern[(p//8)*16+(p%8)+8]>>(7-x))&1)for p in range(16)for x in range(8)}-{0}))]))
    art=json.loads((V7/'art.json').read_text());body=(V7/'body.chr').read_bytes();shots=(V7/'shots.chr').read_bytes();metal=[]
    for kind,items,data in[('body',art['body_packets'],body),('shot',art['shot_packets'],shots)]:
        for r in items:
            if kind=='shot'and r['type']==131 and r['phase']>2:continue
            for cell in r['cells']:
                p=data[cell['pattern_index']*32:cell['pattern_index']*32+32];counts=collections.Counter(((p[(y//8)*16+y%8]>>(7-x))&1)+2*((p[(y//8)*16+y%8+8]>>(7-x))&1)for y in range(16)for x in range(8));pal=cell['attributes']&3
                metal.append(dict(kind=kind,pattern=cell['pattern_index'],palette=pal,opaque_indices=sorted(set(counts)-{0}),opaque_counts={str(v):n for v,n in counts.items()if v},colors=[art['source_sprite_palette'][pal*4+v]for v in sorted(set(counts)-{0})]))
    metal=list({(r['kind'],r['pattern'],r['palette']):r for r in metal}.values())
    rows=[]
    for area,pals in palettes.items():
        for r in records:
            if r['name']=='MISC':
                if r['pose']=='BLOCK'and r['native_R3']!=(3 if area=='Ground'else 1):continue
                if r['pose']=='BRICK_GROUND'and area!='Ground':continue
                if r['pose']=='BRICK_OTHER'and area=='Ground':continue
            colors=set();cellsets=[]
            for cell in r['cells']:
                attr=cell['attributes'];pal=(attr&3)if attr&32 else(attr|r['native_R3'])&3;values=cell['values'];c=[pals[pal][v]for v in values];colors.update(c);cellsets.append(dict(palette=pal,indices=values,colors=c))
            rows.append(dict(area=area,name=r['name'],pose=r['pose'],native_R3=r['native_R3'],used_colors=sorted(colors),cells=cellsets))
    result=dict(passed=True,native=False,installed=False,resource_granted=False,baseline_ROM_sha256=pin,successor_ROM_sha256=NEW,successor_owners=succ['owners'],native_CHR_init_logical=native_chr_init,native_CHR_init_packet_file_offset=native_chr_init_at,world_sprite_palettes=palettes,palette_packets=palette_packets,native_descriptors=records,native_patterns=patterns,native_used_colors=rows,Metal_used_patterns=metal,Metal_source_palette=art['source_sprite_palette'],legacy_publication_maximum=max(physical),proposed_renderer_pages=[831,500,494],old1023_rejected=True,global_CHR_consumer_closure=False,source_objects_read=used,native_palette_callers=caller_clauses,scope='Exact native ROM palette/CHR init/descriptors and original Metal colors, with source-backed block palette callers and real star/flower P0 phase. No whole baseline ROM/debug or graph restored; resource500 needs full consumer closure.',bindings={str(p.resolve()):sha(p)for p in[Path(__file__),closure,V8/'source-stage.json',V8/'native-witness.json',V7/'source-stage.json',V7/'art.json',V7/'body.chr',V7/'shots.chr',successor_path,ROOT/'tools/audit/check_karnov_hud_integrated_1101_v9.py']})
    (OUT/'palette-inputs.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,ROM=pin,world_descriptors=len(records),native_patterns=len(patterns),Metal_patterns=len(metal),world_color_contexts=len(rows),indexed_source_objects=len(used))))
if __name__=='__main__':main()
