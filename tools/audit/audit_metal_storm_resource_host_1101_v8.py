"""Pin compact current-bank ownership evidence; no baseline ROM/debug copy."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
OUT=ROOT/'build/metal-storm-resource-host-1101-v8'
HOST=ROOT/'build/karnov-host-resource-base-1101-v1'
PIN='1c073196b51b6aaaaac90d1bea925b68807fcaa3055665cf6dd0cc8f7858fe33'
V7=ROOT/'build/metal-storm-render-host-1101-v7'
HOLES=[('GATE',31,0x1f69,151),('ENTRY',78,0xb6d,147),('WORK',37,0x1f89,119),('CHECK',21,0x1f8a,118),('AUTH',25,0x1f9e,98),('ZERO',116,0xf87,121),('COPY',95,0x580,128),('MAP',34,0x1d9e,98),('FINISH',99,0x176e,146)]
ACTOR=[247,248,249,250,827,828,829,830];RENDER=[831,1023,494];BODY=list(range(495,500))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if '--append-direct0'in sys.argv:
        installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');raw=installed.read_bytes();assert hashlib.sha256(raw).hexdigest()==PIN
        path=OUT/'native-witness.json';w=json.loads(path.read_text());at=16+62*8192+0x9c0;data=raw[at:at+32]
        assert data.hex()=='08c984f00c29038d3051ad470128090060a9028d3051ad47011869a828090060'
        w['spans']=[s for s in w['spans']if s['name']!='NativeDirect0']+[dict(name='NativeDirect0',pc=0xa9c0,offset=at,size=32,hex=data.hex(),sha256=hashlib.sha256(data).hexdigest())]
        path.write_text(json.dumps(w,indent=2)+'\n');print(json.dumps(dict(passed=True,installed_exact_PIN=PIN,extra_witness_bytes=32,no_O_reads=True)));return
    if '--seal-captured'in sys.argv:
        path=OUT/'ownership.json';q=json.loads(path.read_text());q['historical_mutable_inputs']={p:h for p,h in q['bindings'].items()if Path(p).is_relative_to(HOST)}
        q['bindings']={p:h for p,h in q['bindings'].items()if not Path(p).is_relative_to(HOST)};q['bindings'][str(Path(__file__).resolve())]=sha(__file__)
        q['historical_mutable_inputs_scope']='Captured1c source configuration hashes, no claim they remain current after parent rebuild; all further work uses serialized exact ownership/witness only.'
        path.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,sealed_captured_only=True,no_O_reads=True)));return
    p=HOST/'candidate.nes';assert sha(p)==PIN;b=scoped_load(p);raw=b['raw'];OUT.mkdir(exist_ok=True)
    own=[]
    for g in b['segs'].values():
        if 'ooffs'in g and Path(g['oname'].strip('"')).resolve()==p.resolve():own.append((int(g['ooffs'],0),int(g['ooffs'],0)+int(g['size'],0),g))
    holes=[]
    for role,bank,start,size in HOLES:
        at=16+bank*8192+start;data=raw[at:at+size];inter=[g['name'].strip('"')for a,z,g in own if a<at+size and z>at]
        assert not inter and data==bytes([255])*size,(role,inter)
        holes.append(dict(role=role,bank=bank,A_PC=0xa000+start,physical_offset=start,bytes=size,file_interval=[at,at+size],preimage_sha256=hashlib.sha256(data).hexdigest(),linked_segment_intersections=inter,grant=False))
    pages=[]
    for page in ACTOR+RENDER+BODY:
        at=1048592+page*1024;data=raw[at:at+1024];owners=[g['name'].strip('"')for a,z,g in own if a<at+1024 and z>at]
        assert not any(data)and owners in[[],['CV3_CHR']],(page,owners)
        pages.append(dict(page=page,owners=owners,bytes=1024,zero=True,preimage_sha256=hashlib.sha256(data).hexdigest(),grant=False))
    domains={}
    for variant,count in[(1,41),(2,43),(3,34)]:
        for side in['R','L']:
            name=f'Cv3V{variant}Chr{side}';lo,hi=location(b,name+'Lo'),location(b,name+'Upper');low,upper=raw[lo:lo+count],raw[hi:hi+count]
            domains[name]=dict(count=count,choices=sorted(set(a+256*z for a,z in zip(low,upper))),low_hex=low.hex(),upper_hex=upper.hex())
    assert set(v for d in domains.values()for v in d['choices'])==set(range(460,494))
    cv_draw=(ROOT/'src/cv3_draw.s').read_text();assert 'adc #<516'in cv_draw and'adc #<517'in cv_draw and'lda Cv3Variant\n asl'in cv_draw
    # Original CV3 valid variants1..3 yield the actual paired518..523 weapons.
    worlds=(ROOT/'src/metasprite.s').read_text();assert 'PODOBOO_VRAM_OFFSET = SPRITE_BANK_4'in worlds and'BOWSER_VRAM_OFFSET = SPRITE_BANK_4'in worlds
    v7=json.loads((V7/'native-render-witness.json').read_text());names=list(v7['syms'])+'FamilyMainCommit DisableScreenFlag Mirror_PPUMASK Mirror_PPUCTRL NmiDisable HorizontalScroll VerticalScroll NextBank_SMC SafereturnA_SMC'.split()
    syms={n:{k:v for k,v in b['syms'][n].items()if k in['name','val','seg','addrsize','size','type']}for n in set(names)}
    # Reuse only the exact tiny witness if every current emitted byte is equal.
    for s in v7['spans']:assert raw[s['offset']:s['offset']+s['size']]==bytes.fromhex(s['hex']),s['name']
    segids={s['seg']for s in syms.values()if 'seg'in s}|{k for k,g in b['segs'].items()if g['name']=='"SMCCODE"'}
    segs={k:{n:v for n,v in b['segs'][k].items()if n in['id','name','start','size','addrsize','type','ooffs']}for k in segids}
    witness=dict(raw_length=len(raw),spans=v7['spans'],syms=syms,segs=segs,ROM_sha256=PIN,debug_sha256=sha(HOST/'candidate.dbg'))
    (OUT/'native-witness.json').write_text(json.dumps(witness,indent=2)+'\n')
    result=dict(passed=True,granted=False,native=False,installed=False,ROM_sha256=PIN,debug_sha256=sha(HOST/'candidate.dbg'),PRG_proposals=holes,CHR_proposals=pages,actor_pages=ACTOR,render_pages=RENDER,body_pages=BODY,shot_page=499,shot_pattern_bias=16,CV3_linked_body_domains=domains,CV3_weapon_pages=list(range(518,524)),CV3_zero_gap=[494,518],C2_state=[0xc000,0xc800],C2_host=[0xc800,0xc83d],C2_packet=[0xc880,0xc8a1],C2_renderer=[0xcd00,0xd632],paired_headers=[0xdfe0,0xdff0],world_sprite_windows_preserved=[1,2,3,4,7],selected_sprite_windows=[0,5,6],world_palette_conflict='Original shots require spritepalette1, also native Piranha/greenKoopa/1UP/flag/flowerstem. Exact original player and all native world palettes cannot be claimed with the present allocation. Do not publish original3F15 blindly as coexistence.',open_ownership_gates=['Whole-current compiled/indirect selector domains for low pages247..250 and reclaimed CV3 pages494..499; a zero preimage or CV3 table gap alone is not a grant.','Global other-owner mapping/retirement proof for conditional C2/C3; both full headers invalidate first and publish only after readback.','Root must partition existing physical memory owners for each FF hole without shifting any other emitted byte/publicPC; fragments do not reserve the holes.','Final current ROM/DBG/source/CHR consumer binding, actual Main ISR/SMC and native menu/gameplay qualification.'],excluded_PRG125='Fixed-E/DMC post-link mirror; never a free linker gap.',bindings={str(p.resolve()):sha(p)for p in[Path(__file__),V7/'source-stage.json',V7/'source-proof.zip',V7/'native-render-witness.json',ROOT/'src/cv3_art.inc',ROOT/'src/cv3_draw.s',ROOT/'src/cv3_render.s',ROOT/'src/metasprite.s',ROOT/'src/metasprite_engine.s',ROOT/'src/world_firebars.s',ROOT/'src/world_sprite_palette.s',HOST/'candidate.cfg']})
    (OUT/'ownership.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,ROM=PIN,PRG_holes=len(holes),PRG_bytes=sum(h['bytes']for h in holes),CHR_pages=len(pages),no_more_O_reads=True,granted=False)))
if __name__=='__main__':main()
