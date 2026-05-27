#!/usr/bin/env python3
"""Create 9 webhook-based n8n workflows (Docker-compatible — no Execute Command nodes)."""
import json, os, uuid, urllib.request, urllib.error

# ── Config ───────────────────────────────────────────────────────────────────
API_KEY = ""
TG_CHAT_ID = ""
for line in open(os.path.expanduser("~/.claude/.secrets/n8n.env")):
    if line.startswith("N8N_API_KEY="): API_KEY = line.split("=",1)[1].strip()
for line in open(os.path.expanduser("~/.claude/.secrets/tg.env")):
    if line.startswith("TELEGRAM_CHAT_ID="): TG_CHAT_ID = line.split("=",1)[1].strip()

BASE = "http://localhost:5678"
TG_CRED_ID   = "YJkcTsUxMJDH2L2N"
TG_CRED_NAME = "Telegram Claude Bot"

# ── Helpers ──────────────────────────────────────────────────────────────────
def uid(): return str(uuid.uuid4())

def api(method, path, data=None):
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"{BASE}/api/v1/{path}", data=body, method=method,
        headers={"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise Exception(f"HTTP {e.code}: {e.read().decode()[:300]}")

def create_workflow(name, nodes, connections):
    wf = {"name": name, "nodes": nodes, "connections": connections,
          "settings": {"executionOrder": "v1"}, "staticData": None}
    result = api("POST", "workflows", wf)
    wid = result["id"]
    # Activate via POST /activate
    try: api("POST", f"workflows/{wid}/activate")
    except: pass
    print(f"  ✓ {name}  id={wid}")
    return wid

def conn(c, frm, to, out=0):
    c.setdefault(frm, {"main": []})
    while len(c[frm]["main"]) <= out: c[frm]["main"].append([])
    c[frm]["main"][out].append({"node": to, "type": "main", "index": 0})

# ── Node factories ────────────────────────────────────────────────────────────
def n_webhook(name, pos, path):
    return {"id": uid(), "name": name, "type": "n8n-nodes-base.webhook",
            "typeVersion": 2, "position": pos,
            "parameters": {"httpMethod": "POST", "path": path,
                           "responseMode": "onReceived", "options": {}}}

def n_code(name, pos, js):
    return {"id": uid(), "name": name, "type": "n8n-nodes-base.code",
            "typeVersion": 2, "position": pos,
            "parameters": {"jsCode": js}}

def n_if(name, pos, expr):
    return {"id": uid(), "name": name, "type": "n8n-nodes-base.if",
            "typeVersion": 2.2, "position": pos,
            "parameters": {"conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                "conditions": [{"id": uid(), "leftValue": expr, "rightValue": True,
                                "operator": {"type": "boolean", "operation": "true", "singleValue": True}}],
                "combinator": "and"}}}

def n_telegram(name, pos):
    return {"id": uid(), "name": name, "type": "n8n-nodes-base.telegram",
            "typeVersion": 1.2, "position": pos,
            "parameters": {"resource": "message", "operation": "sendMessage",
                           "chatId": TG_CHAT_ID, "text": "={{ $json.message }}",
                           "additionalFields": {"parse_mode": "HTML"}},
            "credentials": {"telegramApi": {"id": TG_CRED_ID, "name": TG_CRED_NAME}}}

def n_noop(name, pos):
    return {"id": uid(), "name": name, "type": "n8n-nodes-base.noOp",
            "typeVersion": 1, "position": pos, "parameters": {}}

# ════════════════════════════════════════════════════════════════════════════════
# [1] FOLLOWUPS.md Reminder  /webhook/claude-followups
# Host sends: {content: "...", today: "YYYY-MM-DD"}
# ════════════════════════════════════════════════════════════════════════════════
print("\n[1] FOLLOWUPS.md Reminder")

