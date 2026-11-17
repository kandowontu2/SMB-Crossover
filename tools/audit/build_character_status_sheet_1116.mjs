import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';

// Resolve the bundled runtime without a junction in the storage-guarded tree.
const modules = 'C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1112-611-0_26.1112.611.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules';
const require = createRequire(path.join(modules, '__spreadsheet_resolver__.cjs'));
const {Workbook, SpreadsheetFile} = await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const root = process.cwd();
const input = await fs.readFile(path.join(root, 'docs/qa/character-status-sheet-data-1116.json'));
const inputHash = createHash('sha256').update(input).digest('hex');
if (inputHash !== '134b9bf385308680ee6bb50e8f076cd69a343413b6aa8d6294a98850b3f7e91e') throw Error('Status source changed; reconcile first');
const data = JSON.parse(input.toString('utf8'));
if (data.rows.length !== 101 || new Set(data.rows.map(r => r.name)).size !== 101) throw Error('101 distinct characters required');
const out = path.join(root, 'build/character-status-sheet-1116/outputs/01a1404e-46cd-7840-b178-def1eda87a64');
await fs.mkdir(out, {recursive:true});
const workbook = Workbook.create();
const main = workbook.worksheets.add('Characters');
const evidence = workbook.worksheets.add('Evidence');
const labels = {CURRENT:'Current', CURRENT_PRESERVED:'Preserved', EARLIER:'Earlier', FIXTURE_OR_PRIVATE_ONLY:'Limited', UNKNOWN:'Unconfirmed'};
const proofOptions = ['Current','Preserved','Earlier','Limited','Unconfirmed','Source only','Issue'];
const reviewOptions = ['Open','Partial','Issue','Severe lag','Unconfirmed'];
const review = s => s.includes('KNOWN_ISSUE') ? 'Issue' : s.includes('SEVERE') ? 'Severe lag' : s.includes('PARTIAL') ? 'Partial' : s.includes('UNMEASURED') ? 'Unconfirmed' : 'Open';
const repo = 'https://github.com/kandowontu2/SMB-Crossover/blob/master/';
const snapshot = 'https://github.com/kandowontu2/SMB-Crossover/blob/63fb4f43/docs/qa/character-status-sheet-data-1116.json';
const url = p => repo+p.split('/').map(encodeURIComponent).join('/');
const specific = r => r.evidence_paths.filter(p => p.endsWith('.md') && !p.includes('character-select-access') && !p.includes('expanded-roster-next-native-checklist'));
const primaryUrl = r => specific(r).length ? url(specific(r)[0]) : snapshot;
const note = s => typeof s === 'string' && s.startsWith('=') ? "'"+s : s;
function next(r) {
  if (r.name === 'ROGUE DAWN') return 'Verify the HUD transition repair in Mesen, then check remaining upgrades and impacts.';
  if (r.performance_status.includes('SEVERE')) return 'Reduce severe idle/walk lag, then check natural pickups, weapons and remaining moves.';
  if (r.next_action.startsWith('Retain versioned stage proof; locate natural-item evidence')) return 'Find existing pickup tests, then finish moves, graphics, sound and lag checks.';
  return r.next_action.replaceAll('qualify','check').replaceAll('Qualify','Check');
}
const headers = ['Character','Menu access','Playable','1-1 clear','Mushroom','Flower','1-UP','Star','Ability review','Graphics / audio','Lag review','Next priority','Evidence'];
const records = data.rows.map(r => [r.name, `R${r.menu_row} C${r.menu_column}. Select ${r.select_presses}`, 'Yes', labels[r.stage_status], labels[r.M_status], labels[r.F_status], labels[r.L_status], labels[r.S_status], review(r.abilities_status), review(r.art_status), review(r.performance_status), next(r), primaryUrl(r)].map(note));
const last = records.length+7;
main.getRange(`A7:M${last}`).values = [headers, ...records];
const mainTable = main.tables.add(`A7:M${last}`, true, 'CharacterGoals');
mainTable.style = 'TableStyleLight1';
main.getRange(`A1:M${last}`).format.font = {name:'Arial', size:11, color:'#202124'};
main.getRange(`A1:M${last}`).format.fill = '#FFFFFF';
main.getRange(`A1:M${last}`).format.verticalAlignment = 'center';
main.getRange('A2').values = [['SMB Crossover goals']];
main.getRange('A2').format.font = {name:'Arial', size:16, bold:true};
main.getRange('A3:C5').values = [
  [`Snapshot ${data.as_of}`,'Gameplay paused','MMC5 nightly cb95eb8d'],
  ['Status key','','Current: cb95 native check. Preserved: earlier pass plus preservation proof. Earlier: another build. Limited: fixture/private only.'],
  ['Review key','','Unconfirmed: proof not located. Open review does not mean missing abilities. Startup/stage clears do not certify all moves.'],
];
main.getRange('A3:M5').format.font = {name:'Arial', size:10, color:'#5F6368'};
main.getRange('A3:M5').format.rowHeightPx = 21;
main.getRange('A2:M2').format.rowHeightPx = 29;
main.getRange('D2').values = [['Names']];
main.getRange('E2').formulas = [[`=COUNTA(A8:A${last})`]];
main.getRange('F2').values = [['Current 1-1']];
main.getRange('G2').formulas = [[`=COUNTIFS(D8:D${last},"Current")`]];
main.getRange('H2').values = [['Earlier proof']];
main.getRange('I2').formulas = [[`=COUNTIFS(D8:D${last},"Earlier")+COUNTIFS(D8:D${last},"Preserved")`]];
main.getRange('D2:I2').format.font = {name:'Arial', size:10};
main.getRange('D2:I2').format.horizontalAlignment = 'center';
main.getRange('E2').setNumberFormat('0');
main.getRange('G2').setNumberFormat('0');
main.getRange('I2').setNumberFormat('0');
const widths = [195,150,110,130,155,155,155,155,145,165,155,380,540];
for (let i=0;i<widths.length;i++) main.getRangeByIndexes(0,i,last,1).format.columnWidthPx = widths[i];
main.getRange(`A8:M${last}`).format.rowHeightPx = 66;
main.getRange(`A8:B${last}`).format.wrapText = true;
main.getRange(`L8:M${last}`).format.wrapText = true;
main.getRange(`L8:M${last}`).format.verticalAlignment = 'top';
main.getRange(`C8:K${last}`).format.horizontalAlignment = 'center';
main.getRange(`M8:M${last}`).format.font = {name:'Arial',size:10,color:'#1A73E8'};
main.getRange('A7:M7').format = {fill:'#F1F3F4',font:{name:'Arial',size:11,bold:true,color:'#202124'},wrapText:true,horizontalAlignment:'center',verticalAlignment:'center',rowHeightPx:40,borders:{bottom:{style:'thin',color:'#DADCE0'}}};
main.getRange(`C8:C${last}`).dataValidation = {rule:{type:'list',values:['Yes','No']}};
main.getRange(`D8:H${last}`).dataValidation = {rule:{type:'list',values:proofOptions}};
main.getRange(`I8:K${last}`).dataValidation = {rule:{type:'list',values:reviewOptions}};
const colors = [['Current','#E6F4EA','#137333'],['Preserved','#E8F0FE','#174EA6'],['Earlier','#F1F3F4','#3C4043'],['Limited','#FEF7E0','#8D6100'],['Unconfirmed','#F8F9FA','#5F6368'],['Source only','#FEF7E0','#8D6100'],['Issue','#FCE8E6','#A50E0E'],['Severe lag','#FCE8E6','#A50E0E'],['Partial','#FEF7E0','#8D6100']];
for (const [value,fill,color] of colors) main.getRange(`D8:K${last}`).conditionalFormats.addCustom(`D8="${value}"`,{fill,font:{color}});
main.freezePanes.freezeRows(7);
main.freezePanes.freezeColumns(2);
main.showGridLines = true;

