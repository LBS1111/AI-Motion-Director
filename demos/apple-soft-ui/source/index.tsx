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
const CameraRig:React.FC<{x?:number;y?:number;z?:number;yaw?:number;pitch?:number;children:React.ReactNode}>=({x=0,y=0,z=0,yaw=0,pitch=0,children})=><div style={{position:'absolute',inset:0,perspective:1450,overflow:'visible'}}><div style={{position:'absolute',inset:0,transformStyle:'preserve-3d',transform:`translate3d(${x}px,${y}px,${z}px) rotateY(${yaw}deg) rotateX(${pitch}deg)`}}>{children}</div></div>;

const Intro=()=>{const t=time();const show=visibility(t,.22,.48,3.38,.40),expand=step(t,.70,.85)*(1-step(t,3.05,.55));const w=112+970*expand;const h=100+44*expand;const text=visibility(t,1.12,.52,2.91,.42);const mark=visibility(t,.54,.47,3.04,.45);const lens=step(t,.55,.98)*(1-step(t,3.05,.57));
  return <Stage>
   <CameraRig z={-155+205*lens} yaw={-9+9*lens} pitch={4*(1-lens)}>
    <Soft style={{position:'absolute',left:960-w/2,top:540-h/2,width:w,height:h,borderRadius:h/2,opacity:show,display:'flex',alignItems:'center',justifyContent:'center',overflow:'hidden',transform:`translateZ(88px) scale(${.94+.06*step(t,.22,.50)})`}}>
      <div style={{position:'absolute',left:`${50-43*expand}%`,top:'50%',transform:'translate(-50%,-50%)',width:66,height:66,borderRadius:'50%',boxShadow:insetShadow,opacity:mark}}>
        <div style={{position:'absolute',inset:18,border:'4px solid #858D93',borderRadius:'50%',boxShadow:'1px 1px 2px rgba(255,255,255,.9)'}}/>
      </div>
      <Word style={{fontSize:67,opacity:text,transform:`translateY(${14*(1-step(t,1.12,.5))}px)`}}>AI Motion Director</Word>
    </Soft>
   </CameraRig>
  </Stage>;
};

const SceneIcon:React.FC<{type:number}>=({type})=>{
  if(type===0)return <div style={{width:125,height:125,borderRadius:'50%',background:'linear-gradient(145deg,#F3F5F6,#C3C8CC)',boxShadow:'12px 12px 25px rgba(80,90,100,.18), -10px -10px 20px rgba(255,255,255,.8)'}}/>;
  if(type===1)return <div style={{width:150,height:106,borderRadius:26,background:'linear-gradient(140deg,#D0D5D8,#F0F2F3)',transform:'rotate(-9deg)',boxShadow:softShadow}}/>;
  return <svg width="168" height="120" viewBox="0 0 168 120"><path d="M12 102 Q47 22 86 68 T156 22" fill="none" stroke="#949DA3" strokeWidth="13" strokeLinecap="round"/></svg>;
};
const Brief=()=>{const t=time();const enter=step(t,.22,.54);const fold=step(t,1.01,.83)*(1-step(t,3.02,.65));const cam=step(t,.53,1.53);const camBack=step(t,3.02,.65);const exit=step(t,3.60,.28);const scene=visibility(t,1.55,.42,2.98,.38);
 return <Stage><CameraRig x={195-195*cam-115*camBack} z={-130+200*cam-180*camBack} yaw={-15+15*cam+9*camBack} pitch={6*(1-cam)+3*camBack}>
  <Soft inner style={{position:'absolute',left:470,top:532,width:970,height:16,borderRadius:12,opacity:fold*(1-exit),transform:'translateZ(-65px)'}}/>
  {[0,2].map((type,i)=>{const side=i===0?-1:1;return <Soft key={type} style={{position:'absolute',left:810+side*360*fold,top:410,width:320,height:280,borderRadius:42,opacity:enter*fold*(1-exit),transform:`translateZ(66px) rotateY(${side*72*(1-fold)}deg) scaleX(${.82+.18*fold})`,display:'flex',alignItems:'center',justifyContent:'center'}}><div style={{position:'absolute',inset:20,borderRadius:29,boxShadow:insetShadow}}/><SceneIcon type={type}/></Soft>})}
  <Soft style={{position:'absolute',left:810,top:410-135*exit,width:320,height:280,borderRadius:42,opacity:enter*(1-exit),transform:`translateZ(${100+20*fold}px) rotate(${4*(1-enter)-5*exit}deg)`,display:'flex',alignItems:'center',justifyContent:'center'}}>
    <div style={{position:'absolute',inset:20,borderRadius:29,boxShadow:insetShadow}}/>
    <Word style={{fontSize:48,opacity:visibility(t,.47,.38,1.27,.35)}}>BRIEF</Word>
    <div style={{position:'absolute',opacity:step(t,1.52,.43)*(1-step(t,3.03,.43))}}><SceneIcon type={1}/></div>
  </Soft>
  <Word style={{position:'absolute',left:760,top:286,width:420,textAlign:'center',fontSize:60,opacity:scene*(1-exit),transform:'translateZ(130px)'}}>SCENE</Word>
 </CameraRig></Stage>;
};

