"""Link isolated selected WWF/native boundary imports from exact current a126."""
from pathlib import Path
import json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,address,location
import wwf_c2_relocation_model_v2 as M
T=M.T;L=R/'build/wwf-frame-recovery-v2';O=R/'build/wwf-native-proxy-lab-v1'
J=R/'build/contra-force-world-roles-1031-v2/joint'
CURRENT=R/'docs/qa/checkpoints/2026-10-31/contra-force-jump-contact-source-v1/handoff.json'
SOURCE=R/'tools/reference/wwf_native_proxy_lab_v1.s'

def main():
    assert not O.exists();O.mkdir();logs=[]
    try:
        q=json.loads(CURRENT.read_text());assert T.sha(CURRENT)=='072c8e8855ff60b0524d9f62a2e7e2e3e9c762660f3e9bff0c96031f8ba86359'
        assert T.sha(J/'candidate.nes')==q['candidate']
        for p,h in json.loads((L/'build-proof.json').read_text())['bindings'].items():assert T.sha(p)==h,p
        b=load(J/'candidate.nes');text=SOURCE.read_text();imports={}
        for line in text.splitlines():
            match=re.match(r'\.import(zp)?\s+(.+)',line)
            if match:
                for name in match[2].split(','):
                    if name=='WfState':continue
                    name=name.strip();assert name not in imports;imports[name]=bool(match[1])
        metadata={};aliases=['.setcpu "6502"\n']
        for name,zp in imports.items():
            value=address(b,name);s=b['syms'][name];data=dict(value=value,import_zeropage=zp,actual_addrsize=s.get('addrsize'))
            if 'seg'in s and 'ooffs'in b['segs'][s['seg']]:
                pos=location(b,name);data.update(physical_ROM_bank=(pos-16)//8192,ROM_offset=pos)
            metadata[name]=data
            aliases.append(f'.export{"zp"if zp else""} {name}\n{name}:=${value:04x}\n')
        for name in ['ShellOrBlockDefeat','ImposeGravitySprObj','BlockBufferAddr']:assert metadata[name]['physical_ROM_bank']==126,name
        for name in ['MTileAttribute','BoundBoxCtrlData']:assert metadata[name]['physical_ROM_bank']==127,name
        assert [metadata[f'R{i}']['value']for i in range(8)]==M.SCOPED
        (O/'native-imports.s').write_text(''.join(aliases));(O/'proxy.s').write_text(text)
        host=(L/'host.s').read_text().replace('.import WfFrameRecoveryCore,','.import WfProxyResetCore,WfFrameRecoveryCore,').replace(' jsr WfInitDescriptors\n',' jsr WfProxyResetCore\n jsr WfInitDescriptors\n')
        (O/'host.s').write_text(host)
        cfg=(L/'private.cfg').read_text().replace(L.as_posix(),O.as_posix())
        cfg=cfg.replace('MEMORY {','MEMORY { PROXYCTX:start=$c820,size=$40,type=rw,file="";')
        cfg=cfg.replace('SEGMENTS {','SEGMENTS { WF_PROXY_CONTEXT:load=PROXYCTX,type=bss;')
        cfg=cfg.replace('WF_FRAME_RECOVERY:load=C2,type=ro,start=$cc00;','WF_FRAME_RECOVERY:load=C2,type=ro,start=$cc00; WF_NATIVE_PROXY:load=C2,type=ro,start=$d000;')
        cfg=cfg.replace('WF_SELECTED_CONTACT:load=C2,type=ro,start=$dc00;','WF_SELECTED_CONTACT:load=C2,type=ro,start=$dc00; WF_NATIVE_PROXY_TAIL:load=C2,type=ro,start=$dd90;')
        (O/'private.cfg').write_text(cfg)
        def run(name,cmd):
            guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);p=O/(name+'.json');T.save(p,dict(command=cmd,output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));logs.append(p);assert z.returncode==0,(name,z.stderr)
        ca=R/'tools/Windows/cc65/bin/ca65.exe';ld=R/'tools/Windows/cc65/bin/ld65.exe'
        for name in ['proxy','native-imports','host']:run(name+'-build',[str(ca),'-g',str(O/(name+'.s')),'-o',str(O/(name+'.o')),'-l',str(O/(name+'.lst')),'--create-dep',str(O/(name+'.dep'))])
        objects=[M.L/(n+'.o')for n in ['vm','data','helpers','environment','irq']]+[R/'build/wwf-selected-contact-v2/aliases.o',L/'contact.o',L/'recovery.o']+[O/(n+'.o')for n in ['native-imports','proxy','host']]
        run('link',[str(ld),'-C',str(O/'private.cfg'),'-o',str(O/'lab.out'),'-Ln',str(O/'lab.lbl'),'-m',str(O/'lab.map'),'--dbgfile',str(O/'lab.dbg'),*map(str,objects)])
        labels={m[2]:int(m[1],16)for line in(O/'lab.lbl').read_text().splitlines()if(m:=re.match(r'al ([0-9A-Fa-f]+) \.(\S+)',line))}
        assert(O/'vm.bin').read_bytes()==(M.L/'vm.bin').read_bytes()
        footprint=dict(proxy_core=labels['WfNativeProxyCoreEnd']-0xd000,proxy_tail=labels['WfNativeProxyTailEnd']-0xdd90,selected_context=64,new_global_RAM=0,new_ZP=0)
        result=dict(source=True,isolated_lab=True,native_host=False,no_host_allocation=True,host_candidate=q['candidate'],labels=labels,host_imports=metadata,footprint=footprint,contracts=dict(public='Actual inputAXYP preserved except resultC, all8 scoped nativeR0..7 restored. Original callerP is edited only at liveSP+12 for resultC.',point='Native two-page block-buffer addressing, physical worldX/page and screenY/hi; nativeMTileAttribute mask SOLID|CLIMB equalsSOLID.',enemy='Snapshot current native tuple+selected epoch, original source victim-health/hurt transitions retained, same tuple+epoch required before actual fixed ShellOrBlockDefeat.',coordinates='Source2E/2F stays ring depth; sourceX rebased128 to export relative delta; source30 offsetdelta separate from native unsupported fall. Import current native clamps before the next source update.'),limits=['Private CPU lab only: code is not admitted to any shared cache/loader or physical hook.','Actual native CheckpointEnemyID/EraseEnemyObject notification coverage is required before WfProxyEpochs can protect real slot reuse; this packet provides the interface, not those hooks.','Ordinary enemies only; frenzybullet/Podoboo/powerup/Bowser are not admitted proxies.','Native16x32 player body is explicitWIP geometry, not a claim that every wrestler pose has that exact collision extent.','Export is followed by existing native terrain/platform resolution in the future host sequence. This lab does not silently install that Main hook.'])
        result['bindings']={str(p.resolve()):T.sha(p)for p in [Path(__file__),SOURCE,CURRENT,J/'candidate.nes',J/'candidate.dbg',L/'build-proof.json',*objects,O/'proxy.s',O/'native-imports.s',O/'host.s',O/'private.cfg',O/'vm.bin',O/'c2.bin',O/'lab.lbl',O/'lab.dbg',*logs]}
        T.save(O/'build-proof.json',result);print(json.dumps(dict(passed=True,footprint=footprint,proof=T.sha(O/'build-proof.json'))))
    except Exception as e:T.save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