js1 = r"""
const body = $input.first().json.body || $input.first().json;
const content = body.content || '';
const today = new Date(body.today || new Date());
today.setHours(0, 0, 0, 0);

const pending = [];
const patterns = [
  /Review target:\s+\*\*(\d{4}-\d{2}-\d{2})\*\*/g,
  /next:\s+\*\*(\d{4}-\d{2}-\d{2})\*\*/g,
];
for (const re of patterns) {
  let m;
  while ((m = re.exec(content)) !== null) {
    const t = new Date(m[1]);
    t.setHours(0,0,0,0);
    const days = Math.round((t - today) / 86400000);
    if (days < 0 || days > 3) continue;
    const before = content.substring(Math.max(0, m.index - 300), m.index);
    const h = before.match(/##\s+\d+\.\s+(.+)/g);
    const title = h ? h[h.length-1].replace(/^##\s+\d+\.\s+/, '') : 'Task';
    pending.push({ title, date: m[1], days });
  }
}

const seen = new Set();
const unique = pending.filter(p => {
  const k = p.date + p.title;
  return seen.has(k) ? false : seen.add(k);
});

if (unique.length === 0) return [{ json: { hasPending: false } }];

const lines = unique.map(p => {
  const e = p.days === 0 ? '🔴' : p.days === 1 ? '🟠' : '🟡';
  const w = p.days === 0 ? 'TODAY' : p.days === 1 ? 'tomorrow' : `in ${p.days} days`;
  return `${e} <b>${p.title}</b>\n   Due: ${p.date} (${w})`;
});
const message = `⏰ <b>FOLLOWUPS.md Reminder</b>\n\n${lines.join('\n\n')}`;
return [{ json: { hasPending: true, message } }];
"""

n1 = [n_webhook("Webhook", [240,300], "claude-followups"),
      n_code("Parse Dates", [460,300], js1),
      n_if("Has Pending?", [680,300], "={{ $json.hasPending }}"),
      n_telegram("Telegram", [900,200]),
      n_noop("No Reminders", [900,420])]
c1 = {}
conn(c1, n1[0]["name"], n1[1]["name"])
conn(c1, n1[1]["name"], n1[2]["name"])
conn(c1, n1[2]["name"], n1[3]["name"], out=0)
conn(c1, n1[2]["name"], n1[4]["name"], out=1)
create_workflow("Claude — FOLLOWUPS Reminder", n1, c1)


# ════════════════════════════════════════════════════════════════════════════════
# [2] Pipeline Phase Tracker  /webhook/claude-stop
# Host sends enriched Stop payload (see n8n-notify.sh)
# ════════════════════════════════════════════════════════════════════════════════
print("\n[2] Pipeline Phase Tracker")

js2 = r"""
const staticData = $getWorkflowStaticData('global');
const body = $input.first().json.body || $input.first().json;

const cwdHash    = body.cwd_hash || 'unknown';
const lastSkill  = body.last_skill || '';
const phases     = body.checkpoint_phases || [];
const cwd        = body.cwd || '';
const projectName = cwd.split('/').filter(Boolean).pop() || cwdHash;

if (!staticData.pipelines) staticData.pipelines = {};
const prev = staticData.pipelines[cwdHash] || { sa:false, ux:false, fe:false };
const updated = { sa: prev.sa, ux: prev.ux, fe: prev.fe };

if (lastSkill === 'sa') updated.sa = true;
if (lastSkill === 'ux') updated.ux = true;
if (lastSkill === 'fe') updated.fe = true;
for (const p of phases) {
  if (p === 'sa') updated.sa = true;
  if (p === 'ux') updated.ux = true;
  if (p === 'fe') updated.fe = true;
}

if (!updated.sa && !updated.ux && !updated.fe) {
  return [{ json: { shouldNotify: false } }];
}

const changed = updated.sa !== prev.sa || updated.ux !== prev.ux || updated.fe !== prev.fe;
staticData.pipelines[cwdHash] = updated;

if (!changed) return [{ json: { shouldNotify: false } }];

const sa = updated.sa ? '✅' : '⏳';
const ux = updated.ux ? '✅' : '⏳';
const fe = updated.fe ? '✅' : '⏳';
const allDone = updated.sa && updated.ux && updated.fe;

let message;
if (allDone) {
  message = `🎉 <b>Pipeline Complete!</b>\n📁 <code>${projectName}</code>\n\nsa ${sa} → ux ${ux} → fe ${fe}\n\nRun <code>/verify</code> or <code>/pr</code> next.`;
  staticData.pipelines[cwdHash] = { sa:false, ux:false, fe:false };
} else {
  message = `🔄 <b>Pipeline Update</b>\n📁 <code>${projectName}</code>\n\nsa ${sa} → ux ${ux} → fe ${fe}`;
  if (lastSkill && ['sa','ux','fe'].includes(lastSkill)) {
    message += `\n\nCompleted: <code>${lastSkill}</code>`;
  }
}
return [{ json: { shouldNotify: true, message } }];
"""

