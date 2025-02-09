from graphviz import Digraph

def generate_flowchart_full():
    dot = Digraph(format='png')
    
    # Nodes
    with dot.subgraph(name='cluster_webapp') as cluster:
        cluster.attr(label="Web App", style="dashed")
        cluster.node('WC', 'WebClient (Browser)')
        cluster.node('WS', 'WebServer (Flask App)')

    with dot.subgraph() as same_rank:
        same_rank.attr(rank='same')
        same_rank.node('RPC1', 'RPC bridge for ASR',shape='box')
        same_rank.node('DB', 'Document Database', shape='cylinder')
        same_rank.node('RPC2', 'RPC bridge for NLP',shape='box')

    dot.node('ASR', 'ASR (Speech-to-Text)')
    dot.node('NLP', 'NLP (Diagnosis)')

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

def generate_flowchart():
    dot = Digraph(format='png')
    
    # Nodes
    with dot.subgraph(name='cluster_webapp') as cluster:
        cluster.attr(label="Web App", style="dashed")
        cluster.node('WC', 'WebClient (Browser)')
        cluster.node('WS', 'WebServer (Flask App)')

    with dot.subgraph() as same_rank:
        same_rank.attr(rank='same')
        same_rank.node('ASR', 'ASR (Speech-to-Text)',shape='box')
        same_rank.node('DB', 'Document Database', shape='cylinder')
        same_rank.node('NLP', 'NLP (Diagnosis)',shape='box')

    # Edges
    dot.edge('WC', 'WS', 'Interview')
    dot.edge('WC', 'WS', 'Interview',style='invis')
    dot.edge('WS', 'DB', 'Recording')
    dot.edge('WS', 'ASR', 'Transcription',style='dashed')
    dot.edge('ASR', 'DB', 'Recording',dir='both')
    dot.edge('ASR', 'DB', 'Transcription')
    dot.edge('WS', 'NLP', 'Diagnosis',dir='both')
    dot.edge('DB', 'NLP', 'Transcription',style='invis')
    dot.edge('NLP', 'DB', 'Transcription',dir='both')
    dot.edge('WS', 'WC', 'Diagnosis')
    
    return dot



# Generowanie schematu
flowchart = generate_flowchart()
flowchart.render('system_diagnosis_flowchart', format='png', cleanup=False)
flowchart.render('system_diagnosis_flowchart', format='svg', cleanup=False)

flowchart = generate_flowchart_full()
flowchart.render('system_diagnosis_flowchart_full', format='png', cleanup=False)
flowchart.render('system_diagnosis_flowchart_full', format='svg', cleanup=False)

