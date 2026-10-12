# 🛠️ AI 程式碼審查與架構規範審計助手 (AI PR Reviewer Agent)
> **專為軟體工程師設計的真實可運行實戰範例 (Real-World Practical Learning Project)**

---

## 🌟 為什麼這個範例真正適合拿來學習？

許多 AI 教程的範例往往流於**「虛擬假資料」**或**「純粹調用一次 Prompt 輸出一串 Markdown 字串」**，在真正的工程落地中無法直接使用。

本專案解決的是每個開發團隊每天都會遇到的真實痛點 —— **「自動化 Pull Request 程式碼審查、架構合規性檢查與資安漏洞修復」**。你可以直接拿它來審查你電腦裡的**任何真實 Python 檔案**！

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 AI CODE REVIEWER AGENT ARCHITECTURE PIPELINE                │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. 原始代碼輸入 ──▶ 2. AST 確定性預檢 ──▶ 3. 團隊規則檢索 ──▶ 4. LLM 語義分析 │
│   (Target File)     (ast.parse 靜態語法)   (RAG: GEMINI.md)   (Gemini/Local) │
│                                                                      │      │
│ 6. CI/CD 閘門阻擋 ◀── 5. Pydantic v2 規格契約校驗 ◀────────────────────┘      │
│    (Exit Code 0/1)    (嚴格 JSON 格式 + 防敷衍驗證器)                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 專案目錄結構

```text
practical_examples/ai_code_reviewer/
├── schemas.py              # 【契約】Pydantic v2 嚴格資料模型與防敷衍驗證器
├── ast_analyzer.py         # 【靜態】Python AST 抽象語法樹分析（免 Key 100% 確定性檢測）
├── rule_engine.py          # 【檢索】團隊架構規範 RAG 檢索引擎（讀取 Markdown 規則）
├── reviewer_agent.py       # 【編排】雙軌 Agent：支援 Google Gemini 或本機離線規則引擎
├── cli.py                  # 【介面】Rich 彩色終端報表、Unified Diff 補丁預覽與 CI/CD 狀態碼
├── test_reviewer.py        # 【測試】Pytest 單元測試與回歸驗證套件
├── samples/
│   ├── vulnerable_api.py   # 【靶場】包含 5 種真實常見資安缺陷的微服務範例
│   └── clean_api.py        # 【解答】符合企業級標準的安全乾淨實作
└── LEARNING_GUIDE.md       # 本學習指南
```

---

## 🚀 5 分鐘快速上手體驗

### 步驟 1：審查具有資安漏洞的真實靶場代碼
在終端機中執行：
```bash
python -m practical_examples.ai_code_reviewer.cli practical_examples/ai_code_reviewer/samples/vulnerable_api.py
```

你將在終端機中看到漂亮的彩色報表，精確指出：
1. **第 15 行 [SEC-002]**：硬編碼生產環境 API 金鑰（`OPENAI_API_KEY = "sk-..."`）
2. **第 22 行 [SEC-001]**：使用 f-string 拼接 SQL 造成的 SQL Injection 漏洞
3. **第 30 行 [PERF-001]**：出站 HTTP 請求缺少 `timeout` 參數（易造成執行緒耗盡）
4. **第 35 行 [SEC-003]**：危險調用 `eval()` 執行任意字串
5. **第 42 行 [ARCH-001]**：業務邏輯中未經授權的破壞性 `DROP TABLE` 操作
6. **自動修復補丁 (Unified Diff)**：提供立即可用的修正代碼！
7. **CI/CD Quality Gate**：觸發 `BLOCKED`，退出狀態碼為 `1`。

---

### 步驟 2：審查安全合規的標準範例代碼
執行乾淨範例：
```bash
python -m practical_examples.ai_code_reviewer.cli practical_examples/ai_code_reviewer/samples/clean_api.py
```
* **結果**：獲得 `100/100` 分，狀態為 `PASSED`，退出狀態碼為 `0`！

---

### 步驟 3：拿你自己的代碼來審查！
你可以傳入你專案中的任何一個 `.py` 檔案：
```bash
python -m practical_examples.ai_code_reviewer.cli path/to/your_script.py
```

---

