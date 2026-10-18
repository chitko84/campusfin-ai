import React, {useCallback,useEffect,useMemo,useRef,useState} from 'react';
import {createRoot} from 'react-dom/client';
import './style.css';
import {RescuePage,TransferTruthPage,RequestsPage,AuditPage} from './PhaseThree.jsx';
import {CopilotPage} from './PhaseFour.jsx';
import {WowLab} from './WowLab.jsx';
import {JudgeTour, JUDGE_STEPS} from './JudgeTour.jsx';
import {PHOTOS,EditorialPhoto,PhotoBanner,PhotoCredits} from './Photography.jsx';

const SHAPES={
 home:<><path d="m3 10 9-7 9 7v10H3V10Z"/><path d="M9 20v-6h6v6"/></>,
 wallet:<><rect x="2" y="5" width="20" height="16" rx="3"/><path d="M2 10h20m-6 5h3"/></>,
 plan:<><path d="M3 18h6v3H3zM15 3h6v7h-6zM4 14l7-7 5 5"/></>,
 bot:<><rect x="4" y="7" width="16" height="14" rx="4"/><path d="M12 7V3m-3 0h6M9 14h.01M15 14h.01M9 18h6"/></>,
 arrow:<path d="M4 12h16m-7-7 7 7-7 7"/>,
 back:<path d="m14 6-6 6 6 6"/>,
 chevron:<path d="m9 18 6-6-6-6"/>,
 alert:<><path d="m12 3 10 18H2L12 3Z"/><path d="M12 9v4m0 4h.01"/></>,
 check:<path d="m5 12 4 4L19 6"/>,
 time:<><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
 info:<><circle cx="12" cy="12" r="10"/><path d="M12 11v6m0-10h.01"/></>,
 calendar:<><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4m10-4v4M3 10h18"/></>,
 shield:<><path d="M12 2 3 6v6c0 5 4 8 9 10 5-2 9-5 9-10V6l-9-4Z"/><path d="m8 12 3 3 5-6"/></>,
 plus:<path d="M12 5v14M5 12h14"/>,
 edit:<><path d="M12 20h9"/><path d="m16 4 4 4-12 12H4v-4L16 4Z"/></>,
 trash:<><path d="M4 7h16M10 4h4M6 7l1 14h10l1-14M10 11v6m4-6v6"/></>,
 close:<path d="M5 5 19 19M19 5 5 19"/>,
 refresh:<><path d="M20 8V3h-5M4 16v5h5"/><path d="M20 8a8 8 0 0 0-14-2M4 16a8 8 0 0 0 14 2"/></>,
 sparkle:<><path d="m12 2 2.5 7.5L22 12l-7.5 2.5L12 22l-2.5-7.5L2 12l7.5-2.5Z"/></>,
 lock:<><rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></>,
 arrowup:<path d="m5 15 7-7 7 7"/>,
 more:<><circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/></>,
};
function Icon({name,size=19}){return <svg viewBox="0 0 24 24" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{SHAPES[name]||SHAPES.info}</svg>}
const rm=n=>'RM '+Number(n||0).toLocaleString('en-MY',{minimumFractionDigits:2,maximumFractionDigits:2});
const short=d=>new Date(d+'T12:00:00').toLocaleDateString('en-GB',{day:'numeric',month:'short'});
const parseError=async r=>{let body=await r.json().catch(()=>({})); let detail=body.detail||body.message||`Request failed (${r.status})`;return typeof detail==='string'?detail:JSON.stringify(detail)};
async function api(path,method='GET',body){const r=await fetch('/api'+path,{method,headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});if(!r.ok)throw Error(await parseError(r));return r.json()}

