# Photo sources and licensing — CampusFin AI (Phase 4 photo edition)

Photos are credited below and used as remote image URLs in `frontend/src/Photography.jsx`. Their pages label them free to use under the Pexels License. License: https://www.pexels.com/legal-pages/license/ . They are **editorial illustrative imagery** only; the people in the images are not the fictional student Amina, actual customers, team members, or endorsers of CampusFin AI. The prototype must not imply otherwise.

IMPORTANT — ENVIRONMENT LIMITATION: This build environment could not download the original image binaries. Therefore the ZIP includes the image URLs, visual implementations, responsive styling and local gradient fallback, **not offline photo binaries**. Images require internet when viewing the app. For an offline demo, run `py scripts/download_photos.py` once on your internet-connected Windows PC. This downloads verified JPEGs to `frontend/public/photos/`. The app automatically tries local cached JPGs first, then remotely hosted Pexels images, then uses its visual gradient fallback if both fail. Do not claim the ZIP contains downloaded stock photo binaries.

| Photo / placement | Photographer | Source page |
| --- | --- | --- |
| Homepage hero | Andy Barbour | https://www.pexels.com/photo/a-college-student-using-a-laptop-6684514/ |
| Homepage insight | Kampus Production | https://www.pexels.com/photo/concentrated-young-diverse-students-using-laptops-during-lesson-in-library-5940711/ |
| Funding page story | Kampus Production | https://www.pexels.com/photo/multiethnic-students-doing-research-together-in-library-5940829/ |
| Scenario Lab banner | George Pak | https://www.pexels.com/photo/three-young-people-studying-together-outdoors-with-laptops-7972948/ |
| Rescue page backdrop | Yan Krukau | https://www.pexels.com/photo/student-using-laptop-8199167/ |
| TransferTruth backdrop | Startup Stock Photos | https://www.pexels.com/photo/person-sitting-in-front-of-the-laptop-computer-7102/ |
| FamilyBridge banner | Charlotte May | https://www.pexels.com/photo/cheerful-diverse-students-with-gadgets-on-stairs-5965686/ |
| Copilot side photography | Ludovic Delot | https://www.pexels.com/photo/a-student-sitting-in-a-library-and-with-a-laptop-and-studying-16420237/ |
| Demo settings banner | Keira Burton | https://www.pexels.com/photo/focused-multiethnic-students-with-laptop-studying-together-on-campus-of-university-6146987/ |

**License summary:** Pexels offers photos for free use on websites and apps, including commercial use; attribution is appreciated. Do not imply people pictured endorse your service, do not use images as trademarks, and avoid problematic depictions. Verify each source page if you change the URLs.

### QA checklist
- [ ] With internet: images render and crop properly at 390px and 1440px
- [ ] Without internet: gradient fallbacks show and all text remains readable
- [ ] Landing hero, funding, planning, rescue, transfer, FamilyBridge, Copilot and settings displays checked
- [ ] No image is required to understand numerical results, warnings or navigation
- [ ] All image sources remain documented
