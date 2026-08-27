#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
manifest=json.loads((root/'references/guizang-inheritance-manifest.json').read_text(encoding='utf-8'))
missing=[]; changed=[]
for rec in manifest['files']:
    p=root/rec['target']
    if not p.is_file(): missing.append(rec['target']); continue
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    if h!=rec['sha256']: changed.append(rec['target'])
# Active SKILL must contain the entire original Guizang body (frontmatter may differ).
active=(root/'SKILL.md').read_text(encoding='utf-8')
original=(root/'references/guizang-original-skill.md').read_text(encoding='utf-8')
parts=original.split('---',2)
body=parts[2].lstrip('\n') if len(parts)==3 else original
body_missing = body not in active
required=[
 'references/academic-overlay.md','references/academic-content-mapping.md','references/brand-overlay.md','references/brand-profile.md',
 'references/brands/ki.json','references/brands/ki-swiss.json','references/brands/ki-editorial.json','references/ki-templates.md',
 'assets/template-ki-swiss.html','assets/template-ki-editorial.html','assets/brands/ki-logo-white.png','assets/brands/ki-logo-accent.png',
 'references/scientific-fidelity.md','references/scientific-figures-tables.md','references/figure-generation-whitelist.md','references/narrative-patterns.md',
 'references/pptx-fidelity.md','references/deck-spec.md','references/quality-checklist.md',
 'scripts/inspect-brand-template.py','scripts/apply-brand-profile.py','scripts/check-brand-token-lock.py','scripts/check-ki-template-lock.py',
 'scripts/finalize-pptx.py','scripts/capture-guizang-visual-plates.py','scripts/check-visual-plate-fidelity.py',
 'scripts/render-academic-pptx.mjs','scripts/check-academic-pptx-hybrid.py','scripts/check-pptx-layout-integrity.py','scripts/check-ki-pptx-palette.py'
]
academic_missing=[x for x in required if not (root/x).is_file()]
print(f'Guizang base: {len(manifest["files"])} files; missing={len(missing)} changed={len(changed)} active_body_missing={int(body_missing)} academic_missing={len(academic_missing)}')
if missing:
 print('MISSING:'); print('\n'.join(missing))
if changed:
 print('CHANGED:'); print('\n'.join(changed))
if body_missing: print('ERROR: active SKILL.md does not contain the complete original Guizang body')
if academic_missing:
 print('ACADEMIC MISSING:'); print('\n'.join(academic_missing))
sys.exit(1 if missing or changed or body_missing or academic_missing else 0)
