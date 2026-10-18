import React from 'react';

// A presentation guide, not an automatic scripted simulation.
// Every screen shown is powered by the current API; the guide never invents pass results.
export const JUDGE_STEPS = [
  {page:'home', scenario:'base', number:'01', title:'The financial picture',
    description:'Start with Amina’s synthetic opening cash, tuition deadline and expected family funding.',
    action:'Show Dashboard', tip:'Point out that forecast money is not a bank balance.'},
  {page:'plan', scenario:'stress', number:'02', title:'Watch the deadline collide',
    description:'Stress mode moves the family transfer to 28 October. DeadlineShield recalculates the tuition gap.',
    action:'Inspect Financial Horizon', tip:'Use Show the math to demonstrate the deterministic calculation.'},
  {page:'wow', number:'03', title:'Challenge the future',
    description:'Show EssentialGuard, Decision X-Ray and the Crisis Time Machine in Innovation Lab.',
    action:'Open Innovation Lab', tip:'Explain how the proposed plans protect essential living needs.'},
  {page:'rescue', number:'04', title:'Validate recovery options',
    description:'Compare conditional rescue approaches and see when no confirmed option closes the gap.',
    action:'Open Rescue Planner', tip:'A drafted request is not a confirmed transfer or university approval.'},
  {page:'copilot', number:'05', title:'Let the AI explain',
    description:'Ask about the delayed transfer. Gemini may call read-only financial tools; the numbers remain deterministic.',
    action:'Open AI Copilot', tip:'Live Gemini needs your private key; labeled local guidance remains available.'},
  {page:'wow', number:'06', title:'Hand the controls to the judges',
    description:'Run Chaos Lab’s real synthetic fixture checks, then show audit history for the recorded actions.',
    action:'Run Judge Checks', tip:'Only describe checks as passed after they really complete.'}
];

export function JudgeTour({stepIndex,onNext,onPrevious,onClose,onNavigate,loading}) {
  if(stepIndex===null || stepIndex===undefined)return null;
  const step=JUDGE_STEPS[stepIndex];if(!step)return null;
  return <aside className="cf-judge-tour" aria-label="Guided judge demonstration" aria-live="polite">
    <div className="cf-tour-top"><span><span className="cf-tour-star">✦</span> LIVE JUDGE DEMO</span><button type="button" onClick={onClose} aria-label="Close guided demonstration">×</button></div>
    <div className="cf-tour-progress" role="progressbar" aria-label="Demo step" aria-valuemin={1} aria-valuemax={JUDGE_STEPS.length} aria-valuenow={stepIndex+1}>
      {JUDGE_STEPS.map((_,i)=><span key={i} className={i<=stepIndex?'active':''}/>)}</div>
    <div className="cf-tour-count">SCENE {step.number} / 0{JUDGE_STEPS.length}</div>
    <h2>{step.title}</h2><p>{step.description}</p>
    <div className="cf-tour-tip"><strong>Presenter cue</strong> {step.tip}</div>
    <div className="cf-tour-controls"><button className="cf-tour-back" disabled={stepIndex===0||loading} type="button" onClick={onPrevious}>← Back</button>
      {stepIndex<JUDGE_STEPS.length-1?<button className="cf-tour-next" type="button" disabled={loading} onClick={onNext}>Next scene →</button>:
       <button className="cf-tour-next" type="button" onClick={()=>{onNavigate('audit');onClose();}}>Finish · Audit history →</button>}
    </div>
  </aside>;
}
