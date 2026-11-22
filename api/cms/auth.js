import crypto from 'node:crypto';
const cookie = (state) => `nathans_cms_state=${state}; HttpOnly; Secure; SameSite=Lax; Path=/api/cms; Max-Age=600`;
export default function handler(req,res) {
  if(req.method!=='GET') return res.status(405).end();
  if(!process.env.GITHUB_CLIENT_ID || !process.env.GITHUB_CLIENT_SECRET) return res.status(503).send('CMS OAuth is not configured');
  const state=crypto.randomBytes(32).toString('hex');
  const origin='https://nathansdrycleaners.com';
  const callback=origin+'/api/cms/callback';
  const url=new URL('https://github.com/login/oauth/authorize');
  url.searchParams.set('client_id',process.env.GITHUB_CLIENT_ID);
  url.searchParams.set('redirect_uri',callback);
  url.searchParams.set('scope','repo');
  url.searchParams.set('state',state);
  res.setHeader('Set-Cookie',cookie(state));
  res.setHeader('Cache-Control','no-store');
  return res.redirect(302,url.toString());
}
