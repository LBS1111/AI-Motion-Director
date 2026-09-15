const path=require('path');
const fs=require('fs');
const {bundle}=require('@remotion/bundler');
const {selectComposition,renderStill,renderMedia,openBrowser}=require('@remotion/renderer');
const root=path.resolve(__dirname,'..');
fs.mkdirSync(path.join(root,'.checks'),{recursive:true});
fs.mkdirSync(path.join(root,'posters'),{recursive:true});
fs.mkdirSync(path.join(root,'videos'),{recursive:true});
const clips=[
  ['01-Intro','01_AI-Motion-Director_Intro'],
  ['02-Brief','02_Brief-to-Scene'],
  ['03-Route','03_Skill-Routing'],
  ['04-Direct','04_2.5D-Camera'],
  ['05-Learn','05_Review-and-Learn'],
];
const mode=process.argv[2]||'all';
(async()=>{
  const serveUrl=await bundle({entryPoint:path.join(__dirname,'index.tsx')});
  const browser=await openBrowser('chrome');
  try{
    for(const [id,name] of clips){
      const composition=await selectComposition({serveUrl,id,browserInstance:browser});
      if(mode==='all'||mode==='stills'){
        for(const sec of [0,.8,1.5,2.5,3.3,3.9]){
          await renderStill({serveUrl,composition,frame:Math.round(sec*30),output:path.join(root,'.checks',`${name}_${sec}.png`),scale:.5,chromiumInstance:browser});
        }
        await renderStill({serveUrl,composition,frame:Math.round(2.5*30),output:path.join(root,'posters',`${name}.png`),scale:1,chromiumInstance:browser});
      }
      if(mode==='all'||mode==='media'){
        console.log('Rendering '+name);
        await renderMedia({serveUrl,composition,codec:'h264',crf:18,concurrency:4,muted:true,outputLocation:path.join(root,'videos',`${name}.mp4`),chromiumInstance:browser});
      }
    }
  }finally{await browser.close({silent:true});}
})().catch(e=>{console.error(e);process.exit(1)});
