import json
import os
from datetime import datetime, timedelta

# ===================== VARIÁVEIS GLOBAIS =====================
tarefas = []
tarefas_arquivadas = []
ultimo_id = 0

ARQ_TAREFAS = "tarefas.json"
ARQ_ARQUIVADAS = "tarefas_arquivadas.json"

# ===================== VERIFICA/CRIA ARQUIVOS =====================
def carregar_arquivos():
    """
    Garante existência dos arquivos JSON e carrega dados em memória.
    Ajusta 'ultimo_id' com base nos IDs existentes (em tarefas e arquivadas).
    """
    print("Executando: carregar_arquivos")
    global tarefas, tarefas_arquivadas, ultimo_id

    # cria arquivos se não existirem
    if not os.path.exists(ARQ_TAREFAS):
        with open(ARQ_TAREFAS, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)
        print(f"Arquivo criado: {ARQ_TAREFAS}")

    if not os.path.exists(ARQ_ARQUIVADAS):
        with open(ARQ_ARQUIVADAS, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)
        print(f"Arquivo criado: {ARQ_ARQUIVADAS}")

    # carrega arquivos com tratamento
    try:
        with open(ARQ_TAREFAS, "r", encoding="utf-8") as f:
            tarefas = json.load(f)
            if not isinstance(tarefas, list):
                print(f"Aviso: formato inesperado em {ARQ_TAREFAS}, resetando para lista vazia.")
                tarefas = []
    except Exception as e:
        print(f"Erro ao ler {ARQ_TAREFAS}: {e}")
        tarefas = []

    try:
        with open(ARQ_ARQUIVADAS, "r", encoding="utf-8") as f:
            tarefas_arquivadas = json.load(f)
            if not isinstance(tarefas_arquivadas, list):
                print(f"Aviso: formato inesperado em {ARQ_ARQUIVADAS}, resetando para lista vazia.")
                tarefas_arquivadas = []
    except Exception as e:
        print(f"Erro ao ler {ARQ_ARQUIVADAS}: {e}")
        tarefas_arquivadas = []

    # determina último ID
    max_id = 0
    for lista in (tarefas, tarefas_arquivadas):
        for t in lista:
            try:
                tid = t.get("id")
                if isinstance(tid, int) and tid > max_id:
                    max_id = tid
            except Exception:
                continue
    ultimo_id = max_id