const short = s => s ? s.slice(0,8) : 'not recorded';
const pickup = (r,k,label) => `${label}: ${labels[r[k+'_status']]} (${short(r[k+'_build'])}). ${r[k+'_scope']}`;
const detailRows = data.rows.map(r => [r.name,`${labels[r.stage_status]} (${short(r.stage_build)}). ${r.stage_scope}`,
  [pickup(r,'M','Mushroom'),pickup(r,'F','Flower'),pickup(r,'L','1-UP'),pickup(r,'S','Star')].join('\n'),
  `Abilities: ${r.abilities_scope}\nGraphics: ${r.art_scope}\nAudio: ${r.audio_scope}`,
  r.performance_scope,
  (specific(r).length ? specific(r).slice(0,3).map(url) : [snapshot]).join('\n')].map(note));
const endEvidence = detailRows.length+6;
evidence.getRange(`A6:F${endEvidence}`).values = [['Character','1-1 proof and build','Pickup proof and build','Remaining review scope','Performance scope','Sources'],...detailRows];
const evidenceTable = evidence.tables.add(`A6:F${endEvidence}`, true, 'CharacterEvidence');
evidenceTable.style = 'TableStyleLight1';
evidence.getRange(`A1:F${endEvidence}`).format.font = {name:'Arial',size:11,color:'#202124'};
evidence.getRange(`A1:F${endEvidence}`).format.fill = '#FFFFFF';
evidence.getRange('A2').values = [['Verification details']];
evidence.getRange('A2').format.font = {name:'Arial',size:16,bold:true};
evidence.getRange('A3:B4').values = [['Build-specific proof','Earlier entries retain their tested ROM and scope. Unconfirmed means qualifying proof was not located.'],['Full source inventory',snapshot]];
evidence.getRange('A3:F4').format.font = {name:'Arial',size:10,color:'#5F6368'};
const ew = [195,340,540,440,420,600];
for (let i=0;i<ew.length;i++) evidence.getRangeByIndexes(0,i,endEvidence,1).format.columnWidthPx = ew[i];
evidence.getRange(`A7:F${endEvidence}`).format.wrapText = true;
evidence.getRange(`A7:F${endEvidence}`).format.verticalAlignment = 'top';
for (let i=0;i<detailRows.length;i++) {
  const lines = Math.max(...detailRows[i].map((v,c) => String(v).split('\n').reduce((n,t)=>n+Math.max(1,Math.ceil(t.length/(ew[c]/6))),0)));
  evidence.getRangeByIndexes(i+6,0,1,6).format.rowHeightPx = Math.max(100,lines*16+12);
}
evidence.getRange(`F7:F${endEvidence}`).format.font = {name:'Arial',size:10,color:'#1A73E8'};
evidence.getRange('A6:F6').format = {fill:'#F1F3F4',font:{name:'Arial',size:11,bold:true,color:'#202124'},wrapText:true,horizontalAlignment:'center',verticalAlignment:'center',rowHeightPx:36,borders:{bottom:{style:'thin',color:'#DADCE0'}}};
evidence.freezePanes.freezeRows(6);
evidence.freezePanes.freezeColumns(1);
evidence.showGridLines = true;
workbook.recalculate();
const check = await workbook.inspect({kind:'region',sheetId:main.name,range:'D2:I2',maxChars:1500,tableMaxRows:2,tableMaxCols:6});
console.log(check.ndjson);
const errors = await workbook.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},maxChars:1500});
console.log(errors.ndjson);
const previews = [];
for (const [sheetName,range,filename] of [['Characters','A1:M14','characters-preview.png'],['Evidence','A1:F9','evidence-preview.png']]) {
  const image = await workbook.render({sheetName,range,scale:1,format:'png'});
  previews.push([filename,new Uint8Array(await image.arrayBuffer())]);
}
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
const filename = path.join(out,'SMB-Crossover-Character-Goals.xlsx');
await xlsx.save(filename);
// The exporter adds a disposable inspection sidecar; retain only the deliverable/previews.
const sidecar = filename+'.inspect.ndjson';
if (path.dirname(sidecar) !== out) throw Error('Inspection cleanup escaped owned output');
try { await fs.unlink(sidecar); } catch (error) { if (error.code !== 'ENOENT') throw error; }
for (const [name,bytes] of previews) await fs.writeFile(path.join(out,name),bytes);
console.log('RESULT '+JSON.stringify({passed:true,inputHash,characters:records.length,unique:101,sourceStageCounts:data.counts.stage,
  sheets:[{name:'Characters',table:'CharacterGoals',range:`A7:M${last}`,headers},{name:'Evidence',table:'CharacterEvidence',range:`A6:F${endEvidence}`}],
  xlsx:filename,bytes:(await fs.stat(filename)).size,outputFiles:3,goalPaused:true}));
