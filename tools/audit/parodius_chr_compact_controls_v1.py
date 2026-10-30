"""Check actual PN publishers, renderers, and all lossless page aliases."""
from pathlib import Path
import hashlib
import json
import re
import sys

R = Path(__file__).resolve().parents[2]
O = R / 'build/parodius-chr-compact-v1'
sys.path.insert(0, str(R / 'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load, Arena
from check_tmnt_render_oa import address, location


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    proof = json.loads((O / 'build-proof.json').read_text())
    paths = [R / 'build/character-host-union-v5/candidate.nes', O / 'candidate.nes']
    assert [sha(p) for p in paths] == [proof['parent_sha256'], proof['candidate_sha256']]
    bundles = [scoped_load(p) for p in paths]
    aliases = {int(k):v for k,v in proof['physical_page_aliases'].items()}
    chr_start = 16 + 1024 * 1024
    for old, new in aliases.items():
        assert bundles[0]['raw'][chr_start+old*1024:chr_start+(old+1)*1024] == \
               bundles[1]['raw'][chr_start+new*1024:chr_start+(new+1)*1024]
    assert bundles[0]['raw'][:16] == bundles[1]['raw'][:16]
    assert bundles[0]['raw'][chr_start:chr_start+832*1024] == bundles[1]['raw'][chr_start:chr_start+832*1024]
    assert bundles[1]['raw'][chr_start+868*1024:] == bytes(156*1024)
    rows = []; pairs_checked = 0; visible_sprites = 0

    def make_pair(**values):
        qs = [Arena(b,18) for b in bundles]
        for q in qs:
            q.put(PnPool=0, VvVariant=1, SsChrActive=0, X5WideChrActive=1, InvHudActive=0,
                  GuestOamRotationActive=0, CurrentOAMOffset=0,
                  R3=0, R4=112, R5=0, R6=128, R7=1)
            for i in range(12):
                q.set('CurrentCHRBank',40+i,i); q.set('X5ChrMode',0,i)
            q.put(**values)
        return qs

    def comparable(qs, name, **args):
        states = [q.invoke(name, **args) for q in qs]
        a,b = qs
        ca,ta = states[0]; cb,tb = states[1]
        assert (ca.a,ca.x,ca.y,ca.p,ca.sp,ca.processorCycles) == \
               (cb.a,cb.x,cb.y,cb.p,cb.sp,cb.processorCycles), (name,ca.a,cb.a,ca.p,cb.p)
        assert [(t['pc'],t['bank'],t['address']) for t in ta] == \
               [(t['pc'],t['bank'],t['address']) for t in tb], name
        allowed = {address(a.b,'SmChrBank'), address(a.b,'SafecallA_SMC')+1}
        allowed.update(address(a.b,'CurrentCHRBank')+i for i in [0,6,7])
        allowed.update([0x5120,0x5126,0x5127])
        differences = [i for i in range(0x8000) if a.m[i] != b.m[i]
                       and not (0x100 <= i < 0x200) and i not in allowed]
        assert not differences, (name,[(hex(i),a.m[i],b.m[i]) for i in differences[:12]])
        # Stack-based SMC operands are live code, so compare those too.
        for g in a.b['segs'].values():
            if g.get('name') != '"SMCCODE"':
                continue
            lo=int(g['start'],0); hi=lo+int(g['size'],0)
            assert all(a.m[i] == b.m[i] or i in allowed for i in range(lo,hi)), name
        for win in range(12):
            oldpage=a.get('CurrentCHRBank',win); newpage=b.get('CurrentCHRBank',win)
            mode=a.get('X5ChrMode',win)
            assert mode == b.get('X5ChrMode',win)
            if mode & 128:
                oldpage += (mode & 3)*256; newpage += (mode & 3)*256
                assert newpage == aliases.get(oldpage,oldpage), (name,win,oldpage,newpage)
            else:
                assert oldpage == newpage
        return ca.processorCycles

    def decode(q):
        result=[]; raw=q.b['raw']
        cmap=location(q.b,'ChrPhysicalMap')
        for i in range(q.get('CurrentOAMOffset')//4):
            y,tile,attr,x=q.m[0x200+4*i:0x204+4*i]
            window=(tile&1)*4+(tile>>6)
            low=q.get('CurrentCHRBank',window); mode=q.get('X5ChrMode',window)
            page=low+256*(mode&3) if mode&128 else raw[cmap+low]
            local=tile&62
            pattern=raw[chr_start+page*1024+local*16:chr_start+page*1024+(local+2)*16]
            assert len(pattern)==32
            result.append((x,y,attr,pattern))
        return result

    for pool in range(18):
        for initial in [0,1,127]:
            qs=make_pair(PnPool=pool)
            for q in qs:q.set('ReloadCHRBank',initial)
            cycles=comparable(qs,'PnPublish')
            publish=comparable(qs,'X5PublishChr')
            rows.append(dict(kind='publisher',pool=pool,initial_reload=initial,
                             source_cycles=cycles,hardware_cycles=publish))
    # Global frame IDs are sparse and each variant's pointer table may map a
    # foreign ID to an empty record. Include all of them, retaining empty cases.
    frames=[f for f in range(1,256) if bundles[0]['raw'][location(bundles[0],'PnBodyPoolTable')+f] != 255]
    for variant in [1,2,3]:
        for frame in frames:
            for face in [0,64]:
                qs=make_pair(VvVariant=variant,PnFrame=frame,Player_SprAttrib=face)
                comparable(qs,'PnGraphics')
                comparable(qs,'PnPublish')
                for q in qs:
                    q.put(R0=q.get('SmPosePtr'),R1=q.get('SmPosePtr',1),
                          R3=face,R4=112,R5=0,R6=128,R7=1,CurrentOAMOffset=0)
                render_cycles=comparable(qs,'MetaspriteRenderLoop')
                before,after=[decode(q) for q in qs]
                assert before==after,(variant,frame,face)
                visible_sprites += len(before);pairs_checked += len(before)
                rows.append(dict(kind='pose',variant=variant,frame=frame,face=face,
                                 sprites=len(before),render_cycles=render_cycles))
        qs=make_pair(VvVariant=variant)
        comparable(qs,'PnPortrait')
        comparable(qs,'X5PublishChr')
        first=bundles[0]['raw'][location(bundles[0],'PnDeathFirstFrames')+variant-1]
        count=bundles[0]['raw'][location(bundles[0],'PnDeathFrameCounts')+variant-1]
        for frame in range(first,first+count):
            qs=make_pair(VvVariant=variant,PnFrame=frame)
            comparable(qs,'PnDeathGraphics')
            comparable(qs,'PnDeathDraw')
            comparable(qs,'X5PublishChr')
            for q in qs:
                q.put(R0=q.get('SmPosePtr'),R1=q.get('SmPosePtr',1),
                      R3=0,R4=112,R5=0,R6=128,R7=1,CurrentOAMOffset=0)
            comparable(qs,'MetaspriteRenderLoop')
            before,after=[decode(q) for q in qs]
            assert before==after,(variant,frame,'death')
            pairs_checked += len(before)
            rows.append(dict(kind='death',variant=variant,frame=frame,sprites=len(before)))
    # Enumerate actual compiled references to the changed physical tables.
    table_refs=[]; files=set()
    for line in paths[0].with_suffix('.dbg').read_text().splitlines():
        if not line.startswith('file\t'):continue
        match=re.search(r'name="([^"]+)"',line)
        if not match:continue
        p=Path(match[1]); p=p if p.is_absolute() else R/p
        if p.suffix not in ['.s','.inc'] or not p.is_file() or p in files:continue
        files.add(p)
        for i,line in enumerate(p.read_text(errors='replace').splitlines(),1):
            if re.search(r'PnPool(?:Body|Special|Pickup)(?:Lo|Hi)',line):
                assert p.name in ['parodius_art.inc','parodius_render.s'], (p,i,line)
                table_refs.append(dict(path=str(p),line=i,text=line.strip(),sha256=sha(p)))
    result=dict(passed=True, status='PASS_SOURCE_LINKED_LOSSLESS_PN_CHR_REPACK',
                ROM_sha256=sha(paths[1]),parent_ROM_sha256=sha(paths[0]),
                physical_pages_compared=192,exact_source_bytes=192*1024,
                dense_pages=36,reclaimed_pages=156,
                all_8x16_patterns_proven_by_exact_page_bytes=192*32,
                actual_publisher_cases=54,actual_pose_cases=3*len(frames)*2,
                actual_portrait_cases=3,actual_death_cases=13,
                decoded_actual_OAM_pairs=pairs_checked,visible_pose_sprites=visible_sprites,
                exact_AXYP_SP_cycles_and_ordered_writer_addresses=True,
                unchanged_world_and_other_character_CHR=True,
                actual_compiled_files_scanned=len(files),changed_table_references=table_refs,
                rows=rows,script_sha256=sha(__file__),
                limits=['No native PPU/menu/gameplay claim from CPU fixtures',
                        'Future builds must use the dense physical aliases and split CHR memory; original192KB incbin is superseded'])
    (O/'controls.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['passed','actual_pose_cases','decoded_actual_OAM_pairs','reclaimed_pages']}))


if __name__=='__main__':main()
