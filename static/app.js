const form=document.getElementById("form"), input=document.getElementById("input"), messages=document.getElementById("messages"), send=document.getElementById("send");
function addMessage(role,text){
 const welcome=messages.querySelector(".welcome"); if(welcome) welcome.remove();
 const wrap=document.createElement("div");wrap.className=`message ${role}`;
 const bubble=document.createElement("div");bubble.className="bubble";bubble.textContent=text;
 const meta=document.createElement("span");meta.className="meta";meta.textContent=role==="user"?"You":"CampusBuddy";
 wrap.append(bubble,meta);messages.append(wrap);messages.scrollTop=messages.scrollHeight;
}
async function sendMessage(text){
 const value=text.trim();if(!value)return;addMessage("user",value);input.value="";send.disabled=true;
 const typing=document.createElement("div");typing.className="typing";typing.textContent="CampusBuddy is thinking...";messages.append(typing);
 try{
  const res=await fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:value})});
  const data=await res.json();typing.remove();if(!res.ok)throw new Error(data.error||"Request failed");addMessage("bot",data.reply);
 }catch(err){typing.remove();addMessage("bot","I couldn't reach the server. Check that Flask is running, then try again.");console.error(err);}
 finally{send.disabled=false;input.focus();}
}
form.addEventListener("submit",e=>{e.preventDefault();sendMessage(input.value);});
function bindPrompts(){document.querySelectorAll("[data-prompt]").forEach(b=>b.addEventListener("click",()=>sendMessage(b.dataset.prompt)));}
bindPrompts();
document.getElementById("clear").addEventListener("click",async()=>{
 await fetch("/clear",{method:"POST"});
 messages.innerHTML=`<div class="welcome"><div class="spark">✦</div><small>YOUR CAMPUS, MADE SIMPLER</small><h2>Hey there! What can I help you with?</h2><p>Ask a question or choose a quick topic below.</p><div class="quick"><button data-prompt="Tell me about placements">💼 <span>Placements</span></button><button data-prompt="What is the attendance requirement?">📚 <span>Attendance</span></button><button data-prompt="When are the exams?">🗓️ <span>Exams</span></button><button data-prompt="Suggest an AI project">🧠 <span>Project ideas</span></button></div></div>`;
 bindPrompts();
});