n2 = [n_webhook("Webhook", [240,300], "claude-stop"),
      n_code("Track Pipeline", [460,300], js2),
      n_if("Should Notify?", [680,300], "={{ $json.shouldNotify }}"),
      n_telegram("Telegram", [900,200]),
      n_noop("No Change", [900,420])]
c2 = {}
conn(c2, n2[0]["name"], n2[1]["name"])
conn(c2, n2[1]["name"], n2[2]["name"])
conn(c2, n2[2]["name"], n2[3]["name"], out=0)
conn(c2, n2[2]["name"], n2[4]["name"], out=1)
create_workflow("Claude — Pipeline Tracker", n2, c2)


# ════════════════════════════════════════════════════════════════════════════════
# [3] Weekly Skill Report  /webhook/claude-weekly
# Host sends: {counts: "N skill\n...", total: N, today: "YYYY-MM-DD", week_start: "YYYY-MM-DD"}
# ════════════════════════════════════════════════════════════════════════════════
print("\n[3] Weekly Skill Report")

js3 = r"""
const body = $input.first().json.body || $input.first().json;
const countsRaw = body.counts || '';
const total     = parseInt(body.total || 0, 10);
const today     = body.today || new Date().toISOString().slice(0,10);
const weekStart = body.week_start || '';

if (total === 0) {
  return [{ json: { message: '📊 <b>Weekly Skill Report</b>\n\nNo skill invocations this week.' } }];
}

const rows = countsRaw.trim().split('\n').filter(Boolean).map(line => {
  const parts = line.trim().split(/\s+/);
  const n = parseInt(parts[0], 10);
  const skill = parts.slice(1).join(' ');
  const bar = '▓'.repeat(Math.min(n, 12));
  return `  <code>${skill.padEnd(14)}</code> ${bar} ${n}×`;
});

const range = weekStart ? `${weekStart} → ${today}` : today;
const message = `📊 <b>Weekly Skill Report</b>\n${range}\n\n${rows.join('\n')}\n\nTotal: <b>${total}</b> invocations`;
return [{ json: { message } }];
"""

n3 = [n_webhook("Webhook", [240,300], "claude-weekly"),
      n_code("Format Report", [460,300], js3),
      n_telegram("Telegram", [680,300])]
c3 = {}
conn(c3, n3[0]["name"], n3[1]["name"])
conn(c3, n3[1]["name"], n3[2]["name"])
create_workflow("Claude — Weekly Skill Report", n3, c3)


# ════════════════════════════════════════════════════════════════════════════════
# [4] Memory Health Monitor  /webhook/claude-memory
# Host sends enriched Stop payload (mem_files, mem_bytes from n8n-notify.sh)
# ════════════════════════════════════════════════════════════════════════════════
print("\n[4] Memory Health Monitor")

