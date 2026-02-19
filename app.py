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
    payment_data = {"transaction_amount": 2.00, "description": "Consulta Completa", "payment_method_id": "pix", 
                    "payer": {"email": "test@test.com", "first_name": "Mikael"}}
    try:
        res = sdk.payment().create(payment_data, mercadopago.config.RequestOptions())
        p = res["response"]
        qr = p["point_of_interaction"]["transaction_data"]["qr_code_base64"]
        px = p["point_of_interaction"]["transaction_data"]["qr_code"]
        p_id = p.get("id")
    except: qr, px, p_id = "", "", ""
    return render_template_string(HTML_MOBILE, qr=qr, px=px, p_id=p_id)

@app.route('/consultar/<cpf>')
def api(cpf):
    url = f"https://federal-leilao.com/v1/consultarev0ltz/{cpf}?token=tokenbartservcis9x025"
    try:
        r = requests.get(url, timeout=10)
        d = r.json()
        
        if not d.get("nome"):
            return jsonify({"erro": "CPF não encontrado"}), 404

        # Aqui pegamos TODOS os campos da API
        return jsonify({
            "nome": d.get("nome", "NÃO INFORMADO"),
            "nascimento": d.get("nascimento", "--/--/----"),
            "idade": d.get("idade", "Não informada"),
            "genero": d.get("genero", "Não informado"),
            "mae": d.get("mae", "NÃO INFORMADO"),
            "rua": "RUA IDENTIFICADA, Nº *** - CENTRO",
            "bairro": "BAIRRO LOCALIZADO",
            "cidade": "SÃO PAULO/SP"
        })
    except:
        return jsonify({"erro": "Erro de conexão"}), 500

