# Academic Overlay for Guizang

本文件是 **Guizang 原 Skill 的增量覆盖层**。先执行主 `SKILL.md` 中完整复制的 Guizang 规则，再应用这里明确列出的覆盖。没有写在这里的 Guizang 规则继续保持 P0。

## 1. 适用范围与默认选择

- Academic deck 默认使用 **Style B · Swiss**，因为其 S01-S22、数据/结构/图像版式更适合科研。
- 如果用户明确要求 Guizang Style A，允许使用；此时仍执行原 Style A 全部规则。
- 不再建立独立的 `A01-A12` 视觉版式体系。Academic 语义只用于**选择现有 Sxx**，不能成为新的 geometry source。
- 先读 `references/academic-content-mapping.md`，然后回到 `references/swiss-layout-lock.md` / `references/layouts-swiss.md` 选真实 Sxx。

## 2. Template-first 是最高设计规则

Academic 不从零设计页面。对每一页：

1. 先确定 Guizang Style 与真实 layout（Swiss 为 `S01-S22`，封面/封底为已有 cover/closing）；
2. 读取对应模板 `<style>` 与 layout 骨架；
3. 先复制/复用模板结构，再替换文案、数字、图片和科研对象；
4. 内容不适配时，先换另一个已有 layout 或拆页；
5. 只有用户明确要求“实验版式/新布局”才允许偏离原 geometry。

**禁止顺序：**先设计 academic slide → 再找一个 Sxx 来解释它。

开工前必须列：

`页码 → Guizang layout/Sxx → 选用理由 → scientific treatment → image/table slot`

不得再写 `Axx → Sxx` 双层布局代码。

## 3. Scientific fidelity

读：
- `references/scientific-fidelity.md`
- `references/scientific-figures-tables.md`
- `references/narrative-patterns.md`

核心原则：**Preserve scientific information. Reduce visual competition.**

以下内容只要源材料支持就不能为了留白而删除：n/denominator、effect estimate、CI/CrI、单位、reference line、risk table、关键 model/estimand/interaction、匹配比例、时间窗、null/contradictory result、影响解释的 sensitivity analysis。

复杂科研 visual 只能选择：`preserve / relayout / redraw / annotate / expand-zoom`。低分辨率截图无可靠数值时禁止“猜着重画”。

### Guizang 原规则的 Academic 例外

- 连续可比的 Results/evidence 页允许重复同一个 Sxx；一致性高于强制版式多样性。
- scientific figure 内已有数据编码颜色可以保留：**data colors own the figure; theme colors own the slide**。
- publication/statistical figure 默认 `contain`，不得裁 axis、legend、risk table、panel label、CI/CrI。
- 高密度不是错误；先重构层级、拆页或 overview → focus，不要自动删科学信息。

## 4. 学术内容必须直接映射 Guizang Sxx

读 `references/academic-content-mapping.md`。常用原则：

- research question / core claim → S03 / S09 / S10
- study design / cohort / registry → S17 / S11
- analysis pipeline → S11 / S15
- dense statistical specification → S21 / S16
- full scientific figure → S22
- published vs our data / two-group result → S08
- result table → S21 / S20
  - when the active preset is `ki-editorial`, keep the Style A parent layout and apply `references/ki-editorial-tables.md`; a table remains a native editable table, with header fill + white-first alternating body bands rather than a three-line or line-only treatment.
- mechanism / definition → S14 / S17
- alternative explanations → S13 / S19

这些只是**选择建议**，最终 geometry 完全服从原 Sxx。

## 5. 机构/学校模板 = Brand Overlay，不是第二套 layout

如果用户提供机构/学校/实验室 PPT、brand deck、旧模板或 logo 参考，必须读 `references/brand-overlay.md`。

默认解释：
- Guizang = design/layout/typography/spacing/geometry source；
- institutional template = logo/color/approved brand token source；
- KI is a first-class special case with two locked presets: `KI x Swiss` and `KI x Electronic Magazine`; read `references/ki-templates.md` and do not improvise a third KI visual system.
- 用户科研内容 = content source。

除非用户明确要求“沿用机构 PPT 的版式”，不得从机构 PPT 复制它的标题位置、导航、卡片、表格 geometry、默认字体层级来覆盖 Guizang。

