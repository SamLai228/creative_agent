const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "EDM 素材工廠 - AI 驅動行銷內容自動化";

// ─── 色彩系統 ───────────────────────────────────────
const C = {
  deepBlue:   "065A82",
  teal:       "1C7293",
  tealLight:  "21B5D8",
  navy:       "021E2E",
  white:      "FFFFFF",
  offWhite:   "F0F7FB",
  lightGray:  "E8F4FA",
  muted:      "89C0D8",
  accent:     "F4B942",   // amber accent
  accentDark: "E0991A",
  darkText:   "0D2B3E",
  bodyText:   "1A4A65",
};

// ─── 字體 ─────────────────────────────────────────
const FONT_TITLE  = "Georgia";
const FONT_BODY   = "Calibri";

// ─── helper: 深色底共用 header bar ────────────────
function addDarkHeader(slide, title, subtitle) {
  // 深色頂部橫條
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.15,
    fill: { color: C.navy },
    line: { color: C.navy },
  });
  // 左側 teal 裝飾線
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.12, h: 1.15,
    fill: { color: C.tealLight },
    line: { color: C.tealLight },
  });
  // 標題
  slide.addText(title, {
    x: 0.28, y: 0.18, w: 7.5, h: 0.5,
    fontFace: FONT_TITLE, fontSize: 22, bold: true,
    color: C.white, margin: 0,
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.28, y: 0.65, w: 7, h: 0.35,
      fontFace: FONT_BODY, fontSize: 13, color: C.muted, margin: 0,
    });
  }
}

// ─── helper: 小 tag chip ──────────────────────────
function addTag(slide, label, x, y) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w: label.length * 0.125 + 0.3, h: 0.3,
    fill: { color: C.teal, transparency: 15 },
    line: { color: C.tealLight },
    rectRadius: 0.08,
  });
  slide.addText(label, {
    x: x + 0.04, y: y + 0.02,
    w: label.length * 0.125 + 0.22, h: 0.26,
    fontFace: FONT_BODY, fontSize: 10, color: C.white,
    align: "center", margin: 0,
  });
}

// ─── helper: feature card ─────────────────────────
function addFeatureCard(slide, emoji, title, body, x, y, w = 2.1, h = 1.65) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: C.white },
    line: { color: C.lightGray, width: 1.2 },
    shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 135, opacity: 0.08 },
  });
  // top teal accent bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h: 0.055,
    fill: { color: C.teal },
    line: { color: C.teal },
  });
  slide.addText(emoji, {
    x: x + 0.15, y: y + 0.12, w: 0.5, h: 0.45,
    fontFace: FONT_BODY, fontSize: 24, margin: 0,
  });
  slide.addText(title, {
    x: x + 0.15, y: y + 0.55, w: w - 0.3, h: 0.32,
    fontFace: FONT_BODY, fontSize: 12, bold: true,
    color: C.deepBlue, margin: 0,
  });
  slide.addText(body, {
    x: x + 0.15, y: y + 0.88, w: w - 0.3, h: h - 1.05,
    fontFace: FONT_BODY, fontSize: 10, color: C.bodyText,
    margin: 0, wrap: true,
  });
}

// ─── helper: step box ────────────────────────────
function addStep(slide, num, label, desc, x, y) {
  const W = 1.6, H = 1.3;
  // circle
  slide.addShape(pres.shapes.OVAL, {
    x: x + 0.55, y, w: 0.5, h: 0.5,
    fill: { color: C.teal }, line: { color: C.tealLight },
  });
  slide.addText(String(num), {
    x: x + 0.55, y: y + 0.06, w: 0.5, h: 0.4,
    fontFace: FONT_BODY, fontSize: 16, bold: true,
    color: C.white, align: "center", margin: 0,
  });
  slide.addText(label, {
    x, y: y + 0.55, w: W, h: 0.3,
    fontFace: FONT_BODY, fontSize: 11, bold: true,
    color: C.deepBlue, align: "center", margin: 0,
  });
  slide.addText(desc, {
    x, y: y + 0.85, w: W, h: 0.45,
    fontFace: FONT_BODY, fontSize: 9.5, color: C.bodyText,
    align: "center", margin: 0, wrap: true,
  });
}

