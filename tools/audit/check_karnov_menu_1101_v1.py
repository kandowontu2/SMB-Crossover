"""Real menu Select/Start, ROM-only original portrait, names and palette."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_hogan_current_bounded_v1 as C
import ff_wram_host_controls_v7 as H
from check_tmnt_render_oa import address,location
from recover_karnov_art_1101_v1 import pixels
O=R/'build/karnov-host-resource-base-1101-v1';J=R/'build/doki-current-component-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
COUNTS=[7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,8,1,2,1,6,2,4,2]

def call(m,name,**kw):
    c=H.start(m,name,**kw)
    def watch(mem,c,i):
        assert not(0xa000<=c.pc<0xc000 and mem.rawtags[1]==3),('Cold menu executed RAM3',name,hex(c.pc))
    c,_=H.finish(m,c,watch);return c

def main():
    q=dict(passed=False,source_CPU=True,native=False,installed=False)
    paths=[Path(__file__),O/'terrain-assembly.json',O/'candidate.nes',O/'candidate.dbg',J/'candidate.nes',J/'candidate.dbg',R/'build/karnov-original-art-1101-v1/art-controls.json']
    try:
        stage=json.loads((O/'terrain-assembly.json').read_text());assert stage['passed']and stage['menu']
        for p,h in stage['bindings'].items():assert sha(p)==h,p
        old,new=[H.C.qualified(p/'candidate.nes')for p in [J,O]]
        old_count=new_count=identities=0
        def menu_state(m):
            at=address(m.bundle,'VRAM_Buffer1');n=H.get(m,'VRAM_Buffer1_Offset')
            return bytes(m[0x200:0x300]),H.get(m,'CurrentOAMOffset'),bytes(m[at:at+n+1]),bytes(m[address(m.bundle,'CurrentCHRBank'):address(m.bundle,'CurrentCHRBank')+12]),bytes(m[address(m.bundle,'X5ChrMode'):address(m.bundle,'X5ChrMode')+12]),H.get(m,'FmAlts'),H.get(m,'SelectedCharacter')
        for slot,total in enumerate(COUNTS):
            pair=[C.fresh(b)for b in [old,new]]
            for m in pair:H.put(m,CrossoverMenuIndex=slot);C.invoke(m,'MenuResolveCharacter');C.invoke(m,'QueueSelection');C.invoke(m,'DrawSelectionPreview')
            for variant in range(total):
                if variant:
                    for m in pair:
                        H.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
                        C.invoke(m,'CrossoverMenuInput');C.invoke(m,'DrawSelectionPreview')
                pending=[bool(C.invoke(m,'FmPending')['P']&1)for m in pair];identities+=1
                old_count+=not pending[0];new_count+=not pending[1]
                if (slot,variant)==(7,1):
                    assert pending==[True,False]and H.get(pair[1],'SelectedCharacter')==34
                else:
                    assert pending[0]==pending[1]and menu_state(pair[0])==menu_state(pair[1]),('Old menu identity changed',slot,variant)
        assert(identities,old_count,new_count)==(90,85,86)
        body=json.loads(paths[-1].read_text());pose=next(p for p in body['poses']if p['state']==0 and p['facing']==0 and p['hurt']==0 and p['phase']==0)
        expected=[]
        for i in range(1,len(pose['packet']),4):
            t,a,y,x=pose['packet'][i:i+4];expected.append(((160+32+y)&255,t,a,(120+8+x)&255))
        contexts=0;starts=0;digest=hashlib.sha256()
        for pattern,outlines in itertools.product([0,90,167],[0,1]):
            m=C.fresh(new);H.put(m,CrossoverMenuIndex=7,PlayerOutlinesOff=outlines)
            call(m,'MenuResolveCharacter');call(m,'QueueSelection');call(m,'DrawSelectionPreview')
            for bank in [2,3]:m.ram[bank][:]=bytes((i*19+bank*7+pattern)&255 for i in range(8192))
            before=[bytes(z)for z in m.ram];m.ram_writes.clear();m.writes.clear()
            H.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
            call(m,'CrossoverMenuInput');call(m,'DrawSelectionPreview');call(m,'X5PublishChr')
            assert H.get(m,'SelectedCharacter')==34 and H.get(m,'FmAlts')&1
            assert m.ppu_reads==0 and [bytes(z)for z in m.ram]==before and not m.ram_writes,'Cold menu read/wrote a conditional cache'
            n=H.get(m,'CurrentOAMOffset');actual=[tuple(m[0x200+i:0x204+i])for i in range(0,n,4)if m[0x200+i]<240]
            assert actual==expected,('Exact original idle portrait/OAM order',pattern,outlines,actual,expected)
            assert m.chr_latches[0]==408
            visible={}
            for y,t,a,x in actual:
                ppu=(t&1)*4096+(t&254)*16;page=m.chr_latches[ppu//1024];at=1048592+page*1024+(ppu&1023)
                for(dx,dy),v in pixels(new['raw'][at:at+32],a).items():visible.setdefault((x+dx,y+dy),v)
            source={}
            art=(R/'build/karnov-original-art-1101-v1/body.chr').read_bytes()
            for y,t,a,x in expected:
                at=pose['packed_page']*1024+t*16
                for(dx,dy),v in pixels(art[at:at+32],a).items():source.setdefault((x+dx,y+dy),v)
            assert visible==source and len(visible)==pose['pixels'];digest.update(bytes(v for z in actual for v in z))
            at=address(new,'VRAM_Buffer1');length=H.get(m,'VRAM_Buffer1_Offset');queue=list(m[at:at+length+1])
            name=[0x23,0x28,16,*[ord(c)-55 if c!=' 'else 36 for c in '     KARNOV     ']]
            assert any(queue[i:i+len(name)]==name for i in range(len(queue)-len(name)+1)),('Real selected name',queue)
            assert queue[:7]==[63,16,4,15,40,22,15],('Real cold palette',queue)
            for key,p in itertools.product([16,128],[0x30,0x31,0x71,0xf1]):
                z=C.fork(m);H.put(z,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
                c=call(z,'CrossoverMenuInput',p=p);assert H.get(z,'CrossoverMenuState')==0 and H.get(z,'SelectedCharacter')==34 and H.get(z,'FmAlts')&1
                assert z.ppu_reads==0 and all((bank,at,value)==(2,0x1fe0,0)for bank,at,value in z.ram_writes if bank in [2,3]),('Unexpected Start cache write',z.ppu_reads,z.ram_writes[:12])
                assert all(z.ram[i][j]==m.ram[i][j]for i in [2,3]for j in range(8192)if(i,j)!=(2,0x1fe0))
                starts+=1
            # Select back restores Rygar instead of retaining the Karnov ID.
            H.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
            call(m,'CrossoverMenuInput');call(m,'DrawSelectionPreview')
            assert H.get(m,'SelectedCharacter')==7 and not H.get(m,'FmAlts')&1
            contexts+=1
        for area in range(4):
            m=C.fresh(new);H.put(m,SelectedCharacter=34,FmAlts=1,AreaType=area)
            c=call(m,'HuWorldPalette');assert c.a==c.y==6*(area+1)
        q.update(passed=True,ROM_sha256=stage['ROM_sha256'],private_menu_enabled=True,native_admitted=False,identities=identities,existing_playable=85,private_selectable=86,legacy_menu_contexts_unchanged=89,original_idle_contexts=contexts,original_idle_pixels=pose['pixels'],cold_menu_cache_data_unchanged=True,Start_only_native_tag_invalidation=True,no_cold_RAM_opcode_execution=True,cache_PPU_reads=0,real_Select_Start_A_cases=starts,real_Select_return_to_Rygar=True,world_palette_cases=4,portrait_trace_sha256=digest.hexdigest(),scope='Actual emitted menu resolution, Select, palette/name queue, native portrait pipeline and Start/A handlers. Conditional caches contain foreign patterns, never preloaded code. Menu cache payloads stay unchanged; native fresh-Start may invalidate C2/DFE0 only. Original idle physical pixels/OAM order verified. No emulator/raster/playthrough/combat/item/audio or nightly-admission claim.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in paths}
    (O/'menu-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','traceback']}));assert q['passed'],q.get('error')

if __name__=='__main__':main()
