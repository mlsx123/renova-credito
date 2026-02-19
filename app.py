from flask import Flask, render_template_string, request, jsonify
import mercadopago
import random
import os
import requests

app = Flask(__name__)

# ================= CREDENCIAIS DE TESTE =================
ACCESS_TOKEN = "TEST-8139252928482096-012603-3771e09c396d70b8633407ab01809ced-1378615355"
sdk = mercadopago.SDK(ACCESS_TOKEN)
VALOR_CONSULTA = 2.00 
# ========================================================

@app.route('/')
def index():
    payment_data = {
        "transaction_amount": VALOR_CONSULTA,
        "description": "Acesso Painel DATA-SEARCH",
        "payment_method_id": "pix",
        "payer": {"email": "teste@teste.com", "first_name": "Mikael", "last_name": "User"}
    }
    try:
        request_options = mercadopago.config.RequestOptions()
        request_options.custom_headers = {"x-idempotency-key": str(random.randint(1, 999999))}
        payment_response = sdk.payment().create(payment_data, request_options)
        payment = payment_response["response"]
        payment_id = payment.get("id")
        qr_code = payment["point_of_interaction"]["transaction_data"]["qr_code_base64"]
        pix_copia_cola = payment["point_of_interaction"]["transaction_data"]["qr_code"]
    except:
        payment_id, qr_code, pix_copia_cola = "", "", ""

    return render_template_string(HTML_PANEL, qr_code=qr_code, pix_payload=pix_copia_cola, payment_id=payment_id)

@app.route('/consultar/<cpf>')
def api_consulta(cpf):
    url = f"https://federal-leilao.com/v1/consultarev0ltz/{cpf}?token=tokenbartservcis9x025"
    try:
        r = requests.get(url, timeout=10)
        dados_api = r.json()
        return jsonify({
            "nome": dados_api.get("nome", "NÃO LOCALIZADO"),
            "nascimento": dados_api.get("nascimento", "--/--/----"),
            "mae": dados_api.get("mae", "NÃO CONSTA"),
            "logradouro": "RUA LOCALIZADA VIA SATÉLITE",
            "bairro": "CENTRO ECONÔMICO"
        })
    except:
        return jsonify({"erro": "Erro na API"}), 500

@app.route('/verificar_pagamento/<payment_id>')
def verificar(payment_id):
    if not payment_id or payment_id == "undefined":
        return jsonify({"status": "pendente"})
    payment_info = sdk.payment().get(payment_id)
    if payment_info["response"].get("status") == "approved":
        return jsonify({"status": "pago"})
    return jsonify({"status": "pendente"})

HTML_PANEL = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DATA-SEARCH v10.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #020617; color: #f1f5f9; font-family: monospace; }
        .glass { background: rgba(15, 23, 42, 0.95); border: 1px solid #1e3a8a; border-radius: 8px; }
    </style>
</head>
<body class="p-4">
    <div class="max-w-md mx-auto">
        <h1 class="text-blue-500 font-bold mb-6 border-b border-blue-900 pb-2 italic">DATA-SEARCH v10.0</h1>

        <div class="glass p-6 mb-4">
            <p class="text-[10px] text-blue-400 font-bold mb-2">BUSCAR CPF:</p>
            <div class="flex gap-2">
                <input type="tel" id="cpf_input" placeholder="000.000.000-00" class="flex-1 bg-black border border-blue-900 p-3 outline-none">
                <button onclick="buscar()" class="bg-blue-600 px-6 font-bold uppercase text-xs">OK</button>
            </div>
        </div>

        <div id="results" class="hidden space-y-4">
            <div class="glass p-5 border-l-4 border-blue-600">
                <p class="text-[9px] text-slate-500 uppercase">Nome Completo:</p>
                <p id="res_nome" class="font-bold mb-3"></p>
                <p class="text-[9px] text-slate-500 uppercase">Mãe:</p>
                <p id="res_mae" class="font-bold text-xs"></p>
            </div>

            <div class="glass p-5 border-l-4 border-red-600">
                <div id="lock_area">
                    <p class="text-[10px] font-bold text-red-500 mb-4 uppercase">Endereço Bloqueado</p>
                    <button onclick="document.getElementById('modal_pix').classList.remove('hidden'); document.getElementById('modal_pix').classList.add('flex');" class="w-full bg-red-600 p-4 rounded font-bold uppercase text-xs">Liberar Dossiê (R$ 2,00)</button>
                </div>
                <div id="unlock_area" class="hidden">
                    <p class="text-green-500 text-[10px] font-bold uppercase">Endereço Liberado:</p>
                    <p id="res_rua" class="font-bold text-xs"></p>
                </div>
            </div>
        </div>
    </div>

    <div id="modal_pix" class="fixed inset-0 bg-black/95 hidden items-center justify-center p-6 z-[999]">
        <div class="bg-white p-6 rounded-lg w-full max-w-xs text-center text-black">
            <p class="font-bold text-xs mb-4 uppercase">Escaneie o QR Code abaixo:</p>
            
            <img src="data:image/png;base64,{{ qr_code }}" class="w-48 h-48 mx-auto mb-4 border border-slate-200">
            
            <button onclick="copiarPix()" class="w-full bg-blue-600 text-white py-3 rounded font-bold mb-4 uppercase text-[10px]">Copiar Código Pix</button>
            
            <button onclick="simularPagamento()" class="w-full bg-green-500 text-white py-3 rounded font-bold uppercase text-[10px] mb-4">
                SIMULAR PAGAMENTO (DEBUG)
            </button>

            <button onclick="document.getElementById('modal_pix').classList.add('hidden')" class="text-[9px] text-slate-400 font-bold uppercase tracking-widest">Fechar / Cancelar</button>
        </div>
    </div>

    <script>
        const paymentId = "{{ payment_id }}";

        async function buscar() {
            const cpf = document.getElementById('cpf_input').value;
            if(!cpf) return;
            const res = await fetch('/consultar/' + cpf);
            const d = await res.json();
            document.getElementById('res_nome').innerText = d.nome;
            document.getElementById('res_mae').innerText = d.mae;
            document.getElementById('res_rua').innerText = d.logradouro;
            document.getElementById('results').classList.remove('hidden');
        }

        function copiarPix() {
            const text = "{{ pix_payload }}";
            const el = document.createElement('textarea');
            el.value = text; document.body.appendChild(el);
            el.select(); document.execCommand('copy');
            document.body.removeChild(el);
            alert("Pix Copiado!");
        }

        function simularPagamento() {
            alert("SIMULAÇÃO ATIVA: Liberando dados...");
            document.getElementById('modal_pix').classList.add('hidden');
            document.getElementById('lock_area').classList.add('hidden');
            document.getElementById('unlock_area').classList.remove('hidden');
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
