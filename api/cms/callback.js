import crypto from 'node:crypto';
const ORIGIN='https://nathansdrycleaners.com';
function fail(res,msg,status=403){return res.status(status).setHeader('Cache-Control','no-store').send(msg)}
function safeEqual(a,b){if(!a||!b||a.length!==b.length)return false;return crypto.timingSafeEqual(Buffer.from(a),Buffer.from(b))}
export default async function handler(req,res){
  if(req.method!=='GET')return res.status(405).end();
  res.setHeader('Cache-Control','no-store');
  res.setHeader('Set-Cookie','nathans_cms_state=; HttpOnly; Secure; SameSite=Lax; Path=/api/cms; Max-Age=0');
  const cookies=Object.fromEntries((req.headers.cookie||'').split(';').map(s=>s.trim().split('=')));
  const state=typeof req.query.state==='string'?req.query.state:'';
  const code=typeof req.query.code==='string'?req.query.code:'';
  if(!safeEqual(cookies.nathans_cms_state,state)||!code)return fail(res,'Invalid or expired sign-in request');
  if(!process.env.GITHUB_CLIENT_ID||!process.env.GITHUB_CLIENT_SECRET)return fail(res,'OAuth is not configured',503);
  try{
    const response=await fetch('https://github.com/login/oauth/access_token',{method:'POST',headers:{'Accept':'application/json','Content-Type':'application/json'},body:JSON.stringify({client_id:process.env.GITHUB_CLIENT_ID,client_secret:process.env.GITHUB_CLIENT_SECRET,code,redirect_uri:ORIGIN+'/api/cms/callback'})});
    if(!response.ok)return fail(res,'GitHub token exchange failed',502);
    const payload=await response.json();
    if(!payload.access_token)return fail(res,'GitHub authentication was not completed');
    const who=await fetch('https://api.github.com/user',{headers:{'Authorization':'Bearer '+payload.access_token,'Accept':'application/vnd.github+json','User-Agent':'nathans-journal-cms'}});
    if(!who.ok)return fail(res,'Could not verify GitHub account');
    const user=await who.json();
    if(String(user.login||'').toLowerCase()!=='ocspeedwell')return fail(res,'This GitHub account is not authorised');
    const msg='authorization:github:success:'+JSON.stringify({token:payload.access_token,provider:'github'});
    const encoded=JSON.stringify(msg).replace(/</g,'\\u003c');
    res.setHeader('Content-Type','text/html; charset=utf-8');
    res.setHeader('Content-Security-Policy',"default-src 'none'; script-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'");
    res.setHeader('Referrer-Policy','no-referrer');
    return res.status(200).send(`<!doctype html><html><head><meta charset="utf-8"><title>Nathans CMS sign-in</title></head><body><p>Completing sign-in...</p><script>if(window.opener){window.opener.postMessage(${encoded},${JSON.stringify(ORIGIN)});}window.close();</script></body></html>`);
  }catch{return fail(res,'Authentication service unavailable',502)}
}