js4 = r"""
const staticData = $getWorkflowStaticData('global');
const body = $input.first().json.body || $input.first().json;

const totalBytes = parseInt(body.mem_bytes || 0, 10);
const totalFiles = parseInt(body.mem_files || 0, 10);
const today = new Date().toISOString().slice(0,10);
const kb = b => (b / 1024).toFixed(1);

if (!staticData.memHistory) staticData.memHistory = [];

// Only record once per day
const last = staticData.memHistory[staticData.memHistory.length - 1];
if (!last || last.date !== today) {
  staticData.memHistory.push({ date: today, bytes: totalBytes, files: totalFiles });
  if (staticData.memHistory.length > 30) {
    staticData.memHistory = staticData.memHistory.slice(-30);
  }
}

// Skip if no data
if (totalBytes === 0) return [{ json: { shouldAlert: false } }];

let shouldAlert = false, message = '';

// Growth check: compare to 7 readings ago
const h = staticData.memHistory;
if (h.length >= 7) {
  const old = h[h.length - 7];
  const pct = old.bytes > 0 ? (totalBytes - old.bytes) / old.bytes * 100 : 0;
  if (pct > 20) {
    shouldAlert = true;
    message = `⚠️ <b>Memory Growing Fast</b>\n\n📊 Size: <b>${kb(totalBytes)} KB</b> (+${pct.toFixed(1)}% in 7 days)\n📄 Files: <b>${totalFiles}</b>\n\nRun <code>/distill-memory</code> to prune.`;
  }
}

// Hard threshold: 500 KB
if (!shouldAlert && totalBytes > 500 * 1024) {
  shouldAlert = true;
  message = `📦 <b>Memory Size Alert</b>\n\n📊 Total: <b>${kb(totalBytes)} KB</b> (threshold: 500 KB)\n📄 Files: <b>${totalFiles}</b>\n\nRun <code>/distill-memory</code>.`;
}

return [{ json: { shouldAlert, message, totalKB: parseFloat(kb(totalBytes)) } }];
"""

n4 = [n_webhook("Webhook", [240,300], "claude-memory"),
      n_code("Check Health", [460,300], js4),
      n_if("Should Alert?", [680,300], "={{ $json.shouldAlert }}"),
      n_telegram("Telegram Alert", [900,200]),
      n_noop("Memory OK", [900,420])]
c4 = {}
conn(c4, n4[0]["name"], n4[1]["name"])
conn(c4, n4[1]["name"], n4[2]["name"])
conn(c4, n4[2]["name"], n4[3]["name"], out=0)
conn(c4, n4[2]["name"], n4[4]["name"], out=1)
create_workflow("Claude — Memory Health Monitor", n4, c4)


# ════════════════════════════════════════════════════════════════════════════════
# [5] TypeCheck Trend  /webhook/claude-typecheck
# Host sends: {project, label, exit_code, error_count, top_errors, timestamp}
# ════════════════════════════════════════════════════════════════════════════════
print("\n[5] TypeCheck Trend")

js5 = r"""
const staticData = $getWorkflowStaticData('global');
const body = $input.first().json.body || $input.first().json;

const project    = body.project || 'unknown';
const label      = body.label || 'TS';
const exitCode   = parseInt(body.exit_code ?? 0, 10);
const errorCount = parseInt(body.error_count ?? 0, 10);
const topErrors  = body.top_errors || '';
const today      = new Date().toISOString().slice(0,10);

if (!staticData.typeChecks) staticData.typeChecks = {};
const prev = staticData.typeChecks[project];
staticData.typeChecks[project] = { date: today, exitCode, errorCount };

let trend = '';
if (prev !== undefined) {
  if (errorCount > prev.errorCount) trend = ` 📈 +${errorCount - prev.errorCount} vs last`;
  else if (errorCount < prev.errorCount && prev.errorCount > 0) trend = ` 📉 −${prev.errorCount - errorCount} fixed`;
  else if (exitCode === 0 && prev.exitCode !== 0) trend = ' 🎉 newly passing';
}

let message;
if (exitCode === 0) {
  message = `✅ <b>Type check passed</b>\n📁 <code>${project}</code> (${label}) — 0 errors${trend}`;
} else {
  const hdr = (trend.includes('📈')) ? '🚨' : '❌';
  message = `${hdr} <b>Type check: ${errorCount} error(s)</b>\n📁 <code>${project}</code> (${label})${trend}`;
  if (topErrors.trim()) {
    const esc = topErrors.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    message += `\n\n<code>${esc}</code>`;
  }
}
return [{ json: { message } }];
"""

n5 = [n_webhook("Webhook", [240,300], "claude-typecheck"),
      n_code("Compute Trend", [460,300], js5),
      n_telegram("Telegram", [680,300])]
