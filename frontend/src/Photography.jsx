import React from 'react';

// Photos are hosted by Pexels and used in accordance with the Pexels License.
// If an image is unavailable/offline, the original gradient design remains legible.
// These are editorial images, not photographs of Amina or actual CampusFin customers.
const img=(id,width=1500)=>`https://images.pexels.com/photos/${id}/pexels-photo-${id}.jpeg?auto=compress&cs=tinysrgb&w=${width}`;
export const PHOTOS={
 hero:{local:"/photos/hero.jpg",src:img(6684514),alt:'University students collaborating around a laptop',source:'https://www.pexels.com/photo/a-college-student-using-a-laptop-6684514/',credit:'Andy Barbour'},
 companion:{local:"/photos/companion.jpg",src:img(5940711,1100),alt:'Student studying with a laptop in a bright university library',source:'https://www.pexels.com/photo/concentrated-young-diverse-students-using-laptops-during-lesson-in-library-5940711/',credit:'Kampus Production'},
 funding:{local:"/photos/funding.jpg",src:img(5940829),alt:'University students reviewing a project together',source:'https://www.pexels.com/photo/multiethnic-students-doing-research-together-in-library-5940829/',credit:'Kampus Production'},
 planning:{local:"/photos/planning.jpg",src:img(7972948),alt:'Students working outdoors together with their laptops',source:'https://www.pexels.com/photo/three-young-people-studying-together-outdoors-with-laptops-7972948/',credit:'George Pak'},
 rescue:{local:"/photos/rescue.jpg",src:img(8199167),alt:'Student concentrating on a laptop during a lecture',source:'https://www.pexels.com/photo/student-using-laptop-8199167/',credit:'Yan Krukau'},
 transfers:{local:"/photos/transfers.jpg",src:img(7102),alt:'Desk with laptop and notebook during study',source:'https://www.pexels.com/photo/person-sitting-in-front-of-the-laptop-computer-7102/',credit:'Startup Stock Photos'},
 family:{local:"/photos/family.jpg",src:img(5965686,1100),alt:'Two students studying on university steps',source:'https://www.pexels.com/photo/cheerful-diverse-students-with-gadgets-on-stairs-5965686/',credit:'Charlotte May'},
 copilot:{local:"/photos/copilot.jpg",src:img(16420237,1100),alt:'Student working independently at a university library',source:'https://www.pexels.com/photo/a-student-sitting-in-a-library-and-with-a-laptop-and-studying-16420237/',credit:'Ludovic Delot'},
 campus:{local:"/photos/campus.jpg",src:img(6146987,1200),alt:'Students studying outdoors with laptops and notebooks',source:'https://www.pexels.com/photo/focused-multiethnic-students-with-laptop-studying-together-on-campus-of-university-6146987/',credit:'Keira Burton'},
};

export function EditorialPhoto({photo,className='',children,loading='lazy',overlay=true}){
 return <div className={'editorial-photo '+className}>
   <img className="editorial-photo-img" src={photo.local} alt={photo.alt} loading={loading} decoding="async" onError={e=>{const el=e.currentTarget;if(el.dataset.fallback!=="remote"){el.dataset.fallback="remote";el.src=photo.src;}else{el.hidden=true}}} />
   {overlay&&<div className="editorial-photo-shade" aria-hidden="true"/>}
   {children&&<div className="editorial-photo-content">{children}</div>}
 </div>;
}
export function PhotoBanner({photo,kicker,title,body,compact=false}){
 return <section className={'cf-story-banner '+(compact?'cf-story-banner-compact':'')}>
  <div className="cf-story-copy"><span className="cf-story-kicker">{kicker}</span><h2>{title}</h2><p>{body}</p><span className="cf-photo-disclaimer">Illustrative student-life photography</span></div>
  <EditorialPhoto className="cf-story-image" photo={photo}/>
 </section>;
}

export function PhotoCredits(){return <div className="cf-credits"><h3>Photography sources</h3><p>Illustrative photos from Pexels, used under the <a target="_blank" rel="noopener noreferrer" href="https://www.pexels.com/legal-pages/license/">Pexels License</a>. People shown are stock models or photographed students, not Amina, CampusFin users, sponsors or endorsers.</p><div className="cf-credit-grid">{Object.entries(PHOTOS).map(([key,p])=><a key={key} href={p.source} target="_blank" rel="noopener noreferrer">{key.replace(/^./,m=>m.toUpperCase())} — {p.credit} ↗</a>)}</div></div>}