function Pill({kind='neutral',children}){return <span className={'pill '+kind}>{children}</span>}
function Title({eyebrow,title,subtitle,aside}){return <div className="page-title"><div><div className="kicker">{eyebrow}</div><h1>{title}</h1>{subtitle&&<p>{subtitle}</p>}</div>{aside}</div>}
function Horizon({result,data,onProof,compact=false}){
 if(!result||!data)return <div className="panel"><div className="skeleton-card">Calculating financial horizon…</div></div>;
 const points=result.timeline||[], vals=points.map(p=>Number(p.projected_available)),risk=!!result.next_shortfall;
 const w=740,h=215, top=18,bottom=174, low=Math.min(...vals, -1200),high=Math.max(...vals,1500),span=Math.max(1,high-low);
 const x=i=>32+(w-64)*i/Math.max(1,points.length-1);
 const y=v=>top+(high-v)/span*(bottom-top);
 const path=points.map((p,i)=>(i?'L':'M')+x(i).toFixed(1)+' '+y(Number(p.projected_available)).toFixed(1)).join(' ');
 const z=y(0);
 const billEvents=data.obligations.map(o=>({...o,idx:points.findIndex(p=>p.date===o.due_date)})).filter(o=>o.idx>=0);
 const riskDay=result.next_shortfall?.due_date;
 return <section className={'horizon-v2 '+(compact?'horizon-short':'')}>
  <div className="section-flex"><div><div className="eyebrow">FINANCIAL HORIZON</div><h3>Your money, across time.</h3></div><Pill kind={risk?'danger':'success'}>{risk?'Deadline at risk':'On track'}</Pill></div>
  <p className="hint">Change a funding date to see your projected financial position update.</p>
  <div className="graph-scroll"><svg viewBox={`0 0 ${w} ${h}`} role="img" aria-label={'Projected balance timeline with '+(risk?'a funding shortfall':'no shortfall') }>
   <defs><linearGradient id="horizonFade" x1="0" x2="0" y1="0" y2="1"><stop stopColor={risk?'#c0392b':'#0e7c7b'} stopOpacity=".16"/><stop offset="1" stopColor="#fff" stopOpacity="0"/></linearGradient></defs>
   {[0,500,1000,1500].filter(v=>v>=low&&v<=high).map(v=><g key={v}><line x1="31" x2="710" y1={y(v)} y2={y(v)} stroke="#DFE7E3" strokeDasharray="4 6"/><text x="30" y={y(v)-6} fontSize="10" textAnchor="start" fill="#7e8b87">{v===0?'0':rm(v).replace('RM ','')}</text></g>)}
   <path d={`${path} L ${x(points.length-1)} ${bottom+4} L 32 ${bottom+4} Z`} fill="url(#horizonFade)"/>
   <path d={path} fill="none" stroke={risk?'#c0392b':'#0e7c7b'} strokeWidth="3.4" strokeLinejoin="round" strokeLinecap="round"/>
   {billEvents.map(e=><g key={e.id}><line x1={x(e.idx)} x2={x(e.idx)} y1="15" y2="179" stroke={e.due_date===riskDay?'#C0392B':'#A3B0AA'} strokeDasharray="3 6"/><circle cx={x(e.idx)} cy={y(vals[e.idx])} r="6" stroke="white" strokeWidth="3" fill={e.due_date===riskDay?'#C0392B':'#0E7C7B'}/><text x={x(e.idx)} y="198" textAnchor="middle" fontSize="11" fontWeight="700" fill="#667775">{short(e.due_date)}</text><text x={x(e.idx)} y="212" textAnchor="middle" fontSize="10" fill="#85938f">{e.name}</text></g>)}
   <text x="32" y="198" fontSize="11" fill="#667775">{short(points[0]?.date)}</text><text x="710" y="198" fontSize="11" fill="#667775" textAnchor="end">{short(points.at(-1)?.date)}</text>
   {z>=top&&z<=bottom&&<line x1="32" x2="710" y1={z} y2={z} stroke="#8b9996" opacity=".5" strokeDasharray="2 5"/>}
  </svg></div>
  <div className="graph-footer"><span><span className="small-dot"/> Projected funds (not bank balance)</span><button type="button" className="text-link" onClick={onProof}><Icon name="info" size={15}/> Show the math</button></div>
 </section>
}