c5 = {}
conn(c5, n5[0]["name"], n5[1]["name"])
conn(c5, n5[1]["name"], n5[2]["name"])
create_workflow("Claude — TypeCheck Trend", n5, c5)


# ════════════════════════════════════════════════════════════════════════════════
# [6] Repo Sync Drift  /webhook/claude-drift
# Host sends: {drifts: ["file.sh", ...], drift_count: N}
# ════════════════════════════════════════════════════════════════════════════════
print("\n[6] Repo Sync Drift Detector")

js6 = r"""
const body = $input.first().json.body || $input.first().json;
const drifts = body.drifts || [];
const count  = body.drift_count || drifts.length || 0;

if (count === 0) return [{ json: { hasDrift: false } }];

const list = drifts.map(f => `  • <code>${f}</code>`).join('\n');
const message = `⚠️ <b>Hook Drift Detected</b>\n\n${count} file(s) differ between <code>~/.claude/hooks/</code> and repo:\n\n${list}\n\nSync to <code>~/Project/claude-skill-copy/hooks/</code> then commit + push.`;
return [{ json: { hasDrift: true, message } }];
"""

n6 = [n_webhook("Webhook", [240,300], "claude-drift"),
      n_code("Parse Drifts", [460,300], js6),
      n_if("Has Drift?", [680,300], "={{ $json.hasDrift }}"),
      n_telegram("Telegram Alert", [900,200]),
      n_noop("In Sync", [900,420])]
c6 = {}
conn(c6, n6[0]["name"], n6[1]["name"])
conn(c6, n6[1]["name"], n6[2]["name"])
conn(c6, n6[2]["name"], n6[3]["name"], out=0)
conn(c6, n6[2]["name"], n6[4]["name"], out=1)
create_workflow("Claude — Repo Sync Drift Detector", n6, c6)


# ════════════════════════════════════════════════════════════════════════════════
# [7] Cross-Project Pattern Digest  /webhook/claude-cross-project
# Host sends: {candidates: [{slug, count, projects: [...]}], count: N}
# ════════════════════════════════════════════════════════════════════════════════
print("\n[7] Cross-Project Pattern Digest")

js7 = r"""
const body = $input.first().json.body || $input.first().json;
const candidates = body.candidates || [];
const count = body.count || candidates.length || 0;

if (count === 0) return [{ json: { hasCandidates: false } }];

const items = candidates.map(c => {
  const projects = (c.projects || []).join(', ');
  return `  • <code>${c.slug}</code> — ${c.count} projects: ${projects}`;
});

const message = `🔗 <b>Cross-Project Pattern Digest</b>\n\n${count} pattern(s) found in ≥2 projects:\n\n${items.join('\n')}\n\nRun <code>/distill-memory</code> to promote.`;
return [{ json: { hasCandidates: true, message } }];
"""

n7 = [n_webhook("Webhook", [240,300], "claude-cross-project"),
      n_code("Format Digest", [460,300], js7),
      n_if("Has Candidates?", [680,300], "={{ $json.hasCandidates }}"),
      n_telegram("Telegram Digest", [900,200]),
      n_noop("No Candidates", [900,420])]
c7 = {}
conn(c7, n7[0]["name"], n7[1]["name"])
conn(c7, n7[1]["name"], n7[2]["name"])
conn(c7, n7[2]["name"], n7[3]["name"], out=0)
conn(c7, n7[2]["name"], n7[4]["name"], out=1)
create_workflow("Claude — Cross-Project Pattern Digest", n7, c7)

# ════════════════════════════════════════════════════════════════════════════════
# [8] State Store + Pre-fetch Cache
# GET  /webhook/claude-prefetch?cwd_hash=X  → returns pre-computed session context
# POST /webhook/claude-state-store          → writes state from n8n-notify.sh / followups
# ════════════════════════════════════════════════════════════════════════════════
print("\n[8] State Store + Pre-fetch Cache")

