# app_roleta.py
import streamlit as st
from collections import Counter

# --- CLASSE 'AnalistaRoleta' ATUALIZADA COM LÓGICA REFINADA ---
class AnalistaRoleta:
    def __init__(self):
        self.historico = []
        # Dados Estruturais
        self.CILINDRO_EUROPEU = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
        
        # Mapeamentos para performance
        self.NUMERO_INFO = self._mapear_info_numeros()
        self.VIZINHOS = self._mapear_vizinhos()
        self.CAVALOS_TRIPLOS = {
            0: [3, 7], 1: [4, 8], 2: [5, 9], 3: [6, 0], 4: [7, 1],
            5: [8, 2], 6: [9, 3], 7: [0, 4], 8: [1, 5], 9: [2, 6]
        }
        self.CAVALOS_LATERAIS_PARA_CENTRAL = self._mapear_cavalos_inversos()
        self.DISFARCADOS = {
            0: {11, 19, 22, 28, 33}, 1: {12, 23, 29, 32, 34},
            2: {11, 13, 24, 31, 35}, 3: {12, 14, 21, 25, 26, 36},
            4: {13, 15, 22, 26, 28, 31}, 5: {14, 16, 23, 27, 32},
            6: {15, 17, 24, 28, 33}, 7: {16, 18, 25, 29, 34},
            8: {17, 19, 24, 26, 35}, 9: {18, 27, 33, 36}
        }

    def _mapear_info_numeros(self):
        info = {}
        voisins = {0, 2, 3, 4, 7, 12, 15, 18, 19, 21, 22, 25, 26, 28, 29, 32, 35}
        tiers = {5, 8, 10, 11, 13, 16, 23, 24, 27, 30, 33, 36}
        for num in range(37):
            secao = "Voisins" if num in voisins else "Tiers" if num in tiers else "Orphelins"
            info[num] = {'terminal': num % 10, 'secao': secao}
        return info

    def _mapear_vizinhos(self):
        vizinhos = {}
        tamanho = len(self.CILINDRO_EUROPEU)
        for i, num in enumerate(self.CILINDRO_EUROPEU):
            vizinhos[num] = {
                "v-3": self.CILINDRO_EUROPEU[(i - 3 + tamanho) % tamanho],
                "v-2": self.CILINDRO_EUROPEU[(i - 2 + tamanho) % tamanho],
                "v-1": self.CILINDRO_EUROPEU[(i - 1 + tamanho) % tamanho],
                "num": num,
                "v+1": self.CILINDRO_EUROPEU[(i + 1) % tamanho],
                "v+2": self.CILINDRO_EUROPEU[(i + 2) % tamanho],
                "v+3": self.CILINDRO_EUROPEU[(i + 3) % tamanho],
            }
        return vizinhos
        
    def _mapear_cavalos_inversos(self):
        mapa = {}
        for central, laterais in self.CAVALOS_TRIPLOS.items():
            chave = tuple(sorted(laterais))
            mapa[chave] = central
        return mapa

    def adicionar_numero(self, numero):
        if 0 <= numero <= 36:
            self.historico.insert(0, numero)
            if len(self.historico) > 20:
                self.historico.pop()

    def _get_terminais_recentes(self, quantidade):
        return [self.NUMERO_INFO[n]['terminal'] for n in self.historico[:quantidade]]

    def _calcular_valor_falso(self, num):
        if num >= 10:
            return (num // 10 + num % 10) % 10
        return None
        
    # --- NOVA FUNÇÃO DE DOBRA/METADE REFINADA ---
    def _checar_dobra_metade(self):
        if len(self.historico) < 2: return None
        h = self.historico
        
        # Procura por um gatilho de dobra/metade (exato ou próximo) no histórico recente
        gatilho_encontrado = None
        for i in range(len(h) - 1, 0, -1):
            n1, n2 = h[i], h[i-1] # n1 é o mais antigo, n2 o mais recente
            if abs(n2 - (n1 * 2)) <= 1 or abs(n2 - (n1 / 2)) <= 1:
                gatilho_encontrado = f"{n1} -> {n2}"
                break
        
        if gatilho_encontrado:
            ultimo_num = h[0]
            dobra = ultimo_num * 2
            metade = ultimo_num // 2
            alvos = {n for n in [dobra, dobra-1, dobra+1, metade, metade-1, metade+1] if 0 <= n <= 36}
            if alvos:
                return {"analise": f"Padrão Dobra/Metade Ativo (visto: {gatilho_encontrado}).",
                        "estrategia": f"Analisando {ultimo_num}, apostar na região dos alvos próximos: {sorted(list(alvos))}."}
        return None

    def analisar(self):
        if len(self.historico) < 5:
            return {"analise": "Aguardando mais números...", "estrategia": "Insira pelo menos 5 números."}

        h = self.historico
        terminais_h = [self.NUMERO_INFO[n]['terminal'] for n in h]

        # --- ORDEM DE PRIORIDADE DAS ANÁLISES ---

        # 1. Padrão Dobra/Metade (Nova Lógica Refinada)
        resultado_dobra = self._checar_dobra_metade()
        if resultado_dobra:
            return resultado_dobra
            
        # 2. Padrões de Cavalo com Quebra
        if len(h) >= 3:
            par_terminais = tuple(sorted([terminais_h[1], terminais_h[2]]))
            if par_terminais in self.CAVALOS_LATERAIS_PARA_CENTRAL:
                central_alvo = self.CAVALOS_LATERAIS_PARA_CENTRAL[par_terminais]
                trindade = set(list(par_terminais) + [central_alvo])
                if terminais_h[0] not in trindade:
                    return {"analise": f"Padrão de Cavalo com Quebra! Par ({terminais_h[2]},{terminais_h[1]}) + Quebra em {h[0]}.",
                            "estrategia": f"Apostar na região do Terminal {central_alvo}."}

        # 3. Padrão Vai e Vem
        if len(h) >= 3:
            secao_a, secao_b, secao_c = self.NUMERO_INFO[h[2]]['secao'], self.NUMERO_INFO[h[1]]['secao'], self.NUMERO_INFO[h[0]]['secao']
            if secao_a == secao_c and secao_a != secao_b:
                return {"analise": f"Gatilho Vai e Vem! Alternância entre {secao_a} e {secao_b}.",
                        "estrategia": f"Apostar na região de {h[1]}, buscando retorno para {secao_b}."}

        # 4. Padrão Falso -> Verdadeiro
        if len(h) >= 2:
            vf_penultimo = self._calcular_valor_falso(h[1])
            if vf_penultimo is not None and vf_penultimo == terminais_h[0]:
                vf_atual = self._calcular_valor_falso(h[0])
                if vf_atual is not None:
                    return {"analise": f"Padrão Falso/Verdadeiro Ativo! {h[0]} é um T{vf_atual} Falso.",
                            "estrategia": f"Apostar na região do Terminal {vf_atual} Verdadeiro."}

        # 5. Manipulação de Terminal
        terminais = self._get_terminais_recentes(7)
        if terminais:
            terminal_dominante = max(set(terminais), key=terminais.count)
            contagem = terminais.count(terminal_dominante)
            if contagem >= 4:
                if contagem >= 5: # Saturação
                    disfarçados_str = ", ".join(map(str, sorted(list(self.DISFARCADOS[terminal_dominante]))))
                    return {"analise": f"Manipulação de T{terminal_dominante} (SATURADO - {contagem}x).",
                            "estrategia": f"Apostar na QUEBRA. Focar na região dos Disfarçados: {{{disfarçados_str}}}."}
                else:
                    cavalos = self.CAVALOS_TRIPLOS[terminal_dominante]
                    return {"analise": f"Manipulação de T{terminal_dominante} forte.",
                            "estrategia": f"Seguir tendência. Focar na região do Cavalo Triplo {{{terminal_dominante},{cavalos[0]},{cavalos[1]}}}."}

        return {"analise": "Nenhum padrão claro identificado.", "estrategia": "Aguardar um gatilho."}

# --- INTERFACE DO APLICATIVO (STREAMLIT) ---

st.set_page_config(layout="wide", page_title="Roleta Mestre")

# Título do App
st.title("Roleta Mestre - Agente Analista 2.0")

# Inicializa o analista na memória da sessão
if 'analista' not in st.session_state:
    st.session_state.analista = AnalistaRoleta()

# --- TABELA DE ROLETA INTERATIVA ---
st.header("Clique no número para adicionar ao histórico (mais recente primeiro):")

numeros_layout = [
    [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
    [-1, 2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
    [-1, 1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
]

cols = st.columns(13)
for i in range(13):
    for j in range(3):
        num = numeros_layout[j][i]
        if num != -1:
            if cols[i].button(f"{num}", key=f"num_{num}", use_container_width=True):
                st.session_state.analista.adicionar_numero(num)
                st.rerun()

st.divider()

# ---- PAINEL DE ANÁLISE ----
st.header("Análise em Tempo Real")

historico_str = ", ".join(map(str, st.session_state.analista.historico))
st.write(f"**Tempo de Tela:** `{historico_str or 'Vazio'}`")

resultado_analise = st.session_state.analista.analisar()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Diagnóstico:")
    st.info(resultado_analise['analise'])
with col2:
    st.subheader("Estratégia Recomendada:")
    st.success(resultado_analise['estrategia'])

# ---- Botão de Limpar ----
if st.button("Limpar Histórico"):
    st.session_state.analista.historico = []
    st.rerun()
