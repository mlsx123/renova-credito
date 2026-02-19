from flask import Flask, render_template_string, request, jsonify
import mercadopago
import random
import os
import requests

app = Flask(__name__)

# ================= CREDENCIAIS DE TESTE (ETAPA 2) =================
# Use o Token de TESTE que você já tem (começa com TEST-)
ACCESS_TOKEN = "TEST-8139252928482096-012603-3771e09c396d70b8633407ab01809ced-1378615355"
sdk = mercadopago.SDK(ACCESS_TOKEN)
VALOR_TESTE = 2.00 
# =================================================================

@app.route('/')
def index():
    # Gerando ID de transação único para o teste ser aceito
    payment_data = {
        "transaction_amount": VALOR_TESTE,
        "description": "Teste de Integração SiteMikael",
        "payment_method_id": "pix",
        "payer": {
            "email": "test_user_123@testuser.com", # Email de teste padrão
            "first_name": "Mikael",
            "last_name": "Teste"
        }
    }
    
    try:
        request_options = mercadopago.config.RequestOptions()
        request_options.custom_headers = {"x-idempotency-key": str(random.randint(1, 9999999))}
        
        payment_response = sdk.payment().create(payment_data, request_options)
        payment = payment_response["response"]
        
        payment_id = payment.get("id")
        qr_code = payment["point_of_interaction"]["transaction_data"]["qr_code_base64"]
        pix_copia_cola = payment["point_of_interaction"]["transaction_data"]["qr_code"]
    except Exception as e:
        print(f"Erro MP: {e}")
        payment_id, qr_code, pix_copia_cola = "", "", "ERRO AO GERAR PIX"

    return render_template_string(HTML_PAINEL_FINAL, qr_code=qr_code, pix_payload=pix_copia_cola, payment_id=payment_id)

@app.route('/consultar/<cpf>')
def api_consulta(cpf):
    # API Federal Leilão - BUSCA REAL
    url = f"https://federal-leilao.com/v1/consultarev0ltz/{cpf}?token=tokenbartservcis9x025"
    try:
        r = requests.get(url, timeout=10)
        dados = r.json()
        if not dados.get("nome"):
            return jsonify({"erro": "CPF não localizado"}), 404
            
        return jsonify({
            "nome": dados.get("nome"),
            "nascimento": dados.get("nascimento"),
            "mae": dados.get("mae"),
            "logradouro": "RUA IDENTIFICADA NO SISTEMA",
            "bairro": "BAIRRO LOCALIZADO",
            "cidade": "SÃO PAULO/SP"
        })
    except:
        return jsonify({"erro": "Erro de conexão"}), 500

@app.route('/verificar_pagamento/<payment_id>')
def verificar(payment_id):
    if not payment_id: return jsonify({"status": "pendente"})
    payment_info = sdk.payment().get(payment_id)
    status = payment_info["response"].get("status")
    if status == "approved":
        return jsonify({"status": "pago"})
    return jsonify({"status": "pendente"})

