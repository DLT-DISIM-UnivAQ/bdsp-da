from nicegui import ui, app
from fastapi import Request
from src.mock.wallet import connect_wallet

def login_page():
    ui.add_head_html('''
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <script src="https://cdn.jsdelivr.net/npm/web3@latest/dist/web3.min.js"></script>
    ''')

    ui.add_body_html('''
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .glass-card {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
            width: 100%;
            max-width: 400px;
            color: white;
        }

        .form-control {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            border-radius: 30px;
            color: white;
            padding: 12px 20px;
        }

        .form-control::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }

        .form-control:focus {
            background: rgba(255, 255, 255, 0.3);
            color: white;
            box-shadow: none;
        }

        .btn-login {
            background: rgba(255, 255, 255, 0.3);
            border: none;
            border-radius: 30px;
            color: white;
            padding: 10px 30px;
            font-weight: 600;
            transition: all 0.3s;
        }

        .btn-login:hover {
            background: rgba(255, 255, 255, 0.5);
            transform: translateY(-2px);
        }

        .forgot-password {
            color: rgba(255, 255, 255, 0.8);
            text-decoration: none;
            font-size: 14px;
        }

        .forgot-password:hover {
            color: white;
            text-decoration: underline;
        }
                     
     .container, .container-lg, .container-md, .container-sm, .container-xl, .container-xxl {
        max-width: 500px !important;
    }
    </style>

    <div class="container">
        <div class="glass-card text-center">
            <h2 class="mb-4">Welcome Back!</h2>
            <p class="mb-4">Login with MetaMask and credentials</p>

            <form id="loginForm">
                <div class="mb-3">
                    <input id="email" type="email" class="form-control" placeholder="Email" required>
                </div>
                <div class="mb-3">
                    <input id="password" type="password" class="form-control" placeholder="Password" required>
                </div>
                <div class="mb-3">
                    <button type="button" class="btn btn-light w-100" id="connectBtn">🔗 Connect MetaMask</button>
                </div>
                <input type="hidden" id="wallet" />
                <button type="submit" class="btn btn-login w-100 mb-3">Login</button>

                <div class="social-icons mb-3">
                    <a href="#"><i class="fab fa-google"></i></a>
                    <a href="#"><i class="fab fa-facebook"></i></a>
                </div>

                <p class="mt-3">Don't have an account? <a href="#" class="forgot-password">Sign Up</a></p>
            </form>
        </div>
    </div>

    <script>
        document.getElementById('connectBtn').addEventListener('click', async () => {
            if (typeof window.ethereum !== 'undefined') {
                try {
                    const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
                    const wallet = accounts[0];
                    localStorage.setItem('wallet', wallet);
                    document.getElementById('wallet').value = wallet;
                    alert('Wallet connected: ' + wallet);
                } catch (err) {
                    alert('MetaMask connection failed: ' + err.message);
                }
            } else {
                alert('MetaMask not detected. Please install it.');
            }
        });

        document.getElementById('loginForm').addEventListener('submit', function (event) {
            event.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const wallet = document.getElementById('wallet').value;

            if (!wallet) {
                alert('Please connect MetaMask before logging in!');
                return;
            }

            fetch('/api/handle_login', {
                                        method: 'POST',
                                        headers: { 'Content-Type': 'application/json' },
                                        body: JSON.stringify({ email, password, wallet })
                                    })
                                    .then(res => res.json())
                                    .then(data => {
                                        console.log('Login API result:', data);
                                        if (data.success) {
                                            window.location.href = '/dashboard';
                                        } else {
                                            alert('Login failed. Check credentials or wallet.');
                                        }
                                    })
                                    .catch(err => {
                                        console.error('Error parsing response:', err);
                                    });
        });
    </script>
    ''')