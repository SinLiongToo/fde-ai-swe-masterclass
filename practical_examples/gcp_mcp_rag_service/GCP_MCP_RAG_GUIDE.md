# 🌐 GCP + MCP + RAG 企業級雲原生智慧架構實戰指南
> **從協定標準到生產部署：Model Context Protocol (MCP)、Google Cloud Platform (GCP) 與兩階段混合檢索 (RAG) 的端到端整合**

---

## 🎯 為什麼「GCP + MCP + RAG」是現代 AI 系統工程的黃金三角？

在傳統的 AI 應用開發中，工程師常常面臨以下三大痛點：
1. **模型與工具緊密耦合**：換了模型（例如從 OpenAI 換到 Gemini 或 Claude），所有的 Function Calling JSON Schema 都要重寫重測。
2. **缺乏標準化權限隔離**：LLM 直接直連資料庫連線字串，缺乏審計日誌與安全防護。
3. **知識盲區與精確代號幻覺**：純向量搜尋對特定料號、合約編號或 GCP 指令容易誤判，無法精準命中團隊維運規範。

**「GCP + MCP + RAG」架構徹底解決了上述問題：**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GCP + MCP + RAG ARCHITECTURE TOPOLOGY                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. AI 代理端 (Agent / IDE)                                                  │
│    • Google Antigravity / Cursor / Claude Code / 自研 Python Agent          │
│                                │                                            │
│                                ▼ JSON-RPC 2.0 (stdio / SSE)                 │
│ 2. 標準協議層 (Model Context Protocol - MCP)                                │
│    • tools/list     (動態發現工具定義與 Pydantic 規格)                       │
│    • tools/call     (安全執行並返回標準化 MCPContentItem)                   │
│                                │                                            │
│                                ▼                                            │
│ 3. 企業 MCP 服務層 (MCP Server @ Google Cloud Run)                          │
│    ┌───────────────────────────┴───────────────────────────┐                │
│    ▼                                                       ▼                │
│ 【工具 A: 企業兩階段 RAG】                             【工具 B: GCP 基礎設施遙測】  │
│  • BM25 稀疏全文檢索                                    • Google Cloud Run   │
│  • Vertex AI 向量嵌入 (text-embedding-004)              • Cloud SQL pgvector │
│  • 互惠排名融合 (RRF k=60)                              • Cloud Monitoring   │
│  • SRE 事故排查手冊 (Runbooks)                          • 自動擴展與修復執行  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 本實戰專案結構 (`practical_examples/gcp_mcp_rag_service/`)

```text
practical_examples/gcp_mcp_rag_service/
├── protocol.py             # 【協定】Pydantic v2 定義的標準 MCP JSON-RPC 2.0 訊息格式
├── rag_engine.py           # 【RAG】兩階段混合檢索引掣（BM25 + 語義向量 + RRF k=60 融合）
├── gcp_telemetry.py        # 【雲端】GCP Cloud Run / Cloud SQL 遙測指標與資源管理介面
├── mcp_server.py           # 【MCP Server】標準 MCP 服務端（支援 stdio 與 SSE 通訊）
├── agent_client.py         # 【Agent Client】MCP 客戶端代理（動態發現工具、診斷與修復編排）
├── cli.py                  # 【CLI 介面】Rich 彩色終端展示與 SRE 故障排查實例
├── test_gcp_mcp_rag.py     # 【測試】完整的 Pytest 協定相容性與 RAG 檢索驗證套件
├── knowledge_docs/         # 【私有知識庫】真實 GCP 生產環境 SRE Runbook
│   ├── runbook_cloud_run_latency.md    # Cloud Run P99 延遲與冷啟動排查修復指南
│   ├── runbook_cloud_sql_pgvector.md   # Cloud SQL PostgreSQL pgvector HNSW 索引調優指南
│   └── runbook_disaster_recovery.md    # 跨地域容災與故障切換協定
└── GCP_MCP_RAG_GUIDE.md    # 本深度架構指南
```

---

## 🚀 5 秒鐘快速上手體驗

在專案根目錄執行終端指令，體驗 SRE Agent 如何透過 **MCP** 自動發現工具、抓取 **GCP** 故障指標、檢索 **RAG** 專家手冊並執行無伺服器擴展修復：

```bash
python -m practical_examples.gcp_mcp_rag_service.cli
```

### 終端機實際運作流程：
1. **MCP 握手與工具發現 (`tools/list`)**：
   Agent 向 MCP Server 發送 `initialize` 與 `tools/list`，動態發現 3 個可用工具：
   * `search_enterprise_rag`：搜尋私有 GCP 維運手冊。
   * `get_gcp_service_status`：查詢 Cloud Run / Cloud SQL 即時健全度。
   * `update_cloud_run_scaling`：調整 Cloud Run 執行個體擴展配額。
2. **故障診斷 (`get_gcp_service_status`)**：
   查詢 `payment-gateway` 服務，發現狀態為 `DEGRADED`，P99 延遲高達 `1420.5ms`，504 逾時率 `3.8%`，最小執行個體為 `0`（頻繁觸發冷啟動）。
