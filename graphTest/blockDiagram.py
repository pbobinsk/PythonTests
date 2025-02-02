from graphviz import Digraph

def generate_flowchart():
    dot = Digraph(format='png')
    
    # # Nodes
    # dot.node('WC', 'WebClient (Lekarz)')
    # dot.node('WS', 'WebServer')
    # dot.node('DB', 'Baza Danych')
    # dot.node('ASR', 'Moduł ASR (Speech-to-Text)')
    # dot.node('NLP', 'Moduł NLP (Analiza diagnozy)')
    # dot.node('RPC1', 'Mostek jsonRPC (ASR)')
    # dot.node('RPC2', 'Mostek jsonRPC (NLP)')
    
    # # Edges
    # dot.edge('WC', 'WS', 'Nagrywanie rozmowy')
    # dot.edge('WS', 'DB', 'Zapis nagrania')
    # dot.edge('WS', 'RPC1', 'Żądanie transkrypcji')
    # dot.edge('RPC1', 'ASR', 'Przetwarzanie mowy')
    # dot.edge('ASR', 'DB', 'Zapis transkryptu')
    # dot.edge('WS', 'RPC2', 'Żądanie analizy NLP')
    # dot.edge('RPC2', 'NLP', 'Generowanie diagnozy')
    # dot.edge('NLP', 'WS', 'Przekazanie wyników')
    # dot.edge('WS', 'WC', 'Prezentacja wyników lekarzowi')

    # Nodes
    dot.node('WC', 'WebClient (Lekarz)', shape='ellipse')
    dot.node('DB', 'Baza Danych', shape='cylinder')

    # dot.node('WC', 'WebClient (Lekarz)')
    dot.node('WS', 'WebServer')
    # dot.node('DB', 'Baza Danych')
    dot.node('ASR', 'Moduł ASR (Speech-to-Text)')
    dot.node('NLP', 'Moduł NLP (Analiza diagnozy)')
    dot.node('RPC1', 'Mostek jsonRPC (ASR)')
    dot.node('RPC2', 'Mostek jsonRPC (NLP)')
    
    # Edges
    dot.edge('WC', 'WS', 'Nagrywanie rozmowy')
    # dot.edge('WS', 'DB', 'Zapis nagrania')
    dot.edge('WS', 'DB', 'Zapis nagrania', style='dashed', color='red', arrowhead='diamond')

    dot.edge('WS', 'RPC1', 'Żądanie transkrypcji')
    dot.edge('RPC1', 'ASR', 'Przetwarzanie mowy')
    dot.edge('ASR', 'DB', 'Zapis transkryptu')
    dot.edge('WS', 'RPC2', 'Żądanie analizy NLP')
    dot.edge('RPC2', 'NLP', 'Generowanie diagnozy')
    dot.edge('NLP', 'RPC2', 'Przekazanie wyników')
    # dot.edge('RPC2', 'WC', 'Prezentacja wyników lekarzowi')
    dot.edge('RPC2', 'WC', 'Prezentacja wyników', style='bold', color='blue', arrowhead='vee')
    dot.edge('DB', 'NLP', 'Pobranie transkrypcji')
    
    return dot

# Generowanie schematu
flowchart = generate_flowchart()
flowchart.render('system_diagnosis_flowchart', format='png', cleanup=False)
flowchart.render('system_diagnosis_flowchart', format='svg', cleanup=False)


