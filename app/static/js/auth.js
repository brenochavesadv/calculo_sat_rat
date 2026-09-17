function token() { return localStorage.getItem('token') || ''; }
function logout() { localStorage.removeItem('token'); location.href = '/login'; }
async function refreshToken() {
  const r = await fetch('/auth/refresh', { method: 'POST', credentials: 'include' });
  const j = await r.json();
  if (j.access_token) { localStorage.setItem('token', j.access_token); alert('Token renovado'); }
  else { alert('Falha ao renovar token'); }
}
function initLogin() {
  const form = document.getElementById('loginForm');
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const body = { username: form.username.value, password: form.password.value };
    try {
      const r = await fetch('/auth/login', { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const j = await r.json();
      if (j.access_token) {
        localStorage.setItem('token', j.access_token);
        // successful login: navigate to dashboard
        location.href = '/';
      } else {
        document.getElementById('msg').textContent = j.error || 'Falha no login';
      }
    } catch (ex) {
      console.error('login error', ex);
      document.getElementById('msg').textContent = 'Erro de rede ou CORS. Veja console.';
    }
  });
}