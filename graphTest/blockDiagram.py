from graphviz import Digraph

def generate_flowchart():
    dot = Digraph(format='png')
    
    # # Nodes
    dot.node('WC', 'WebClient (Browser)')
    dot.node('WS', 'WebServer (Flask App)')
    dot.node('DB', 'Document Database', shape='cylinder')
    dot.node('ASR', 'ASR (Speech-to-Text)')
    dot.node('NLP', 'NLP (Diagnosis)')
    dot.node('RPC1', 'RPC bridge for ASR')
    dot.node('RPC2', 'RPC bridge for NLP')
    
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

    
    # Edges
    dot.edge('WC', 'WS', 'Interview recording')
    dot.edge('WS', 'DB', 'Save recording')
    dot.edge('WS', 'RPC1', 'Transcription request',style='dashed')
    dot.edge('RPC1', 'ASR', 'Transcription request',style='dashed')
    dot.edge('ASR', 'DB', 'Recording request',style='dashed')
    dot.edge('DB', 'ASR', 'Recording data')
    dot.edge('ASR', 'DB', 'Save transcription')
    dot.edge('WS', 'RPC2', 'Diagnosis request',style='dashed')
    dot.edge('RPC2', 'NLP', 'Diagnosis request',style='dashed')
    dot.edge('NLP', 'DB', 'Transcription request',style='dashed')
    dot.edge('DB', 'NLP', 'Transcription data')
    dot.edge('NLP', 'RPC2', 'Diagnosis results')
    dot.edge('RPC2', 'WS', 'Diagnosis results')
    dot.edge('WS', 'WC', 'Diagnosis presentation')
    
    return dot

# Generowanie schematu
flowchart = generate_flowchart()
flowchart.render('system_diagnosis_flowchart', format='png', cleanup=False)
flowchart.render('system_diagnosis_flowchart', format='svg', cleanup=False)


