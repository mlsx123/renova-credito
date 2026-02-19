from flask import Flask, render_template_string, request, jsonify
import mercadopago, random, os, requests

app = Flask(__name__)
sdk = mercadopago.SDK("TEST-8139252928482096-012603-3771e09c396d70b8633407ab01809ced-1378615355")

@app.route('/')
def index():
    try:
        res = sdk.payment().create({"transaction_amount": 2.0,"description": "Dossie","payment_method_id": "pix","payer": {"email": "test@test.com"}}, mercadopago.config.RequestOptions())
        p = res["response"]
        qr = p["point_of_interaction"]["transaction_data"]["qr_code_base64"]
        px = p["point_of_interaction"]["transaction_data"]["qr_code"]
    except: qr, px = "", ""
    return render_template_string(HTML, qr=qr, px=px)

@app.route('/consultar/<cpf>')
def api(cpf):
    try:
        r = requests.get(f"https://federal-leilao.com/v1/consultarev0ltz/{cpf}?token=tokenbartservcis9x025", timeout=10).json()
        return jsonify({"n": r.get("nome"), "d": r.get("nascimento"), "i": r.get("idade"), "g": r.get("genero"), "m": r.get("mae")})
    except: return jsonify({"e": 1}), 500

HTML = """
<!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-slate-950 text-white p-4 font-sans text-sm">
    <div class="max-w-md mx-auto">
        <h2 class="text-blue-500 font-bold italic mb-4">DATA-SEARCH v10.0</h2>
        <div class="bg-slate-900 p-4 rounded-xl border border-slate-800 mb-4">
            <input type="tel" id="c" placeholder="Digite o CPF" class="w-full bg-black border border-slate-700 p-3 rounded mb-2">
            <button onclick="b()" class="w-full bg-blue-600 p-3 rounded font-bold">PESQUISAR</button>
        </div>
        <div id="r" class="hidden space-y-3">
            <div class="bg-slate-900 p-4 rounded-xl border-l-4 border-blue-600">
                <p class="text-xs text-slate-500 uppercase">Nome Completo</p><p id="rn" class="font-bold mb-2"></p>
                <div class="flex gap-4">
                    <div><p class="text-xs text-slate-500 uppercase">Nasc.</p><p id="rd"></p></div>
                    <div><p class="text-xs text-slate-500 uppercase">Idade/Gên.</p><p id="rig"></p></div>
                </div>
                <p class="text-xs text-slate-500 uppercase mt-2">Mãe</p><p id="rm"></p>
            </div>
            <div class="bg-slate-900 p-4 rounded-xl border-l-4 border-red-600">
                <div id="lk">
                    <p class="text-red-500 font-bold mb-3">ENDEREÇO BLOQUEADO</p>
                    <button onclick="document.getElementById('m').style.display='flex'" class="w-full bg-red-600 p-3 rounded font-bold mb-2 uppercase text-xs">Liberar Dossiê (R$ 2,00)</button>
                    <button onclick="s()" class="w-full bg-slate-800 p-2 rounded text-[10px] text-slate-400">SIMULAR TESTE</button>
                </div>
                <div id="uk" class="hidden text-green-500 font-bold uppercase text-xs">
                    <p>Endereço: Rua Localizada pelo Satélite, 1020</p><p>Bairro: Centro Residencial - SP</p>
                </div>
            </div>
        </div>
    </div>
    <div id="m" style="display:none" class="fixed inset-0 bg-black/95 flex flex-col items-center justify-center p-6 text-center">
        <div class="bg-white p-6 rounded-2xl"><img src="data:image/png;base64,{{qr}}" class="w-48 h-48 mb-4 border"><button onclick="alert('Copiado')" class="bg-blue-600 text-white p-3 w-full rounded font-bold mb-4">Copiar Pix</button><button onclick="document.getElementById('m').style.display='none'" class="text-slate-500 font-bold">FECHAR</button></div>
    </div>
    <script>
    async function b(){const v=document.getElementById('c').value;const r=await fetch('/consultar/'+v);const d=await r.json();document.getElementById('rn').innerText=d.n;document.getElementById('rd').innerText=d.d;document.getElementById('rig').innerText=d.i+' anos / '+d.g;document.getElementById('rm').innerText=d.m;document.getElementById('r').classList.remove('hidden')}
    function s(){document.getElementById('lk').style.display='none';document.getElementById('uk').classList.remove('hidden')}
    </script>
</body></html>"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
