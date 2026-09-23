
(function(){
var KB=[
[/\b(submit|add my|list my|join|submission)\b/i,"Founders can submit for free: open the + Add Startup page, fill 5 fields - startup name, website, monthly revenue, email and a revenue-proof link. Review takes up to 7 days."],
[/\b(verif|proof|badge)\b/i,"Every verified listing carries a revenue-proof link (Stripe, Razorpay or a live dashboard). Once the proof is checked, the startup earns the Founder Verified badge."],
[/\b(price|pricing|sponsor|featured|cost|payment|pay)\b/i,"Sponsorship: homepage slot Rs 15,000/mo or $200/mo. Featured listing: Rs 3,000 / $40 for 30 days. Verified-badge fast-track: Rs 1,500 / $20. Listings themselves are free - see the Pricing page."],
[/\b(service|hire|website|chatbot|agent|develop|freelance)\b/i,"Our studio builds business websites (Rs 20,000), AI chatbots (Rs 15,000) and AI agents (Rs 35,000), delivered in 7-14 days. See the Services page or email honestmrr.official@gmail.com for a fixed quote."],
[/\b(sell|acquisition|buy|marketplace)\b/i,"Startups open to acquisition are listed in the Buy/Sell marketplace with revenue, growth and asking price - see the Browse page."],
[/\b(contact|human|email|talk|support|help)\b/i,"You can reach the team at honestmrr.official@gmail.com - a human replies within 24 hours."],
[/\b(data|update|fresh|stats|benchmark)\b/i,"The database refreshes daily. The Stats page shows category benchmarks; public-company figures come from filings and press reports."],
[/\b(hi|hello|hey|namaste)\b/i,"Hello! I am the HonestMRR assistant. Ask me about submissions, verification, pricing or our studio services."]
];
var FALL="I can help with submissions, verification, pricing and studio services. For anything else, email honestmrr.official@gmail.com - a human replies within 24 hours.";
var st=document.createElement("style");
st.textContent="#hmchat-btn{position:fixed;right:18px;bottom:18px;width:56px;height:56px;border-radius:50%;background:#FF8A3D;border:none;font-size:26px;cursor:pointer;z-index:999;box-shadow:0 6px 24px rgba(255,138,61,.4)}#hmchat-box{position:fixed;right:18px;bottom:86px;width:320px;max-width:calc(100vw - 36px);height:420px;max-height:60vh;background:rgba(22,24,38,.97);border:1px solid rgba(255,255,255,.15);border-radius:16px;display:none;flex-direction:column;z-index:999;font-family:inherit}#hmchat-head{padding:12px 14px;font-weight:700;color:#EDEFF7;border-bottom:1px solid rgba(255,255,255,.1);font-size:14px}#hmchat-msgs{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:8px}#hmchat-msgs div{max-width:85%;padding:9px 12px;border-radius:12px;font-size:13px;line-height:1.45;color:#EDEFF7}#hmchat-msgs .b{background:rgba(255,255,255,.09);align-self:flex-start}#hmchat-msgs .u{background:#FF8A3D;color:#14161F;align-self:flex-end}#hmchat-chips{display:flex;gap:6px;flex-wrap:wrap;padding:0 12px 8px}#hmchat-chips button{background:rgba(255,138,61,.15);border:1px solid rgba(255,138,61,.4);color:#FF8A3D;border-radius:14px;padding:5px 10px;font-size:11px;cursor:pointer}#hmchat-in{display:flex;border-top:1px solid rgba(255,255,255,.1)}#hmchat-in input{flex:1;background:none;border:none;color:#EDEFF7;padding:12px;font-size:13px;outline:none}#hmchat-in button{background:none;border:none;color:#FF8A3D;font-size:18px;padding:0 14px;cursor:pointer}";
document.head.appendChild(st);
var btn=document.createElement("button");btn.id="hmchat-btn";btn.textContent="💬";btn.setAttribute("aria-label","Chat with us");
var box=document.createElement("div");box.id="hmchat-box";
box.innerHTML='<div id="hmchat-head">🤖 HonestMRR Assistant · online</div><div id="hmchat-msgs"></div><div id="hmchat-chips"></div><div id="hmchat-in"><input placeholder="Type your question..." /><button>➤</button></div>';
document.body.appendChild(btn);document.body.appendChild(box);
var msgs=box.querySelector("#hmchat-msgs"),inp=box.querySelector("input"),open=false;
function add(cls,txt){var d=document.createElement("div");d.className=cls;d.textContent=txt;msgs.appendChild(d);msgs.scrollTop=msgs.scrollHeight;return d;}
function bot(txt){var t=add("b","…");setTimeout(function(){t.textContent=txt;msgs.scrollTop=msgs.scrollHeight;},450);}
function answer(q){for(var i=0;i<KB.length;i++){if(KB[i][0].test(q))return KB[i][1];}return FALL;}
function send(q){if(!q.trim())return;add("u",q);bot(answer(q));}
btn.onclick=function(){open=!open;box.style.display=open?"flex":"none";if(open&&msgs.children.length===0){bot("Hi! I am the HonestMRR assistant. How can I help you today?");chips();}};
function chips(){var c=box.querySelector("#hmchat-chips");["How do I submit?","Pricing?","Talk to a human"].forEach(function(s){var b=document.createElement("button");b.textContent=s;b.onclick=function(){send(s);};c.appendChild(b);});}
box.querySelector("#hmchat-in button").onclick=function(){send(inp.value);inp.value="";};
inp.addEventListener("keydown",function(e){if(e.key==="Enter"){send(inp.value);inp.value="";}});
})();