## 6. PPTX native-first

原 Guizang `references/pptx-hybrid.md` 继续作为 inherited baseline；Academic PPTX 以 `references/pptx-fidelity.md` 与 `references/deck-spec.md` 的 **native-first override** 为准。

- 普通标题、正文、kicker、chrome、页码、表格、panel/card、hairline 与普通 slide layout 默认用 PowerPoint 原生元素；
- 不要把普通 slide text 或普通版面 rasterize 成 `visualPlate`；
- 对 scientific figure 采用白名单制，先读 `references/figure-generation-whitelist.md`：forest/effect plot、methods pipeline、study-design / conceptual / treatment-state / cohort-flow 等明确 figure 可作为一个 coherent generated/preserved image；
- 用户明确要求编辑某个**非定量解释型 figure** 时，读 `references/canva-editable-figures.md`。如果 Canva connector 可用，可把 coherent generated image 交给 Magic Layers (`image-to-design`) 生成一个可编辑 Canva companion design；PPTX 仍默认保留原始 figure image。不要把“Canva 可编辑”写成“PowerPoint 原生可编辑”，除非最终 Canva-exported PPTX 已单独检查并验证 figure 内部对象可选中编辑；
- `forest-plot` / `effect-plot`、精确坐标轴/tick、CI/CrI、risk table、KM/Love/balance 等定量证据禁止经过 Magic Layers 重构；需要 PowerPoint 全可编辑时只能 deterministic/native rebuild；
- 白名单 figure 的内部轴、CI、节点标签、结果值可以一起被确定性渲染；但 slide title、footer、page chrome、普通正文仍保持 native；
- 只有 WebGL / canvas / ASCII / complex CSS / map 等浏览器效果才使用 browser raster layer，并在 spec 里声明 `rasterPurpose`；
- 版式 geometry、字体层级、留白和比例仍然必须来自 Guizang parent layout，而不是重新设计一个“类似 Guizang”的 PowerPoint。

Academic renderer 是原 Guizang renderer 的**增量能力**，不能修改原 Guizang baseline 文件。

## 7. PPTX 可打开性是 P0

任何 renderer 直接输出只算 `deck.raw.pptx`，不得交付。

最终必须：

```bash
python <SKILL_ROOT>/scripts/finalize-pptx.py deck.raw.pptx deck.pptx --brand-profile <active-profile-id>
```

要求 ZIP/OOXML/relationships 可解析；有 office engine 时必须真实打开、重存、再解析、转 PDF/图片验证。后续任何 XML patch 都会使认证失效，必须重新 finalization。

## 8. QA 顺序

Academic 交付必须按以下顺序：

1. 原 Guizang `references/checklist.md`，按当前 family 执行 shared + Style A 或 shared + Style B/Swiss 对应条目，**不得只跑 Swiss 子集**；
2. 当前 family 的原始 validator / hybrid checker；
3. `references/quality-checklist.md` 科研保真检查；
4. 若使用浏览器 raster layer，确认它只包含声明的 browser-only effect，不含普通 slide text；
5. finalization；
6. `python <SKILL_ROOT>/scripts/check-pptx-layout-integrity.py deck.pptx`，检查真实 PPTX 的 text overlap、logo/image 拉伸、logo/text collision、越界；
7. 渲染最终 normalized PPTX 做肉眼 QA。

如果肉眼“不像 Guizang”，即使所有结构测试通过也算失败。先检查：是否真的从模板/Sxx 开始、是否自创 geometry、display typography 是否由模板保真、是否把 institution PPT 当成 layout source。

## 8. Brand profiles are mechanical overlays, not design prompts

When a user supplies an institutional template, read `references/brand-overlay.md` and `references/brand-profile.md` before making any branded slide.

- Run `scripts/inspect-brand-template.py` before selecting a palette.
- Freeze an explicit brand profile.
- Apply the profile to Guizang HTML through `scripts/apply-brand-profile.py` rather than manually recoloring components.
- Set `meta.designSource: "guizang-template"` and reuse the same `meta.brandProfile` in the PPTX deck spec.
- Run `scripts/check-brand-token-lock.py` before PPTX finalization.
- If the branded result does not read as Guizang first, treat that as a design-system regression. Do not continue free-form beautification.
