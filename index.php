<?php
// Define que o arquivo retornará dados em formato JSON
header('Content-Type: application/json');
session_start(); 

// Define constantes importantes
define('URL_API', 'https://bateu.bet.br/api/bff/address-by-cpf');
define('LIMITE_MAX_CPFS', 100);

// ***************************************************************
// ATENÇÃO: NOVO MAPA DE CAMPOS (COM 'Número' logo após 'Rua')
// ***************************************************************
$map_campos = [
    'zipcode' => 'CEP',
    'street' => 'Rua',        
    'number' => 'Número',     // AGORA EM PORTUGUÊS E NA POSIÇÃO CORRETA
    'neighborhood' => 'Bairro',
    'city' => 'Cidade',
    'state' => 'Estado'
];

// ***************************************************************
// ATENÇÃO: PREENCHA SEUS HEADERS AQUI. (SEUS TOKENS E COOKIES)
// ***************************************************************
$headers_api = [
    'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36',
    'Accept: application/json',
    'language: pt-br',
    'authorization: Bearer SEU_TOKEN_AQUI', // <-- MUDE ESTA LINHA!
    'city: Fortaleza',
    'tenant: bateu.bet.br',
    'origin: https://bateu.bet.br',
    'sec-fetch-site: same-origin',
    'sec-fetch-mode: cors',
    'sec-fetch-dest: empty',
    'referer: https://bateu.bet.br/?btag=...',
    'Cookie: __cf_bm=SEU_CF_BM_AQUI; bet7k_session=SEU_SESSION_AQUI' // <-- MUDE ESTA LINHA!
];
// ***************************************************************

// --- FUNÇÕES PHP ---

/**
 * Realiza a consulta do endereço pelo CPF na API usando file_get_contents.
 */
function consultar_cpf($cpf_consulta, $headers) {
    
    $payload = json_encode(["cpf" => $cpf_consulta]);

    $header_string = implode("\r\n", $headers) . "\r\n" . 
                     "Content-Type: application/json\r\n" . 
                     "Content-Length: " . strlen($payload);

    $options = [
        'http' => [
            'method'  => 'POST',
            'header'  => $header_string,
            'content' => $payload,
            'timeout' => 15,
        ],
        'ssl' => [
            'allow_self_signed' => true,
            'verify_peer' => false,
            'verify_peer_name' => false,
        ]
    ];
    
    $context = stream_context_create($options);
    $response = @file_get_contents(URL_API, false, $context);

    if ($response === false) {
        return ["error" => true, "message" => "Falha de Conexão: O host pode estar bloqueando a requisição externa."];
    }
    
    $resultado = json_decode($response, true);
    
    if (json_last_error() !== JSON_ERROR_NONE) {
        return ["error" => true, "message" => "Resposta da API inválida ou ilegível."];
    }

    if (isset($resultado['message']) && is_string($resultado['message'])) {
         return ["error" => true, "message" => $resultado['message']];
    }
    
    return $resultado;
}

/**
 * EXTRAI o número da rua e o separa do campo 'street'.
 */
function processar_resultado_endereco($data) {
    if (isset($data['street']) && is_string($data['street'])) {
        $street = trim($data['street']);
        
        $pattern = '/^(.+?),\s*(\d+)\s*[-|–]?\s*(.*)$/';
        $matches = [];
        
        if (preg_match($pattern, $street, $matches)) {
            
            $data['number'] = trim($matches[2]);
            $nova_rua = trim($matches[1]);
            $complemento = trim($matches[3]);
            
            $data['street'] = $nova_rua . ($complemento ? ' - ' . $complemento : '');
        } else {
            // Tenta procurar só um número no final da rua
            $pattern_end = '/^(.+?)\s+(\d+)$/';
             if (preg_match($pattern_end, $street, $matches)) {
                $data['number'] = trim($matches[2]);
                $data['street'] = trim($matches[1]);
            } else {
                // Se nada for encontrado
                $data['number'] = 'S/N';
            }
        }
    }
    
    if (!isset($data['number'])) {
        $data['number'] = 'S/N'; 
    }
    
    return $data;
}


/**
 * Extrai CPFs válidos de um bloco de texto.
 */
function extrair_cpfs($texto_entrada) {
    preg_match_all('/\d{11}/', $texto_entrada, $matches);
    $cpfs = $matches[0] ?? [];
    $lista_unica = array_unique($cpfs);
    
    if (count($lista_unica) > LIMITE_MAX_CPFS) {
        $alerta = "[ALERTA]: Lista com " . count($lista_unica) . " CPFs. Processando apenas os primeiros " . LIMITE_MAX_CPFS . ".";
        return ['cpfs' => array_slice($lista_unica, 0, LIMITE_MAX_CPFS), 'warning' => $alerta];
    }
    return ['cpfs' => $lista_unica, 'warning' => null];
}


// --- PROCESSAMENTO PRINCIPAL ---
$response_data = ['success' => false, 'results' => [], 'error' => null, 'warning' => null, 'mode' => 'lote'];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $modo_consulta = $_POST['modo_consulta'] ?? 'lote';
    $response_data['mode'] = $modo_consulta;
    $cpfs_a_processar = [];
    $warning_msg = null;

    if ($modo_consulta === 'unitario' && !empty($_POST['cpf_unitario'])) {
        $cpf_limpo = preg_replace('/\D/', '', $_POST['cpf_unitario']); 
        if (strlen($cpf_limpo) === 11) {
            $cpfs_a_processar = [$cpf_limpo];
        } else {
            $response_data['error'] = "O CPF inserido não é válido (deve ter 11 dígitos).";
        }
    } elseif ($modo_consulta === 'lote' && !empty($_POST['cpf_bloco'])) {
        $extracao = extrair_cpfs($_POST['cpf_bloco']);
        $cpfs_a_processar = $extracao['cpfs'];
        $warning_msg = $extracao['warning'];
        
        if (empty($cpfs_a_processar)) {
            $response_data['error'] = "Nenhum CPF válido (11 dígitos) encontrado no texto fornecido.";
        }
    }
    
    if (!empty($cpfs_a_processar)) {
        $response_data['success'] = true;
        $response_data['warning'] = $warning_msg;
        
        // ********************************************************
        // AQUI ESTÁ A CHAVE: USAMOS O ARRAY $map_campos COMO GUIA
        // PARA GARANTIR A ORDEM CORRETA DE EXIBIÇÃO.
        // ********************************************************
        foreach ($cpfs_a_processar as $cpf) {
            $resultado_consulta = consultar_cpf($cpf, $headers_api);
            
            // Se não for um erro, processa para separar o número
            if (!isset($resultado_consulta['error'])) {
                $resultado_consulta = processar_resultado_endereco($resultado_consulta);
                
                // Reordena o resultado final usando a ordem de $map_campos
                $resultado_ordenado = [];
                foreach (array_keys($map_campos) as $key) {
                    if (isset($resultado_consulta[$key])) {
                        $resultado_ordenado[$key] = $resultado_consulta[$key];
                    }
                }
                $resultado_consulta = $resultado_ordenado;
            }
            
            $response_data['results'][] = [
                'cpf' => $cpf,
                'data' => $resultado_consulta
            ];
        }
    }
} else {
     $response_data['error'] = "Método de requisição inválido. Use POST.";
}

echo json_encode($response_data);
session_write_close();
exit;

?>