js8_read = r"""
const sd = $getWorkflowStaticData('global');
const query = $input.first().json.query || {};
const cwdHash = query.cwd_hash || '';

const pipeline = sd.pipelines?.[cwdHash] || null;
const memAlert = sd.memAlert || null;
const followups = sd.pendingFollowups || null;

const items = [];
if (pipeline && (pipeline.sa || pipeline.ux || pipeline.fe)) {
  const sa = pipeline.sa ? '✅' : '⏳';
  const ux = pipeline.ux ? '✅' : '⏳';
  const fe = pipeline.fe ? '✅' : '⏳';
  items.push(`Pipeline: sa ${sa} → ux ${ux} → fe ${fe}`);
}
if (memAlert) items.push(memAlert);
if (followups) items.push(followups);

return [{ json: {
  has_context: items.length > 0,
  items,
  pipeline: pipeline || { sa: false, ux: false, fe: false }
}}];
"""

js8_write = r"""
const sd = $getWorkflowStaticData('global');
const body = $input.first().json.body || $input.first().json;

const cwdHash   = body.cwd_hash   || '';
const lastSkill = body.last_skill || '';
const phases    = body.checkpoint_phases || [];
const memFiles  = parseInt(body.mem_files  || 0, 10);
const memBytes  = parseInt(body.mem_bytes  || 0, 10);

// ── pipeline ──────────────────────────────────────────────────────────────────
if (cwdHash) {
  if (!sd.pipelines) sd.pipelines = {};
  const prev = sd.pipelines[cwdHash] || { sa: false, ux: false, fe: false };
  const upd  = { sa: prev.sa, ux: prev.ux, fe: prev.fe };
  if (lastSkill === 'sa') upd.sa = true;
  if (lastSkill === 'ux') upd.ux = true;
  if (lastSkill === 'fe') upd.fe = true;
  for (const p of phases) {
    if (p === 'sa') upd.sa = true;
    if (p === 'ux') upd.ux = true;
    if (p === 'fe') upd.fe = true;
  }
  if (upd.sa && upd.ux && upd.fe) { delete sd.pipelines[cwdHash]; }
  else { sd.pipelines[cwdHash] = upd; }
}

// ── memory alert ──────────────────────────────────────────────────────────────
if (memBytes > 0 || memFiles > 0) {
  const kb = memBytes / 1024;
  if (kb > 500 || memFiles > 45) {
    sd.memAlert = `Memory: ${memFiles} files, ${kb.toFixed(0)} KB — run /distill-memory`;
  } else if (memFiles > 30) {
    sd.memAlert = `Memory: ${memFiles} files — consider /distill-memory`;
  } else {
    sd.memAlert = null;
  }
}

// ── followups (payload from n8n-followups-check.sh) ──────────────────────────
if (body.content && body.today) {
  const content = body.content;
  const today = new Date(body.today);
  today.setHours(0, 0, 0, 0);
  const pats = [
    /Review target:\s+\*\*(\d{4}-\d{2}-\d{2})\*\*/g,
    /next:\s+\*\*(\d{4}-\d{2}-\d{2})\*\*/g,
  ];
  const pending = [];
  for (const re of pats) {
    let m;
    while ((m = re.exec(content)) !== null) {
      const t = new Date(m[1]);
      t.setHours(0, 0, 0, 0);
      const days = Math.round((t - today) / 86400000);
      if (days < 0 || days > 3) continue;
      const before = content.substring(Math.max(0, m.index - 300), m.index);
      const h = before.match(/##\s+\d+\.\s+(.+)/g);
      const title = h ? h[h.length - 1].replace(/^##\s+\d+\.\s+/, '') : 'Task';
      pending.push({ title, date: m[1], days });
    }
  }
  if (pending.length > 0) {
    const lines = pending.map(p => {
      const w = p.days === 0 ? 'TODAY' : p.days === 1 ? 'tmr' : `${p.days}d`;
      return `${p.title} (${w})`;
    });
    sd.pendingFollowups = `FOLLOWUPS: ${lines.join(', ')}`;
  } else {
    sd.pendingFollowups = null;
  }
}

return [{ json: { ok: true } }];
"""

wh_get  = {"id": uid(), "name": "WH GET",  "type": "n8n-nodes-base.webhook",
            "typeVersion": 2, "position": [240, 200],
            "parameters": {"httpMethod": "GET", "path": "claude-prefetch",
                           "responseMode": "responseNode", "options": {}}}