function Dialog({title,onClose,children,wide=false}){useEffect(()=>{const k=e=>{if(e.key==='Escape')onClose()};document.addEventListener('keydown',k);return()=>document.removeEventListener('keydown',k)},[onClose]);return <div className="scrim" onMouseDown={e=>e.target===e.currentTarget&&onClose()}><section role="dialog" aria-modal="true" aria-label={title} className={'dialog '+(wide?'dialog-wide':'')}><header className="dialog-header"><div><div className="kicker">CAMPUSFIN AI · DEMO</div><h2>{title}</h2></div><button className="icon-btn" onClick={onClose} aria-label="Close dialog"><Icon name="close"/></button></header><div className="dialog-body">{children}</div></section></div>}
function Field({label,children,help}){return <label className="form-field"><span>{label}</span>{children}{help&&<small>{help}</small>}</label>}
const formatState=status=>status.replace('_',' ');
function FundingEditor({item,onClose,onSave,onDelete,busy,asOf}){
 const original=item||{name:'',currency:'MYR',amount:'',fee_deducted:'0',status:'expected',arrivals:{best:'2026-10-19',base:'2026-10-19',stress:'2026-10-19'}};
 const [value,setValue]=useState(()=>JSON.parse(JSON.stringify(original))); const locked=item?.status==='settled';
 const set=(key,next)=>setValue(p=>({...p,[key]:next}));
 const setDate=(key,next)=>setValue(p=>({...p,arrivals:{...p.arrivals,[key]:next}}));
 const submit=e=>{e.preventDefault();onSave({name:value.name,amount:value.amount,currency:value.currency,fee_deducted:value.fee_deducted||'0',status:value.status,arrivals:value.arrivals})};
 return <Dialog title={item?'Funding details':'Add funding source'} onClose={onClose}><form className="editor-form" onSubmit={submit}>
  {locked&&<div className="notice-v2"><Icon name="lock"/> Settled historical income is included in the opening balance and is locked to prevent double-counting.</div>}
  <Field label="Source name"><input value={value.name} required minLength={2} maxLength={70} onChange={e=>set('name',e.target.value)} disabled={locked}/></Field>
  <div className="form-grid"><Field label="Amount"><input inputMode="decimal" type="number" step="0.01" min="0" required value={value.amount} onChange={e=>set('amount',e.target.value)} disabled={locked}/></Field><Field label="Currency"><select value={value.currency} onChange={e=>set('currency',e.target.value)} disabled={locked}><option value="MYR">MYR</option><option value="USD">USD</option></select></Field></div>
  <div className="form-grid"><Field label="Fee deducted from amount"><input inputMode="decimal" type="number" min="0" step="0.01" value={value.fee_deducted||'0'} onChange={e=>set('fee_deducted',e.target.value)} disabled={locked}/></Field><Field label="Funding status"><select value={value.status} onChange={e=>set('status',e.target.value)} disabled={locked}><option value="expected">Expected</option><option value="in_transit">In transit</option>{locked&&<option value="settled">Settled</option>}</select></Field></div>
  <div className="form-panel"><h4>Estimated arrival window</h4><p>Best ≤ Base ≤ Stress. These are assumptions, not probability forecasts.</p><div className="form-grid form-three">{['best','base','stress'].map(s=><Field key={s} label={s[0].toUpperCase()+s.slice(1)}><input type="date" required value={value.arrivals[s]} min={asOf} onChange={e=>setDate(s,e.target.value)} disabled={locked}/></Field>)}</div></div>
  <div className="form-actions">{item&&!locked&&<button type="button" className="danger-outline" disabled={busy} onClick={()=>onDelete(item.id)}><Icon name="trash" size={15}/> Delete</button>}<button type="button" className="button-muted" onClick={onClose}>Cancel</button>{!locked&&<button className="button-primary" disabled={busy}>{busy?'Saving…':'Save funding'}</button>}</div>
 </form></Dialog>
}
function ObligationEditor({item,onClose,onSave,onDelete,busy}){
 const [v,setV]=useState(item||{name:'',amount:'',currency:'MYR',due_date:'2026-10-25',priority:3});
 const set=(key,next)=>setV(p=>({...p,[key]:next}));
 return <Dialog title={item?'Edit obligation':'Add obligation'} onClose={onClose}><form className="editor-form" onSubmit={e=>{e.preventDefault();onSave(v)}}>
  <Field label="Payment title"><input value={v.name} required minLength={2} maxLength={70} onChange={e=>set('name',e.target.value)}/></Field>
  <div className="form-grid"><Field label="Amount (MYR)"><input type="number" min="0.01" required step="0.01" value={v.amount} onChange={e=>set('amount',e.target.value)}/></Field><Field label="Priority"><select value={v.priority} onChange={e=>set('priority',Number(e.target.value))}><option value={1}>Urgent</option><option value={2}>High</option><option value={3}>Normal</option></select></Field></div>
  <Field label="Payment deadline"><input type="date" required value={v.due_date} onChange={e=>set('due_date',e.target.value)}/></Field>
  <div className="notice-v2"><Icon name="info"/> Editing an obligation changes only the forecast; no payment is made.</div>
  <div className="form-actions">{item&&<button type="button" className="danger-outline" onClick={()=>onDelete(item.id)} disabled={busy}><Icon name="trash" size={15}/> Delete</button>}<button className="button-muted" type="button" onClick={onClose}>Cancel</button><button className="button-primary" disabled={busy}>{busy?'Saving…':'Save obligation'}</button></div>
 </form></Dialog>
}
function Proof({proof,onClose}){return <Dialog title="ProofCard · Show the math" onClose={onClose} wide><div className="proof-top"><div className="eyebrow">DETERMINISTIC FINANCIAL ENGINE</div>{proof.status==='at_risk'?<><strong>{rm(proof.gap)}</strong><span>Projected shortage · {short(proof.due_date)}</span></>:<><strong className="green-text">No shortfall</strong><span>All included obligations are covered under these assumptions.</span></>}</div>{proof.rows?.length>0&&<div className="proof-rows"><h4>Inputs and calculation trace</h4>{proof.rows.map((r,i)=><div key={i} className="proof-row"><div><strong>{r.label}</strong><small>{short(r.date)} · {r.kind}</small></div><b>{Number(r.signed_amount)>=0?'+':''}{rm(r.signed_amount)}</b></div>)}<div className="proof-row total"><b>Projected available</b><b>{rm(proof.projected_available)}</b></div></div>}<div className="proof-assumptions"><h4>Model assumptions</h4>{proof.assumptions?.map((a,i)=><p key={i}>• {a}</p>)}</div><div className="note-small">Not a real bank statement. All values are synthetic. Explanations are computed from stored records, not generated by Gemini.</div></Dialog>}