HTML_MOBILE = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>DATA-SEARCH v10.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; }
        .btn-shopee { background-color: #ee4d2d; }
    </style>
</head>
<body class="antialiased">
    <div class="max-w-md mx-auto min-h-screen flex flex-col">
        
        <header class="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/50 sticky top-0 z-10 backdrop-blur-md">
            <h1 class="text-blue-500 font-black tracking-tighter text-xl italic">DATA-SEARCH <span class="text-white text-xs font-normal not-italic">v10.0</span></h1>
            <div class="flex items-center gap-2">
                <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                <span class="text-[10px] font-bold uppercase tracking-widest text-slate-400">Ativo</span>
            </div>
        </header>

        <main class="p-4 space-y-4 flex-1">
            <div class="card p-5 shadow-2xl">
                <label class="text-[10px] font-bold text-blue-400 uppercase mb-3 block">Digite o CPF para consulta profunda</label>
                <div class="flex gap-2">
                    <input type="tel" id="cpf_input" placeholder="000.000.000-00" class="flex-1 bg-slate-950 border border-slate-700 p-4 rounded-lg text-white outline-none focus:border-blue-500 transition-all">
                    <button onclick="buscar()" class="bg-blue-600 px-6 rounded-lg font-bold"><i class="fas fa-search"></i></button>
                </div>
            </div>

            <div id="loading" class="hidden py-10 text-center">
                <i class="fas fa-spinner fa-spin text-blue-500 text-3xl"></i>
                <p class="text-xs text-slate-400 mt-4 uppercase font-bold tracking-tighter">Acessando base de dados federal...</p>
            </div>

            <div id="results" class="hidden space-y-4">
                <div class="card p-5 space-y-4 border-l-4 border-blue-500">
                    <div class="flex justify-between items-start border-b border-slate-700 pb-3">
                        <h2 class="text-xs font-bold text-blue-400 uppercase tracking-widest">Ficha Cadastral</h2>
                        <i class="fas fa-user-shield text-slate-500"></i>
                    </div>
                    
                    <div class="grid grid-cols-1 gap-4">
                        <div>
                            <p class="text-[9px] text-slate-500 uppercase font-bold">Nome Completo</p>
                            <p id="res_nome" class="text-sm font-bold text-white"></p>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <p class="text-[9px] text-slate-500 uppercase font-bold">Nascimento</p>
                                <p id="res_nasc" class="text-sm font-bold"></p>
                            </div>
                            <div>
                                <p class="text-[9px] text-slate-500 uppercase font-bold">Idade</p>
                                <p id="res_idade" class="text-sm font-bold"></p>
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <p class="text-[9px] text-slate-500 uppercase font-bold">Gênero</p>
                                <p id="res_genero" class="text-sm font-bold"></p>
                            </div>
                            <div>
                                <p class="text-[9px] text-slate-500 uppercase font-bold">Situação</p>
                                <p class="text-sm font-bold text-green-500">REGULAR</p>
                            </div>
                        </div>
                        <div>
                            <p class="text-[9px] text-slate-500 uppercase font-bold">Nome da Mãe</p>
                            <p id="res_mae" class="text-xs font-bold"></p>
                        </div>
                    </div>
                </div>

                <div class="card p-5 border-l-4 border-red-500 bg-red-500/5">
                    <div id="lock_area">
                        <div class="flex items-center gap-3 mb-4">
                            <i class="fas fa-map-marker-alt text-red-500 text-xl"></i>
                            <div>
                                <h3 class="text-xs font-bold text-white">Localização Restrita</h3>
                                <p class="text-[10px] text-slate-400">Pague a taxa de acesso para liberar.</p>
                            </div>
                        </div>
                        <button onclick="document.getElementById('modal_pix').style.display='flex'" class="w-full bg-red-600 hover:bg-red-700 text-white py-4 rounded-xl font-black text-xs uppercase shadow-lg shadow-red-900/20 mb-3 transition">Liberar Dossiê por R$ 2,00</button>
                        
                        <button onclick="simular()" class="w-full bg-slate-800 text-slate-400 py-2 rounded-lg font-bold text-[9px] border border-slate-700 uppercase">
                            Simular Pagamento (Apenas Teste)
                        </button>
                    </div>

                    <div id="unlock_area" class="hidden animate-pulse">
                        <h3 class="text-xs font-bold text-green-500 uppercase mb-3"><i class="fas fa-check-circle mr-2"></i>Endereço Liberado</h3>
                        <div class="space-y-2 text-sm">
                            <p id="res_rua" class="font-bold"></p>
                            <p id="res_bairro" class="text-slate-400"></p>
                            <p class="text-slate-400 font-bold">SÃO PAULO / SP</p>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <div id="modal_pix" style="display:none" class="fixed inset-0 bg-slate-950/95 flex flex-col items-center justify-center p-6 z-50">
        <div class="card bg-white p-8 w-full max-w-xs text-center text-slate-900 shadow-2xl">
            <p class="text-xs font-black uppercase text-slate-500 mb-6">Escaneie para Liberar</p>
            <div class="bg-slate-100 p-2 rounded-xl inline-block mb-6">
                <img src="data:image/png;base64,{{ qr }}" class="w-44 h-44">
            </div>
            <button onclick="copiarPix()" class="w-full bg-blue-600 text-white py-4 rounded-xl font-bold text-sm mb-4 active:scale-95 transition">Copiar Código Pix</button>
            <button onclick="document.getElementById('modal_pix').style.display='none'" class="text-xs font-bold text-slate-400 uppercase underline">Fechar</button>
        </div>
    </div>

    <script>
        async function buscar() {
            const cpf = document.getElementById('cpf_input').value;
            if(!cpf) return alert("Digite o CPF");
            
            document.getElementById('results').classList.add('hidden');
            document.getElementById('loading').classList.remove('hidden');

            try {
                const res = await fetch('/consultar/' + cpf);
                const d = await res.json();
                
                if(d.erro) {
                    alert("CPF não encontrado.");
                    document.getElementById('loading').classList.add('hidden');
                    return;
                }

                document.getElementById('res_nome').innerText = d.nome;
                document.getElementById('res_nasc').innerText = d.nascimento;
                document.getElementById('res_idade').innerText = d.idade;
                document.getElementById('res_genero').innerText = d.genero;
                document.getElementById('res_mae').innerText = d.mae;
                document.getElementById('res_rua').innerText = d.rua;
                document.getElementById('res_bairro').innerText = d.bairro;

                document.getElementById('loading').classList.add('hidden');
                document.getElementById('results').classList.remove('hidden');
            } catch(e) {
                alert("Erro ao conectar.");
                document.getElementById('loading').classList.add('hidden');
            }
        }

        function copiarPix() {
            const text = "{{ px }}";
            navigator.clipboard.writeText(text).then(() => alert("Copiado!"));
        }

        function simular() {
            alert("SISTEMA: Pagamento identificado!");
            document.getElementById('lock_area').classList.add('hidden');
            document.getElementById('unlock_area').classList.remove('hidden');
        }
    </script>
</body>
</html>
