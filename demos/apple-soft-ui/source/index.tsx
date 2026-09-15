import React from 'react';
import {AbsoluteFill,Composition,registerRoot,useCurrentFrame} from 'remotion';

const W=1920,H=1080,FPS=30;
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const ease=(v:number)=>{const x=clamp(v);return x*x*x*(10+x*(-15+6*x));};
const step=(t:number,a:number,d:number)=>ease((t-a)/d);
const visibility=(t:number,a:number,b:number,c:number,d:number)=>step(t,a,b)*(1-step(t,c,d));
const ink='#3E454A',paper='#DDE1E4',stage='#CBD1D5';
const font='Segoe UI, Microsoft YaHei UI, Microsoft YaHei, sans-serif';
const softShadow='18px 18px 40px rgba(88,97,105,.27), -16px -16px 37px rgba(255,255,255,.68), inset 1px 1px 2px rgba(255,255,255,.75), inset -1px -1px 2px rgba(85,94,102,.20)';
const insetShadow='inset 8px 8px 18px rgba(95,104,112,.23), inset -8px -8px 18px rgba(255,255,255,.73), 1px 1px 3px rgba(255,255,255,.75)';
const time=()=>useCurrentFrame()/FPS;

const Stage:React.FC<{children:React.ReactNode}>=({children})=><AbsoluteFill style={{background:`radial-gradient(ellipse at 50% 34%, #E9ECEE 0%, ${stage} 78%)`,overflow:'hidden',fontFamily:font,color:ink}}>{children}</AbsoluteFill>;
const Soft:React.FC<{style?:React.CSSProperties;children?:React.ReactNode;inner?:boolean}>=({style,children,inner})=><div style={{background:paper,border:'1px solid rgba(255,255,255,.64)',boxShadow:inner?insetShadow:softShadow,...style}}>{children}</div>;
const Word:React.FC<{children:React.ReactNode;style?:React.CSSProperties}>=({children,style})=><div style={{fontWeight:300,letterSpacing:'.055em',whiteSpace:'nowrap',...style}}>{children}</div>;

const Intro=()=>{const t=time();const show=visibility(t,.22,.48,3.38,.40),expand=step(t,.70,.85)*(1-step(t,3.05,.55));const w=112+970*expand;const h=100+44*expand;const text=visibility(t,1.12,.52,2.91,.42);const mark=visibility(t,.54,.47,3.04,.45);
  return <Stage>
    <Soft style={{position:'absolute',left:960-w/2,top:540-h/2,width:w,height:h,borderRadius:h/2,opacity:show,display:'flex',alignItems:'center',justifyContent:'center',overflow:'hidden',transform:`scale(${.94+.06*step(t,.22,.50)})`}}>
      <div style={{position:'absolute',left:`${50-43*expand}%`,top:'50%',transform:'translate(-50%,-50%)',width:66,height:66,borderRadius:'50%',boxShadow:insetShadow,opacity:mark}}>
        <div style={{position:'absolute',inset:18,border:'4px solid #858D93',borderRadius:'50%',boxShadow:'1px 1px 2px rgba(255,255,255,.9)'}}/>
      </div>
      <Word style={{fontSize:67,opacity:text,transform:`translateY(${14*(1-step(t,1.12,.5))}px)`}}>AI Motion Director</Word>
    </Soft>
  </Stage>;
};