function App(){
 const [data,setData]=useState(null),[result,setResult]=useState(null),[comparison,setComparison]=useState(null),[scenario,setScenario]=useState('base'),[overrides,setOverrides]=useState({}),[page,setPage]=useState('home'),[tab,setTab]=useState('funding');
 const [modal,setModal]=useState(null),[proof,setProof]=useState(null),[error,setError]=useState(''),[loading,setLoading]=useState(true),[saving,setSaving]=useState(false),[resetConfirm,setResetConfirm]=useState(false);
 const [tourIndex,setTourIndex]=useState(null);
 const activeRequest=useRef(0);
 const fetchState=useCallback(async(s='base',o={})=>{
  const id=++activeRequest.current;setLoading(true);
  try{const [d,c,r]=await Promise.all([api('/demo'),api('/compare'),api('/forecast','POST',{scenario:s,arrival_overrides:o})]);if(id!==activeRequest.current)return;setData(d);setComparison(c);setResult(r);setError('');}
  catch(e){if(id===activeRequest.current)setError(e.message)}finally{if(id===activeRequest.current)setLoading(false)}
 },[]);
 useEffect(()=>{fetchState()},[fetchState]);
 const selectScenario=s=>{setScenario(s);setOverrides({});fetchState(s,{})};
 const onDateChange=value=>{if(!value)return;const o={...overrides,family:value};setOverrides(o);fetchState(scenario,o)};
 const currentDate=overrides.family||data?.funding.find(f=>f.id==='family')?.arrivals[scenario]||'';
 const atRisk=!!result?.next_shortfall;
 const showProof=async(ctx)=>{try{const s=ctx?.scenario||scenario, o=ctx?.arrival_overrides||overrides;const p=await api('/proof','POST',{scenario:s,arrival_overrides:o});setProof(p);setError('')}catch(e){setError(e.message)}};
 const previewChatScenario=ctx=>{if(ctx?.source!=='chat_hypothetical')return;setScenario(ctx.scenario);setOverrides(ctx.arrival_overrides);fetchState(ctx.scenario,ctx.arrival_overrides)};
 const save=async(kind,item,payload)=>{setSaving(true);try{const path=kind==='funding'?'/funding':'/obligations';await api(path+(item?'/'+item.id:''),item?'PUT':'POST',payload);setModal(null);setScenario('base');setOverrides({});await fetchState('base',{})}catch(e){setError(e.message)}finally{setSaving(false)}};
 const del=async(kind,item)=>{if(!window.confirm('Delete this synthetic demo record?'))return;setSaving(true);try{await api((kind==='funding'?'/funding/':'/obligations/')+item,'DELETE');setModal(null);setScenario('base');setOverrides({});await fetchState('base',{})}catch(e){setError(e.message)}finally{setSaving(false)}};
 const reset=async()=>{try{await api('/reset','POST');setResetConfirm(false);setScenario('base');setOverrides({});setPage('home');setError('');await fetchState('base',{})}catch(e){setError(e.message)}};
 const navigate=p=>{setPage(p);setError('');window.scrollTo?.({top:0,behavior:window.matchMedia?.('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'})};
 const visitTourStep=i=>{const step=JUDGE_STEPS[i];if(!step){setTourIndex(null);return;}if(step.scenario)selectScenario(step.scenario);navigate(step.page);setTourIndex(i)};
 const beginTour=()=>visitTourStep(0);
 const nav=[{key:'home',label:'Home',icon:'home'},{key:'funding',label:'Funding',icon:'wallet'},{key:'plan',label:'Plan',icon:'plan'},{key:'rescue',label:'Rescue',icon:'shield'},{key:'wow',label:'Innovation Lab',icon:'plan'},{key:'copilot',label:'Copilot',icon:'bot'},{key:'transfers',label:'Transfers',icon:'arrow'},{key:'requests',label:'Requests',icon:'wallet'},{key:'audit',label:'Activity',icon:'time'}];
 const mobileNav=nav.filter(n=>['home','funding','plan','rescue','copilot'].includes(n.key));
 const loadDelayedRescue=()=>{selectScenario('stress');navigate('rescue')};
 const useDelayedLab=()=>{selectScenario('stress')};
 const family=data?.funding.find(x=>x.id==='family');
 return <div className="app"><a className="cf-skip-link" href="#campusfin-content">Skip to main content</a>
  <aside className="sidebar"><div className="brand"><span className="brand-symbol">◈</span><span>CampusFin <em>AI</em></span></div><p className="side-tag">PREDICT. RESCUE. PROVE.</p><div className="side-category">WORKSPACE</div><nav aria-label="Desktop navigation">{nav.map(n=><button key={n.key} className={'nav-button '+(page===n.key?'active':'')} onClick={()=>navigate(n.key)} aria-current={page===n.key?'page':undefined}><Icon name={n.icon}/>{n.label}</button>)}</nav><div className="side-category side-category-bottom">SAFETY & CONTROLS</div><button className={'nav-button '+(page==='settings'?'active':'')} onClick={()=>navigate('settings')}><Icon name="shield"/>Demo settings</button><div className="sidebar-foot"><Icon name="lock"/><div><b>Private local simulation</b><small>No connected accounts or transfers</small></div></div></aside>
  <main className="main" id="campusfin-content" tabIndex="-1"><header className="topbar"><div className="mobile-brand"><span className="brand-symbol">◈</span> CampusFin <em>AI</em></div><div className="breadcrumb">CAMPUSFIN <span>/</span> {page==='settings'?'Demo Settings':nav.find(n=>n.key===page)?.label}</div><div className="top-right"><button className="cf-demo-launch" type="button" onClick={beginTour} aria-label="Launch guided six-step judge demonstration"><Icon name="sparkle" size={15}/> <span>Guided demo</span></button><span className="demo-indicator"><span/> SYNTHETIC DATA</span><span className="profile-bubble">AM</span></div></header>
  <div className="content phase2">
   {error&&<div className="alert-error" role="alert"><Icon name="alert"/>{error}<button className="icon-btn" aria-label="Dismiss error" onClick={()=>setError('')}><Icon name="close" size={15}/></button></div>}
   {page==='home'&&<>
    <div className="intro cf-intro"><div><div className="kicker">YOUR FINANCIAL HORIZON · CAMPUSFIN AI</div><h1>Everything in sight.<br/><em>Even what's ahead.</em></h1><p>Welcome back, Amina. Your financial horizon starts here.</p><div className="cf-intro-actions"><button className="button-outline" onClick={beginTour}><Icon name="sparkle" size={16}/> Launch judge demo</button><button className="button-primary" onClick={()=>navigate('plan')}>Explore your future <Icon name="arrow" size={16}/></button><span>Predict. Rescue. Prove.</span></div></div><EditorialPhoto photo={PHOTOS.hero} className="cf-home-hero" loading="eager"><div className="cf-photo-caption"><span className="cf-caption-dot"/> STUDENT LIFE / GLOBAL POSSIBILITIES</div></EditorialPhoto></div>
    <div className="hero-grid-v2"><div className="main-balance"><div className="section-flex"><span>AVAILABLE CASH · AS OF 17 OCT</span><Icon name="wallet" size={21}/></div><h2>{rm(data?.opening_cash)}</h2><div className="balance-actions"><span>Local account · MYR</span><button onClick={()=>navigate('funding')}>Manage funding <Icon name="arrow" size={15}/></button></div><div className="balance-decoration"/></div><div className={'shield-card '+(atRisk?'warning':'clear')}><div className="section-flex"><span><Icon name="shield" size={18}/> DeadlineShield</span><Pill kind={atRisk?'danger':'success'}>{atRisk?'Attention':'Covered'}</Pill></div><h2>{atRisk?rm(result?.next_shortfall?.amount):'On track.'}</h2><p>{atRisk?`Your ${result.next_shortfall.name.toLowerCase()} has an unfunded gap by ${short(result.next_shortfall.due_date)}.`:'All listed payments are covered under this scenario.'}</p><button className="text-link" onClick={()=>navigate('plan')}>{atRisk?'Explore the shortfall':'Test a different scenario'} <Icon name="arrow" size={16}/></button></div></div>
    <div className="dashboard-main"><div className="panel horizon-card"><Horizon result={result} data={data} onProof={showProof}/><div className="scenario-bar"><div><b>What if family support arrives late?</b><span>Compare funding timelines instantly</span></div><div className="segmented">{['base','stress'].map(s=><button key={s} className={scenario===s&&!overrides.family?'active':''} onClick={()=>selectScenario(s)}>{s==='base'?'On time':'Delayed'}</button>)}</div></div></div><div className="dashboard-side"><div className="panel upcoming-card"><div className="section-flex"><h3>Upcoming payments</h3><button className="text-link" onClick={()=>{setTab('obligations');navigate('funding')}}>View all <Icon name="arrow" size={15}/></button></div>{data?.obligations.map(o=><div className="list-row" key={o.id}><span className="item-icon"><Icon name="calendar" size={16}/></span><div><b>{o.name}</b><small>Due {short(o.due_date)}</small></div><strong>{rm(o.amount)}</strong></div>)}</div><div className="insight-panel"><EditorialPhoto className="cf-insight-photo" photo={PHOTOS.companion} overlay={false}/><div className="eyebrow">THE IDEA BEHIND CAMPUSFIN</div><h3>Money has a schedule. <em>So do your deadlines.</em></h3><p>One delayed transfer can change everything. See the impact while there's still time to act.</p><button className="button-primary" onClick={()=>navigate('wow')}>Enter Innovation Lab <Icon name="arrow" size={16}/></button></div></div></div>
    </>}
   {page==='funding'&&<>
    <Title eyebrow="YOUR FINANCIAL FOUNDATION" title="Funding & commitments" subtitle="Manage the synthetic records that power every financial forecast." aside={<button className="button-outline" onClick={()=>setResetConfirm(true)}><Icon name="refresh" size={16}/> Reset demo</button>}/>
    <PhotoBanner photo={PHOTOS.funding} compact kicker="FUNDING / FROM MANY PLACES" title="Support crosses borders. Your plan should connect it." body="Bring family transfers, scholarships and payment commitments into one view."/>
    <div className="tab-row"><button className={tab==='funding'?'active':''} onClick={()=>setTab('funding')}>Funding sources</button><button className={tab==='obligations'?'active':''} onClick={()=>setTab('obligations')}>Payment obligations</button></div>
    {tab==='funding'?<div className="panel records-panel"><div className="section-flex"><div><h3>Funding sources</h3><p>Expected, in-transit and settled (locked) historical income.</p></div><button className="button-primary" onClick={()=>setModal({kind:'funding',item:null})}><Icon name="plus" size={16}/> Add source</button></div><div className="record-list">{data?.funding.map(f=><button key={f.id} className="record-tile" onClick={()=>setModal({kind:'funding',item:f})}><span className="record-symbol"><Icon name="wallet" size={19}/></span><div className="record-data"><strong>{f.name}</strong><small>{formatState(f.status)} · {short(f.arrivals[scenario])}</small></div><div className="record-amount"><strong>{f.currency} {Number(f.amount).toFixed(2)}</strong><small>{f.status==='settled'?'Included in opening cash':'Synthetic estimate'}</small></div><Icon name="chevron" size={17}/></button>)}</div></div>:<div className="panel records-panel"><div className="section-flex"><div><h3>Payment obligations</h3><p>Upcoming bills and deadlines used by DeadlineShield.</p></div><button className="button-primary" onClick={()=>setModal({kind:'obligation',item:null})}><Icon name="plus" size={16}/> Add bill</button></div><div className="record-list">{data?.obligations.map(o=><button key={o.id} className="record-tile" onClick={()=>setModal({kind:'obligation',item:o})}><span className="record-symbol"><Icon name="calendar" size={19}/></span><div className="record-data"><strong>{o.name}</strong><small>Due {short(o.due_date)} · Priority {o.priority}</small></div><div className="record-amount"><strong>{rm(o.amount)}</strong><small>Projected obligation</small></div><Icon name="chevron" size={17}/></button>)}</div></div>}
    <div className="notice-v2"><Icon name="info"/><span>All changes are saved locally to SQLite. This is a fictional student dataset, not a bank-linked account. Refresh to confirm data persists.</span></div>
   </>}
   {page==='plan'&&<>
    <Title eyebrow="CAMPUSFIN DECISION LAB" title="Explore your financial future." subtitle="Simulate changes to funding arrivals and inspect the evidence behind each outcome." aside={<Pill kind="neutral">Scenario simulation</Pill>}/>
    <PhotoBanner photo={PHOTOS.planning} compact kicker="FINANCIAL HORIZON / WHAT-IF LAB" title="Make room for every possible future." body="Move a funding date and watch the forecast change — before a real deadline arrives."/>
    <div className="panel scenario-workspace"><div className="section-flex"><div><h3>Scenario Lab</h3><p>Choose an assumption set. Each simulation uses the latest edited records.</p></div><Pill kind="neutral">No money moves</Pill></div><div className="scenario-grid">{['best','base','stress'].map(s=>{const item=comparison?.[s],risk=item?.next_shortfall;return <button className={'scenario-choice '+(scenario===s?'active':'')} key={s} onClick={()=>selectScenario(s)}><span className="scenario-choice-top"><b>{s==='best'?'Best case':s==='base'?'Base case':'Stress case'}</b>{scenario===s&&<Icon name="check" size={16}/>}</span><strong className={risk?'red-text':'green-text'}>{risk?rm(risk.amount)+' gap':'Covered'}</strong><small>{s==='stress'?'Later funding arrival assumptions':s==='best'?'Earliest funding arrival assumptions':'Expected funding arrivals'}</small></button>})}</div><div className="scenario-editor"><div><div className="eyebrow">LIVE SIMULATION</div><h4>Move the family remittance date.</h4><p>One change can shift the outcome of your tuition deadline.</p></div><div className="date-input-box"><label htmlFor="dateOverride">Assumed arrival date</label><input id="dateOverride" type="date" min="2026-10-18" max="2026-12-31" value={currentDate} onChange={e=>onDateChange(e.target.value)}/><small>Changes this scenario only — does not edit the funding record.</small></div></div></div>
    <div className="horizon-slot-v2"><div className="panel horizon-card"><Horizon result={result} data={data} onProof={showProof}/></div><div className={'result-panel '+(atRisk?'warning':'clear')}><div className="eyebrow">DEADLINESHIELD · {scenario.toUpperCase()}</div><div className="status-icon"><Icon name={atRisk?'alert':'shield'} size={22}/></div><h3>{atRisk?'A deadline needs attention.':'Your current plan is covered.'}</h3><div className="major-value">{atRisk?rm(result?.next_shortfall?.amount):'RM 0.00'}</div><p>{atRisk?`Projected ${result.next_shortfall.name.toLowerCase()} funding gap by ${short(result.next_shortfall.due_date)}.`:'No projected deficit for the included obligations.'}</p><button className="button-outline" onClick={showProof}>Show the math <Icon name="arrow" size={16}/></button><button className="button-primary p3-full" onClick={()=>navigate('rescue')}>Explore recovery options <Icon name="arrow" size={16}/></button></div></div>
    <div className="wow-rescue-callout"><div><span className="wow-kicker">CAMPUSFIN INNOVATION STUDIO</span><h3>Challenge a future before it becomes real.</h3><p>Five interactive tests: living reserves, decision evidence, four futures, chaos checks and FX shocks.</p></div><button className="button-primary" onClick={()=>navigate('wow')}>Explore Innovation Lab <Icon name="arrow" size={15}/></button></div><div className="p3-plan-actions"><button className="button-primary" onClick={()=>navigate('rescue')}>Launch Rescue Planner <Icon name="arrow" size={16}/></button><button className="button-outline" onClick={()=>navigate('transfers')}>Compare transfer costs <Icon name="arrow" size={16}/></button></div><div className="comparison-section"><div className="section-flex"><div><h3>Three possible futures</h3><p>Useful assumptions — not statistically estimated probabilities.</p></div></div><div className="compare-grid">{['best','base','stress'].map(s=>{const f=comparison?.[s];return <div key={s} className="compare-card"><div className="eyebrow">{s.toUpperCase()} CASE</div><h4>{f?.next_shortfall?rm(f.next_shortfall.amount)+' gap':'Obligations covered'}</h4><p>{s==='stress'?'Assumes later funding arrivals.':s==='base'?'Uses current expected dates.':'Assumes earliest funding arrivals.'}</p><button className="text-link" onClick={()=>selectScenario(s)}>Inspect <Icon name="arrow" size={15}/></button></div>})}</div></div>
    <div className="notice-v2"><Icon name="info"/> Expected funding, date windows, FX rates and forecasts are assumptions. They are not guarantees of financial availability.</div>
   </>}
   {page==='wow'&&<WowLab api={api} Icon={Icon} Title={Title} Pill={Pill} rm={rm} short={short} scenario={scenario} overrides={overrides} onError={setError} onDelayed={useDelayedLab} navigate={navigate}/>}
   {page==='rescue'&&<RescuePage api={api} Icon={Icon} Title={Title} Pill={Pill} rm={rm} short={short} scenario={scenario} overrides={overrides} onError={setError} onDelayed={loadDelayedRescue} navigate={navigate} onProof={showProof}/>}
   {page==='transfers'&&<TransferTruthPage api={api} Icon={Icon} Title={Title} Pill={Pill} rm={rm} onError={setError}/>}
   {page==='requests'&&<RequestsPage api={api} Icon={Icon} Title={Title} Pill={Pill} rm={rm} scenario={scenario} overrides={overrides} onError={setError} onDelayed={()=>{selectScenario('stress');navigate('requests')}} navigate={navigate}/>}
   {page==='audit'&&<AuditPage api={api} Icon={Icon} Title={Title} Pill={Pill} onError={setError}/>}
   {page==='copilot'&&<CopilotPage api={api} Icon={Icon} Title={Title} Pill={Pill} rm={rm} scenario={scenario} overrides={overrides} navigate={navigate} onError={setError} onProof={showProof} onApplyScenario={previewChatScenario}/>}
   {page==='settings'&&<><Title eyebrow="DEMO CONTROLS" title="Your private sandbox." subtitle="The Phase 5 prototype uses a fictional student and local SQLite persistence."/><PhotoBanner photo={PHOTOS.campus} compact kicker="CAMPUSFIN / BUILT AROUND STUDENT LIFE" title="A little more certainty, wherever you study." body="This is a demonstration with synthetic student data. No one pictured represents a CampusFin account."/><div className="panel settings-card"><div><h3>Reset Amina's demo</h3><p>Restore the original funding sources, dates and tuition records. This cannot be undone.</p></div><button className="button-outline" onClick={()=>setResetConfirm(true)}><Icon name="refresh" size={17}/> Reset synthetic data</button></div><div className="p3-plan-actions"><button className="button-outline" onClick={()=>navigate('requests')}>Funding requests</button><button className="button-outline" onClick={()=>navigate('audit')}>Audit history</button><button className="button-outline" onClick={()=>navigate('transfers')}>TransferTruth</button></div><div className="notice-v2"><Icon name="shield"/> No authentication, production-grade security, live payments or banking integration. Keep this prototype on localhost.</div><PhotoCredits/></>}
   {loading&&<div className="loading-indicator" role="status"><span/> Recalculating your financial horizon…</div>}
   <footer className="footer"><span>CampusFin AI · Predict. Rescue. Prove.</span><span>Phase 5 · Judge demo · Synthetic data only</span></footer>
  </div></main>
  <JudgeTour stepIndex={tourIndex} onNext={()=>visitTourStep(tourIndex+1)} onPrevious={()=>visitTourStep(Math.max(0,tourIndex-1))} onClose={()=>setTourIndex(null)} onNavigate={navigate} loading={loading}/>
  <nav className="bottom-nav" aria-label="Mobile navigation">{mobileNav.map(n=><button key={n.key} onClick={()=>navigate(n.key)} className={page===n.key?'active':''}><Icon name={n.icon}/><span>{n.label}</span></button>)}</nav>
  {modal?.kind==='funding'&&<FundingEditor key={modal.item?.id||'new-f'} item={modal.item} asOf={data?.as_of} busy={saving} onClose={()=>setModal(null)} onSave={v=>save('funding',modal.item,v)} onDelete={id=>del('funding',id)}/>}
  {modal?.kind==='obligation'&&<ObligationEditor key={modal.item?.id||'new-o'} item={modal.item} busy={saving} onClose={()=>setModal(null)} onSave={v=>save('obligation',modal.item,v)} onDelete={id=>del('obligation',id)}/>}
  {proof&&<Proof proof={proof} onClose={()=>setProof(null)}/>}
  {resetConfirm&&<Dialog title="Reset fictional demo?" onClose={()=>setResetConfirm(false)}><p className="reset-copy">This will restore Amina's original funding sources and tuition deadlines and discard all saved local changes. It will not affect any real financial accounts.</p><div className="form-actions"><button className="button-muted" onClick={()=>setResetConfirm(false)}>Cancel</button><button className="button-primary" onClick={reset}>Reset demo data</button></div></Dialog>}
 </div>
}
createRoot(document.getElementById('root')).render(<App/>);
