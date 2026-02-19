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
        "description": "Consulta CPF Painel",
        "payment_method_id": "pix",
        "payer": {"email": "teste@teste.com", "first_name": "User", "last_name": "Teste"}
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
    # AQUI ESTÁ A CHAVE: Usamos o CPF que VOCÊ digitar na URL
    url = f"https://federal-leilao.com/v1/consultarev0ltz/{cpf}?token=tokenbartservcis9x025&cache={random.randint(1,999)}"
    
    try:
        r = requests.get(url, timeout=10)
        dados_api = r.json()
        
        # Se a API retornar erro ou não encontrar, avisamos
        if not dados_api.get("nome"):
             return jsonify({"erro": "CPF inexistente"}), 404

        return jsonify({
            "nome": dados_api.get("nome"),
            "nascimento": dados_api.get("nascimento"),
            "mae": dados_api.get("mae"),
            "logradouro": "RUA IDENTIFICADA",
            "bairro": "BAIRRO LOCALIZADO"
        })
    except:
        return jsonify({"erro": "Erro na API"}), 500

@app.route('/verificar_pagamento/<payment_id>')
def verificar(payment_id):
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
    <title>DATA-SEARCH</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-slate-900 text-white p-4 font-mono">
    <div class="max-w-md mx-auto">
        <div class="border border-blue-500 p-4 rounded mb-6">
            <h2 class="text-blue-500 mb-4 font-bold">TERMINAL DE BUSCA</h2>
            <input type="tel" id="cpf_input" placeholder="DIGITE O CPF" class="w-full bg-black border border-blue-900 p-3 mb-2 outline-none">
            <button onclick="buscar()" class="w-full bg-blue-700 p-3 font-bold uppercase">Consultar</button>
        </div>

        <div id="results" class="hidden space-y-4">
            <div class="bg-slate-800 p-4 rounded">
                <p class="text-blue-400 text-xs">NOME COMPLETO:</p>
                <p id="res_nome" class="font-bold mb-3 italic">---</p>
                
                <p class="text-blue-400 text-xs">NASCIMENTO:</p>
                <p id="res_nasc" class="font-bold mb-3">---</p>

                <p class="text-blue-400 text-xs">MÃE:</p>
                <p id="res_mae" class="font-bold">---</p>
            </div>
            
            <button onclick="document.getElementById('modal').style.display='flex'" class="w-full bg-red-600 p-4 rounded font-bold">PAGAR R$ 2,00 PARA VER ENDEREÇO</button>
        </div>
    </div>

    <div id="modal" style="display:none" class="fixed inset-0 bg-black/90 items-center justify-center p-4">
        <div class="bg-white p-6 rounded text-black text-center">
            <p class="font-bold mb-4">PAGUE O PIX</p>
            <img src="data:image/png;base64,{{ qr_code }}" class="w-48 mx-auto mb-4">
            <button onclick="alert('Código Copiado')" class="bg-blue-600 text-white p-2 rounded">Copiar Pix</button>
            <button onclick="location.reload()" class="block mt-4 text-xs text-slate-400 mx-auto">Fechar</button>
        </div>
    </div>

    <script>
        async function buscar() {
            const cpf = document.getElementById('cpf_input').value;
            if(!cpf) return;
            
            // Limpa antes de mostrar
            document.getElementById('res_nome').innerText = "PESQUISANDO...";
            
            const res = await fetch('/consultar/' + cpf);
            const d = await res.json();
            
            if(d.erro) {
                alert("Erro: " + d.erro);
                return;
            }

            document.getElementById('res_nome').innerText = d.nome;
            document.getElementById('res_nasc').innerText = d.nascimento;
            document.getElementById('res_mae').innerText = d.mae;
            document.getElementById('results').classList.remove('hidden');
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
