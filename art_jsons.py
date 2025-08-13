from datetime import datetime


CREATE_ART_JSON = {
    "id": 0,
    "formaDeRegistro": 1,
    "vinculoFormaDeRegistro": None,
    "vinculoComplementacao": None,
    "participacaoTecnica": 1,
    "vinculoParticipacaoTecnica": None,
    "vinculoEmpreendimento": None,
    "relatorioDeFiscalizacao": None,
    "apelido": None,
    "finalidade": None,
    "profissional": 770778,
    "tipo": 1,
    "situacao": 1,
    "funcionario": 999997,
    "subTipo": 1,
    "observacoes": None,
    "acessibilidade": None,
    "entidadeDeClasse": None,
    "empresa": 778812,
    "filial": None
}


def get_atividade_json(art_id):
    return {
        "id": 0,
        "tituloId": 1310800,
        "atividadesProfissionais": [80],
        "obraServicoNaoRelacionada": None,
        "quantidade": 1,
        "unidadeDeMedida": 2720,
        "observacoes": None,
        "acessibilidade": None,
        "ObraServicoComplementoId": 51,
        "artId": int(art_id)
    }


def get_contrato_json_SLD(art_id, documento_cliente, razao_social_cliente, data_prevista_inicio):
    today = datetime.today()

    # Conversão das variáveis de entrada
    art_id = int(art_id)
    documento_cliente = str(documento_cliente)
    razao_social_cliente = str(razao_social_cliente)
    data_prevista_inicio = datetime.strptime(data_prevista_inicio, "%d/%m/%Y").strftime("%Y-%m-%dT00:00:00.000Z")

    data_prevista_conclusao = datetime.now().isoformat()

    if isinstance(data_prevista_conclusao, datetime):
        data_prevista_conclusao = data_prevista_conclusao.strftime("%Y-%m-%dT00:00:00.000Z")
    else:
        data_prevista_conclusao = str(data_prevista_conclusao)

    return {
        "id": 0,
        "contratante": {
            "id": 0,
            "contrato": 0,
            "tipoPessoa": 3,
            "documento": "19791896005838",
            "nome": "SUPERGASBRAS ENERGIA LTDA",
            "nomeSocial": "",
            "ddd": None,
            "telefone": None,
            "email": None,
            "endereco": {
                "id": 0,
                "contrato": 0,
                "pais": "BRA",
                "cep": "86073015",
                "logradouro": "R DA RECICLAGEM",
                "numero": "100",
                "complemento": None,
                "bairro": "GLEBA JACUTINGA",
                "cidadeExterior": None,
                "tipoEndereco": 2
            }
        },
        "proprietario": {
            "id": 0,
            "contrato": 0,
            "tipoPessoa": 3,
            "documento": documento_cliente,
            "nome": razao_social_cliente,
            "nomeSocial": "",
            "ddd": None,
            "telefone": None
        },
        "numeroContrato": None,
        "codigoObraPublica": None,
        "dataContrato": "2021-02-18T03:00:00.000Z",
        "valorContrato": 925.44,
        "dataPrevistaInicio": data_prevista_inicio,
        "dataPrevistaConclusao": data_prevista_conclusao,
        "valorObra": None,
        "unidadeDeMedida": None,
        "quantidade": None,
        "camposExtras": "{}",
        "clausulaCompromissoria": False,
        "artId": art_id
    }


def get_endereco_cliente_json(contrato_id, cep, numero, bairro=None, logradouro=None):
    contrato_id = int(contrato_id)
    cep = str(cep)
    logradouro = str(logradouro) if logradouro else None
    numero = str(numero)
    bairro = str(bairro) if bairro else None

    return {
        "id": 0,
        "contrato": contrato_id,
        "tipoEndereco": 1,
        "pais": "BRA",
        "cep": cep,
        "logradouro": logradouro,
        "numero": numero,
        "bairro": bairro,
        "cidadeExterior": None,
        "complemento": None,
        "latitude": None,
        "longitude": None
    }


def get_atividade_tecnica_json(art_id, codigo_becus):
    art_id = int(art_id)

    return {
        "id": 0,
        "tituloId": 1310800,
        "atividadesProfissionais": [80],
        "obraServicoNaoRelacionada": None,
        "quantidade": 1,
        "unidadeDeMedida": 2720,
        "observacoes": f'Elaboração de projeto de central de gás GLP conforme projeto número {codigo_becus}	',
        "acessibilidade": None,
        "ObraServicoComplementoId": 51,
        "artId": art_id
    }
