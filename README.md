# AI 時代的軟體工程：FDE 前線工程師大師班
### Software Engineering with AI: The Forward Deployed Engineer (FDE) Masterclass

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Demo-success?logo=github)](https://sinliongtoo.github.io/fde-ai-swe-masterclass/)
[![RWD Supported](https://img.shields.io/badge/Design-Responsive%20(RWD)-blue?logo=html5)](https://sinliongtoo.github.io/fde-ai-swe-masterclass/)
[![Bilingual](https://img.shields.io/badge/Language-EN%20%7C%20%E7%B9%81%E9%AB%94%E4%B8%AD%E6%96%87-purple)](https://sinliongtoo.github.io/fde-ai-swe-masterclass/)
[![Dark / Light Mode](https://img.shields.io/badge/Theme-%E2%98%80%EF%B8%8F%20%2F%20%F0%9F%8C%99%20Toggle-orange)](https://sinliongtoo.github.io/fde-ai-swe-masterclass/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **🚀 體驗線上互動應用：**  
> **[https://sinliongtoo.github.io/fde-ai-swe-masterclass/](https://sinliongtoo.github.io/fde-ai-swe-masterclass/)**

---

## 📖 專案概述 (Overview)

單純打字寫樣板代碼 (Boilerplate) 與檢查基本語法的時代已經過去。現代軟體工程師已轉化為**「系統架構編排者 (System Orchestrator)」**與**「規格定義師 (Specification Architect)」**。

本專案提供一套專為現代 AI 軟體工程打造的互動式高階架構課程與生產交付指南。協助工程師成長為頂尖的 **前線部署工程師 (Forward Deployed Engineer, FDE)** —— 能夠在企業複雜系統、Agent 代理工作流與業務商業價值的交會點上，極速交付高可靠度、可審計的企業級 AI 生產系統。

---

## 🌟 核心特性 (Key Features)

1. **📱 全方位 RWD 響應式手勢設計 (Responsive Web Design)**：
   - 支援手機（320px+）、平板到 4K 螢幕自適應排版。
   - 導覽分頁支援原生慣性橫向滑動 (`scroll-touch`) 與切換自動平滑置中 (`scrollIntoView`)。
   - 代碼區塊、對比表格均具備防擠壓與滑動優化。
2. **🌐 即時雙語切換 (Bilingual Support)**：
   - 一鍵切換 **英文 (EN)** 與 **繁體中文 (ZH)**。
   - 內建輕量獨立的 `i18nData` 字典，所有標題、卡片、架構流程與實戰防禦機制無縫切換。
3. **☀️ / 🌙 深淺雙色模式 (Dark / Light Mode)**：
   - 支援原生 CSS 變數主題切換，獨立於 iframe 宿主環境，在所有瀏覽器均能穩定運行。
4. **📦 原生 Antigravity 技能化封裝 (Agent Skill Integration)**：
   - 內建符合規範的 `.agents/skills/fde-ai-swe/SKILL.md`，可直接供 Antigravity、Claude Code 等自主代理人作為專家知識庫調用。

---

## 🏛️ 6 大核心模組架構 (Curriculum Modules)

| 模組 | 內容重點 | 核心交付價值 |
| :--- | :--- | :--- |
| **1. 角色核心與定位** | FDE 能力金字塔 (40/35/25 法則)、傳統 SWE vs 解決方案架構師 vs FDE 對比矩陣 | 建立從後台手寫代碼轉型至業務一線系統編排者的全景認知 |
| **2. 現代 AI 工具鏈矩陣** | AI 原生 IDE、Agent 編排框架、DSPy 自動 Prompt 編譯、向量資料庫、可觀測性與安全護欄 | 掌握全棧 5 層 AI 原生開發利器 |
| **3. 權威認證與學習路徑** | 高投報率雲端架構認證 (AWS/Databricks/GCP)、必修經典經典著作、90 天轉型互動式檢查清單 | 擺脫表面快餐證書，建立高權威說服力的端到端實戰資歷 |
| **4. 五階段生產交付手冊** | 45 天從業務調研、黃金基準、極速 PoC、評測加固到生產叢集上線交接之標準 SOP | 提供企業客戶最看重的系統化可靠交付流程 |
| **5. 就緒度能力評估** | 5 大維度自我檢測測驗，即時量化計分並給予專屬突破方向指南 | 診斷目前實力並獲得具體的技術成長優先順序 |
| **6. 生產級架構與代碼庫** | **5 大企業級硬核架構藍圖**，附帶執行流程、SLA 保證、帶註解的生產代碼與實戰防禦血淚史 | 包含 Pydantic v2、LangGraph、pgvector HNSW、Ragas CI Gate 與 SKILL.md 模板 |

---

## 💻 5 大硬核生產架構藍圖 (Production Blueprints)

### 1. 規格驅動開發與強型別合約 (Spec-Driven Dev)
- **技術**：`Pydantic v2` + `Instructor` + 有限狀態機 (FSM) 語法遮罩解碼 (Grammar Masking)。
- **價值**：在 Token 取樣階段強制符號閉合，配合 Traceback 自我修復，將 Schema 解析失敗率從 4.8% 降至 **0.00%**。

### 2. 循環狀態機代理架構 (LangGraph Cyclical State Machine)
- **技術**：集中式型別狀態 (Typed State) + PostgreSQL ACID 快照 (Checkpointing) + 人工審批門禁 (HITL)。
- **價值**：告別脆弱易斷的線性 DAG，為寫入/變更操作建立狀態持久化與安全暫停機制。

### 3. 企業級兩階段混合檢索管線 (Hybrid RAG: HNSW + BM25 + RRF)
- **技術**：PostgreSQL `pgvector` HNSW 向量索引 ($m=16, ef=64$) + GIN 全文檢索 + 互惠排名融合 ($RRF(k=60)$) + Cross-Encoder 重排序。
- **價值**：兼顧語義理解與精確料號/合約編號匹配，Recall@5 躍升至 **94.2%**，延遲低於 85ms。

### 4. CI/CD 自動化評測守門員 (Continuous Evals Harness)
- **技術**：`Ragas` / `LangSmith` 黃金標準評測集 + GitHub Actions 自動化門禁。
- **價值**：告別憑感覺測試 (Vibe Checking)，強制每次 PR 必須滿足真實性 $F \ge 0.92$ 與召回率 $\ge 0.90$ 始得合併。

### 5. Agent 技能架構與漸進式揭露 (SKILL.md & CLI Pattern)
- **技術**：YAML 元資料索引 + 漸進式揭露 (Progressive Disclosure) + `uv run` 隔離環境 + 跨行程文件鎖 (`fcntl.flock`)。
- **價值**：杜絕將 50 頁 SOP 塞入 System Prompt 造成的注意力退化與 Token 浪費，縮減 **95%+ 上下文** 並確保執行確定性。

---

## 📂 專案結構 (Repository Structure)

```text
├── index.html                   # GitHub Pages 入口網頁 (完整 RWD 互動應用)
├── fde_ai_swe_tutorial.html     # 原始大師班教學應用檔案
├── GEMINI.md                    # Antigravity 專案指導原則與 UI 標準
├── .agents/
│   └── skills/
│       └── fde-ai-swe/
│           └── SKILL.md         # 原生 Antigravity Agent Skill 規範檔
├── .gitignore                   # Git 忽略設定
└── README.md                    # 專案說明文件
```

---

## 🚀 本地開發與預覽 (Local Development)

本專案無需任何複雜建置步驟，純靜態無依賴設計，即開即用：

```bash
# 複製儲存庫
git clone https://github.com/SinLiongToo/fde-ai-swe-masterclass.git
cd fde-ai-swe-masterclass

# 使用任何靜態伺服器啟動（例如 Python 或 Node.js）
python -m http.server 8000
# 或
npx serve .
```

開啟瀏覽器造訪 `http://localhost:8000` 即可進行本地除錯與預覽。

---

## 📄 授權條款 (License)

本專案採用 [MIT License](LICENSE) 授權開放。