// ─── helper: arrow between steps ─────────────────
function addArrow(slide, x, y) {
  slide.addShape(pres.shapes.LINE, {
    x, y: y + 0.22, w: 0.4, h: 0,
    line: { color: C.teal, width: 2 },
  });
  // arrowhead triangle (manual)
  slide.addShape(pres.shapes.LINE, {
    x: x + 0.35, y: y + 0.12, w: 0.12, h: 0.2,
    line: { color: C.teal, width: 2 },
  });
  slide.addShape(pres.shapes.LINE, {
    x: x + 0.35, y: y + 0.32, w: 0.12, h: -0.2,
    line: { color: C.teal, width: 2 },
  });
}

// ════════════════════════════════════════════════════
// Slide 1 — 封面
// ════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  // 右側 teal 幾何裝飾塊
  s.addShape(pres.shapes.RECTANGLE, {
    x: 7.2, y: 0, w: 2.8, h: 5.625,
    fill: { color: C.deepBlue }, line: { color: C.deepBlue },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 8.5, y: 0, w: 1.5, h: 5.625,
    fill: { color: C.teal, transparency: 30 }, line: { color: C.teal },
  });
  // 橫向 accent 線
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 2.7, w: 5.8, h: 0.05,
    fill: { color: C.tealLight }, line: { color: C.tealLight },
  });

  // 主標題
  s.addText("EDM 素材工廠", {
    x: 0.6, y: 0.9, w: 6.5, h: 1.0,
    fontFace: FONT_TITLE, fontSize: 46, bold: true,
    color: C.white, margin: 0,
  });
  // 副標題
  s.addText("AI 驅動的行銷 EDM 內容自動化平台", {
    x: 0.6, y: 1.9, w: 6.5, h: 0.6,
    fontFace: FONT_BODY, fontSize: 20, color: C.muted, margin: 0,
  });
  // tag chips
  addTag(s, "OpenAI GPT-4o Vision", 0.6, 2.85);
  addTag(s, "FastAPI", 3.1, 2.85);
  addTag(s, "React", 3.9, 2.85);

  // bottom bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 4.9, w: 10, h: 0.73,
    fill: { color: C.deepBlue }, line: { color: C.deepBlue },
  });
  s.addText("Creative Agent  ·  2026", {
    x: 0.6, y: 4.95, w: 8.5, h: 0.5,
    fontFace: FONT_BODY, fontSize: 12, color: C.muted, margin: 0,
  });
}

// ════════════════════════════════════════════════════
// Slide 2 — 問題背景
// ════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };
  addDarkHeader(s, "傳統 EDM 製作的痛點", "為什麼需要自動化？");

  const pains = [
    { icon: "⏱️", title: "耗時的手動流程", body: "設計師需逐一挑選素材、撰寫文案、調整排版，一份 EDM 往往需要數小時。" },
    { icon: "🔍", title: "素材難以搜尋", body: "素材庫缺乏語義標籤，找一張合適的圖要翻遍整個資料夾。" },
    { icon: "✍️", title: "文案難以把控字數", body: "不同版面的文字區域大小各異，文案常常超出邊框或留白過多。" },
    { icon: "🔄", title: "修改成本高", body: "每次調整都需要回到設計軟體重新輸出，溝通與迭代成本高。" },
  ];

  pains.forEach((p, i) => {
    const x = 0.45 + i * 2.3;
    addFeatureCard(s, p.icon, p.title, p.body, x, 1.4, 2.1, 1.8);
  });

  // bottom quote
  s.addShape(pres.shapes.RECTANGLE, {
    x: 1.5, y: 3.45, w: 7, h: 0.8,
    fill: { color: C.teal, transparency: 88 },
    line: { color: C.teal, width: 1 },
  });
  s.addText("EDM 素材工廠的目標：讓行銷人員 10 分鐘內生成一份高品質 EDM", {
    x: 1.65, y: 3.55, w: 6.7, h: 0.6,
    fontFace: FONT_BODY, fontSize: 13, italic: true,
    color: C.deepBlue, align: "center", margin: 0,
  });
}

