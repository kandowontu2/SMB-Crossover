"""Execute linked Doki drawing/menu code and all old/new Start boundaries."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_hogan_current_bounded_v1 as C
from check_tmnt_render_oa import Memory,address,location
from verify_native_relocation import NesMPU
O=R/'build/doki-current-component-1101-v1';A=R/'build/doki-original-art-1101-v1';P=R/'build/wwf-roster-native-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def call(m,name,*,a=0,x=0,y=0):
    c=NesMPU(memory=m,pc=address(m.bundle,name));c.a=a;c.x=x;c.y=y;c.p=0x31;c.sp=224;c.stPushWord(0x7ffe)
    for _ in range(30000):
        if c.pc==0x7fff:return c
        assert m[c.pc]!=0,(name,hex(c.pc));c.step()
    raise AssertionError(('Call bound',name,hex(c.pc)))


def memory(b):
    m=Memory(b);m.page(1,118);m.page(2,80);return m


def main():
    report=dict(passed=False,source_CPU=True,native=False,installed=False)
    try:
        stage=json.loads((O/'graphics-assembly.json').read_text());art=json.loads((A/'asset-controls.json').read_text())
        for p,h in stage['bindings'].items():assert sha(p)==h,p
        old=C.scoped_load(P/'candidate.nes');b=C.scoped_load(O/'candidate.nes');poses=0;usa=0;palettes=0
        for v,row in enumerate(art['profiles'],4):
            for case in row['poses']:
                m=memory(b)
                for n,value in dict(S2Variant=v,S2Face=case['facing'],S2Holding=case['holding'],S2Animation=case['action']).items():m[address(b,n)]=value
                call(m,'DdqBuildPose');ptr=m[address(b,'SmPosePtr')]+256*m[address(b,'SmPosePtr')+1]
                assert list(m[ptr:ptr+17])==case['packet'],('Compiled original Doki packet',v,case,list(m[ptr:ptr+17]))
                assert m[address(b,'SmChrBank')]==32+v
                call(m,'DdqStanding');assert list(m[ptr:ptr+17])==row['poses'][1]['packet']
                assert [m[address(b,n)]for n in ['S2Face','S2Holding','S2Animation']]==[case['facing'],case['holding'],case['action']]
                poses+=1
            m=memory(b)
            for n,value in dict(SelectedCharacter=25,S2Variant=v).items():m[address(b,n)]=value
            call(m,'S2PalettePointer');ptr=m[address(b,'R0')]+256*m[address(b,'R1')]
            assert list(m[ptr:ptr+4])==row['palette'];palettes+=1
        # Every old record remains byte exact; computed pointers preserve Y/R0..7.
        for record in range(73):
            m=memory(b)
            for i in range(8):m[address(b,'R0')+i]=37+i
            c=call(m,'S2SetRecord',a=record,y=91)
            ptr=m[address(b,'SmPosePtr')]+256*m[address(b,'SmPosePtr')+1]
            off=location(old,'S2Art'+str(record));size=old['raw'][off]+1
            assert bytes(m[ptr:ptr+size])==old['raw'][off:off+size],('Old art record',record)
            assert c.x==record and c.y==91 and list(m[address(b,'R0'):address(b,'R0')+8])==list(range(37,45))
        for native in range(4):
            for size in range(2):
                for action in [0,2,4,6,7,8,9,10]:
                    for holding in range(2):
                        for face in range(2):
                            out=[]
                            for bundle in [old,b]:
                                m=memory(bundle)
                                for n,value in dict(S2Variant=0,S2NativeCharacter=native,S2Size=size,S2Animation=action,S2Holding=holding,S2Face=face,Player_Rel_XPos=83).items():m[address(bundle,n)]=value
                                call(m,'S2Graphics::Pose');ptr=m[address(bundle,'SmPosePtr')]+256*m[address(bundle,'SmPosePtr')+1];out.append((list(m[ptr:ptr+m[ptr]+1]),m[address(bundle,'SmChrBank')]))
                            assert out[0]==out[1],('Old USA graphics',native,size,action,holding,face);usa+=1
        strings=['MARIO','LUIGI','TOAD','PEACH','IMAJIN','LINA','PAPA','MAMA']
        # Actual charmap A..Z is10..35. Match seven-character HUD/eight title cells.
        for v,name in enumerate(strings):
            for count in [7,8]:
                m=memory(b);m[address(b,'S2Variant')]=v;m[address(b,'R0')]=count
                call(m,'S2MenuCopyC',x=11);actual=list(m[address(b,'VRAM_Buffer1')+11:address(b,'VRAM_Buffer1')+11+count])
                assert actual==[ord(c)-55 for c in name]+[36]*(count-len(name)),('Names',v,actual)
        parent=C.collect(old);counts=[7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,8,1,2,1,6,2,4,2];rows={};starts=0
        for slot,count in enumerate(counts):
            m=C.fresh(b);C.put(m,CrossoverMenuIndex=slot);C.invoke(m,'MenuResolveCharacter');C.invoke(m,'QueueSelection')
            for v in range(count):
                if v:
                    C.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);C.invoke(m,'CrossoverMenuInput')
                actual=C.get(m,'MarioVariant')if slot==0 else v;pending=bool(C.invoke(m,'FmPending')['P']&1)
                rows[slot,actual]=dict(raw=C.get(m,'SelectedCharacter'),pending=pending)
                if slot==24:assert C.get(m,'S2Variant')==v and not pending,('Doki real menu',v,C.get(m,'S2Variant'),pending,C.get(m,'SelectedCharacter'))
                if(slot,actual)in parent:assert rows[slot,actual]==parent[slot,actual]
                for key in [16,128]:
                    for flags in [0x30,0x31,0x71,0xf1]:
                        n=C.fork(m);C.put(n,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0);C.invoke(n,'CrossoverMenuInput',p=flags)
                        assert(C.get(n,'CrossoverMenuState')==0)!=pending,(slot,v,key,flags)
                        if slot==24:assert C.get(n,'S2Variant')==v,('Start discarded Doki mode',v)
                        starts+=1
        assert len(rows)==90 and sum(not r['pending']for r in rows.values())==85
        report.update(passed=True,candidate=sha(O/'candidate.nes'),compiled_original_Doki_packets=poses,original_USA_pose_cases=usa,original_USA_records=73,original_Doki_palettes=palettes,HUD_title_names=16,menu_identities=90,playable=85,Start_A_cases=starts,scope='Actual assembled drawing packets against original FDS renderer; prior USA art bytes/pointer cases; linked names/palettes; all90 real menu identities and720 Start/A cases. No emulator/display/native/full-level qualification.')
    except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
    report['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(C.__file__),O/'graphics-assembly.json',A/'asset-controls.json',O/'candidate.nes',O/'candidate.dbg',P/'candidate.nes',P/'candidate.dbg']}
    (O/'graphics-controls.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k!='bindings'}));assert report['passed']


if __name__=='__main__':main()
