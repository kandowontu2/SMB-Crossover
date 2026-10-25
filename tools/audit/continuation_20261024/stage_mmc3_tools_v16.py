from pathlib import Path
import hashlib,json,shutil,subprocess,sys,zipfile
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;S=D/'mmc3-consolidated-v15';O=D/'mmc3-tools-v16';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((S/'proof.json').read_text())['passed']
tools=O/'tools';tools.mkdir();assets=tools/'mmc3_oversized';shutil.copytree(S/'assets',assets)
shutil.copy2(S/'mmc3_current_repairs.py',tools/'mmc3_current_repairs.py')
t=(S/'prepare_mmc3_current.py').read_text();t=t.replace("Path(__file__).resolve().parent/'assets'","Path(__file__).resolve().parent/'mmc3_oversized'")
a='def main():\n    parser=';assert t.count(a)==1;t=t.replace(a,'def main():\n    global ROOT, OUT\n    parser=')
a="    args=parser.parse_args()\n    OUT.mkdir(parents=True, exist_ok=True)";assert t.count(a)==1
t=t.replace(a,"    parser.add_argument('--source-root',type=Path,default=ROOT,help='Project source root; defaults to this tools directory parent')\n    parser.add_argument('--output',type=Path,help='Prepared source directory; use a fresh external directory for audit builds')\n    args=parser.parse_args()\n    ROOT=args.source_root.resolve()\n    if args.output: OUT=args.output.resolve()\n    OUT.mkdir(parents=True, exist_ok=True)")
t=t.replace('No canonical release or prepared artwork is replaced by this tool.','No release is installed. The guarded repair recipe includes current native art,\nCHR caching, audio banking, pause restoration and all37 menu identities.')
prep=tools/'prepare_mmc3_oversized.py';prep.write_text(t)
builder=(R/'tools/build_mmc3_oversized.py').read_text();a='    args=parser.parse_args()';assert builder.count(a)==1
builder=builder.replace(a,"    parser.add_argument('--output-dir',type=Path,default=ROOT/'build/oversized-mmc3-nf',help='Build directory, including prepared sources; may be outside the workspace')\n"+a)
a="    subprocess.run([sys.executable,str(ROOT/'tools/prepare_mmc3_oversized.py'),\n                    '--reference-rom',str(args.reference_rom.resolve())],check=True)\n    source=ROOT/'build/oversized-mmc3-nf/source'\n    out=ROOT/'build/oversized-mmc3-nf/smb-crossover-mmc3-oversized.nes'";assert builder.count(a)==1
builder=builder.replace(a,"    destination=args.output_dir.resolve()\n    source=destination/'source'\n    out=destination/'smb-crossover-mmc3-oversized.nes'\n    subprocess.run([sys.executable,str(ROOT/'tools/prepare_mmc3_oversized.py'),\n                    '--reference-rom',str(args.reference_rom.resolve()),'--output',str(source)],check=True)")
(tools/'build_mmc3_oversized.py').write_text(builder)
source=O/'fresh-source'
with(O/'prepare.log').open('w')as log:p=subprocess.run([sys.executable,str(prep),'--source-root',str(R),'--output',str(source),'--reference-rom',str(R/'build/checkpoints/native-head-pz/candidate.nes')],cwd=R,stdout=log,stderr=subprocess.STDOUT)
assert p.returncode==0,(O/'prepare.log').read_text()[-3000:]
target=D/'ryu-head-oversized-mmc3-v12/roundtrip-v1/prepared-source.zip'
with zipfile.ZipFile(target)as z:
 for name in z.namelist():
  if not name.endswith('/'):assert(source/name).read_bytes()==z.read(name),name
files={p.relative_to(O).as_posix():sha(p)for p in tools.rglob('*')if p.is_file()and'__pycache__'not in p.parts}
before={n:sha(R/n)if(R/n).exists()else None for n in files}
q=dict(passed=True,staged_tools=files,root_before=before,prepared_source_exact_629_files=True,expected_ROM_sha256='43134c243d752fcaeab93d348ef56849df810f069788de9af1d76ed498359867',adopted=False,goal_complete=False,scope='Self-contained current MMC3 preparation plus explicit external output paths. Fresh command-line preparation exactly matches the qualified629-file source bundle. Build-tool installation and its integration rebuild are separate.')
(O/'staging-proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