const RouteIcon:React.FC<{type:number}>=({type})=>type===0?<div style={{width:68,height:68,borderRadius:'50%',boxShadow:insetShadow}}/>:type===1?<div style={{width:79,height:56,borderRadius:15,boxShadow:insetShadow}}/>:<div style={{width:70,height:70,borderRadius:17,transform:'rotate(45deg)',boxShadow:insetShadow}}/>;
const Route=()=>{const t=time();const track=step(t,.78,1.35);const leave=step(t,3.06,.65);const cameraX=185-360*track-105*leave;const cameraZ=-180+285*track-210*leave;
 return <Stage><CameraRig x={cameraX} z={cameraZ} yaw={-20+20*track+9*leave} pitch={8-8*track+3*leave}>
  <Soft inner style={{position:'absolute',left:818,top:403,width:664,height:260,borderRadius:60,opacity:visibility(t,.37,.48,3.32,.44),transform:'translateZ(-48px)'}}/>
  {[0,1,2].map(i=><Soft inner key={i} style={{position:'absolute',left:853+i*208,top:437,width:180,height:192,borderRadius:38,opacity:visibility(t,.53,.45,3.20,.50),transform:'translateZ(-17px)'}}/>)}
  <svg style={{position:'absolute',inset:0,opacity:visibility(t,.42,.36,2.16,.52),transform:'translateZ(-90px)'}} width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
    {[330,545,760].map((y,i)=><path key={i} d={`M415 ${y} C640 ${y}, 655 535, ${943+i*208} 535`} fill="none" stroke="#A0A9AF" strokeWidth="5" strokeLinecap="round" strokeDasharray="850" strokeDashoffset={850*(1-step(t,.75+i*.14,1.05))}/>) }
  </svg>
  {[0,1,2].map(i=>{const f=step(t,.74+i*.16,1.11);const srcY=330+i*215;const endX=943+i*208;const x=385+(endX-385)*f;const y=srcY+(535-srcY)*f-60*Math.sin(Math.PI*f);const lift=i===1?23*step(t,2.22,.30)*(1-leave):0;return <Soft key={i} style={{position:'absolute',left:x-84,top:y-70-lift,width:168,height:140,borderRadius:34,opacity:visibility(t,.22+i*.10,.37,3.31,.40),transform:`translateZ(${118+lift-150*leave}px) rotate(${(i-1)*5*(1-f)}deg) scale(${.89+.11*f-.42*leave})`,display:'flex',justifyContent:'center',alignItems:'center'}}><RouteIcon type={i}/></Soft>})}
  <Word style={{position:'absolute',left:1030,top:303,width:260,textAlign:'center',fontSize:60,opacity:visibility(t,2.00,.40,2.96,.42),transform:'translateZ(156px)'}}>ROUTE</Word>
 </CameraRig></Stage>;
};

const WorldCard:React.FC<{left:number;top:number;depth:number;type:number;opacity:number}>=({left,top,depth,type,opacity})=><Soft style={{position:'absolute',left,top,width:530,height:340,borderRadius:45,opacity,transform:`translateZ(${depth}px)`,display:'flex',alignItems:'center',justifyContent:'center'}}>
  <div style={{position:'absolute',inset:25,borderRadius:30,boxShadow:insetShadow}}/>
  {type===0?<div style={{width:160,height:160,borderRadius:'50%',boxShadow:softShadow,background:'#D7DBDE'}}/>:type===1?<Word style={{fontSize:70}}>DIRECT</Word>:<div style={{display:'flex',gap:22}}>{[0,1,2].map(i=><div key={i} style={{width:60,height:145-i*35,borderRadius:25,boxShadow:softShadow,background:'#D6DBDE'}}/>)}</div>}
 </Soft>;
