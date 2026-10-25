# SMB Crossover player's guide - Astra editorial rebuild

48 pages; 33 published identities and four clearly marked private previews.

Run `python build_guide.py` to create `Player Guide/SMB-Crossover-Players-Guide.pdf`.
Requires Pillow and ReportLab, plus locally licensed Windows Arial, Arial Bold,
Impact and Georgia Italic fonts. No ROM, network access or game repository is
needed. The editable ZIP is verified by extracting it into a separate directory
and reproducing the PDF's exact SHA-256 hash.

`build_astra.py` contains layouts, diagrams, special features and reading order.
`edition_content.py` and `guide_content.py` contain inherited character facts,
rewritten or consolidated by the builder where appropriate. Artwork is under
`assets/edition` and `assets/astra`; the latter takes precedence. `image-audit.json`
maps every retained image to its origin, hash and printed pages. Additional
provenance files record source extraction and the original portrait pixel checks.
The replaced Meta Knight portrait is identified separately.

Baseline content pin: immutable `parodius-death-nr` private checkpoint.
ROM SHA-256: 2931163dd7d3c31f9a81776b16c45631a0abd2120abff4454833084825475590
Source ZIP SHA-256: 81a9912e7001a8c3da3a374ac39ef4b1a2f16812fb2364fa0960dff1b779d2cf
The frozen Meta Knight NU update is recorded in `content-updates.json`; its
corrected portrait and six real practice captures supersede the earlier flight
feature. Meta remains a published roster identity, but these repairs require
the private NU update. Body palette 36/14/0F is exact; sword hues are explicitly
remapped to 30/27/16. No wings or flight are represented. Sword audio uses an SMB
fallback. Earlier field screenshots retain their own recorded provenance.

The two empty mounts in the supplied 1-4 firebar view are authored and activate
in 6-4 independently of Easy/Hard. This is not a claim that all castles are fixed.

The rebuild uses correctly colored native enemies, original 2.02 pickup artwork,
distinct StarTropics manual illustrations, and explicitly labeled diagrams.
Source art is distinguished from installed physical pickups. A complete original
Punch-Out!! HUD star and a Parodius white Bell manual illustration replace
misleading cropped/duplicated pictures. Zelda II's controls, stats and spellbook
are consolidated; duplicate generic jars do not stand in for different spells.

Unofficial fan guide. Source artwork belongs to its creators.
Nintendo StarTropics original manual:
https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAAZE.pdf
Nintendo StarTropics electronic manual (Super Nova illustration, page 8):
https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAAZE_en.pdf
The pack includes artwork needed for the guide, not ROMs or fonts.
No game files were modified. Document QA does not establish campaign completion
or resolve private-preview lag/dropout, dedicated audio or all-item coverage.
