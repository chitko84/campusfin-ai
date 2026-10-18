import React, {useEffect,useRef,useState} from 'react';
import {PHOTOS,EditorialPhoto} from './Photography.jsx';

const suggested=[
  'What if my family transfer arrives on 28 October?',
  'What is at risk if family funding is delayed?',
  'Which rescue options are possible?',
  'Compare sample transfer costs.',
  'Explain why a plan may not be feasible.'
];

// Safe, dependency-free Markdown display: JSX text nodes only (no raw HTML).
function InlineMarkup({value}){
  const cleaned=String(value||'').replace(/\\([*#_`])/g,'$1');
  const parts=cleaned.split(/(\*\*[^*]+\*\*|`[^`]+`|\*[^*\n]+\*)/g);
  return <>{parts.map((part,i)=>part.startsWith('**')&&part.endsWith('**')?<strong key={i}>{part.slice(2,-2)}</strong>:part.startsWith('`')&&part.endsWith('`')?<code key={i}>{part.slice(1,-1)}</code>:part.startsWith('*')&&part.endsWith('*')?<em key={i}>{part.slice(1,-1)}</em>:<React.Fragment key={i}>{part}</React.Fragment>)}</>;
}
function ChatMarkdown({text}){
  const lines=String(text||'').replace(/\\([#*])/g,'$1').split(/\r?\n/);
  const out=[];let items=[];let paragraph=[];
  const flushParagraph=()=>{if(paragraph.length){out.push({type:'p',lines:paragraph});paragraph=[]}};
  const flushList=()=>{if(items.length){out.push({type:'list',items});items=[]}};
  for(const raw of lines){
    const line=raw.trim();
    if(!line){flushParagraph();flushList();continue}
    const heading=line.match(/^(#{1,4})\s+(.+)$/);
    const listItem=line.match(/^(?:[-*•]\s+|\d+[.)]\s+)(.+)$/);
    if(heading){flushParagraph();flushList();out.push({type:'head',depth:heading[1].length,text:heading[2]});continue}
    if(listItem){flushParagraph();items.push(listItem[1]);continue}
    flushList();paragraph.push(line);
  }
  flushParagraph();flushList();
  return <div className="p4-rich-text">{out.map((b,i)=>b.type==='head'?<h4 key={i} className={'p4-md-heading p4-md-h'+b.depth}><InlineMarkup value={b.text}/></h4>:b.type==='list'?<ul key={i}>{b.items.map((x,j)=><li key={j}><InlineMarkup value={x}/></li>)}</ul>:<p key={i}>{b.lines.map((line,j)=><React.Fragment key={j}>{j>0&&' '}<InlineMarkup value={line}/></React.Fragment>)}</p>)}</div>;
}

export function CopilotPage({api,Title,Pill,Icon,rm,scenario,overrides,navigate,onError,onProof,onApplyScenario}){
  const [status,setStatus]=useState(null);
  const [messages,setMessages]=useState([]);
  const [entry,setEntry]=useState('');
  const [busy,setBusy]=useState(false);
  const endRef=useRef(null);
  useEffect(()=>{api('/agent/status').then(setStatus).catch(e=>onError(e.message))},[]);
  useEffect(()=>{endRef.current?.scrollIntoView({behavior:'smooth',block:'nearest'})},[messages,busy]);

  const send=async(text=entry)=>{
    const content=text.trim();
    if(!content||busy)return;
    const history=messages.slice(-4).map(m=>({role:m.role==='assistant'?'assistant':'user',text:m.text.slice(0,500)}));
    setMessages(prev=>[...prev,{role:'user',text:content}]);
    setEntry('');setBusy(true);
    try{
      const reply=await api('/agent/chat','POST',{message:content,history,scenario,arrival_overrides:overrides});
      // Align Horizon and later questions with an explicitly simulated chat date.
      // This modifies React simulation state only, never stored SQLite records.
      if(reply.context?.source==='chat_hypothetical')onApplyScenario?.(reply.context);
      setMessages(prev=>[...prev,{role:'assistant',text:reply.text,mode:reply.mode,liveAI:reply.live_ai,facts:reply.facts,context:reply.context,trace:reply.tool_trace,warning:reply.warning}]);
    }catch(e){onError(e.message);setMessages(prev=>[...prev,{role:'assistant',text:'The request failed. Your records were not changed. Please retry or use Scenario Lab.',mode:'error',liveAI:false}])}
    finally{setBusy(false)}
  };
  return <>
    <Title eyebrow="SUPERVISED FINANCIAL INTELLIGENCE" title="Your CampusFin Copilot." subtitle="Ask about tuition deadlines, funding uncertainty, rescue options and simulated transfers." aside={<Pill kind={status?.gemini_configured?'success':'neutral'}>{status?.gemini_configured?'Gemini configured':'Local guide mode'}</Pill>}/>
    <section className="p4-shell">
      <article className="p4-conversation panel">
        <div className="p4-chat-heading"><div className="p4-avatar">◈</div><div><strong>CampusFin AI</strong><small>{status?.gemini_configured?'Gemini tool-calling available · can fall back safely':'No API key · deterministic local guidance'}</small></div><Pill kind="neutral">Read-only AI</Pill></div>
        <div className="p4-chat-stream" role="log" aria-live="polite">
          {messages.length===0&&<div className="p4-welcome"><span className="p4-welcome-orb">◈</span><div className="eyebrow">PREDICT · RESCUE · PROVE</div><h2>Let's understand what's ahead.</h2><p>My job is to explain your simulated financial picture. A separate, tested Python engine computes the numbers.</p><div className="p4-prompts">{suggested.map(x=><button key={x} disabled={busy} onClick={()=>send(x)}>{x} <Icon name="arrow" size={14}/></button>)}</div></div>}
          {messages.map((m,i)=><div className={'p4-message '+(m.role==='user'?'p4-user':'p4-agent')} key={i}>
            <div className="p4-speaker">{m.role==='user'?'YOU':'CAMPUSFIN AI'}{m.role==='assistant'&&<Pill kind={m.mode==='gemini'?'success':m.mode==='blocked'?'danger':'neutral'}>{m.mode==='gemini'?'Gemini response':m.mode==='blocked'?'Action blocked':'Offline guidance'}</Pill>}</div>
            {m.role==='user'?<p>{m.text}</p>:<ChatMarkdown text={m.text}/>}
            {m.role==='assistant'&&m.context&&<div className={'p4-scenario-context '+(m.context.source==='chat_hypothetical'?'p4-scenario-live':'')}>
              <span className="p4-context-icon">↗</span>
              <div><strong>{m.context.source==='chat_hypothetical'?'Chat scenario simulated':'Scenario used for this calculation'}</strong>
              <small>{m.context.label||m.context.scenario} · No saved funding data changed</small></div>
              {m.context.source==='chat_hypothetical'&&<button className="p4-context-open" type="button" onClick={()=>navigate('plan')}>View Horizon →</button>}
            </div>}
            {m.facts&&<div className="p4-computed-card"><div className="p4-computed-label">VERIFIED FINANCIAL FIGURES · PYTHON ENGINE</div><div className="p4-fact-grid"><div><span>Current synthetic cash</span><strong>{rm(m.facts.opening_cash_myr)}</strong></div><div><span>{m.facts.shortfall?'Upcoming funding gap':'Modeled shortfall'}</span><strong className={m.facts.shortfall?'red-text':'green-text'}>{m.facts.shortfall?rm(m.facts.shortfall.amount_myr):'RM 0.00'}</strong></div></div>{m.facts.shortfall&&<p className="p4-fact-desc">{m.facts.shortfall.name} · deadline {m.facts.shortfall.due_date}</p>}<button className="text-link" onClick={()=>onProof(m.context)}>Inspect ProofCard <Icon name="arrow" size={14}/></button></div>}
            {m.trace?.length>0&&<details className="p4-trace"><summary>Tool activity ({m.trace.length})</summary>{m.trace.map((t,j)=><div key={j}><code>{t.name}</code><span>{t.result} · Tier {t.tier}</span></div>)}</details>}
            {m.warning&&<small className="p4-disclosure">{m.warning}</small>}
          </div>)}
          {busy&&<div className="p4-thinking" role="status"><span className="p4-pulse"/> Checking trusted tools and financial assumptions…</div>}
          <div ref={endRef}/>
        </div>
        <form className="p4-composer" onSubmit={e=>{e.preventDefault();send()}}><label htmlFor="copilot-query" className="sr-only">Ask CampusFin</label><textarea id="copilot-query" rows={2} placeholder="Ask what happens if my family's funding is delayed…" maxLength={1200} value={entry} onChange={e=>setEntry(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}}}/><button className="button-primary" disabled={busy||entry.trim().length<2} type="submit">{busy?'Checking…':'Send'} <Icon name="arrow" size={15}/></button></form>
      </article>
      <aside className="p4-side"><EditorialPhoto photo={PHOTOS.copilot} className="cf-copilot-photo"><div className="cf-photo-caption"><span className="cf-caption-dot"/> FINANCIAL CLARITY FOR STUDENT LIFE</div></EditorialPhoto><div className="panel p4-side-card"><div className="eyebrow">ACTIVE SIMULATION</div><h3>{Object.keys(overrides||{}).length?'Custom scenario preview':scenario==='stress'?'Stress case':scenario==='best'?'Best case':'Base case'}</h3><p>For questions with an explicit funding-arrival date, CampusFin previews that date as a temporary scenario. The Horizon and ProofCard use the same calculated assumptions. Nothing is saved to the ledger.</p><button className="button-outline" onClick={()=>navigate('plan')}>Open Scenario Lab <Icon name="arrow" size={14}/></button></div>
        <div className="panel p4-side-card"><div className="eyebrow">WHY YOU CAN TRUST THE MATH</div><h3>Computation stays separate.</h3><ul><li>Python Decimal calculates all money</li><li>Gemini may only call approved read-only tools</li><li>Unknown or generated figures are never shown as trusted facts</li><li>AI cannot settle funds, modify records or send requests</li></ul><button className="text-link" onClick={()=>navigate('audit')}>Review audit history <Icon name="arrow" size={14}/></button></div>
        <div className="p4-safe-note"><Icon name="shield" size={18}/> Synthetic data only · Keep the API on localhost · No real payments or bank connections.</div>
      </aside>
    </section>
  </>;
}