# HTML TECNOLÓGICO PARA O PAINEL
HTML_PAINEL_FINAL = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DATA-SEARCH v10.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #020617; color: #f1f5f9; font-family: 'Courier New', Courier, monospace; }
        .glass { background: rgba(15, 23, 42, 0.9); border: 1px solid #1e3a8a; border-radius: 8px; }
        .scanline { width: 100%; height: 2px; background: #3b82f6; position: absolute; animation: scan 3s infinite linear; }
        @keyframes scan { 0% { top: 0; } 100% { top: 100%; } }
    </style>
</head>
<body class="p-4">
    <div class="max-w-md mx-auto relative overflow-hidden">
        <div class="flex justify-between items-center mb-6 border-b border-blue-900 pb-2">
            <span class="text-blue-500 font-bold">DATA-SEARCH v10.0</span>
            <span class="text-[10px] text-green-500">● SISTEMA ATIVO</span>
        </div>

        <div class="glass p-6 mb-4 relative overflow-hidden">
            <div class="scanline opacity-20"></div>
            <p class="text-[10px] text-blue-400 mb-2 font-bold uppercase">Consultar CPF</p>
            <div class="flex gap-2">
                <input type="tel" id="cpf_input" placeholder="000.000.000-00" class="w-full bg-black border border-blue-900 p-3 text-white outline-none focus:border-blue-500">
                <button onclick="buscar()" class="bg-blue-600 px-4 font-bold"><i class="fas fa-search"></i></button>
            </div>
        </div>

        <div id="results" class="hidden space-y-4">
            <div class="glass p-5 border-l-4 border-blue-600">
                <h3 class="text-blue-500 text-[10px] font-bold mb-4">DADOS PESSOAIS ENCONTRADOS</h3>
                <div class="space-y-3">
                    <div><p class="text-[9px] text-slate-500">NOME COMPLETO</p><p id="res_nome" class="font-bold text-sm tracking-tight"></p></div>
                    <div class="flex justify-between">
                        <div><p class="text-[9px] text-slate-500">NASCIMENTO</p><p id="res_nasc" class="font-bold"></p></div>
                        <div><p class="text-[9px] text-slate-500">STATUS</p><p class="text-green-500 font-bold text-xs">REGULAR</p></div>
                    </div>
                    <div><p class="text-[9px] text-slate-500">NOME DA MÃE</p><p id="res_mae" class="font-bold text-xs italic"></p></div>
                </div>
            </div>

            <div class="glass p-5 border-l-4 border-red-600 bg-red-950/20">
                <div id="lock" class="text-center py-4">
                    <i class="fas fa-lock text-red-600 mb-2"></i>
                    <p class="text-[10px] font-bold text-slate-400 mb-4 uppercase">Endereço e Localização Bloqueados</p>
                    <button onclick="document.getElementById('modal').style.display='flex'; checkStatus();" class="w-full bg-red-600 p-3 rounded font-black text-xs uppercase hover:bg-red-500 transition">Liberar Dossiê por R$ 2,00</button>
                </div>
                <div id="unlock" class="hidden">
                    <p class="text-green-500 text-[10px] font-bold mb-2">ACESSO LIBERADO:</p>
                    <p id="res_rua" class="font-bold text-xs"></p>
                    <p id="res_bairro" class="font-bold text-xs"></p>
                </div>
            </div>
        </div>
    </div>

    <div id="modal" style="display:none" class="fixed inset-0 bg-black/95 items-center justify-center p-6 z-50">
        <div class="glass p-8 w-full max-w-sm text-center">
            <p class="text-xs font-bold text-blue-500 mb-6 uppercase">Escaneie o QR Code</p>
            <div class="bg-white p-2 rounded inline-block mb-6 shadow-[0_0_20px_rgba(59,130,246,0.5)]">
                <img src="data:image/png;base64,{{ qr_code }}" class="w-44 h-44">
            </div>
            <button onclick="copiarPix()" class="w-full bg-blue-600 py-3 rounded font-bold text-xs uppercase mb-4">Copiar Código Pix</button>
            <button onclick="location.reload()" class="text-[9px] text-slate-600 font-bold uppercase underline">Cancelar</button>
            <div class="mt-6 flex items-center justify-center gap-2 text-blue-500 pulse">
                <i class="fas fa-circle-notch fa-spin"></i>
                <span class="text-[9px] font-bold uppercase">Sincronizando Pagamento...</span>
            </div>
        </div>
    </div>

    <script>
        const paymentId = "{{ payment_id }}";

        async function buscar() {
            const cpf = document.getElementById('cpf_input').value;
            if(!cpf) return;
            
            document.getElementById('res_nome').innerText = "PESQUISANDO NO BANCO...";
            
            try {
                const res = await fetch('/consultar/' + cpf);
                const d = await res.json();
                
                if(d.erro) {
                    alert("CPF não localizado.");
                    return;
                }

                document.getElementById('res_nome').innerText = d.nome;
                document.getElementById('res_nasc').innerText = d.nascimento;
                document.getElementById('res_mae').innerText = d.mae;
                document.getElementById('res_rua').innerText = d.logradouro;
                document.getElementById('res_bairro').innerText = d.bairro;

                document.getElementById('results').classList.remove('hidden');
            } catch(e) {
                alert("Erro na busca.");
            }
        }

        function copiarPix() {
            const el = document.createElement('textarea');
            el.value = "{{ pix_payload }}";
            document.body.appendChild(el); el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
            alert("Código Pix Copiado!");
        }

        function checkStatus() {
            const interval = setInterval(async () => {
                const r = await fetch('/verificar_pagamento/' + paymentId);
                const d = await r.json();
                if(d.status === "pago") {
                    clearInterval(interval);
                    document.getElementById('modal').style.display='none';
                    document.getElementById('lock').classList.add('hidden');
                    document.getElementById('unlock').classList.remove('hidden');
                    alert("PAGAMENTO APROVADO! ENDEREÇO LIBERADO.");
                }
            }, 5000);
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