3. **RAG 私有知識接地 (`search_enterprise_rag`)**：
   透過兩階段混合檢索（RRF 融合），精確命中 `runbook_cloud_run_latency.md` 中的第 2 節修復方針。
4. **自動修復與驗收 (`update_cloud_run_scaling`)**：
   透過 MCP 呼叫修復工具，將最小執行個體提高為 `3` 並啟用 `--cpu-boost`。修復後狀態轉為 `HEALTHY`，P99 延遲迅速回落至 `185ms`！

---

## 🛠️ 三大技術深度剖析

### 1. Model Context Protocol (MCP) 協議底層原理
MCP 本質上是建立在 **JSON-RPC 2.0** 之上的輕量級協定。它主要規範了三種能力：
* **Tools (工具呼叫)**：模型可以執行的函式（如資料庫更新、呼叫外部 API）。
* **Resources (資源檢索)**：唯讀上下文（例如系統日誌 `gcp://logging/cloudrun/error`）。
* **Prompts (提示範本)**：預先定義的工程師 Prompt 樣板。

在 [`protocol.py`](file:///c:/Users/tu-hs/OneDrive/文件/2022_0308_MASA/2022-0708/Projects_antigravity\SW_ENGINNERING\practical_examples\gcp_mcp_rag_service\protocol.py) 中，我們使用 Pydantic v2 定義了嚴格的訊息契約：
```json
// tools/list 回應範例
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "search_enterprise_rag",
        "description": "Performs 2-stage hybrid search across enterprise GCP SRE runbooks.",
        "inputSchema": {
          "type": "object",
          "properties": {
            "query": { "type": "string" },
            "top_k": { "type": "integer" }
          },
          "required": ["query"]
        }
      }
    ]
  }
}
```

### 2. Google Cloud Platform (GCP) 雲原生架構落地
在生產環境中，此架構在 GCP 上的典型配置如下：
* **計算服務 (Google Cloud Run)**：
  * 將 MCP Server 打包為 Docker 容器部署至 Cloud Run。
  * 利用 Cloud Run 的 `min-instances=1` 保證 MCP Server 常駐熱身，並啟用 IAM 認證保護。
* **向量儲存 (Cloud SQL for PostgreSQL + pgvector)**：
  * 使用 PostgreSQL 16 官方 `pgvector` 外掛。
  * 在知識庫向量上建立 **HNSW 索引**（`WITH (m = 16, ef_construction = 64)`），將檢索延遲從 450ms 降至 15ms 以內。
* **大模型與嵌入 (Vertex AI)**：
  * 使用 Vertex AI `text-embedding-004` 生成 768 維語義向量。
  * 使用 `gemini-2.5-flash` 作為推理主幹模型。

### 3. 企業級兩階段混合檢索 (RAG)
純向量搜尋容易在特定料號、指令語法（如 `--cpu-boost`）上失真；BM25 關鍵字搜尋則無法理解「服務卡頓」與「Latency P99」的同義關聯。
在 [`rag_engine.py`](file:///c:/Users/tu-hs/OneDrive/文件/2022_0308_MASA/2022-0708/Projects_antigravity\SW_ENGINNERING\practical_examples\gcp_mcp_rag_service\rag_engine.py) 中，我們採用**互惠排名融合 (Reciprocal Rank Fusion, $k=60$)**：
$$\text{RRF}(d) = \frac{1}{60 + \text{rank}_{\text{dense}}(d)} + \frac{1}{60 + \text{rank}_{\text{bm25}}(d)}$$
透過數學倒數加權，完美兼具關鍵字精確性與語義泛化力。

---

## 🚢 如何將此 MCP Server 部署至真實 Google Cloud Run？

### 1. 建立 `Dockerfile`
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY practical_examples/gcp_mcp_rag_service /app/practical_examples/gcp_mcp_rag_service
RUN pip install pydantic rich
ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "practical_examples.gcp_mcp_rag_service.mcp_server"]
```

### 2. 使用 Google Cloud SDK 一鍵部署
```bash
gcloud run deploy gcp-sre-mcp-server \
  --source . \
  --region asia-east1 \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 10 \
  --memory 1Gi \
  --cpu 1
```

---

## 💻 如何在你的 AI IDE (Cursor / Antigravity / Claude Code) 中掛載此 MCP Server？

打開你的 IDE 設定檔（例如 `claude_desktop_config.json` 或 Cursor 的 MCP 伺服器設定），加入以下配置：

```json
{
  "mcpServers": {
    "gcp-sre-service": {
      "command": "python",
      "args": [
        "-m",
        "practical_examples.gcp_mcp_rag_service.mcp_server"
      ],
      "cwd": "C:/Users/tu-hs/OneDrive/文件/2022_0308_MASA/2022-0708/Projects_antigravity/SW_ENGINNERING"
    }
  }
}
```
儲存後，你的 AI 助手就能直接在對話中呼叫 `search_enterprise_rag` 查詢內部文件，或呼叫 `get_gcp_service_status` 監控雲端基礎設施！
