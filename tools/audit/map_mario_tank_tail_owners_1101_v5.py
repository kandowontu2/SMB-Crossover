"""Small exact compiled-source index for the remaining Tank tail review."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_visible_1101_v5 import O,P,PIN
from link_pit_rygar_sophia_audit_cpu import scoped_load
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 b=scoped_load(P/'candidate.nes');assert sha(b['raw'])==PIN;files={};lines={}
 for line in (P/'candidate.dbg').read_text().splitlines():
  if not line.startswith(('file\t','line\t')):continue
  d=dict(x.split('=',1)for x in line.split('\t',1)[1].split(',')if '='in x)
  (files if line.startswith('file\t')else lines)[d['id']]=d
 mapping=[(115,0x195,0x200,'X5_FULL_MUSIC_0F','X5MusicBank0F'),(68,0x1ecc,0x1f20,'MAAA_ART','MaaArtEnd'),(82,0x1fc2,0x2000,'SMB2_NMI_C82','S2C82End'),(13,0x1fc3,0x2000,'SAMUS_GFX','SsNativeChunk'),(62,0x1fc4,0x2000,'ROGUE_AUDIO_ADAPTER_A62','RdaAdapterEnd'),(66,0x1957,0x19a8,'MAAA_CORE','MaaCoreEnd'),(73,0x1fbe,0x2000,'GIMMICK_ART','GmArtEnd'),(58,0x1faa,0x2000,'SOPHIA_BODY_COLD','RyuSourceBodyPlatformFinish'),(12,0x1fad,0x2000,'DONKEY_KONG_ART','DkMenuName'),(89,0x1fb0,0x2000,'BASS_HEAD_GATE','BassHeadAdmission'),(28,0x1fb0,0x2000,'CV_WRAP','Cv3DmcBeforeCv1'),(78,0xf96,0x1000,'CF_LOADER_PROPOSAL_C','CfLoaderExpectedCookie')]
 source_names={115:'bt-ready-menu-1031-v2/joint/src/full_roster_music.inc',68:'character-host-union-v13/maaa-component.s',82:'functional-roster-smb2-v1/joint/nmi-c82.s',13:'bt-ready-menu-1031-v2/joint/src/special_art.inc',62:'arthur-expanded-host-v1/joint/rogue_dawn_audio_scheduler_hooks_v5.s',66:'character-host-union-v13/maaa-component.s',73:'functional-roster-visuals58-v1/joint/src/gimmick_art.inc',58:'bt-ready-menu-1031-v2/joint/src/ryu_source_body.s',12:'current-character-composition-v1/joint/src/donkey_kong_host.s',89:'bt-ready-menu-1031-v2/joint/src/bass_corner_profile.inc',28:'bt-ready-menu-1031-v2/joint/src/cv3_dmc_complete.s',78:'contra-force-projectile-contact-1031-v3/joint/cf-loader.s'}
 archive=zipfile.ZipFile(R/'build/_recovery/legacy-sources-2026-10-31.zip');idx={q['path']:q for q in json.loads(archive.read('index.json'))};rows=[]
 for bank,start,end,segment,symbol in mapping:
  s=next(s for s in b['segs'].values()if s['name'].strip('"')==segment);v=b['syms'][symbol];defs=[]
  key=source_names[bank];p=R/'build'/key
  f=next(q for q in files.values()if Path(q['name'].strip('"'))==p)
  if p.is_file():data=p.read_bytes();origin='live-immutable-source'
  else:
   q=idx[key];data=archive.read('objects/'+q['sha256']);assert sha(data)==q['sha256'];origin='exact-indexed-object-in-memory'
  assert len(data)==int(f['size']),(key,len(data),f['size'])
  text=data.decode('utf-8');found=[i+1 for i,l in enumerate(text.splitlines())if symbol in l];defs.append(dict(path=str(p),matching_source_lines=found,debug_declared_size=int(f['size']),sha256=sha(data),origin=origin,original_debug_definition_id=v.get('def'),debug_line_table_stripped=not bool(lines)))
  rows.append(dict(bank=bank,physical_half_open=[start,end],bytes=end-start,old_segment=segment,compiled_old_half_open=[int(s['start'],0),int(s['start'],0)+int(s['size'],0)],last_producer_symbol=symbol,symbol_PC=int(v['val'],0),symbol_size=int(v.get('size','0'),0),source_definitions=defs,PRG_bank_sha256=sha(b['raw'][16+bank*8192:16+(bank+1)*8192]),consumer_closure=False,formal_grant=False))
 q=dict(passed=True,current_ROM_sha256=PIN,remaining_review=rows,scope='Exact current debug/source definition index only. Not an old-reader closure or interval grant. Root reviews named producers and their typed table readers; source caps must constrain old endpoints before placement.',bindings={str(Path(__file__).relative_to(R)):sha(Path(__file__).read_bytes())});(O/'remaining-tail-source-map.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,intervals=len(rows))))
if __name__=='__main__':main()