// ════════════════════════════════════════════════════
// Slide 3 — 系統架構總覽
// ════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };
  addDarkHeader(s, "系統架構總覽", "兩階段 AI Pipeline");

  // Phase 1 box
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.35, w: 4.2, h: 3.6,
    fill: { color: C.white },
    line: { color: C.teal, width: 1.5 },
    shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 135, opacity: 0.07 },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.35, w: 4.2, h: 0.42,
    fill: { color: C.teal }, line: { color: C.teal },
  });
  s.addText("Phase 1  ·  Material Factory", {
    x: 0.55, y: 1.38, w: 3.9, h: 0.35,
    fontFace: FONT_BODY, fontSize: 12, bold: true,
    color: C.white, margin: 0,
  });

  const steps1 = [
    ["📤", "上傳圖片素材"],
    ["🤖", "Vision API 智能貼標"],
    ["🏷️", "多維度標籤存儲"],
    ["🔍", "語義搜尋素材"],
  ];
  steps1.forEach(([icon, label], i) => {
    const y = 1.95 + i * 0.68;
    s.addShape(pres.shapes.OVAL, {
      x: 0.65, y: y - 0.02, w: 0.32, h: 0.32,
      fill: { color: C.teal, transparency: 75 }, line: { color: C.teal },
    });
    s.addText(icon, { x: 0.66, y: y - 0.01, w: 0.3, h: 0.3, fontFace: FONT_BODY, fontSize: 14, margin: 0 });
    s.addText(label, {
      x: 1.1, y: y, w: 3.2, h: 0.3,
      fontFace: FONT_BODY, fontSize: 12, color: C.darkText, margin: 0,
    });
    if (i < 3) {
      s.addShape(pres.shapes.LINE, {
        x: 0.8, y: y + 0.32, w: 0, h: 0.36,
        line: { color: C.muted, width: 1.5, dashType: "sysDash" },
      });
    }
  });

  // Phase 2 box
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.4, y: 1.35, w: 4.2, h: 3.6,
    fill: { color: C.white },
    line: { color: C.deepBlue, width: 1.5 },
    shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 135, opacity: 0.07 },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.4, y: 1.35, w: 4.2, h: 0.42,
    fill: { color: C.deepBlue }, line: { color: C.deepBlue },
  });
  s.addText("Phase 2  ·  EDM Generator", {
    x: 5.55, y: 1.38, w: 3.9, h: 0.35,
    fontFace: FONT_BODY, fontSize: 12, bold: true,
    color: C.white, margin: 0,
  });

  const steps2 = [
    ["📋", "選擇 EDM 模板"],
    ["🗺️", "自動偵測文字區域"],
    ["✍️", "LLM 生成限字文案"],
    ["🖨️", "合成輸出 PNG"],
  ];
  steps2.forEach(([icon, label], i) => {
    const y = 1.95 + i * 0.68;
    s.addShape(pres.shapes.OVAL, {
      x: 5.65, y: y - 0.02, w: 0.32, h: 0.32,
      fill: { color: C.deepBlue, transparency: 75 }, line: { color: C.deepBlue },
    });
    s.addText(icon, { x: 5.66, y: y - 0.01, w: 0.3, h: 0.3, fontFace: FONT_BODY, fontSize: 14, margin: 0 });
    s.addText(label, {
      x: 6.1, y: y, w: 3.2, h: 0.3,
      fontFace: FONT_BODY, fontSize: 12, color: C.darkText, margin: 0,
    });
    if (i < 3) {
      s.addShape(pres.shapes.LINE, {
        x: 5.8, y: y + 0.32, w: 0, h: 0.36,
        line: { color: C.muted, width: 1.5, dashType: "sysDash" },
      });
    }
  });

  // 中間連接箭頭
  s.addShape(pres.shapes.LINE, {
    x: 4.65, y: 3.1, w: 0.7, h: 0,
    line: { color: C.accentDark, width: 2.5 },
  });
  s.addShape(pres.shapes.LINE, { x: 5.25, y: 2.95, w: 0.18, h: 0.18, line: { color: C.accentDark, width: 2.5 } });
  s.addShape(pres.shapes.LINE, { x: 5.25, y: 3.13, w: 0.18, h: -0.18, line: { color: C.accentDark, width: 2.5 } });

  s.addText("素材搜尋", {
    x: 4.56, y: 3.18, w: 0.88, h: 0.22,
    fontFace: FONT_BODY, fontSize: 8.5, color: C.accentDark, align: "center", margin: 0,
  });
}

