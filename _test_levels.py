import importlib.util
spec=importlib.util.spec_from_file_location('domino', r'c:\Users\jesa9\juego2026\juego.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
for nivel in ['facil','normal','dificil']:
    juego=mod.JuegoDomino('2v2',['Tú','IA1','IA2','IA3'], nivel=nivel)
    print('nivel', nivel, '->', juego.nivel, 'turno inicial', juego.turno)
    for p in [1,2,3]:
        jugables=[str(f) for f in juego.fichas_jugables(p)]
        print('  IA jugador', p, 'jugables', jugables)
        res=juego.ia_jugar(p)
        print('   jugó?', res)
    print('---')
