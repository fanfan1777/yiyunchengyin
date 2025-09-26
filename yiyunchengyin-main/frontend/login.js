document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const msg = document.getElementById('loginMsg');
    msg.textContent = '';

    try {
        const res = await fetch('http://127.0.0.1:8000/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (data.success) {
            msg.textContent = '登录成功，正在跳转...';
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1500);
        } else {
            msg.textContent = data.message || '登录失败';
        }
    } catch (err) {
        msg.textContent = '网络错误，请稍后重试';
    }
});