// ════════════════════════════════════════════════════
// Slide 4 — Material Factory 深入
// ════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };
  addDarkHeader(s, "Phase 1：Material Factory", "圖片上傳 → AI 貼標 → 語義搜尋");

  // 左側：標籤維度說明
  s.addText("六大標籤維度", {
    x: 0.4, y: 1.4, w: 4.5, h: 0.38,
    fontFace: FONT_BODY, fontSize: 14, bold: true, color: C.deepBlue, margin: 0,
  });

  const dims = [
    ["類型 (Category)", "人物、背景、裝飾、物件…"],
    ["風格 (Style)",    "現代、傳統、插畫、寫實…"],
    ["情境 (Scenario)", "家庭、職場、度假、慶典…"],
    ["色系 (Color)",    "暖色、冷色、中性、高對比…"],
    ["氛圍 (Mood)",     "溫暖、專業、歡快、沉穩…"],
    ["關鍵字",           "自由文本，LLM 自動提取"],
  ];
  dims.forEach(([name, desc], i) => {
    const y = 1.88 + i * 0.5;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.4, y: y, w: 0.08, h: 0.3,
      fill: { color: C.teal }, line: { color: C.teal },
    });
    s.addText(name, {
      x: 0.6, y: y, w: 1.8, h: 0.3,
      fontFace: FONT_BODY, fontSize: 11, bold: true,
      color: C.deepBlue, margin: 0,
    });
    s.addText(desc, {
      x: 2.45, y: y, w: 2.3, h: 0.3,
      fontFace: FONT_BODY, fontSize: 11, color: C.bodyText, margin: 0,
    });
  });

  // 右側：技術流程卡
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 1.35, w: 4.4, h: 3.9,
    fill: { color: C.white },
    line: { color: C.lightGray, width: 1 },
    shadow: { type: "outer", color: "000000", blur: 10, offset: 3, angle: 135, opacity: 0.08 },
  });
  s.addText("技術實作", {
    x: 5.4, y: 1.5, w: 4.0, h: 0.35,
    fontFace: FONT_BODY, fontSize: 13, bold: true, color: C.deepBlue, margin: 0,
  });

  const techs = [
    ["image_analyzer.py", "Base64 編碼、色調分析"],
    ["llm_tagger.py",     "呼叫 GPT-4o Vision API"],
    ["tag_database.py",   "JSON 標籤庫讀寫"],
    ["factory.py",        "整合流程主入口"],
    ["/api/materials",    "REST API（上傳/搜尋/刪除）"],
  ];
  techs.forEach(([file, desc], i) => {
    const y = 1.98 + i * 0.62;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 5.4, y: y, w: 3.9, h: 0.5,
      fill: { color: i % 2 === 0 ? C.lightGray : C.white },
      line: { color: C.lightGray },
    });
    s.addText(file, {
      x: 5.55, y: y + 0.05, w: 1.8, h: 0.22,
      fontFace: "Consolas", fontSize: 9.5, bold: true,
      color: C.teal, margin: 0,
    });
    s.addText(desc, {
      x: 5.55, y: y + 0.24, w: 3.5, h: 0.2,
      fontFace: FONT_BODY, fontSize: 9.5, color: C.bodyText, margin: 0,
    });
  });
}