const Direct=()=>{const t=time();const traverse=step(t,.45,1.66);const fly=step(t,2.98,.82);const show=step(t,.20,.37)*(1-step(t,3.78,.12));
 return <Stage><CameraRig x={360-365*traverse-2100*fly} y={46-46*traverse+28*fly} z={-340+420*traverse+215*fly} yaw={-25+25*traverse+28*fly} pitch={9-9*traverse-3*fly}>
  <div style={{position:'absolute',inset:0,opacity:show,transformStyle:'preserve-3d'}}>
    <Soft inner style={{position:'absolute',left:-260,top:300,width:2480,height:500,borderRadius:80,transform:'translateZ(-135px)',opacity:.70}}/>
    <WorldCard left={-140} top={375} depth={30} type={0} opacity={1}/>
    <WorldCard left={700} top={375} depth={198} type={1} opacity={1}/>
    <WorldCard left={1520} top={375} depth={42} type={2} opacity={1}/>
  </div>
 </CameraRig></Stage>;
};

const Learn=()=>{const t=time();const pan=step(t,1.48,1.25);const transfer=step(t,1.62,.86);const leave=step(t,3.14,.65);const show=step(t,.18,.38)*(1-step(t,3.68,.16));
 return <Stage><CameraRig x={210-470*pan} y={16-16*pan} z={-210+325*pan-190*leave} yaw={-19+19*pan+8*leave} pitch={6-6*pan}>
  <Soft inner style={{position:'absolute',left:350,top:390,width:1210,height:300,borderRadius:60,opacity:.65*show,transform:'translateZ(-70px)'}}/>
  <Soft style={{position:'absolute',left:418-255*leave,top:430,width:370,height:235,borderRadius:48,opacity:show,transform:'translateZ(56px)'}}><div style={{position:'absolute',inset:21,borderRadius:33,boxShadow:insetShadow}}/></Soft>
  <Word style={{position:'absolute',left:462,top:729,width:270,textAlign:'center',fontSize:48,opacity:visibility(t,.54,.39,1.55,.40)*(1-leave),transform:'translateZ(98px)'}}>REVIEW</Word>
  <div style={{position:'absolute',left:707,top:583,width:55,height:55,borderRadius:'50%',background:paper,boxShadow:softShadow,opacity:step(t,1.16,.32)*(1-step(t,1.82,.35)),display:'grid',placeItems:'center',fontSize:30,transform:'translateZ(135px)'}}>✓</div>
  <Soft inner style={{position:'absolute',left:1120+255*leave,top:430,width:370,height:235,borderRadius:48,opacity:show,transform:'translateZ(75px)'}}/>
  <svg style={{position:'absolute',left:494+700*transfer,top:488-92*Math.sin(Math.PI*transfer),opacity:show*(1-step(t,3.30,.39)),transform:`translateZ(${155+75*Math.sin(Math.PI*transfer)}px) rotate(${10*(1-transfer)}deg)`}} width="220" height="100" viewBox="0 0 220 100"><path d="M10 75 C50 10 80 95 115 38 S180 65 210 23" fill="none" stroke="#929CA3" strokeWidth="9" strokeLinecap="round"/></svg>
  <div style={{position:'absolute',left:1218,top:576,display:'flex',gap:18,opacity:step(t,2.42,.38)*(1-leave),transform:'translateZ(130px)'}}>{[0,1,2].map(i=><div key={i} style={{width:36,height:22+i*17,borderRadius:12,background:'#9AA3A9',boxShadow:softShadow}}/>)}</div>
  <Word style={{position:'absolute',left:1168,top:729,width:280,textAlign:'center',fontSize:48,opacity:visibility(t,2.48,.38,3.15,.42),transform:'translateZ(150px)'}}>LEARN</Word>
 </CameraRig></Stage>;
};

registerRoot(()=> <>
  <Composition id="01-Intro" component={Intro} width={W} height={H} fps={FPS} durationInFrames={120}/>
  <Composition id="02-Brief" component={Brief} width={W} height={H} fps={FPS} durationInFrames={120}/>
  <Composition id="03-Route" component={Route} width={W} height={H} fps={FPS} durationInFrames={120}/>
  <Composition id="04-Direct" component={Direct} width={W} height={H} fps={FPS} durationInFrames={120}/>
  <Composition id="05-Learn" component={Learn} width={W} height={H} fps={FPS} durationInFrames={120}/>
</>);
