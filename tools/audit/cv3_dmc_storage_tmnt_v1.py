"""Private proof that retained TMNT cold adapters fit the shared125 layout."""
from pathlib import Path
import argparse,hashlib,itertools,json,re,shutil,subprocess,sys
from check_tmnt_render_oa import load,address,location
from robots_weapon_cpu_v1 import Arena
ROOT=Path(__file__).resolve().parents[2]
DONOR=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-oc/candidate-v7')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def apu(q):return[(at,v)for at,v in q.m.writes if 0x4000<=at<=0x4017]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);stage=out/'source';stage.mkdir()
 for n in('src','inc','chr','audio'):shutil.copytree(DONOR/'source'/n,stage/n)
 shutil.copytree(DONOR/'source/build/generated',stage/'build/generated')
 for q in[DONOR/'source/build_options.ini',*(DONOR/'source').glob('*.cfg')]:shutil.copyfile(q,stage/q.name)
 cfg=stage/'smb1base-mmc5-expanded.cfg';text=cfg.read_text();triplet=re.search(r'    TN_AUDIO_PREFIX_MEM:.*?X5_NEW_7B:.*?;\n',text,re.S).group();blank=re.search(r'    X5_NEW_3F:.*?;\n',text).group()
 text=text.replace(triplet,'    X5_UNUSED_7B:start=$a000,size=$2000,type=ro,file=%O,fill=yes,fillval=$ff,bank=$7b;\n').replace(blank,triplet.replace('bank=$7b','bank=$3f'))
 text=text.replace('    X5_NEW_7D: start=$c000, size=$2000, type=ro, file=%O, fill=yes, fillval=$ff, bank=$7d;','    SHARED125_PREFIX:start=$c000,size=$1700,type=ro,file=%O,fill=yes,fillval=$ff,bank=$7d;\n    X5_NEW_7D:start=$d700,size=$03f7,type=ro,file=%O,fill=yes,fillval=$ff,bank=$7d;\n    SHARED125_TAIL:start=$daf7,size=$0509,type=ro,file=%O,fill=yes,fillval=$ff,bank=$7d;');cfg.write_bytes(text.encode())
 f=stage/'src/tmnt_audio_resident.s';raw=f.read_bytes();assert raw.count(b'lda #$fb')==1;f.write_bytes(raw.replace(b'lda #$fb',b'lda #$bf'))
 with(out/'host.log').open('w')as log:r=subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')],cwd=stage,stdout=log,stderr=subprocess.STDOUT)
 assert not r.returncode,(out/'host.log').read_text()[-5000:]
 old,new=load(DONOR/'candidate.nes'),load(out/'candidate.nes');ob,nb=old['raw'],new['raw'];assert ob[:16]==nb[:16]and ob[1048592:]==nb[1048592:]
 assert nb[16+63*8192:16+64*8192]==ob[16+123*8192:16+124*8192]
 assert nb[16+123*8192:16+124*8192]==b'\xff'*8192
 assert address(new,'SamusAudioCold')==0xd700 and address(new,'TnAudioUpdate')==0xd9c9
 for name in('src/tmnt_audio_samus_cold.s','src/tmnt_audio.s'):assert sha(stage/name)==sha(DONOR/'source'/name)
 rows=[];allowed={0x5115}
 # Execute complete native adapters, with unchanged actual native music
 # init/play code. The donor is held for lag; this proves placement only.
 for char,area,event,pause in itertools.product((2,19),(1,2,4,8,16,32,64),(0,1,2,4,8,16,32,64),(0,1)):
  qs=[Arena(b,char)for b in(old,new)]
  for q in qs:q.put(AreaMusicQueue=area,EventMusicQueue=event,GamePauseStatus=pause)
  for tick in range(4):
   cs=[q.invoke('AudioUpdate')[0]for q in qs]
   assert apu(qs[0])==apu(qs[1]),(char,area,event,pause,tick)
   assert(cs[0].a,cs[0].x,cs[0].y,cs[0].p,cs[0].sp,cs[0].processorCycles)==(cs[1].a,cs[1].x,cs[1].y,cs[1].p,cs[1].sp,cs[1].processorCycles)
   changed=[i for i in range(0x8000)if i not in allowed and not 256<=i<512 and qs[0].m[i]!=qs[1].m[i]];assert not changed,[(hex(i),qs[0].m[i],qs[1].m[i])for i in changed[:10]]
   for oldbank,newbank in zip(qs[0].m.banks,qs[1].m.banks):assert newbank==(63 if oldbank==123 else oldbank)
   rows.append(dict(character=char,area=area,event=event,pause=pause,tick=tick,cycles=cs[1].processorCycles))
 result=dict(passed=True,ROM_sha256=sha(out/'candidate.nes'),donor_ROM_sha256=sha(DONOR/'candidate.nes'),actual_full_AudioUpdate_cases=len(rows),cold_source_files_unchanged=True,SamusAudioCold=address(new,'SamusAudioCold'),TnAudioUpdate=address(new,'TnAudioUpdate'),cold_end=0xdaf7,engine_A_identical_at_bank63=True,Mac_bank123_wholly_free=True,all_APU_existing_RAM_regs_cycles_exact=True,scope='Placement proof against held TMNT v7 only. Not a combined current529 build, native qualification or approval of held driver lag. Future final E mirror must clone the final linked127 including all TMNT fixed hooks and drum, never the529 image.')
 (out/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');(out/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