// ════════════════════════════════════════════════════
// Slide 5 — EDM Generator 深入
// ════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };
  addDarkHeader(s, "Phase 2：EDM Generator", "模板 + AI 文案 + 精確排版");

  // 上方：三欄特色
  const features = [
    {
      icon: "🗺️",
      title: "Region 自動偵測",
      body: "從含文字的完稿圖 (reference) 精確提取每個文字區域的位置與大小，準確度 >95%",
    },
    {
      icon: "✍️",
      title: "Template-Aware 文案",
      body: "根據區域尺寸自動計算字數上限，LLM 為每個區域單獨生成，不溢框不留白",
    },
    {
      icon: "🖌️",
      title: "交互式前端編輯",
      body: "React 畫布即時預覽，支援拖移、字型調整、描邊/陰影特效，最終輸出高品質 PNG",
    },
  ];
  features.forEach((f, i) => {
    addFeatureCard(s, f.icon, f.title, f.body, 0.38 + i * 3.15, 1.35, 2.85, 2.0);
  });

  // 下方：字數計算公式 highlight
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.38, y: 3.55, w: 9.24, h: 1.55,
    fill: { color: C.navy }, line: { color: C.teal, width: 1.2 },
  });
  s.addText("核心演算法：精確字數計算", {
    x: 0.6, y: 3.65, w: 5, h: 0.3,
    fontFace: FONT_BODY, fontSize: 12, bold: true, color: C.tealLight, margin: 0,
  });
  s.addText(
    "chars_per_line = int(width / (font_size × 1.2))\n" +
    "max_lines      = int(height / (font_size + 10))\n" +
    "max_chars      = chars_per_line × max_lines",
    {
      x: 0.6, y: 3.97, w: 5.2, h: 1.0,
      fontFace: "Consolas", fontSize: 10, color: C.white, margin: 0,
    }
  );
  s.addText(
    "每個 region 獨立計算\n防止文字溢出邊框\nLLM prompt 嚴格遵守上限",
    {
      x: 6.0, y: 3.68, w: 3.4, h: 1.1,
      fontFace: FONT_BODY, fontSize: 11, color: C.muted, margin: 0,
    }
  );
}

// ════════════════════════════════════════════════════
// Slide 6 — 技術棧
// ════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };
  addDarkHeader(s, "技術棧", "Backend · Frontend · AI");

  // 三欄：Backend / Frontend / AI
  const stacks = [
    {
      title: "Backend",
      color: C.deepBlue,
      items: [
        "Python 3.10+",
        "FastAPI + Uvicorn",
        "Pydantic 資料驗證",
        "Pillow 圖像合成",
        "JSON 輕量資料庫",
      ],
    },
    {
      title: "Frontend",
      color: C.teal,
      items: [
        "React 18+",
        "Vite 開發工具",
        "Axios API 客戶端",
        "CSS3 Flexbox/Grid",
        "Vite Proxy 轉發",
      ],
    },
    {
      title: "AI / LLM",
      color: C.accentDark,
      items: [
        "OpenAI GPT-4o",
        "Vision API 圖像分析",
        "結構化 JSON 輸出",
        "Prompt Engineering",
        "字數約束生成",
      ],
    },
  ];

  stacks.forEach((st, col) => {
    const x = 0.38 + col * 3.15;
    // header
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.35, w: 2.95, h: 0.45,
      fill: { color: st.color }, line: { color: st.color },
    });
    s.addText(st.title, {
      x: x + 0.1, y: 1.38, w: 2.75, h: 0.38,
      fontFace: FONT_BODY, fontSize: 14, bold: true,
      color: C.white, margin: 0,
    });
    // items
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.8, w: 2.95, h: 3.2,
      fill: { color: C.white }, line: { color: C.lightGray },
      shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.07 },
    });
    s.addText(
      st.items.map(item => ({ text: item, options: { bullet: true, breakLine: true } })).slice(0, -1)
        .concat([{ text: st.items[st.items.length - 1], options: { bullet: true } }]),
      {
        x: x + 0.15, y: 1.92, w: 2.65, h: 2.85,
        fontFace: FONT_BODY, fontSize: 12, color: C.darkText, margin: 0,
      }
    );
  });
}

