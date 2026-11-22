/**
 * Nathans Decap CMS GitHub OAuth bridge for Cloudflare Workers.
 * Deploy separately from the static website. Never commit OAuth credentials.
 * Required secrets: GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET.
 * Required vars: CMS_ORIGIN (e.g. https://nathansdrycleaners.com).
 * GitHub OAuth callback: https://<worker-host>/callback
 */
function bytesToBase64url(bytes) {
  return btoa(String.fromCharCode(...bytes)).split('+').join('-').split('/').join('_').replace(/=+$/, '');
}
function randomState() {
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  return bytesToBase64url(bytes);
}
function page(origin, message) {
  const safe = JSON.stringify(message).replace(/</g, '\\u003c');
  const target = JSON.stringify(origin);
  return new Response(`<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Nathans CMS Authentication</title></head><body><p>Completing secure sign-in. You may close this window.</p><script>
    const message = ${safe};
    if (window.opener) window.opener.postMessage(message, ${target});
    window.close();
  </script></body></html>`, {headers: {'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store','Content-Security-Policy':"default-src 'none'; script-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'",'Referrer-Policy':'no-referrer'}});
}
function fail(origin, reason, status=400) {
  return new Response('Authentication failed: '+reason, {status,headers:{'Content-Type':'text/plain; charset=utf-8','Cache-Control':'no-store'}});
}
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = (env.CMS_ORIGIN || '').replace(/\/$/, '');
    if (!origin.startsWith('https://') || !env.GITHUB_CLIENT_ID || !env.GITHUB_CLIENT_SECRET) return new Response('OAuth bridge is not configured.',{status:503});
    if (url.pathname === '/auth' && request.method === 'GET') {
      const state = randomState();
      const github = new URL('https://github.com/login/oauth/authorize');
      github.searchParams.set('client_id',env.GITHUB_CLIENT_ID);
      github.searchParams.set('redirect_uri',url.origin+'/callback');
      github.searchParams.set('scope','repo');
      github.searchParams.set('state',state);
      const headers = new Headers({'Location':github.toString(),'Cache-Control':'no-store'});
      headers.append('Set-Cookie',`nathans_oauth_state=${state}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=600`);
      return new Response(null,{status:302,headers});
    }
    if (url.pathname === '/callback' && request.method === 'GET') {
      const cookie = request.headers.get('Cookie') || '';
      const stateCookie = cookie.split(';').map(x=>x.trim()).find(x=>x.startsWith('nathans_oauth_state='));
      const expected = stateCookie?.slice('nathans_oauth_state='.length);
      const state = url.searchParams.get('state');
      const code = url.searchParams.get('code');
      if (!expected || !state || state !== expected || !code) return fail(origin,'Invalid or expired OAuth state');
      const tokenResponse = await fetch('https://github.com/login/oauth/access_token',{
        method:'POST',headers:{'Accept':'application/json','Content-Type':'application/json'},
        body:JSON.stringify({client_id:env.GITHUB_CLIENT_ID,client_secret:env.GITHUB_CLIENT_SECRET,code,redirect_uri:url.origin+'/callback'})
      });
      if (!tokenResponse.ok) return fail(origin,'GitHub token exchange failed',502);
      const tokenData = await tokenResponse.json();
      if (!tokenData.access_token) return fail(origin,'GitHub did not return an access token');
      const response = page(origin,'authorization:github:success:'+JSON.stringify({token:tokenData.access_token,provider:'github'}));
      response.headers.append('Set-Cookie','nathans_oauth_state=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0');
      return response;
    }
    return new Response('Not found',{status:404});
  }
};