const SceneIcon:React.FC<{type:number}>=({type})=>{
  if(type===0)return <div style={{width:125,height:125,borderRadius:'50%',background:'linear-gradient(145deg,#F3F5F6,#C3C8CC)',boxShadow:'12px 12px 25px rgba(80,90,100,.18), -10px -10px 20px rgba(255,255,255,.8)'}}/>;
  if(type===1)return <div style={{width:150,height:106,borderRadius:26,background:'linear-gradient(140deg,#D0D5D8,#F0F2F3)',transform:'rotate(-9deg)',boxShadow:softShadow}}/>;
  return <svg width="168" height="120" viewBox="0 0 168 120"><path d="M12 102 Q47 22 86 68 T156 22" fill="none" stroke="#949DA3" strokeWidth="13" strokeLinecap="round"/></svg>;
};
const Brief=()=>{const t=time();const show=visibility(t,.18,.47,3.45,.38);const unfold=step(t,.95,.94)*(1-step(t,3.16,.42));const cardW=370+840*unfold,cardH=124+374*unfold;const labelA=visibility(t,.47,.38,1.04,.27);const labelB=visibility(t,1.42,.39,3.02,.35);
 return <Stage>
  <Soft style={{position:'absolute',left:960-cardW/2,top:540-cardH/2,width:cardW,height:cardH,borderRadius:unfold<.2?72:58,opacity:show,overflow:'hidden'}}>
    <Word style={{position:'absolute',left:0,right:0,top:37,textAlign:'center',fontSize:46,opacity:labelA}}>BRIEF</Word>
    <Word style={{position:'absolute',left:0,right:0,top:47,textAlign:'center',fontSize:47,opacity:labelB}}>SCENE</Word>
    <div style={{position:'absolute',left:80,right:80,bottom:70,display:'flex',justifyContent:'space-between',gap:35}}>
      {[0,1,2].map(i=><Soft key={i} inner style={{width:290,height:240,borderRadius:38,display:'flex',alignItems:'center',justifyContent:'center',opacity:visibility(t,1.42+i*.11,.41,3.03,.34),transform:`translateY(${34*(1-step(t,1.42+i*.11,.41))}px) scale(${.93+.07*step(t,1.42+i*.11,.41)})`}}><SceneIcon type={i}/></Soft>)}
    </div>
  </Soft>
 </Stage>;
};

const RouteIcon:React.FC<{type:number}>=({type})=>type===0?<div style={{width:68,height:68,borderRadius:'50%',boxShadow:insetShadow}}/>:type===1?<div style={{width:79,height:56,borderRadius:15,boxShadow:insetShadow}}/>:<div style={{width:70,height:70,borderRadius:17,transform:'rotate(45deg)',boxShadow:insetShadow}}/>;
const Route=()=>{const t=time();const source=visibility(t,.22,.42,1.93,.37);const converge=step(t,1.05,.88);const hub=visibility(t,1.42,.55,3.36,.41);const sel=visibility(t,1.72,.50,3.12,.35);const line=visibility(t,.96,.3,2.03,.30);
 return <Stage>
  <svg style={{position:'absolute',inset:0,opacity:line}} width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
    {[360,540,720].map((y,i)=><path key={i} d={`M500 ${y} C610 ${y}, 620 540, 770 540`} fill="none" stroke="#A3ACB2" strokeWidth="5" strokeDasharray="450" strokeDashoffset={450*(1-step(t,1.12+i*.1,.76))} strokeLinecap="round"/>) }
  </svg>
  {[0,1,2].map(i=>{const y=360+i*180;const f=step(t,1.14+i*.11,.83);return <Soft key={i} style={{position:'absolute',left:390+520*f-112,top:y+(540-y)*f-72,width:224,height:144,borderRadius:36,opacity:source*(1-.63*f),transform:`rotate(${(i-1)*3*(1-f)}deg) scale(${1-.25*f})`,display:'flex',justifyContent:'center',alignItems:'center'}}><RouteIcon type={i}/></Soft>})}
  <Soft style={{position:'absolute',left:730,top:410,width:460,height:260,borderRadius:62,opacity:hub,transform:`scale(${.90+.12*step(t,1.42,.56)-.02*step(t,2.08,.26)})`,display:'flex',alignItems:'center',justifyContent:'center'}}>
    <div style={{position:'absolute',inset:20,borderRadius:47,boxShadow:insetShadow}}/>
    <Word style={{fontSize:70,opacity:sel}}>ROUTE</Word>
  </Soft>
 </Stage>;
};

const WorldCard:React.FC<{left:number;top:number;depth:number;type:number;opacity:number}>=({left,top,depth,type,opacity})=><Soft style={{position:'absolute',left,top,width:530,height:340,borderRadius:45,opacity,transform:`translateZ(${depth}px)`,display:'flex',alignItems:'center',justifyContent:'center'}}>
  <div style={{position:'absolute',inset:25,borderRadius:30,boxShadow:insetShadow}}/>
  {type===0?<div style={{width:160,height:160,borderRadius:'50%',boxShadow:softShadow,background:'#D7DBDE'}}/>:type===1?<Word style={{fontSize:70}}>DIRECT</Word>:<div style={{display:'flex',gap:22}}>{[0,1,2].map(i=><div key={i} style={{width:60,height:145-i*35,borderRadius:25,boxShadow:softShadow,background:'#D6DBDE'}}/>)}</div>}
 </Soft>;
