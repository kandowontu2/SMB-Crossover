"""Actual reclaimed BT loader plus palette-triggered forcedblank construction."""
from pathlib import Path
import itertools,json,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_current_loader_controls_v1 as T
import battletoads_native_adapter_controls_v1 as A
H=T.H;address=T.address
O=R/'build/battletoads-cold-acquire-v4';J=O/'joint'

def main():
    out=O/'loader-controls.json';assert not out.exists();q=dict(passed=False,native=False,cold=[],acquire=[])
    try:
        b=H.C.qualified(J/'candidate.nes');cache=(J/'bt/cache.bin').read_bytes();cookie=(J/'bt/cookie.bin').read_bytes()
        expected=bytearray(cache);expected[0x1fe0:0x1ff0]=cookie
        for wide,reload,ctrl in itertools.product([0,1],[0,1],[128,160,164]):
            m=T.make(b,X5WideChrActive=wide,ReloadCHRBank=reload,Mirror_PPUCTRL=ctrl)
            H.invoke(m,'X5PublishChr');latches=m.chr_latches[:];before=[bytes(x)for x in m.ram[:3]]
            c,low=T.call(m,'BtLoad')
            assert c.p&1 and(c.a,c.x,c.y,c.sp)==(85,7,91,224)
            assert m.ram[3]==expected and[bytes(x)for x in m.ram[:3]]==before
            assert m.ppu_reads==16400 and m.ram_writes[0]==(3,0x1fe0,0)and m.ram_writes[-1]==(3,0x1fe0,167)
            assert m.chr_latches==latches and m.upper==0 and m.ppuctrl==ctrl and m.toggle==0
            assert m.protection==[2,1]and not any(a in[0x5102,0x5103,0x5113]for a,v in m.writes)
            reads=m.ppu_reads;writes=len(m.ram_writes);T.call(m,'BtLoad')
            assert reads==m.ppu_reads and writes==len(m.ram_writes)
            q['cold'].append(dict(wide=wide,reload=reload,CTRL=ctrl,CPU=c.processorCycles,minimum_SP=low))
        # Directly exercise all eight genuine destination addresses and all
        # input flags. The second LSR clears C because actual R1 mod4 is zero.
        mapcases=0
        for page,flags in itertools.product(range(8),range(64)):
            m=T.make(b);H.put(m,R1=192+4*page);T.call(m,'BtMapPage',p=T.flags(flags))
            assert m.chr_latches[11]==919+page and H.get(m,'R1')==192+4*page
            assert m.ppu_reads==1 and m.ppu_addr==0xc01;mapcases+=1
        rejects=[]
        for name,fields in [('foreign',dict(SelectedCharacter=0)),('FF',dict(SelectedCharacter=22)),
            ('Bowser',dict(SelectedCharacter=27)),('title',dict(OperMode=0)),('active',dict(DisableScreenFlag=0)),
            ('mask',dict(Mirror_PPUMASK=30)),('normalNMI',dict(NmiDisable=0)),('notbusy',dict(FamilyMainCommit=0))]:
            m=T.make(b,**fields);before=[bytes(x)for x in m.ram];c,_=T.call(m,'BtAcquire')
            assert not c.p&1 and[bytes(x)for x in m.ram]==before and m.ppu_reads==0;rejects.append(name)
        for variant,player in itertools.product(range(2),range(2)):
            m=T.make(b,FmGroups=variant<<5,CurrentPlayer=player,VRAM_Buffer1_Offset=0)
            foreign=[bytes(x)for x in m.ram[:3]]
            c,low=T.call(m,'BtColdColors',a=173,x=91,y=37,p=0xff)
            assert(c.a,c.x,c.y,c.p,c.sp)==(173,91,37,253,224)
            assert m.ppu_reads==16400 and[bytes(x)for x in m.ram[:3]]==foreign
            assert A.get(m,'BtHostReady')==1 and A.get(m,'BtSrc_Objects_Life',player)==47
            assert m.ram[3][0x1fe0:0x1ff0]==cookie
            assert m.ram_writes[0]==(3,0x1fe0,0)
            assert m.ram_writes[-1]==(3,address(b,'BtHostReady')&8191,1),'ready published last by constructor'
            # Warm area-palette publication must preserve earned health and
            # original script state, and must not run another integrator.
            A.put(m,'BtSrc_Objects_Life',19,player);A.put(m,'BtSrc_FrameCounter',73)
            before=bytes(m.ram[3]);reads=m.ppu_reads;H.put(m,VRAM_Buffer1_Offset=0)
            T.call(m,'BtColdColors');assert bytes(m.ram[3])==before and m.ppu_reads==reads
            H.put(m,DisableScreenFlag=0,Mirror_PPUMASK=30,NmiDisable=0,VRAM_Buffer1_Offset=0)
            T.call(m,'BtColdColors');assert bytes(m.ram[3])==before and m.ppu_reads==reads
            q['acquire'].append(dict(variant=variant,player=player,buffered_reads=reads,minimum_SP=low,
                genuine_palette_to_loader_to_source_constructor=True,warm_and_active_earned_health_clock_preserved=True))
        # The moved helpers had no external relocatable consumer in the exact
        # linked producer set. Record each actual object, not only source names.
        recipe=json.loads((O/'final-link.json').read_text())['command'];consumers={}
        for v in recipe:
            if v.endswith('.o')and not v.replace('\\','/').endswith('/bt/loader.o'):
                text=subprocess.run([str(R/'tools/Windows/cc65/bin/od65.exe'),'--dump-imports',v],capture_output=True,text=True,check=True).stdout
                assert not any(n in text for n in['BtRetire','BtMapPage','BtCookie','BtRestorePPU'])
                consumers[v]=T.sha(v)
        q.update(passed=True,cold_cases=len(q['cold']),map_allflags_true_destination_pairs=mapcases,
            acquisition_cases=len(q['acquire']),reject_contexts=rejects,actual_linked_moved_helper_import_closure=consumers,
            loader_bytes=487,preview_bytes=239,header_current64_readiness_menu_unchanged=True,
            scope='Own true ROM cold palette->verified8192-byte loader->cookie->source Ensure constructor. Actual menu/InitScreen/controller progression and selected33 retirement integration still pending.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):T.sha(p)for p in[Path(__file__),Path(T.__file__),Path(A.__file__),O/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'bt/loader.s',J/'bt/preview.s',J/'bt/api.s',J/'bt/cache.bin',J/'bt/cookie.bin']}
    out.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['cold','acquire','bindings','traceback','actual_linked_moved_helper_import_closure']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
