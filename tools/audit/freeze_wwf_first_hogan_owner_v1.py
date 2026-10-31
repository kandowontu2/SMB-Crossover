"""Freeze granted first-Hogan physical ownership milestone, without admission."""
from pathlib import Path
import hashlib,json,re,zipfile
R=Path(__file__).resolve().parents[2]
from freeze_wwf_native_proxy_lab_v1 import local_imports
J=R/'build/wwf-first-hogan-host-v6/joint'
O=R/'build/wwf-first-hogan-owner-qualified-v1'
D=R/'docs/qa/checkpoints/2026-10-31/wwf-first-hogan-owner-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n')

def main():
 assert not O.exists()and not D.exists();O.mkdir();D.mkdir(parents=True)
 stage=J.parent/'source-stage.json';q=json.loads(stage.read_text());assert q['source'] and q['inert']
 tests=[R/'build'/n/'controls.json'for n in ['wwf-first-hogan-owner-controls-v1','wwf-first-hogan-owner-isr-v1']]
 reports=[json.loads(p.read_text())for p in tests];assert all(z['passed']for z in reports)
 external=set()
 for z in [q,*reports]:
  for p,h in z['bindings'].items():assert sha(p)==h,p;external.add(Path(p))
 # Full actual Main dependency source is externally pinned without duplicating
 # the existing74-character checkout/archive into this delta ZIP.
 line=(J/'host-main/main.dep').read_text().splitlines()[0].split('\t',1)[1]
 dependencies={Path(p.replace('\\ ',' ')).resolve()for p in re.split(r'(?<!\\)\s+',line.strip())}
 assert all(p.is_file()for p in dependencies)
 external|=dependencies
 oldmain=R/'build/bt-p2-cf-menu-source-1031-v2/joint/entrypoint.s'
 assert(J/'host-main/entrypoint.s').read_text()==oldmain.read_text()+'\n.export ImposeGravitySprObj,VerticalForce\n'
 p=R/'build/contra-force-world-roles-1031-v2/joint'
 oldpairs=set(re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(p/'candidate.lbl').read_text()))
 newpairs=set(re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(J/'candidate.lbl').read_text()));assert oldpairs<=newpairs
 # Exact linked placement and page occupancy, not pre-assembly estimates.
 segments=[]
 for line in(J/'candidate.dbg').read_text().splitlines():
  if not(line.startswith('seg\t')and 'name="WF_'in line):continue
  name=re.search(r'name="([^"]+)"',line)[1];start=int(re.search(r'start=(0x[0-9a-fA-F]+)',line)[1],16);size=int(re.search(r'size=(0x[0-9a-fA-F]+)',line)[1],16)
  segments.append(dict(name=name,start=start,end=start+size,bytes=size))
 c2names=['WF_STATE','WF_HOST_CONTEXT','WF_PROXY_CONTEXT','WF_DESCRIPTORS','WF_HOGAN_METADATA','WF_FRAME_RECOVERY','WF_HELPERS','WF_HOST_CODE','WF_SELECTED_CONTACT','WF_PROXY_RESET','WF_PRIVATE','WF_OWNER_STATE','WF_UNBOUND_CALLBACKS','WF_OWNER_COOKIE']
 c2=sum(s['bytes']for s in segments if s['name']in c2names);assert c2==7488
 resident=sum(s['bytes']for s in segments if s['name']in['WF_ROM_A','WF_RESIDENT_PROXY','WF_ROM_C']);assert resident==2646
 pages=[]
 for bank,n in [(1,'a1.bin'),(2,'c2.bin'),(3,'a3.bin')]:
  raw=(J/n).read_bytes();assert len(raw)==8192
  for i in range(8):
   block=raw[i*1024:(i+1)*1024];pages.append(dict(raw_bank=bank,page=i,classification='zero'if block==bytes(1024)else'FF'if block==bytes([255])*1024 else'nonuniform',sha256=hashlib.sha256(block).hexdigest()))
 save(O/'physical-fit.json',dict(source=True,segments=segments,C2_emitted=7488,C2_non_cookie_end=0xdd30,C2_cookie=[0xdfe0,0xdff0],A3_VM=7726,A3_marker=16,resident_emitted=2646,resident_granted=5834,template_pages=pages,A1='Explicit inactive zero bank; music is not implemented or executable.'))
 api=dict(source=True,inert=True,no_host_hooks=True,installed=False,readiness_unchanged=True,candidate=q['candidate'],parent=q['parent'],resource_contract=q['resource_contract'],entries={n:q['labels'][n]for n in ['WfLoad','WfCheck','WfRetire','WfConstructCold','WfRuntimeUnavailable','WfHostPoint','WfProxySnapshot','WfProxyCollect','WfProxyCommit','WfProxyNoteReuse','WfHostImport','WfHostExport']},cookie=q['cookie'],resource_use=dict(C2=7488,A3=7742,resident=2646,body_pages=[546,563],template_pages=[629,653],metadata_pages=[653,655]),
  owner='Selected29, FmGroups low3=0 (original Hogan), OperMode1 and FamilyMainCommit odd. Full16-byte C2 cookie checked in ROM before any cache opcode.',
  loader='Additionally requires forcedblank Mirror_PPUMASK&18=0, DisableScreenFlag!=0, NmiDisable negative and unpaused. Actual caller must first retire previous owner under current5FFF protocol. Stable C96 establishes genuine X5PublishChr checkpoint, clears C2 then RAM3 validity, copies/readbacks all24KiB, publishes raw3 marker then complete C2 cookie VALID last.',
  constructor='WfConstructCold repeats full ROM auth/blank guard, invokes genuine cached cold once through real SFC/raw3 with native source actor0ID5/actor1ID0/seed0, then own Ready last. Warm repeated same-epoch calls preserve allC2 state. This is not a natural scene/life policy or installed callback.',
  retirement='Independent of Selected/class: full AXYP preserved; clears C2 then raw3 validity only for family29, even malformed/stale own cookie. Every physical future foreign publication/overwrite needs this function before the write. No actual menu/scene hooks installed.',
  ABI='AXYP preserved except resultC for owner/guard/proxy APIs; Retire preserves C too. All8 scoped R0..7 and actual33 transport bytes restored. A/C shadows+maps, ReloadCHRBank and live upper stack restored. Real SFC retains native entryNZ-from-savedA contract.',
  epoch='Native enemy constructor/erase/reuse must Notify before publishing replacement identity; no hooks installed.',
  runtime='WfRuntimeUnavailable declines. RingClamp/RingBounds/AI/audio callbacks are explicit BRK traps in the inert cache, not executable donor-oracle aliases or replacement gameplay. They must be implemented before any source frame route is offered.',
  limits=q['limits'])
 save(O/'integration-api.json',api)
 readme='''First-Hogan physical owner source milestone, rooted in exact current a126.

The conditional root resource contract is implemented only in physical96 A936..<C000, body546..<563, template629..<653 and metadata653..<655. All original label/name-value pairs survive and every ROM byte outside those granted spans is exact. The genuine current Main was rebuilt with only two zero-byte exports, ImposeGravitySprObj and VerticalForce; its actual source entrypoint, recipe and full dependency hashes are included/pinned. No old whole-main/object overlay, menu mask, common hook or audio gate was installed.

Actual assembled fit resolves the C2 overflow:1258B of native proxy code runs in residentA96 between source VM phases;11B reset core remains in C2 for genuine constructor calls. All1687B Hogan metadata fits in C2. C2 content is7488B including original2KiB state, context, metadata, recovery/contact/helpers and fullcookie; non-cookie content endsDD30, cookieDFE0..<DFF0. A3 source VM/scripts7726B plus16B ownership marker. ResidentA2338B + stableC308B =2646/5834B. physical-fit.json records every actual linked range and24 actual1KiB page classifications. A1 is explicitly inactive zeros: authentic music is still unbuilt/unqualified.

Loader checks selected29/Hogan/mode1/busyodd/forcedblank/negativeNmiDisable/unpaused before transfer. It establishes the actual12-window native publication checkpoint internally, invalidates C2 first andRAM3 second before any copy, uses real buffered PPU reads, compares all24KiB, publishesRAM3 ownership first and completeC2valid last. Caller prior-owner retirement remains a real precondition; this packet does not infer outer menu/scene coverage. Auth is ROM-only before the first C2 opcode. Retire is full-AXYP preserving, independent of current Selected, and clears only family29 in both owned cookies. Future overwrite hooks must call it before publication/write.

Controls pass four dirty-hardware24KiB loads at49200 bufferedreads each,512 fullflag precondition rejections,write-protection plus three-bank readback failures,1024 full16-cookie poison checks before first guest opcode,64 genuine constructor-once/allflag cases,448 retirement/foreign-cookie cases and two real SFC caller checks.116 actual vectors resume correctly at loader/auth/constructor/retire seams, all33SMC/livepage1/R0..7/rawmaps retained, minISRSP149. Accepted load/constructor interruption uses actual forcedblank negative-NmiDisable lag context; normal/pausedNMI is tested at auth/retire, not fabricated inside copying. No native emulator run.

Retained failures: branch ranges; metadata-only prelink BANK() lacked segment provenance; two missing native exports; private-output guard rejected an inherited --create-full-dep path before compiling; a dictionary observer mistook new macro-local LOCAL name for a moved old endpoint (all old name/value pairs and all external bytes were exact). These remain separate build directories. A proxy flag observer incorrectly expected callerN across genuine FarCallCommon, whose final saved-A LDA had already setNZ; direct-entry allflag controls and the actual SFC contract are distinguished without changing product code.

This is not a playable WWF unlock. Physical frame route intentionally declines. Unbound RingClamp/RingBounds/AI/audio boundaries trap rather than silently executing lab oracles or generic substitutes. Next target is native-controlled Hogan menu/lives/walk/jump/punch with authentic metadata/render and actual source punch/native enemy defeat. Ring/world adapters must replace inappropriate ring limits, source AI is conditional on actual selected-script/proxy needs, and physical enemy epoch-notification coverage is mandatory. Advanced wrestling/music can stay explicitly unfinished after the basic loop qualifies.

Source ZIP is a compact delta with actual generated assembly, metadata/body/cookie inputs, genuine guarded recipes, finite receipts and negatives. It does not duplicate donor/current ROMs,24KiB binary templates, other current-character sources or parent archives. Their hashes remain explicit. Frozen builders must be replayed only in a NEW output root with every compiler/config output validated before execution.
'''
 (O/'README.txt').write_text(readme)
 own={R/'tools/audit'/f'prepare_wwf_first_hogan_host_v{i}.py'for i in range(1,7)}|{R/'tools/audit/wwf_first_hogan_owner_controls_v1.py',R/'tools/audit/wwf_first_hogan_owner_isr_v1.py',Path(__file__),R/'tools/reference/wwf_first_hogan_owner_v1.s',R/'tools/reference/wwf_first_hogan_owner_v2.s'}
 files=local_imports(own-{p for p in own if p.suffix!='.py'})|own|{stage,*tests,O/'README.txt',O/'physical-fit.json',O/'integration-api.json',R/'build/wwf-ready74-first-host-resource-v1/resource-contract.json',R/'docs/qa/checkpoints/2026-10-31/wwf-native-proxy-source-v1/handoff.json'}
 files|={p for p in J.rglob('*')if p.is_file()and p.suffix in['.s','.cfg','.json','.dep']}
 files|={p for p in J.parent.glob('*.json')}
 for i in range(1,6):
  base=R/'build'/f'wwf-first-hogan-host-v{i}'
  files|={p for p in base.glob('*.json')}
 for n in ['hogan-metadata.bin','hogan-body.chr','cookie.bin']:files.add(J/n)
 # Do not archive the dependency fixture's preexisting current-character tree.
 files={p.resolve()for p in files};assert len(files)<250
 bindings={str(p.resolve()):sha(p)for p in files|external}
 with zipfile.ZipFile(O/'source-only.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
 with zipfile.ZipFile(O/'source-only.zip')as z:
  for p in files:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
 for p,h in bindings.items():assert sha(p)==h,p
 handoff=dict(source=True,inert=True,installed=False,native=False,readiness_unchanged=True,candidate=q['candidate'],parent=q['parent'],resource_contract=q['resource_contract'],status='FIRST_HOGAN_PHYSICAL_LOADER_AUTH_RETIRE_CTOR_PASS_NO_HOST_HOOKS',bindings=bindings,members={p.relative_to(R).as_posix():sha(p)for p in sorted(files)},archive_sha256=sha(O/'source-only.zip'),archive_bytes=(O/'source-only.zip').stat().st_size,main_dependency_files=len(dependencies),C2_bytes=7488,A3_bytes=7742,resident_bytes=2646,actual_vector_cuts=116,limits=q['limits'])
 save(O/'handoff.json',handoff)
 for n in ['handoff.json','source-only.zip','integration-api.json','physical-fit.json','README.txt']:(D/n).write_bytes((O/n).read_bytes())
 (D/'owned-files.txt').write_text('\n'.join(p.relative_to(R).as_posix()for p in sorted(own))+'\n'+D.relative_to(R).as_posix()+'/\n')
 print(json.dumps(dict(passed=True,handoff=str(D/'handoff.json'),SHA256=sha(D/'handoff.json'),bindings=len(bindings),members=len(files),archive_bytes=handoff['archive_bytes'])))

if __name__=='__main__':main()
