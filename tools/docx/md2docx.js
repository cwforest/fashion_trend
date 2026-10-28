// 체크리스트 마크다운 → docx. 기존 docs/word/*.docx 와 같은 결(맑은 고딕 + Consolas)로 맞춘다.
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  VerticalAlign, LevelFormat,
} = require("docx");

const [, , SRC, OUT] = process.argv;
const KO = { ascii: "맑은 고딕", eastAsia: "맑은 고딕", hAnsi: "맑은 고딕" };
const MONO = { ascii: "Consolas", eastAsia: "맑은 고딕", hAnsi: "Consolas" };

const INK = "1A1A1A", NAVY = "1F3864", RULE = "C9D2E0", HEADFILL = "EDF1F7", GRAY = "6B7280";
const thin = (c = RULE) => ({ style: BorderStyle.SINGLE, size: 2, color: c });
const BOX = { top: thin(), bottom: thin(), left: thin(), right: thin() };

// **굵게** · `코드` 를 런으로 쪼갠다
function runs(text, base = {}, inherit = false) {
  text = text.replace(/\[([^\]]+)\]\([^)]*\)/g, "$1");   // [글자](링크) → 글자
  const F = inherit ? {} : { font: KO, size: 20, color: INK };
  const M = inherit ? { font: MONO } : { font: MONO, size: 18, color: NAVY };
  const out = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last)
      out.push(new TextRun({ text: text.slice(last, m.index), ...F, ...base }));
    const tok = m[0];
    if (tok.startsWith("**"))
      out.push(new TextRun({ text: tok.slice(2, -2).replace(/`/g, ""), ...F, bold: true, ...base }));
    else
      out.push(new TextRun({ text: tok.slice(1, -1), ...M, ...base }));
    last = m.index + tok.length;
  }
  if (last < text.length)
    out.push(new TextRun({ text: text.slice(last), ...F, ...base }));
  return out.length ? out : [new TextRun({ text: "", ...F })];
}

const CONTENT = 9638;  // A4 − 좌우여백 1134×2

function table(rows) {
  const n = Math.max(...rows.map((r) => r.length));
  const widths = Array.from({ length: n }, () => Math.floor(CONTENT / n));
  widths[0] += CONTENT - widths.reduce((a, b) => a + b, 0);
  return new Table({
    columnWidths: widths,
    indent: { size: 0, type: WidthType.DXA },
    width: { size: CONTENT, type: WidthType.DXA },
    rows: rows.map((cells, ri) =>
      new TableRow({
        tableHeader: ri === 0,
        children: Array.from({ length: n }, (_, ci) =>
          new TableCell({
            width: { size: widths[ci], type: WidthType.DXA },
            verticalAlign: VerticalAlign.CENTER,
            shading: ri === 0 ? { type: ShadingType.CLEAR, fill: HEADFILL, color: "auto" } : undefined,
            borders: BOX,
            margins: { top: 80, bottom: 80, left: 120, right: 120 },
            children: [new Paragraph({
              spacing: { before: 0, after: 0, line: 280 },
              indent: { left: 0 },
              children: runs(cells[ci] ?? "", ri === 0 ? { bold: true, color: NAVY } : {}),
            })],
          })),
      })),
  });
}


// ``` 로 감싼 블록 — 한 칸짜리 표에 담아 배경을 깔고 줄을 그대로 보존한다
function codeBlock(lines) {
  return new Table({
    columnWidths: [CONTENT],
    indent: { size: 0, type: WidthType.DXA },
    width: { size: CONTENT, type: WidthType.DXA },
    rows: [new TableRow({
      children: [new TableCell({
        width: { size: CONTENT, type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: "F5F7FA", color: "auto" },
        borders: {
          top: thin("E2E8F0"), bottom: thin("E2E8F0"),
          left: { style: BorderStyle.SINGLE, size: 12, color: RULE },
          right: thin("E2E8F0"),
        },
        margins: { top: 140, bottom: 140, left: 200, right: 140 },
        children: lines.map((l) => new Paragraph({
          spacing: { before: 0, after: 0, line: 260 },
          indent: { left: 0 },
          children: [new TextRun({ text: l || " ", font: MONO, size: 17, color: INK })],
        })),
      })],
    })],
  });
}

const md = fs.readFileSync(SRC, "utf8").split(/\r?\n/);
const body = [];
let i = 0;

const isTableRow = (l) => /^\s*\|.*\|\s*$/.test(l);
const splitRow = (l) => l.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());

while (i < md.length) {
  const line = md[i];

  if (!line.trim()) { i++; continue; }

  if (/^```/.test(line.trim())) {
    const buf = [];
    i++;
    while (i < md.length && !/^```/.test(md[i].trim())) { buf.push(md[i]); i++; }
    i++;                                   // 닫는 ``` 건너뛰기
    body.push(codeBlock(buf));
    body.push(new Paragraph({ spacing: { after: 140 }, children: [new TextRun({ text: "", size: 2 })] }));
    continue;
  }

  if (/^---+$/.test(line.trim())) {
    body.push(new Paragraph({
      spacing: { before: 160, after: 160 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: RULE } },
      children: [new TextRun({ text: "", font: KO, size: 2 })],
    }));
    i++; continue;
  }

  const h = line.match(/^(#{1,4})\s+(.*)$/);
  if (h) {
    const lvl = h[1].length;
    body.push(new Paragraph({
      heading: [HeadingLevel.TITLE, HeadingLevel.HEADING_1, HeadingLevel.HEADING_2,
                HeadingLevel.HEADING_3][lvl - 1],
      children: runs(h[2], {}, true),
    }));
    i++; continue;
  }

  if (isTableRow(line)) {
    const rows = [];
    while (i < md.length && isTableRow(md[i])) {
      const cells = splitRow(md[i]);
      if (!cells.every((c) => /^:?-{2,}:?$/.test(c))) rows.push(cells);
      i++;
    }
    body.push(table(rows));
    body.push(new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: "", size: 2 })] }));
    continue;
  }

  if (/^>\s?/.test(line)) {
    const buf = [];
    while (i < md.length && /^>\s?/.test(md[i])) { buf.push(md[i].replace(/^>\s?/, "")); i++; }
    body.push(new Paragraph({
      spacing: { before: 120, after: 120 },
      indent: { left: 280 },
      border: { left: { style: BorderStyle.SINGLE, size: 12, color: RULE, space: 10 } },
      children: runs(buf.join(" "), { color: GRAY, italics: true }),
    }));
    continue;
  }

  const b = line.match(/^\s*[-*]\s+(.*)$/);
  if (b) {
    body.push(new Paragraph({
      numbering: { reference: "bul", level: 0 },
      spacing: { before: 40, after: 40 },
      children: runs(b[1]),
    }));
    i++; continue;
  }

  body.push(new Paragraph({
    spacing: { before: 60, after: 60, line: 320 },
    children: runs(line.trim()),
  }));
  i++;
}

const doc = new Document({
  styles: {
    default: {
      document: { run: { font: KO, size: 20, color: INK },
                  paragraph: { spacing: { line: 320, after: 80 } } },
      title: { run: { font: KO, size: 32, bold: true, color: INK },
               paragraph: { spacing: { after: 200 } } },
      heading1: { run: { font: KO, size: 26, bold: true, color: NAVY },
                  paragraph: { spacing: { before: 360, after: 140 }, keepNext: true,
                               border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: RULE, space: 6 } } } },
      heading2: { run: { font: KO, size: 23, bold: true, color: NAVY },
                  paragraph: { spacing: { before: 300, after: 120 }, keepNext: true } },
      heading3: { run: { font: KO, size: 21, bold: true, color: INK },
                  paragraph: { spacing: { before: 220, after: 100 }, keepNext: true } },
    },
  },
  numbering: {
    config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
      alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 240 } } } }] }],
  },
  sections: [{
    properties: { page: { margin: { top: 1418, bottom: 1418, left: 1134, right: 1134 } } },
    children: body,
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("written:", OUT, buf.length); });