const Direct=()=>{const t=time();const show=visibility(t,.20,.45,3.40,.42);const cam=step(t,.73,1.42);const retract=step(t,3.13,.52);const x=240-610*cam+80*retract;const yaw=-11+17*cam-6*retract;const zoom=.84+.18*cam-.08*retract;
 return <Stage>
  <div style={{position:'absolute',left:100,top:210,width:2600,height:660,perspective:1600,opacity:show}}>
    <div style={{position:'absolute',left:0,top:0,width:2600,height:660,transformStyle:'preserve-3d',transform:`translateX(${x}px) rotateY(${yaw}deg) rotateX(7deg) scale(${zoom})`}}>
      <Soft inner style={{position:'absolute',left:180,top:100,width:2150,height:440,borderRadius:67,transform:'translateZ(-85px)',opacity:.62}}/>
      <WorldCard left={180} top={170} depth={46} type={0} opacity={1}/>
      <WorldCard left={1130} top={170} depth={132} type={1} opacity={1}/>
      <WorldCard left={2030} top={170} depth={54} type={2} opacity={1}/>
    </div>
  </div>
 </Stage>;
};

const Learn=()=>{const t=time();const show=visibility(t,.22,.45,3.40,.42);const approval=step(t,1.35,.35);const trace=step(t,1.63,.82);const memory=visibility(t,2.10,.42,3.18,.36);const review=visibility(t,.60,.41,1.62,.32);
 return <Stage>
  <svg style={{position:'absolute',inset:0,opacity:show}} width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
    <path d="M760 540 C920 510 1000 630 1170 540" fill="none" stroke="#A0A9AF" strokeWidth="8" strokeLinecap="round" strokeDasharray="450" strokeDashoffset={450*(1-trace)}/>
  </svg>
  <Soft style={{position:'absolute',left:450,top:405,width:350,height:270,borderRadius:50,opacity:show,transform:`translateY(${22*(1-step(t,.22,.48))}px)`,display:'flex',alignItems:'center',justifyContent:'center'}}>
    <div style={{position:'absolute',inset:22,borderRadius:35,boxShadow:insetShadow}}/>
    <svg width="220" height="100" viewBox="0 0 220 100"><path d="M10 75 C50 10 80 95 115 38 S180 65 210 23" fill="none" stroke="#929CA3" strokeWidth="9" strokeLinecap="round"/></svg>
    <div style={{position:'absolute',right:35,bottom:34,width:42,height:42,borderRadius:'50%',background:'#D5DBDE',boxShadow:softShadow,opacity:approval,display:'grid',placeItems:'center',fontSize:27}}>✓</div>
  </Soft>
  <Word style={{position:'absolute',left:456,top:706,width:342,textAlign:'center',fontSize:48,opacity:review}}>REVIEW</Word>
  <Soft style={{position:'absolute',left:1160,top:405,width:350,height:270,borderRadius:50,opacity:memory,transform:`translateY(${26*(1-step(t,2.10,.42))}px)`,display:'flex',alignItems:'center',justifyContent:'center'}}>
    <div style={{position:'absolute',inset:22,borderRadius:35,boxShadow:insetShadow}}/>
    <div style={{display:'flex',flexDirection:'column',gap:15}}>{[0,1,2].map(i=><div key={i} style={{height:13,width:164-i*25,borderRadius:10,background:'#9AA3A9',opacity:.75}}/>)}</div>
  </Soft>
  <Word style={{position:'absolute',left:1163,top:706,width:342,textAlign:'center',fontSize:48,opacity:memory}}>LEARN</Word>
 </Stage>;
};

registerRoot(()=> <>
  <Composition id="01-Intro" component={Intro} width={W} height={H} fps={FPS} durationInFrames={120}/>
  <Composition id="02-Brief" component={Brief} width={W} height={H} fps={FPS} durationInFrames={120}/>
  <Composition id="03-Route" component={Route} width={W} height={H} fps={FPS} durationInFrames={120}/>
  <Composition id="04-Direct" component={Direct} width={W} height={H} fps={FPS} durationInFrames={120}/>
  <Composition id="05-Learn" component={Learn} width={W} height={H} fps={FPS} durationInFrames={120}/>
</>);
