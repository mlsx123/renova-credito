from flask import Flask, render_template_string, request, jsonify
import mercadopago
import random
import os
import requests

app = Flask(__name__)

# CREDENCIAIS
ACCESS_TOKEN = "TEST-8139252928482096-012603-3771e09c396d70b8633407ab01809ced-1378615355"
sdk = mercadopago.SDK(ACCESS_TOKEN)

@app.route('/')
def index():
    payment_data = {"transaction_amount": 2.00, "description": "Consulta", "payment_method_id": "pix", 
                    "payer": {"email": "test@test.com", "first_name": "Mikael"}}
    try:
        res = sdk.payment().create(payment_data, mercadopago.config.RequestOptions())
        p = res["response"]
        qr = p["point_of_interaction"]["transaction_data"]["qr_code_base64"]
        px = p["point_of_interaction"]["transaction_data"]["qr_code"]
    except: qr, px = "", ""
    return render_template_string(HTML, qr=qr, px=px)

@app.route('/consultar/<cpf>')
def api(cpf):
    # BUSCA REAL
    r = requests.get(f"https://federal-leilao.com/v1/consultarev0ltz/{cpf}?token=tokenbartservcis9x025")
    d = r.json()
    return jsonify({
        "nome": d.get("nome", "NÃO ENCONTRADO"),
        "mae": d.get("mae", "NÃO ENCONTRADO"),
        "rua": "RUA TESTE, 123 - CENTRO"
    })

HTML = r"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-black text-white p-6 font-mono">
    <h2 class="text-blue-500 mb-6 border-b border-blue-900 pb-2">DATA-SEARCH v10.0</h2>
    
    <input type="tel" id="cpf" placeholder="DIGITE CPF" class="w-full bg-slate-900 p-4 rounded mb-2 outline-none border border-blue-900">
    <button onclick="buscar()" class="w-full bg-blue-700 p-4 font-bold rounded mb-8">PESQUISAR</button>

    <div id="res" class="hidden border border-slate-700 p-4 rounded bg-slate-900">
        <p class="text-xs text-blue-400">NOME:</p>
        <p id="n" class="mb-4 font-bold"></p>
        
        <div id="lock">
            <p class="text-red-500 font-bold text-xs mb-4">ENDEREÇO BLOQUEADO!</p>
            <button onclick="document.getElementById('pix').style.display='flex'" class="w-full bg-red-600 p-4 rounded font-bold mb-4">PAGAR R$ 2,00</button>
            
            <button onclick="simular()" class="w-full bg-green-600 p-2 rounded text-xs font-bold uppercase">
                [ TESTE: SIMULAR PAGAMENTO APROVADO ]
            </button>
        </div>

        <div id="unlock" class="hidden text-green-500">
            <p class="text-xs font-bold">ENDEREÇO LIBERADO:</p>
            <p id="rua" class="font-bold"></p>
        </div>
    </div>

    <div id="pix" style="display:none" class="fixed inset-0 bg-black/95 flex-col items-center justify-center p-6">
        <p class="mb-4 font-bold">PAGUE O PIX:</p>
        <img src="data:image/png;base64,{{ qr }}" class="w-64 bg-white p-2 rounded mb-4">
        <button onclick="alert('Copiado')" class="bg-blue-600 p-4 w-full rounded font-bold mb-4 italic">COPIAR CÓDIGO</button>
        <button onclick="document.getElementById('pix').style.display='none'" class="text-slate-500 underline">FECHAR</button>
    </div>

    <script>
        async function buscar() {
            const val = document.getElementById('cpf').value;
            const r = await fetch('/consultar/' + val);
            const d = await r.json();
            document.getElementById('n').innerText = d.nome;
            document.getElementById('rua').innerText = d.rua;
            document.getElementById('res').classList.remove('hidden');
        }
        function simular() {
            alert('Simulando aprovação...');
            document.getElementById('lock').classList.add('hidden');
            document.getElementById('unlock').classList.remove('hidden');
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