// ════════════════════════════════════════════════════
// Slide 7 — 使用流程 Step-by-Step
// ════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };
  addDarkHeader(s, "使用者操作流程", "從素材到完稿 EDM 的完整步驟");

  const steps = [
    { n: 1, label: "上傳素材",   desc: "拖拉圖片上傳，系統自動貼上 AI 標籤" },
    { n: 2, label: "選模板",     desc: "從模板庫選擇 EDM 版型" },
    { n: 3, label: "填寫需求",   desc: "輸入產品名稱、主軸訴求、目標受眾" },
    { n: 4, label: "AI 生成",    desc: "LLM 一鍵生成各區域文案" },
    { n: 5, label: "互動調整",   desc: "在畫布上直接編輯文字與樣式" },
    { n: 6, label: "下載輸出",   desc: "輸出高解析度 PNG 直接投放" },
  ];

  const totalW = 9.2;
  const stepW = 1.6;
  const gapW = (totalW - steps.length * stepW) / (steps.length - 1);
  const startX = 0.4;

  steps.forEach((st, i) => {
    const x = startX + i * (stepW + gapW);
    addStep(s, st.n, st.label, st.desc, x, 1.55);
    // arrow
    if (i < steps.length - 1) {
      addArrow(s, x + stepW, 1.77);
    }
  });

  // bottom info bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 3.35, w: 9.2, h: 1.85,
    fill: { color: C.white }, line: { color: C.lightGray },
    shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.06 },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 3.35, w: 0.1, h: 1.85,
    fill: { color: C.teal }, line: { color: C.teal },
  });
  s.addText("整體時間目標：10 分鐘內完成一份 EDM", {
    x: 0.65, y: 3.45, w: 8.6, h: 0.35,
    fontFace: FONT_BODY, fontSize: 13, bold: true, color: C.deepBlue, margin: 0,
  });
  s.addText(
    "傳統流程（手動）：2～4 小時  →  EDM 素材工廠：10 分鐘以內\n" +
    "素材搜尋：從「翻資料夾」變成「語義關鍵字搜尋」\n" +
    "文案排版：告別手動調整字數，AI 自動控制每個區域",
    {
      x: 0.65, y: 3.85, w: 8.6, h: 1.2,
      fontFace: FONT_BODY, fontSize: 11, color: C.bodyText, margin: 0,
    }
  );
}

// ════════════════════════════════════════════════════
// Slide 8 — API 端點 & 目錄結構
// ════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };
  addDarkHeader(s, "API 設計 & 專案結構", "REST Endpoints · 目錄佈局");

  // 左：重要 API endpoints
  s.addText("核心 API Endpoints", {
    x: 0.4, y: 1.42, w: 4.5, h: 0.32,
    fontFace: FONT_BODY, fontSize: 13, bold: true, color: C.deepBlue, margin: 0,
  });

  const apis = [
    ["POST", "/api/materials/upload",                    "上傳圖片素材"],
    ["POST", "/api/materials/tag",                       "AI 自動貼標"],
    ["POST", "/api/materials/search",                    "多維度語義搜尋"],
    ["POST", "/api/generation/detect-regions",           "偵測模板文字區域"],
    ["POST", "/api/generation/generate-copy-for-template", "Template-aware 文案生成"],
    ["POST", "/api/generation/render-with-copy",         "合成輸出 PNG"],
  ];
  apis.forEach(([method, path, desc], i) => {
    const y = 1.82 + i * 0.56;
    const methodColor = method === "POST" ? C.teal : C.deepBlue;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.4, y, w: 0.72, h: 0.27,
      fill: { color: methodColor }, line: { color: methodColor },
    });
    s.addText(method, {
      x: 0.4, y: y + 0.03, w: 0.72, h: 0.22,
      fontFace: "Consolas", fontSize: 9, bold: true,
      color: C.white, align: "center", margin: 0,
    });
    s.addText(path, {
      x: 1.2, y, w: 3.4, h: 0.27,
      fontFace: "Consolas", fontSize: 8.5, color: C.deepBlue, margin: 0,
    });
    s.addText(desc, {
      x: 1.2, y: y + 0.26, w: 3.4, h: 0.22,
      fontFace: FONT_BODY, fontSize: 9.5, color: C.bodyText, margin: 0,
    });
  });

  // 右：目錄結構（code block 風格）
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.1, y: 1.35, w: 4.5, h: 3.95,
    fill: { color: C.navy }, line: { color: C.teal, width: 1 },
  });
  s.addText("專案目錄結構", {
    x: 5.3, y: 1.45, w: 4.1, h: 0.3,
    fontFace: FONT_BODY, fontSize: 11, bold: true, color: C.tealLight, margin: 0,
  });
  s.addText(
    "creative_agent/\n" +
    "├── api/routes/         # REST API\n" +
    "│   ├── materials.py\n" +
    "│   └── generation.py\n" +
    "├── src/\n" +
    "│   ├── material_factory/  # 素材工廠\n" +
    "│   └── generator/         # EDM 生成器\n" +
    "├── frontend/src/       # React UI\n" +
    "├── templates/\n" +
    "│   ├── images/         # 空白模板\n" +
    "│   ├── references/     # 完稿參考圖\n" +
    "│   └── configs/        # 區域配置 JSON\n" +
    "├── assets/             # 素材圖庫\n" +
    "└── output/edm/         # 生成結果",
    {
      x: 5.25, y: 1.82, w: 4.2, h: 3.3,
      fontFace: "Consolas", fontSize: 8.5, color: C.white, margin: 0,
    }
  );
}