def salvar_arquivos():
    """
    Salva as listas de tarefas e tarefas arquivadas em seus arquivos JSON.
    """
    print("Executando: salvar_arquivos")
    global tarefas, tarefas_arquivadas
    try:
        with open(ARQ_TAREFAS, "w", encoding="utf-8") as f:
            json.dump(tarefas, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar {ARQ_TAREFAS}: {e}")

    try:
        with open(ARQ_ARQUIVADAS, "w", encoding="utf-8") as f:
            json.dump(tarefas_arquivadas, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar {ARQ_ARQUIVADAS}: {e}")

# ===================== FUNÇÕES AUXILIARES DE VALIDAÇÃO =====================
def ler_texto_obrigatorio(prompt):
    """
    Lê texto do usuário e valida que não esteja vazio.
    Retorna a string válida.
    """
    print(f"Executando: ler_texto_obrigatorio -> {prompt}")
    while True:
        valor = input(prompt).strip()
        if valor == "":
            print("Entrada inválida: não pode ser vazia. Tente novamente.")
        else:
            return valor

def validar_escolha(prompt, opcoes):
    """
    Lê e valida que o usuário escolha uma das opções fornecidas.
    Recebe lista de opções (strings). Retorna a opção válida (mesma forma).
    """
    print(f"Executando: validar_escolha -> {prompt}")
    opcoes_str = ", ".join(opcoes)
    print(f"Opções válidas: [{opcoes_str}]")
    while True:
        escolha = input(prompt).strip()
        for op in opcoes:
            if escolha.lower() == op.lower():
                return op
        print("Escolha inválida. Tente novamente.")

def encontrar_tarefa_por_id(id_tarefa):
    """Retorna a tarefa (referência) ou None se não encontrar."""
    for t in tarefas:
        if t.get("id") == id_tarefa:
            return t
    return None

# ===================== FUNÇÕES DO SISTEMA =====================

def criar_tarefa():
    """
    Cria uma nova tarefa solicitando informações ao usuário,
    valida os dados e adiciona a tarefa à lista global de tarefas.
    """
    print("Executando: criar_tarefa")
    global ultimo_id, tarefas

    ultimo_id += 1
    titulo = ler_texto_obrigatorio("Título da tarefa: ")
    descricao = input("Descrição (opcional): ").strip()

    prioridades = ["Urgente", "Alta", "Média", "Baixa"]
    prioridade = validar_escolha("Informe a prioridade: ", prioridades)

    origens = ["Email", "Telefone", "Chamado"]
    origem = validar_escolha("Informe a origem: ", origens)

    tarefa = {
        "id": ultimo_id,
        "titulo": titulo,
        "descricao": descricao,
        "prioridade": prioridade,
        "status": "Pendente",
        "origem": origem,
        "data_criacao": datetime.now().isoformat(),
        "data_conclusao": None
    }
    tarefas.append(tarefa)
    salvar_arquivos()  # salva imediatamente para segurança
    print(f"Tarefa criada com sucesso! ID: {tarefa['id']}")

def pegar_tarefa_para_fazer():
    """
    Seleciona a primeira tarefa Pendente da maior prioridade disponível
    e marca como 'Fazendo'. Garante que somente uma esteja em 'Fazendo'.
    """
    print("Executando: pegar_tarefa_para_fazer")
    global tarefas

    # garante apenas uma em 'Fazendo'
    for t in tarefas:
        if t.get("status") == "Fazendo":
            print(f"Já existe uma tarefa em execução: ID {t['id']} - {t['titulo']}.")
            return

    prioridades = ["Urgente", "Alta", "Média", "Baixa"]
    for p in prioridades:
        for tarefa in tarefas:
            if tarefa.get("prioridade") == p and tarefa.get("status") == "Pendente":
                tarefa["status"] = "Fazendo"
                salvar_arquivos()
                print(f"Tarefa selecionada: {tarefa['titulo']} (ID: {tarefa['id']}) — agora com status 'Fazendo'.")
                return
    print("Não há tarefas pendentes.")

def atualizar_prioridade():
    """
    Permite que o usuário altere a prioridade de uma tarefa, validando a nova prioridade.
    """
    print("Executando: atualizar_prioridade")
    try:
        id_tarefa = int(input("ID da tarefa a atualizar: ").strip())
    except ValueError:
        print("Entrada inválida: digite um número para o ID.")
        return

    tarefa = encontrar_tarefa_por_id(id_tarefa)
    if not tarefa:
        print("ID não encontrado.")
        return

    prioridades = ["Urgente", "Alta", "Média", "Baixa"]
    print(f"Prioridade atual: {tarefa.get('prioridade')}")
    nova = validar_escolha("Informe a nova prioridade: ", prioridades)
    tarefa["prioridade"] = nova
    salvar_arquivos()
    print(f"Prioridade atualizada para {nova} na tarefa ID {id_tarefa}.")

def concluir_tarefa():
    """
    Marca tarefa como concluída e registra data de conclusão.
    """
    print("Executando: concluir_tarefa")
    global tarefas

    try:
        id_tarefa = int(input("ID da tarefa: ").strip())
    except ValueError:
        print("Entrada inválida: digite um número para o ID.")
        return

    tarefa = encontrar_tarefa_por_id(id_tarefa)
    if tarefa:
        tarefa["status"] = "Concluída"
        tarefa["data_conclusao"] = datetime.now().isoformat()
        salvar_arquivos()
        print("Tarefa concluída.")
    else:
        print("ID não encontrado.")

def arquivar_tarefas_antigas():
    """
    Arquiva tarefas concluídas há mais de uma semana:
    - move da lista 'tarefas' para 'tarefas_arquivadas' (sem duplicar)
    """
    print("Executando: arquivar_tarefas_antigas")
    global tarefas, tarefas_arquivadas

    hoje = datetime.now()
    arquivadas = []

    for tarefa in tarefas[:]:
        if tarefa.get("status") == "Concluída" and tarefa.get("data_conclusao"):
            try:
                data = datetime.fromisoformat(tarefa["data_conclusao"])
            except Exception:
                print(f"Aviso: data inválida na tarefa ID {tarefa.get('id')}; pulando arquivamento automático.")
                continue
            if (hoje - data).days > 7:
                tarefa["status"] = "Arquivado"
                arquivadas.append(tarefa)
                tarefas.remove(tarefa)

    if arquivadas:
        # carregar histórico existente e evitar duplicatas
        try:
            with open(ARQ_ARQUIVADAS, "r", encoding="utf-8") as f:
                historico = json.load(f)
                if not isinstance(historico, list):
                    historico = []
        except Exception:
            historico = []

        ids_existentes = {t.get("id") for t in historico if isinstance(t.get("id"), int)}
        adicionadas = 0
        for t in arquivadas:
            if t.get("id") not in ids_existentes:
                historico.append(t)
                ids_existentes.add(t.get("id"))
                adicionadas += 1

        tarefas_arquivadas = historico
        try:
            with open(ARQ_ARQUIVADAS, "w", encoding="utf-8") as f:
                json.dump(historico, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar {ARQ_ARQUIVADAS}: {e}")

        salvar_arquivos()
        print(f"{adicionadas} tarefa(s) arquivada(s) com sucesso!")
    else:
        print("Nenhuma tarefa antiga para arquivar.")

def excluir_tarefa():
    """
    Exclusão lógica: atualiza status para 'Excluída' e registra em arquivadas (histórico),
    mas não aparece no relatório de arquivados.
    """
    print("Executando: excluir_tarefa")
    global tarefas, tarefas_arquivadas

    try:
        id_tarefa = int(input("ID da tarefa: ").strip())
    except ValueError:
        print("Entrada inválida: digite um número para o ID.")
        return

    for tarefa in tarefas[:]:
        if tarefa.get("id") == id_tarefa:
            tarefa["status"] = "Excluída"
            tarefa["data_conclusao"] = datetime.now().isoformat()
            # salvar no histórico (arquivo) também como registro de exclusão
            try:
                with open(ARQ_ARQUIVADAS, "r", encoding="utf-8") as f:
                    historico = json.load(f)
                    if not isinstance(historico, list):
                        historico = []
            except Exception:
                historico = []
            # evitar duplicatas
            ids_existentes = {t.get("id") for t in historico if isinstance(t.get("id"), int)}
            if tarefa.get("id") not in ids_existentes:
                historico.append(tarefa)
                tarefas_arquivadas = historico
                try:
                    with open(ARQ_ARQUIVADAS, "w", encoding="utf-8") as f:
                        json.dump(historico, f, indent=4, ensure_ascii=False)
                except Exception as e:
                    print(f"Erro ao salvar {ARQ_ARQUIVADAS}: {e}")

            tarefas.remove(tarefa)
            salvar_arquivos()
            print("Tarefa excluída e arquivada (exclusão lógica).")
            return
    print("ID não encontrado.")

def listar_tarefas():
    """Exibe todas as tarefas ativas de forma legível."""
    print("Executando: listar_tarefas")
    if not tarefas:
        print("Nenhuma tarefa cadastrada.")
        return
    print("-" * 60)
    for tarefa in tarefas:
        print(f"ID: {tarefa.get('id')}")
        print(f"  Título     : {tarefa.get('titulo')}")
        print(f"  Descrição  : {tarefa.get('descricao')}")
        print(f"  Prioridade : {tarefa.get('prioridade')}")
        print(f"  Status     : {tarefa.get('status')}")
        print(f"  Origem     : {tarefa.get('origem')}")
        print(f"  Criado em  : {tarefa.get('data_criacao')}")
        if tarefa.get("data_conclusao"):
            print(f"  Concluído em: {tarefa.get('data_conclusao')}")
        print("-" * 60)

def relatorio_tarefa():
    """
    Relatório detalhado de uma tarefa específica, incluindo tempo de execução
    para tarefas concluídas (diferença entre criação e conclusão).
    """
    print("Executando: relatorio_tarefa")
    try:
        id_tarefa = int(input("ID da tarefa para relatório: ").strip())
    except ValueError:
        print("Entrada inválida: digite um número para o ID.")
        return

    # procurar tanto em ativas quanto em arquivadas
    encontrada = None
    for lista in (tarefas, tarefas_arquivadas):
        for t in lista:
            if t.get("id") == id_tarefa:
                encontrada = t
                break
        if encontrada:
            break

    if not encontrada:
        print("ID não encontrado.")
        return

    print("-" * 60)
    print(f"ID: {encontrada.get('id')}")
    print(f"Titulo     : {encontrada.get('titulo')}")
    print(f"Descricao  : {encontrada.get('descricao')}")
    print(f"Prioridade : {encontrada.get('prioridade')}")
    print(f"Status     : {encontrada.get('status')}")
    print(f"Origem     : {encontrada.get('origem')}")
    print(f"Criado em  : {encontrada.get('data_criacao')}")
    dc = encontrada.get("data_conclusao")
    if dc:
        print(f"Concluído em: {dc}")
        # calcula tempo de execução se possível
        try:
            inicio = datetime.fromisoformat(encontrada.get("data_criacao"))
            fim = datetime.fromisoformat(dc)
            duracao = fim - inicio
            dias = duracao.days
            horas, resto = divmod(duracao.seconds, 3600)
            minutos, segundos = divmod(resto, 60)
            print(f"Tempo de execução: {dias}d {horas}h {minutos}m {segundos}s")
        except Exception:
            print("Não foi possível calcular o tempo de execução (formato de data inválido).")
    print("-" * 60)

def listar_arquivadas():
    """Exibe o histórico de tarefas arquivadas (exclui as que estão com status 'Excluída' do relatório)."""
    print("Executando: listar_arquivadas")
    try:
        with open(ARQ_ARQUIVADAS, "r", encoding="utf-8") as f:
            historico = json.load(f)
            if not isinstance(historico, list):
                historico = tarefas_arquivadas or []
    except Exception:
        historico = tarefas_arquivadas or []

    # Filtra para não mostrar as excluídas no relatório de arquivadas
    relatorio = [t for t in historico if t.get("status") != "Excluída"]

    if not relatorio:
        print("Nenhuma tarefa arquivada (exceto exclusões registradas).")
        return

    print("-" * 60)
    for t in relatorio:
        print(f"ID: {t.get('id')} | Título: {t.get('titulo')} | Status: {t.get('status')} | Conclusão: {t.get('data_conclusao')}")
    print("-" * 60)

# ===================== MENU PRINCIPAL =====================

def menu():
    """Menu principal que agrupa todas as funcionalidades e valida opções."""
    print("Executando: menu")
    carregar_arquivos()

    while True:
        print("\n" + "=" * 60)
        print("GERENCIADOR DE TAREFAS - MENU PRINCIPAL")
        print("=" * 60)
        print("1 - Criar tarefa")
        print("2 - Pegar tarefa para fazer")
        print("3 - Concluir tarefa")
        print("4 - Excluir tarefa (lógica)")
        print("5 - Listar tarefas")
        print("6 - Arquivar tarefas antigas")
        print("7 - Listar tarefas arquivadas")
        print("8 - Atualizar prioridade de uma tarefa")
        print("9 - Relatório detalhado de uma tarefa")
        print("0 - Sair (salva e encerra)")
        print("=" * 60)

        opcao = input("Escolha: ").strip()
        if opcao == "":
            print("Entrada inválida. Digite uma opção.")
            continue

        if opcao not in [str(i) for i in range(0, 10)]:
            print("Opção inválida.")
            continue

        try:
            opcao_int = int(opcao)
        except ValueError:
            print("Entrada inválida. Digite um número correspondente à opção.")
            continue

        if opcao_int == 1:
            criar_tarefa()
        elif opcao_int == 2:
            pegar_tarefa_para_fazer()
        elif opcao_int == 3:
            concluir_tarefa()
        elif opcao_int == 4:
            excluir_tarefa()
        elif opcao_int == 5:
            listar_tarefas()
        elif opcao_int == 6:
            arquivar_tarefas_antigas()
        elif opcao_int == 7:
            listar_arquivadas()
        elif opcao_int == 8:
            atualizar_prioridade()
        elif opcao_int == 9:
            relatorio_tarefa()
        elif opcao_int == 0:
            salvar_arquivos()
            print("Dados salvos. Encerrando...")
            exit()
        else:
            print("Opção inválida.")

# ===================== EXECUÇÃO =====================

if __name__ == "__main__":
    menu()