### 步驟 4：運行自動化測試套件
驗證規格契約與檢測邏輯：
```bash
python -m pytest practical_examples/ai_code_reviewer/test_reviewer.py -v
```

---

## 🧠 核心技術逐行深度拆解（FDE 學習核心）

### 1. 為什麼要用 AST (抽象語法樹) + LLM 雙軌協同？
很多團隊犯的錯誤是：**「把整段代碼直接丟給 LLM 問有沒有 bug」**。
* **缺點**：
  * LLM 容易遺漏微小的語法細節（例如 requests 忘了設 timeout）。
  * 成本高、延遲長、且存在機率性誤報。
* **現代 FDE 做法**：
  * 使用 [`ast_analyzer.py`](file:///c:/Users/tu-hs/OneDrive/文件/2022_0308_MASA/2022-0708/Projects_antigravity/SW_ENGINNERING/practical_examples/ai_code_reviewer/ast_analyzer.py) 在本機以 100% 確定性找出 SQL 拼接、未傳 timeout、危險 eval。
  * 將 AST 掃描出的確鑿問題作為上下文，注入 Prompt 輔助 LLM。這樣 LLM 就能專注在複雜的架構邏輯推導，兩者優勢互補。

### 2. 規格契約如何防止 LLM 亂回答？([`schemas.py`](file:///c:/Users/tu-hs/OneDrive/文件/2022_0308_MASA/2022-0708/Projects_antigravity/SW_ENGINNERING/practical_examples/ai_code_reviewer/schemas.py))
在 [`CodeIssue`](file:///c:/Users/tu-hs/OneDrive/文件/2022_0308_MASA/2022-0708/Projects_antigravity/SW_ENGINNERING/practical_examples/ai_code_reviewer/schemas.py#L10) 中，我們設計了嚴格的 Pydantic 驗證：
```python
@field_validator("suggested_fix")
@classmethod
def reject_lazy_fixes(cls, v: str) -> str:
    prohibited = ["tbd", "todo", "fix later", "contact admin", "n/a"]
    for p in prohibited:
        if p in v.lower():
            raise ValueError(f"Suggested fix contains prohibited placeholder '{p}'.")
    return v
```
這就是 **Anti-Hallucination Gate (防敷衍閘門)**：只要 LLM 給出「請聯絡管理員」或「TODO 之後再修」等毫無意義的敷衍回答，Pydantic 就會在底層拋出錯誤並觸發自癒重試，保證下游系統接收到的全是具體可執行的技術建議。

### 3. 如何切換使用真正的 Google Gemini LLM？
若你有 Google AI Studio 的 Gemini API Key，只需在終端設定環境變數：

**PowerShell (Windows)**:
```powershell
$env:GEMINI_API_KEY = "你的_GEMINI_API_KEY"
python -m practical_examples.ai_code_reviewer.cli practical_examples/ai_code_reviewer/samples/vulnerable_api.py
```

**Bash / Linux / macOS**:
```bash
export GEMINI_API_KEY="你的_GEMINI_API_KEY"
python -m practical_examples.ai_code_reviewer.cli practical_examples/ai_code_reviewer/samples/vulnerable_api.py
```
此時 `reviewer_agent.py` 會自動切換為 `GEMINI_LLM` 引擎，使用 Google 官方 `google-genai` SDK 與 `gemini-2.5-flash` 進行深度語義審查！

---

## 💡 動手練習任務（給學習者的挑戰）

1. **挑戰 1 (新增資安規則)**：打開 [`ast_analyzer.py`](file:///c:/Users/tu-hs/OneDrive/文件/2022_0308_MASA/2022-0708/Projects_antigravity/SW_ENGINNERING/practical_examples/ai_code_reviewer/ast_analyzer.py)，新增一條規則 `SEC-004`，當有人呼叫 `subprocess.Popen(..., shell=True)` 時，發出 `CRITICAL` 警告。
2. **挑戰 2 (自訂 Markdown 規則)**：在本地建立一個 `my_team_rules.md`，寫入你們公司的編程規範，然後使用 `--rules my_team_rules.md` 參數運行審查器。
3. **挑戰 3 (GitHub Action 整合)**：將這套腳本放進專案的 `.github/workflows/code_review.yml`，在每次 Pull Request 提交時自動執行，若有 CRITICAL 漏洞則阻擋合併！
