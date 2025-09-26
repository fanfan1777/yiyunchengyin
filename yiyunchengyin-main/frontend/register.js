document.getElementById('registerForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const msg = document.getElementById('registerMsg');
    msg.textContent = '';

    try {
        const res = await fetch('http://127.0.0.1:8000/api/register', { // 修改为完整后端地址
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        const data = await res.json();
        if (data.success) {
            msg.textContent = '注册成功，正在跳转登录...';
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 1500);
        } else {
            msg.textContent = data.message || '注册失败';
        }
    } catch (err) {
        msg.textContent = '网络错误，请稍后重试';
    }
});