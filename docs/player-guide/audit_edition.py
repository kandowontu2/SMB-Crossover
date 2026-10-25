"""Evidence/coverage audit of the guide, not a gameplay certification."""
from pathlib import Path
import hashlib,json,re,zipfile
from edition_content import FILES,CATALOGUES,IDENTITIES
HERE=Path(__file__).parent;ROOT=HERE.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 expected={'build/smb-crossover-mmc3-oversized.nes':'a03284f691e32be333976806462a5f65ee2d70e0659d0e404a6347b5a0d7bae7','build/smb-crossover-mmc5-expanded.nes':'58e44b4ef7324bf1bd093b92738a35d38df6aba55315133d410b444ad7f09c6e','build/checkpoints/parodius-death-nr/candidate.nes':'2931163dd7d3c31f9a81776b16c45631a0abd2120abff4454833084825475590','build/checkpoints/parodius-death-nr/source.zip':'81a9912e7001a8c3da3a374ac39ef4b1a2f16812fb2364fa0960dff1b779d2cf'}
 for p,h in expected.items():assert sha(ROOT/p)==h,p
 with zipfile.ZipFile(ROOT/'build/checkpoints/parodius-death-nr/source.zip') as z:
  inventory=z.read('src/inventory_data.inc').decode()
  remaining=z.read('src/remaining_weapons.s').decode()
  count=list(map(int,re.search(r'InvItemCount:\s*\.byte ([\d,]+)',inventory)[1].split(',')))
  refs={s for p in FILES for s in p['sources']}
  refs|={'src/inventory.s','src/inventory_drops.s','src/inventory_data.inc','src/remaining_weapons.s','src/darkwing_pickups.s','src/darkwing_weapons.s','src/kirby_weapons.s','src/mike_jones_pickups.s','src/zelda2_reward_tables.inc','src/tmnt_combat.s','src/character_select.s','src/parodius_render.s','src/parodius_art.inc','docs/qa/parodius-rendering-2026-10-23.md'}
  source=[]
  for p in sorted(refs):
   assert (ROOT/p).exists(),p
   frozen=z.read(p) if p in z.namelist() else None
   source.append(dict(path=p,current_sha256=sha(ROOT/p),frozen_NR_sha256=hashlib.sha256(frozen).hexdigest() if frozen else None,kind='Pinned behavior source' if frozen else 'Authored integration/reference note'))
 # Every nonzero item ID in each shared inventory is covered by a labeled
 # illustrated row, including initial growth/passive items and shared pictures.
 inventory_map={
  1:('mega',[0,1,2,3,4,5,6,7,8,9]),
  2:('samus',[1,2,3,4,5,6,0]),
  3:('contra',[0,4,5,2,3,1]),
  4:('link',[3,4,2,5,6,2]),
  5:('simon',[1,3,4,5,2,6,7,8,0]),
  9:('mega',[0,1,2,3,4,5,6,8]),
  10:('ryu',[0,1,2,3,4,5,6]),
  11:('sophia',[1,2,3,4,5,6,0])}
 coverage=[]
 for owner,(key,rowids) in inventory_map.items():
  assert len(rowids)==count[owner],(owner,len(rowids),count[owner])
  cat=next(c for c in CATALOGUES if c['key']==key)
  for i,rowid in enumerate(rowids,1):coverage.append(dict(owner=owner,item_id=i,catalogue=key,row=rowid,name=cat['items'][rowid]['name'],image=cat['items'][rowid]['image']))
 # Verify item-to-picture identity against the actual compiled source lookup,
 # rather than merely proving a picture file exists beside the right name.
 tokens=[]
 for ln in remaining.split('PickupArts:',1)[1].split('.endproc',1)[0].splitlines():
  ln=ln.split(';')[0].strip()
  if ln.startswith('.byte'):tokens += [x.strip() for x in ln[5:].split(',')]
  elif ln.startswith('.res'):tokens += ['0']*int(ln[4:].split(',')[0])
 for row in coverage:
  owner=row['owner'];i=row['item_id']
  if owner in [2,3,4,5,10,11]:
   symbol=tokens[(owner-2)*8+i]
   expected_image='mushroom' if symbol=='0' else symbol.lower()
   assert row['image']==expected_image,(owner,i,row['name'],row['image'],expected_image)
   row['compiled_picture_symbol']=symbol
  elif owner in [1,9]:
   special={1:'mm-arm',2:'mm-metal',3:'mm-knuckle',4:'mm-pharaoh',5:'mm-kick',6:'mm-flame',7:'mm-water',8:'mm-rush',9:'mm-balance',10:'mushroom'}
   expected_image='mm-balance' if owner==9 and i==8 else special[i]
   assert row['image']==expected_image,(owner,i,row['image'],expected_image)
   row['compiled_picture_symbol']='InventoryDrawPickups::UpgradeArt / automatic growth item'
 assert len(coverage)==sum(count)==60
 z2=next(c for c in CATALOGUES if c['key']=='zelda2')['items']
 assert [v['image'] for v in z2[:13]]==['z2-magic','z2-sword','z2-sword','z2-fairy','z2-magic','z2-heart','z2-fire','z2-magic','z2-magic','z2-magic','z2-glove','z2-heart','z2-magic']
 images={v['image'] for c in CATALOGUES for v in c['items']}|{'hero-'+i for i in IDENTITIES}
 for i in images:assert (HERE/'assets/edition'/f'{i}.png').exists(),i
 assert len(IDENTITIES)==37
 previews={i for p in FILES if p['preview'] for i in p['heroes']};assert previews=={'roll','octopus','twinbee','pentarou'}
 facts=[
  dict(topic='Mega Man/Bass energy',source='src/inventory_drops.s :: Collect; src/inventory.s :: InventoryRefillAmount',finding='Actual small8 / large40, maximum112. Earlier draft4/16 was corrected.'),
  dict(topic='Darkwing item tags',source='src/darkwing_pickups.s :: DwGiveItem; src/darkwing_weapons.s :: Cost',finding='22:+1health;23:full4health;24:+10gas;25:+1gas;Arrow3gas, Heavy/Thunder2. Earlier source-game generic assumptions were replaced by installed rules.'),
  dict(topic='Proto Man',source='src/protoman.s; docs/qa/protoman-private-implementation-2026-10-23.md',finding='Mega Man family/inventory including Rush. Shield-bearing art is cosmetic; no new shield defense claimed.'),
  dict(topic='Turtles',source='src/tmnt_core.s :: TnStartAttack; src/tmnt_combat.s :: TnHeal',finding='Four primaries, directed attacks,128health; mushroom32/flower64. No obtainable subweapon-drop inventory claimed.'),
  dict(topic='Parodius',source='reference/parodius-nes/integration-status.json; src/parodius_bells.s',finding='Option caps4/3/3; missile/gun/shield ensembles are distinct. The RST cell before defense removes upgrades. Big cannot fire.'),
  dict(topic='Shared art',source='src/remaining_weapons.s :: PickupArts; src/zelda2_link_draw_world.s :: RewardArt; src/mike_jones_art.inc :: JnItem',finding='Repeated shapes are retained and labeled, not replaced with invented unique item art.'),
  dict(topic='Kirby',source='src/kirby_weapons.s :: KbFamilyForEnemy; src/kirby_core.s :: KbHealPickup',finding='14enemy-family copy assignments; food heals2/6. Copy symbols are actual HUD emblems, distinct from block items.'),
  dict(topic='New guest food',source='src/chip_dale_core.s; src/little_mac_combat.s; src/mike_jones_pickups.s; src/roll_weapons.s',finding='Distinct recovery/capacity/star policies are stated per file; no universal Mario growth claim.'),
 ]
 rec=dict(passed=True,scope='Player-guide factual/image/coverage audit. Does not prove every final gameplay route or powerup test.',roms=expected,identities=sorted(IDENTITIES),published_identities=sorted(IDENTITIES-previews),development_previews=sorted(previews),character_files=len(FILES),catalogues=len(CATALOGUES),labeled_entries=sum(len(c['items'])for c in CATALOGUES),unique_catalogue_images=len({v['image']for c in CATALOGUES for v in c['items']}),shared_inventory_count=60,shared_inventory_item_coverage=coverage,custom_catalogue_coverage={k:len(next(c for c in CATALOGUES if c['key']==k)['items']) for k in ['zelda2','mike','kirby','cv3','smb3','darkwing','preview','vic']},sources=source,manual_source_findings=facts,image_provenance_sha256=sha(HERE/'assets/edition-provenance.json'),limits=['Catalogues use explicit static color/animation phases; shared area palettes can change colors.','Artwork decoding is a guide-image reconstruction, not a proof of every in-game palette in every area.','Custom effects, health scaling, item delivery and playable boss controls retain documented SMB adaptations.','Dedicated audio and full final roster/playthrough verification remain open; no release certification is asserted.'])
 proof=json.loads((HERE/'assets/portrait-pixel-proof.json').read_text())
 assert proof['ROM_sha256']==expected['build/checkpoints/parodius-death-nr/candidate.nes']
 assert len(proof['cases'])==37
 for pic in proof['cases']:
  assert pic['pixels']==pic['screenshot_matches']==pic['opaque_pixels_preserved']
  assert sha(HERE/'assets/edition'/('hero-'+pic['identity']+'.png'))==pic['asset_sha256']
 provenance=json.loads((HERE/'assets/edition-provenance.json').read_text())
 for pic in provenance:
  if 'asset'in pic:assert sha(HERE/'assets/edition'/pic['asset'])==pic['sha256'],pic['asset']
 rec['portrait_pixel_proof']=dict(identities=37,source='Observed native OAM/CHR and hardware palette',all_opaque_pixels_preserved=True,no_color_key_removal=True)
 rec['private_preview_reference']={'checkpoint':'parodius-death-nr','ROM_sha256':expected['build/checkpoints/parodius-death-nr/candidate.nes'],'source_zip_sha256':expected['build/checkpoints/parodius-death-nr/source.zip'],'capture_sets':['build/verification/player-guide-magazine-2026-10-24/portrait-capture','build/verification/parodius-death-nr/entry-v2','build/verification/parodius-render-nq/pickups-v3'],'art_changes':['Every identity portrait reconstructed without color-key damage','Native TwinBee/Pentarou primaries retained','RST remains before defense; earlier NQ item art is individually pinned'],'limits':['Native pilot-specific Parodius death art/animation is present within the adapted SMB lifecycle.','Substantial lag/dropout and dedicated audio remain open.','This guide refresh is not final game certification.']}
 (HERE/'accuracy-audit.json').write_text(json.dumps(rec,indent=2)+'\n')
 text='''# Guide accuracy and edition record\n\nThis edition covers33 published full-roster identities and4 clearly marked private MMC5 previews (Roll, Octopus, TwinBee, Pentarou). It is a player reference, not certification of the unfinished final game.\n\n## Evidence\n\n- The exact current publication and private source hashes are in`accuracy-audit.json`.\n-37 identities have controls and separate Easy/Hard explanations in27 moveset files.\n-157 labeled catalogue entries each have an actual installed-game picture. Shared shapes are labeled explicitly.\n-All60 nonzero shared-inventory IDs map to illustrated rows. Custom health/ability/form/ship systems are covered separately.\n-`assets/edition-provenance.json` identifies the source record or actual native capture behind every generated sprite picture. No AI item art was created.\n- Item pictures retain source opaque pixels and nearest-neighbor enlargement. A static shared world palette/animation phase is shown; colors can vary by area.\n\n## Important corrections from the earlier guide/draft\n\n- Expanded the old14-identity coverage; removed obsolete checkpoint-HR branding.\n- Energy capsules restore8/40 on the112-unit scale, not4/16.\n- Darkwing uses health aids and gas: small health1, full health4, gas1/10; Arrow costs3, Heavy/Thunder2.\n- Proto Man shares Mega Man's inventory, including Rush; no cosmetic shield benefit was invented.\n- Kirby's14 copy emblems are identified as abilities, not physical block rewards.\n- The turtle subweapon system and Mike's utility magic are not described as implemented.\n- The Parodius RST purchase resets gear; it is not random.\n\n## Limits\n\nNo every-level, every-powerup-route, original-audio, physical-cartridge or full source-game parity claim is made. Main game verification is owned by the project's final verification plan. Character artwork and item mechanics were checked against installed source and pinned integration notes; the guide does not convert old narrow gameplay fixtures into a campaign guarantee.\n'''
 text+='\n## Magazine redesign and NR reference\n\nAll37 portraits were rebuilt from actual read-only controller-menu OAM/CHR and native palette observations against immutable`parodius-death-nr`. Every opaque pixel matches the original screenshot. Transparency does not use a color key, so blue clothing and white details remain intact. Images are composited onto an explicit dark RGB matte; large authentic portraits and native gameplay frames anchor the new magazine pages.\n\nBehavior and portrait/scene references are pinned NR. Individually documented NQ item captures remain valid unchanged equipment examples; the exact source hashes are retained. Pilot-specific Parodius death art/animation is now present, within the SMB lifecycle. Substantial lag/dropout, dedicated audio and final campaign checks remain unfinished.\n'
 (HERE/'ACCURACY.md').write_text(text)
 print(json.dumps({k:rec[k]for k in ['passed','character_files','labeled_entries','unique_catalogue_images','shared_inventory_count']}))
if __name__=='__main__':main()
