from flask import Flask, render_template, request, jsonify, session, send_file
import pyotp
import qrcode
import io
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 生成一个固定的密钥用于演示（生产环境应该为每个用户生成独立的密钥）
SECRET_KEY = pyotp.random_base32()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return jsonify({'error': '未授权'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if session.get('authenticated'):
        return render_template('welcome.html')
    return render_template('login.html')

@app.route('/setup')
def setup():
    """显示设置页面，包含QR码供用户扫描"""
    totp = pyotp.TOTP(SECRET_KEY)
    # 生成 provisioning URI
    uri = totp.provisioning_uri(
        name='user@example.com',
        issuer_name='我的网站'
    )
    return render_template('setup.html', secret=SECRET_KEY, uri=uri)

@app.route('/qrcode')
def get_qrcode():
    """生成QR码图片"""
    totp = pyotp.TOTP(SECRET_KEY)
    uri = totp.provisioning_uri(
        name='user@example.com',
        issuer_name='我的网站'
    )

    # 生成QR码
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # 将图片保存到内存
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

@app.route('/verify', methods=['POST'])
def verify():
    """验证TOTP代码"""
    data = request.json
    code = data.get('code', '')

    totp = pyotp.TOTP(SECRET_KEY)

    if totp.verify(code, valid_window=1):
        session['authenticated'] = True
        return jsonify({'success': True, 'message': '登录成功！'})
    else:
        return jsonify({'success': False, 'message': '验证码错误，请重试'})

@app.route('/logout')
def logout():
    """登出"""
    session.pop('authenticated', None)
    return jsonify({'success': True})

@app.route('/welcome')
@login_required
def welcome():
    """欢迎页面（需要登录）"""
    return render_template('welcome.html')

if __name__ == '__main__':
    print(f"\n{'='*60}")
    print(f"🔑 TOTP 密钥: {SECRET_KEY}")
    print(f"{'='*60}\n")
    print("请访问以下地址设置 Google Authenticator:")
    print("http://localhost:5000/setup")
    print("\n然后访问登录页面:")
    print("http://localhost:5000/")
    print(f"\n{'='*60}\n")
    app.run(debug=True, port=5000)