wh_post = {"id": uid(), "name": "WH POST", "type": "n8n-nodes-base.webhook",
            "typeVersion": 2, "position": [240, 500],
            "parameters": {"httpMethod": "POST", "path": "claude-state-store",
                           "responseMode": "onReceived", "options": {}}}
code_r  = {"id": uid(), "name": "Read State",  "type": "n8n-nodes-base.code",
            "typeVersion": 2, "position": [460, 200],
            "parameters": {"jsCode": js8_read}}
code_w  = {"id": uid(), "name": "Write State", "type": "n8n-nodes-base.code",
            "typeVersion": 2, "position": [460, 500],
            "parameters": {"jsCode": js8_write}}
respond = {"id": uid(), "name": "Respond",     "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1.1, "position": [680, 200],
            "parameters": {"respondWith": "json",
                           "responseBody": "={{ JSON.stringify($json) }}", "options": {}}}

n8 = [wh_get, wh_post, code_r, code_w, respond]
c8 = {}
conn(c8, "WH GET",      "Read State")
conn(c8, "WH POST",     "Write State")
conn(c8, "Read State",  "Respond")
create_workflow("Claude — State Store", n8, c8)

# ════════════════════════════════════════════════════════════════════════════════
# [9] Vocab Tracker  /webhook/claude-vocab-correction
# Host sends: {phrase, correct_skill, wrong_skill, auto_applied}
# Accumulates corrections in staticData; Telegrams on recurring mismatch (≥2×)
# ════════════════════════════════════════════════════════════════════════════════
print("\n[9] Vocab Tracker")

js9 = r"""
const sd   = $getWorkflowStaticData('global');
const body = $input.first().json.body || $input.first().json;

const phrase  = (body.phrase        || '(unknown)').toString().trim();
const correct = (body.correct_skill || '?').toString().trim();
const wrong   = (body.wrong_skill   || '?').toString().trim();
const applied = body.auto_applied !== false;

if (!sd.corrections) sd.corrections = [];

const existing = sd.corrections.find(c => c.phrase === phrase && c.correct === correct);
const now = new Date().toISOString();
if (existing) {
  existing.count   = (existing.count || 1) + 1;
  existing.last_ts = now;
} else {
  sd.corrections.push({ phrase, correct, wrong, count: 1, applied, first_ts: now, last_ts: now });
}
if (sd.corrections.length > 200) sd.corrections = sd.corrections.slice(-200);

const entry      = existing || sd.corrections[sd.corrections.length - 1];
const isRecurring = (entry.count || 1) >= 2;
const appliedTag  = applied ? ' (auto-applied ✅)' : ' (parse failed — manual update needed)';

const message = isRecurring
  ? `🔁 <b>Recurring vocab mismatch</b>\n`
    + `"<code>${phrase}</code>" corrected ${entry.count}× → <code>${correct}</code>`
    + (wrong && wrong !== '?' ? ` (was <code>${wrong}</code>)` : '')
    + appliedTag
  : '';

return [{ json: { phrase, correct, wrong, applied, count: entry.count, isRecurring, message } }];
"""

n9 = [{"id": uid(), "name": "WH Vocab", "type": "n8n-nodes-base.webhook",
        "typeVersion": 2, "position": [240, 300],
        "parameters": {"httpMethod": "POST", "path": "claude-vocab-correction",
                       "responseMode": "onReceived", "options": {}}},
      n_code("Track Correction", [460, 300], js9),
      n_if("Recurring?", [680, 300], "={{ $json.isRecurring }}"),
      n_telegram("Telegram Alert", [900, 200]),
      n_noop("Silent", [900, 420])]
c9 = {}
conn(c9, n9[0]["name"], n9[1]["name"])
conn(c9, n9[1]["name"], n9[2]["name"])
conn(c9, n9[2]["name"], n9[3]["name"], out=0)
conn(c9, n9[2]["name"], n9[4]["name"], out=1)
create_workflow("Claude — Vocab Tracker", n9, c9)

print("\n✅ All 9 workflows created and activated.")
