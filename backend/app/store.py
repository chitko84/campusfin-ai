"""Local-only demo store. No real financial information or external actions."""
from __future__ import annotations
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

SEED = Path(__file__).with_name('demo_data.json')
# On Vercel, code is mounted read-only. Only /tmp is writable, and its data is
# EPHEMERAL and may differ between instances/requests. This is a temporary
# synthetic-data demo fallback, not persistent storage or user isolation.
DEFAULT_DB = Path(os.getenv('CAMPUSFIN_DATABASE_PATH',
    '/tmp/campusfin_demo.sqlite3' if os.getenv('VERCEL') else
    str(Path(__file__).resolve().parents[1] / 'local_demo.sqlite3')))

class DemoStore:
    def __init__(self, path: Path = DEFAULT_DB):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as con:
            con.execute('CREATE TABLE IF NOT EXISTS demo_state (id INTEGER PRIMARY KEY CHECK(id=1), document TEXT NOT NULL)')
            con.execute('INSERT OR IGNORE INTO demo_state(id, document) VALUES (1, ?)', (SEED.read_text(encoding='utf-8'),))
            con.execute('''CREATE TABLE IF NOT EXISTS drafts (
                id TEXT PRIMARY KEY, kind TEXT NOT NULL, body TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('draft','approved')),
                scenario TEXT NOT NULL, gap_json TEXT NOT NULL, created_at TEXT NOT NULL,
                approved_at TEXT)''')
            con.execute('''CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL,
                event TEXT NOT NULL, result TEXT NOT NULL,
                details_json TEXT NOT NULL)''')

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def get(self) -> dict:
        with self.connect() as con:
            row = con.execute('SELECT document FROM demo_state WHERE id=1').fetchone()
        return json.loads(row[0])

    def save(self, data: dict) -> dict:
        with self.connect() as con:
            con.execute('UPDATE demo_state SET document=? WHERE id=1', (json.dumps(data, ensure_ascii=False),))
        return data

    def reset(self) -> dict:
        with self.connect() as con:
            con.execute('UPDATE demo_state SET document=? WHERE id=1', (SEED.read_text(encoding='utf-8'),))
            con.execute('DELETE FROM drafts')
            con.execute('DELETE FROM audit_events')
        return self.get()

    def audit(self, event: str, result: str, details: dict):
        with self.connect() as con:
            con.execute('INSERT INTO audit_events(at,event,result,details_json) VALUES (?,?,?,?)',
                        (datetime.now(timezone.utc).isoformat(), event, result, json.dumps(details)))

    def list_events(self):
        with self.connect() as con:
            rows=con.execute('SELECT id,at,event,result,details_json FROM audit_events ORDER BY id DESC LIMIT 100').fetchall()
        return [{'id':row[0], 'at':row[1], 'event':row[2], 'result':row[3], 'details':json.loads(row[4])} for row in rows]

    def create_draft(self, body: str, kind: str, scenario: str, gap: dict):
        record={'id':'draft_'+uuid4().hex[:12], 'kind':kind,'body':body, 'status':'draft',
                'scenario':scenario, 'gap_summary':gap,
                'created_at':datetime.now(timezone.utc).isoformat(),'approved_at':None}
        with self.connect() as con:
            con.execute('INSERT INTO drafts(id,kind,body,status,scenario,gap_json,created_at) VALUES (?,?,?,?,?,?,?)',
                        (record['id'],kind,body,'draft',scenario,json.dumps(gap),record['created_at']))
        self.audit('draft.created','success',{'draft_id':record['id'],'kind':kind,'no_external_delivery':True})
        return record

    def list_drafts(self):
        with self.connect() as con:
            rows=con.execute('SELECT id,kind,body,status,scenario,gap_json,created_at,approved_at FROM drafts ORDER BY created_at DESC').fetchall()
        return [dict(zip(('id','kind','body','status','scenario','gap_json','created_at','approved_at'),row)) | {'gap_summary':json.loads(row[5])} for row in rows]

    def edit_draft(self, draft_id: str, body: str):
        with self.connect() as con:
            row=con.execute('SELECT status FROM drafts WHERE id=?',(draft_id,)).fetchone()
            if row is None: return None
            if row[0]!='draft': raise ValueError('Approved draft cannot be edited')
            con.execute('UPDATE drafts SET body=? WHERE id=?',(body,draft_id))
        self.audit('draft.edited','success',{'draft_id':draft_id})
        return next(x for x in self.list_drafts() if x['id']==draft_id)

    def approve_draft(self, draft_id:str, confirmed:bool):
        if not confirmed: raise ValueError('Explicit confirmation is required to approve a draft')
        at=datetime.now(timezone.utc).isoformat()
        with self.connect() as con:
            row=con.execute('SELECT status FROM drafts WHERE id=?',(draft_id,)).fetchone()
            if row is None: return None
            if row[0]!='draft': raise ValueError('Draft was already approved')
            con.execute('UPDATE drafts SET status=?,approved_at=? WHERE id=?',('approved',at,draft_id))
        self.audit('draft.approved','success',{'draft_id':draft_id,'sent':False,'funds_received':False})
        return next(x for x in self.list_drafts() if x['id']==draft_id)


def get_store() -> DemoStore:
    return DemoStore()