// ════════════════════════════════════════════════════
// Slide 9 — 結語 / 未來規劃
// ════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  // 幾何裝飾
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.25, h: 5.625,
    fill: { color: C.tealLight }, line: { color: C.tealLight },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.25, y: 0, w: 0.1, h: 5.625,
    fill: { color: C.teal, transparency: 40 }, line: { color: C.teal },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 4.7, w: 10, h: 0.925,
    fill: { color: C.deepBlue }, line: { color: C.deepBlue },
  });

  s.addText("現況成果", {
    x: 0.7, y: 0.45, w: 5, h: 0.42,
    fontFace: FONT_TITLE, fontSize: 20, bold: true, color: C.tealLight, margin: 0,
  });

  const achievements = [
    "✅  Material Factory 完整運作（上傳 / 貼標 / 搜尋）",
    "✅  Template 區域自動偵測（from reference）",
    "✅  Template-aware 限字文案生成",
    "✅  交互式前端編輯畫布",
    "✅  文字描邊 / 陰影特效支援",
  ];
  s.addText(
    achievements.map((a, i) => ({
      text: a,
      options: { breakLine: i < achievements.length - 1 },
    })),
    {
      x: 0.7, y: 0.95, w: 5.5, h: 2.5,
      fontFace: FONT_BODY, fontSize: 12.5, color: C.white, margin: 0,
    }
  );

  // 右側：未來規劃
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.5, y: 0.35, w: 3.1, h: 4.1,
    fill: { color: C.deepBlue, transparency: 30 },
    line: { color: C.teal, width: 1 },
  });
  s.addText("未來規劃", {
    x: 6.65, y: 0.48, w: 2.8, h: 0.35,
    fontFace: FONT_BODY, fontSize: 13, bold: true, color: C.accent, margin: 0,
  });
  const roadmap = [
    "🔜  多模板批量生成",
    "🔜  素材推薦 RAG 搜尋",
    "🔜  A/B 文案變體生成",
    "🔜  HTML EDM 輸出格式",
    "🔜  品牌風格設定檔",
  ];
  s.addText(
    roadmap.map((r, i) => ({
      text: r,
      options: { breakLine: i < roadmap.length - 1 },
    })),
    {
      x: 6.65, y: 0.92, w: 2.8, h: 2.8,
      fontFace: FONT_BODY, fontSize: 11.5, color: C.muted, margin: 0,
    }
  );

  // bottom
  s.addText("EDM 素材工廠  ·  2026  ·  Creative Agent", {
    x: 0.7, y: 4.78, w: 8.5, h: 0.38,
    fontFace: FONT_BODY, fontSize: 11, color: C.muted, align: "center", margin: 0,
  });
}

// ════════════════════════════════════════════════════
// 輸出
// ════════════════════════════════════════════════════
pres.writeFile({ fileName: "edm_presentation.pptx" })
  .then(() => console.log("✅ 已輸出：edm_presentation.pptx"))
  .catch(err => { console.error("❌ 失敗：", err); process.exit(1); });
