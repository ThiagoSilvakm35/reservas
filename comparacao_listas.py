# Adicionar um print no início para garantir que o script está executando
print("Iniciando análise de comparação entre listas...")

# Abrir um arquivo para salvar os resultados
arquivo_resultado = open('resultado_comparacao.txt', 'w', encoding='utf-8')

def escrever(texto):
    """Função para escrever tanto no console quanto no arquivo"""
    print(texto)
    arquivo_resultado.write(texto + '\n')

# Gerar conclusões e recomendações com base na análise
def gerar_conclusoes(dic_clamed, dic_sistema, chaves_comuns, diferencas, 
                   chaves_somente_clamed, chaves_somente_sistema, 
                   zeros_somente_clamed, valores_exclusivos_sistema):
    """Gera conclusões e recomendações com base nos resultados da análise"""
    
    escrever("\n\n============= CONCLUSÕES E RECOMENDAÇÕES =============")
    
    # Conclusão sobre duplicatas
    if len(diferencas) > 0:
        escrever("\n1. DIFERENÇAS DE VALORES:")
        escrever(f"   - Foi encontrada apenas {len(diferencas)} chave com valor diferente entre as duas listas: {list(diferencas.keys())[0]}")
        escrever(f"   - A diferença percentual é de {list(diferencas.values())[0]['diferenca_percentual']:.2f}%, considerada pequena a média")
        escrever("   - Recomendação: Verificar manualmente esta chave para determinar qual valor está correto")
    else:
        escrever("\n1. DIFERENÇAS DE VALORES:")
        escrever("   - Não foram encontradas diferenças nos valores para as chaves comuns")
        escrever("   - Recomendação: Nenhuma ação necessária quanto aos valores")
    
    # Conclusão sobre chaves exclusivas
    porcentagem_zeros_clamed = (zeros_somente_clamed / len(chaves_somente_clamed) * 100) if chaves_somente_clamed else 0
    
    escrever("\n2. CHAVES EXCLUSIVAS:")
    escrever(f"   - Clamed tem {len(chaves_somente_clamed)} chaves exclusivas, das quais {zeros_somente_clamed} ({porcentagem_zeros_clamed:.2f}%) têm valor zero")
    escrever(f"   - Sistema tem {len(chaves_somente_sistema)} chaves exclusivas, todas com valores não-zero")
    escrever(f"   - A soma total dos valores exclusivos no sistema é de {valores_exclusivos_sistema:.2f}")
    
    if porcentagem_zeros_clamed == 100:
        escrever("   - IMPORTANTE: Todas as chaves exclusivas em Clamed têm valor zero, o que sugere que estas")
        escrever("     entradas podem ser apenas placeholders ou registros vazios")
    
    escrever("   - Recomendação: Verificar a razão da existência de tantas chaves exclusivas em cada sistema")
    escrever("     e determinar se alguma reconciliação é necessária")
    
    # Conclusão geral
    total_registros = max(len(dic_clamed), len(dic_sistema))
    porcentagem_comuns = len(chaves_comuns) / total_registros * 100
    
    escrever("\n3. CONCLUSÃO GERAL:")
    if porcentagem_comuns > 80:
        escrever(f"   - As duas listas compartilham {porcentagem_comuns:.2f}% de suas chaves, com alta consistência")
    elif porcentagem_comuns > 50:
        escrever(f"   - As duas listas compartilham {porcentagem_comuns:.2f}% de suas chaves, com média consistência")
    else:
        escrever(f"   - As duas listas compartilham apenas {porcentagem_comuns:.2f}% de suas chaves, com baixa consistência")
    
    if len(diferencas) == 0 or (len(diferencas) / len(chaves_comuns) * 100) < 1:
        escrever("   - Os valores para as chaves comuns são altamente consistentes entre os sistemas")
    else:
        escrever("   - Há inconsistências nos valores entre os sistemas que precisam ser reconciliadas")
    
    if porcentagem_zeros_clamed == 100:
        escrever("   - Há evidências de que o sistema Clamed pode conter registros vazios ou incompletos")
        escrever("     que não estão presentes no outro sistema")
    
    escrever("\n4. PRÓXIMOS PASSOS RECOMENDADOS:")
    escrever("   - Verificar manualmente a única chave com valor diferente: " + list(diferencas.keys())[0])
    escrever("   - Investigar por que todas as chaves exclusivas em Clamed têm valor zero")
    escrever("   - Verificar a origem das 91 chaves exclusivas do sistema com valores significativos")
    escrever("   - Estabelecer um processo para sincronização regular entre os sistemas")

lista_clamed = [{'35823':'22,81'},
{'64734':'1064,29'},
{'105678':'373,89'},
{'210854':'1280,38'},
{'237787':'3210,45'},
{'335924':'754,29'},
{'342599':'1356,76'},
{'380148':'677,91'},
{'645672':'0'},
{'714860':'2787,79'},
{'726478':'4320,51'},
{'848115':'5287,32'},
{'883549':'1303,05'},
{'892602':'1538,25'},
{'105759':'1929,94'},
{'892629':'226,6'},
{'23112507':'3536,26'},
{'30895681':'4210,02'},
{'22912747':'0'},
{'50928608':'0'},
{'55667497':'5142,6'},
{'3645630':'3313,83'},
{'45382478':'0'},
{'7974574':'0'},
{'50871827':'0'},
{'1782770':'0'},
{'42274020':'0'},
{'18910438':'0'},
{'4842944':'0'},
{'28137311':'0'},
{'44764989':'598,48'},
{'56383212':'0'},
{'73814':'0'},
{'40842365':'0'},
{'26280':'3757,31'},
{'30067568':'0'},
{'51402146':'0'},
{'2857880':'437,48'},
{'4868374':'0'},
{'43529897':'0'},
{'54733941':'0'},
{'46285255':'0'},
{'26697514':'5314,44'},
{'56578471':'14,96'},
{'43079301':'0'},
{'2046024':'0'},
{'193500':'0'},
{'10309930':'0'},
{'27685692':'0'},
{'50940896':'0'},
{'1271229':'1898,6'},
{'1370472':'0'},
{'1370766':'1058,34'},
{'1505920':'0'},
{'2044463':'79,49'},
{'2061112':'2673,58'},
{'2228637':'0'},
{'2254182':'1962,65'},
{'2323893':'0'},
{'2374137':'1083,66'},
{'2404249':'5475,57'},
{'2748797':'3111,37'},
{'2909243':'481,22'},
{'3460525':'308,39'},
{'3688496':'0'},
{'3771458':'57,02'},
{'3771466':'1523,17'},
{'3914933':'2638,77'},
{'3945588':'632,36'},
{'4550919':'363,65'},
{'4858190':'504,86'},
{'5638054':'4787,52'},
{'6375383':'1623,68'},
{'7624620':'740,36'},
{'7992165':'1121,61'},
{'8259542':'473,28'},
{'24814041':'1053,76'},
{'47352649':'1279,85'},
{'8460507':'8025,12'},
{'8512698':'10745,45'},
{'4878507':'4281,69'},
{'8513228':'4570,08'},
{'8531625':'463,57'},
{'9366679':'2646,49'},
{'9849076':'0'},
{'9911553':'1221,21'},
{'10783933':'1617,24'},
{'11433863':'1990,58'},
{'7192657':'10226,06'},
{'7598416':'4783,98'},
{'12323999':'0'},
{'12323999':'0'},
{'18373815':'767,13'},
{'18702690':'2526,97'},
{'18739917':'2970,91'},
{'19362078':'134,14'},
{'19416372':'42,87'},
{'19433021':'240,07'},
{'19910458':'241,14'},
{'20036516':'129,51'},
{'20123249':'192,5'},
{'22496557':'3801,41'},
{'22758292':'3487,79'},
{'22912674':'1278,76'},
{'23388480':'2732,76'},
{'23684306':'817,74'},
{'23902567':'2261,51'},
{'24051218':'4612,14'},
{'24132013':'0'},
{'24170322':'0'},
{'24492834':'579,68'},
{'24499227':'0'},
{'24934462':'888,16'},
{'25772261':'230,48'},
{'25853482':'0'},
{'26448670':'1739,65'},
{'26718490':'2490,86'},
{'27295606':'0'},
{'27761828':'0'},
{'27797377':'1368,17'},
{'28150180':'939,75'},
{'28875185':'1483,83'},
{'29057575':'1189,73'},
{'29081000':'3318,94'},
{'29537941':'24,97'},
{'29582092':'0'},
{'30136616':'706,13'},
{'30141687':'0'},
{'30151283':'0'},
{'30267214':'725,18'},
{'30621220':'0'},
{'30732812':'912,05'},
{'30970098':'1971,58'},
{'31046823':'1170,03'},
{'31504481':'503,47'},
{'31554730':'377,82'},
{'31563364':'551,31'},
{'31580331':'0'},
{'31766567':'1983,44'},
{'31952433':'918'},
{'32345646':'145,14'},
{'34703485':'1087,75'},
{'34756210':'4429,64'},
{'40205845':'0'},
{'40268030':'6876,57'},
{'40428143':'2295,74'},
{'40457593':'411,28'},
{'40523057':'77,24'},
{'40779418':'0'},
{'40866523':'1081,53'},
{'40872876':'1470,82'},
{'41012188':'2214,01'},
{'41057769':'536,89'},
{'41303239':'0'},
{'41478551':'0'},
{'41732075':'2550,95'},
{'42113247':'0'},
{'42616842':'161,67'},
{'42675695':'437,06'},
{'42750379':'953,31'},
{'43379615':'50,9'},
{'43379747':'18,28'},
{'43435183':'2503,34'},
{'44015790':'0'},
{'44808323':'8178,42'},
{'44862948':'1165,37'},
{'45042235':'0'},
{'45255891':'3013,67'},
{'45361888':'688,05'},
{'45391574':'1622,65'},
{'45391639':'2673,56'},
{'45454045':'425,53'},
{'45500675':'0'},
{'45687228':'74,12'},
{'45762912':'1120'},
{'46034422':'0'},
{'46223691':'2276,36'},
{'46224671':'2701,81'},
{'46312503':'0'},
{'46814380':'1601,29'},
{'46870158':'2772,64'},
{'47498643':'608,85'},
{'47498678':'0'},
{'47498759':'0'},
{'49629559':'847,79'},
{'49630301':'283,26'},
{'49808291':'1370,36'},
{'50188256':'4863,82'},
{'50683796':'858,54'},
{'51012461':'1076,88'},
{'51308867':'3450,71'},
{'30595068':'0'},
{'4747623':'0'},
{'1316940':'6393,85'},
{'3161625':'962,49'},
{'3095070':'636,42'},
{'43356038':'560,77'},
{'4083857':'3473,48'},
{'45814521':'192,61'},
{'5083460':'417,58'},
{'44980142':'2496,68'},
{'27278086':'0'},
{'19112047':'867,03'},
{'21646857':'1801,15'},
{'5270910':'1499,47'},
{'27457576':'12593,86'},
{'45687210':'1982,73'},
{'40493328':'207,41'},
{'1986805':'563,73'},
{'19198286':'1229,01'},
{'3321436':'1903,98'},
{'24637476':'4609,28'},
{'26133025':'1575,79'},
{'2630761':'246,41'},
{'41949686':'321,13'},
{'4074688':'4331,23'},
{'22009567':'1879,33'},
{'2005263':'1656,2'},
{'46060024':'4480,23'},
{'23991284':'0'},
{'57820268':'11,56'},
{'42842290':'0'},
{'4879783':'0'},
{'5085594':'0'},
{'57068396':'0'},
{'683396':'0'},
{'743828':'0'},
{'1019082':'0'},
{'1120492':'0'},
{'1556371':'0'},
{'2851776':'0'},
{'3928560':'0'},
{'6050662':'1829,45'},
{'7181655':'3971,21'},
{'7828470':'0'},
{'8054770':'4153,74'},
{'8271682':'2103,24'},
{'10310059':'0'},
{'11333524':'1795,92'},
{'20883634':'0'},
{'21061581':'0'},
{'23873150':'1240,56'},
{'23875195':'750,03'},
{'27235239':'0'},
{'28078064':'0'},
{'29409854':'2901,06'},
{'29969027':'0'},
{'31921821':'0'},
{'32064272':'0'},
{'40891234':'0'},
{'41437022':'0'},
{'41567139':'0'},
{'42507130':'0'},
{'42669105':'0'},
{'43651072':'0'},
{'43853066':'0'},
{'45494535':'0'},
{'47848245':'0'},
{'50002497':'0'},
{'51684419':'2819,78'},
{'53354750':'0'},
{'54031459':'0'},
{'56210482':'0'},
{'56421033':'0'},
{'56439315':'0'},
{'56492658':'0'},
{'56804935':'0'},
{'56818634':'0'},
{'56873570':'0'},
{'56970797':'0'},
{'57040190':'0'},
{'57187484':'4169,42'},
{'57209470':'0'},
{'57335890':'0'},
{'57439262':'0'},
{'57492864':'1043,77'},
{'57493143':'689,42'},
{'57657952':'2955,25'},
{'57753722':'0'},
{'57760761':'3755,91'},
{'57808365':'0'},
{'1370693':'0'},
{'24421520':'0'},
{'50429520':'0'},
{'57325470':'992,18'},
{'9930604':'0'},
{'57711027':'2871,82'}]


lista_sistema = [{'55524114':'829,95'},
{'43536737':'368,6'},
{'24814041':'1053,76'},
{'23112507':'3536,26'},
{'28875185':'1483,83'},
{'26280':'3757,31'},
{'19416372':'42,87'},
{'35823':'22,81'},
{'20666838':'1395,8'},
{'25772261':'230,48'},
{'105678':'373,89'},
{'105759':'1929,94'},
{'40523057':'77,24'},
{'1724':'1646,37'},
{'50188256':'4863,82'},
{'44808323':'8178,42'},
{'49773471':'1407,75'},
{'210854':'1280,38'},
{'20036516':'129,51'},
{'23506580':'2028,12'},
{'20123249':'192,5'},
{'41117486':'413,5'},
{'335924':'754,29'},
{'34756210':'4429,64'},
{'237787':'3210,45'},
{'40268030':'6876,57'},
{'40565671':'1193'},
{'493341':'536,85'},
{'26718490':'2490,86'},
{'45687228':'74,12'},
{'29537941':'24,97'},
{'30267214':'725,18'},
{'24015009':'214,72'},
{'22912674':'1278,76'},
{'1370766':'1058,34'},
{'45814521':'192,61'},
{'40457593':'411,28'},
{'726478':'4320,51'},
{'46060024':'4480,23'},
{'30895681':'4210,02'},
{'41012188':'2214,01'},
{'31504481':'503,47'},
{'31563364':'551,31'},
{'714860':'2787,79'},
{'848115':'5287,32'},
{'883549':'1303,05'},
{'892629':'226,6'},
{'892602':'1538,25'},
{'64734':'1064,29'},
{'896578':'2183,2'},
{'23902567':'2261,51'},
{'18739917':'2970,91'},
{'42616842':'161,67'},
{'40428143':'2295,74'},
{'980790':'715,76'},
{'51708580':'1085,64'},
{'32397557':'2708,15'},
{'1316940':'6393,85'},
{'24051218':'4612,14'},
{'49381140':'83,47'},
{'49629559':'847,79'},
{'49630301':'283,26'},
{'2044463':'79,49'},
{'28150180':'939,75'},
{'1443348':'274,36'},
{'29057575':'1189,73'},
{'30970098':'1971,58'},
{'47352649':'1279,85'},
{'45391639':'2673,56'},
{'45391574':'1622,65'},
{'54293542':'1228,78'},
{'3914933':'2638,77'},
{'43379615':'50,9'},
{'43379747':'18,28'},
{'55085900':'1789,54'},
{'32345646':'145,14'},
{'34703485':'1087,75'},
{'342599':'1356,76'},
{'46224671':'2701,81'},
{'31382351':'954,4'},
{'22758292':'3487,79'},
{'2061112':'2673,58'},
{'2031230':'990,19'},
{'24492834':'579,68'},
{'1484176':'1073,7'},
{'23388480':'2732,76'},
{'54186967':'4570,76'},
{'2374137':'1083,66'},
{'41484292':'1515,13'},
{'2420082':'1157,22'},
{'2404249':'5475,57'},
{'54593767':'3404,3'},
{'50876870':'1598,64'},
{'1282964':'349,61'},
{'2748797':'3111,37'},
{'2857880':'437,48'},
{'2909243':'481,22'},
{'31554730':'377,82'},
{'55880719':'5936,68'},
{'43474081':'858,97'},
{'3161625':'962,49'},
{'3095070':'636,42'},
{'55667497':'5142,6'},
{'22795007':'2304,16'},
{'41601345':'6809,55'},
{'44107600':'1090,32'},
{'43356038':'560,77'},
{'46465849':'2093,39'},
{'54124244':'800,49'},
{'27797377':'1368,17'},
{'2630761':'246,41'},
{'18931605':'436,08'},
{'53326463':'4146,66'},
{'1986805':'563,73'},
{'3771458':'57,02'},
{'3771466':'1523,17'},
{'40765778':'2913,06'},
{'6119220':'1799,01'},
{'6125263':'577,84'},
{'6096859':'959,48'},
{'24637476':'4609,28'},
{'29414424':'763,2'},
{'42751340':'484,81'},
{'19198286':'1229,01'},
{'3321436':'1903,98'},
{'26133025':'1575,79'},
{'31323592':'1515,53'},
{'31046823':'1170,03'},
{'15579943':'414,3'},
{'4074688':'4331,23'},
{'22009567':'1879,33'},
{'3645630':'3313,83'},
{'51927753':'4688,45'},
{'45687210':'1982,73'},
{'57492864':'1043,77'},
{'56448705':'664,28'},
{'3987841':'3601,89'},
{'19112047':'867,03'},
{'27457576':'12593,86'},
{'4083857':'3473,48'},
{'41949686':'321,13'},
{'44980142':'2496,68'},
{'57657952':'2955,25'},
{'5083460':'417,58'},
{'2005263':'1656,2'},
{'21646857':'1801,15'},
{'5270910':'1499,47'},
{'53775810':'1110,77'},
{'40493328':'207,41'},
{'44862948':'1165,37'},
{'51684419':'2819,78'},
{'21084484':'3031,08'},
{'5638054':'4787,52'},
{'22496557':'3801,41'},
{'8259542':'473,28'},
{'54730004':'2174,53'},
{'6050662':'1829,45'},
{'18373815':'767,13'},
{'23684306':'817,74'},
{'51638646':'1450,11'},
{'51308867':'3450,71'},
{'3945588':'632,36'},
{'6266177':'4373,33'},
{'42178926':'959,48'},
{'6375383':'1623,68'},
{'50429610':'1277,59'},
{'8271682':'2103,24'},
{'49808291':'1370,36'},
{'57760761':'3755,91'},
{'8054770':'4153,74'},
{'18702690':'2526,97'},
{'7192657':'10226,06'},
{'7181655':'3971,21'},
{'53663001':'3923,44'},
{'1271229':'1898,6'},
{'6625126':'1682,67'},
{'7598416':'4783,98'},
{'55685142':'2710,68'},
{'9911553':'1221,21'},
{'7624620':'740,36'},
{'41057769':'536,89'},
{'47498643':'608,85'},
{'57187484':'4169,42'},
{'47376980':'109'},
{'6956831':'3298,17'},
{'23873150':'1240,56'},
{'23875195':'750,03'},
{'57711027':'2871,82'},
{'7849095':'3836,71'},
{'43435183':'2503,34'},
{'7992165':'1121,61'},
{'7995679':'4383,31'},
{'49285965':'1035,8'},
{'380148':'677,91'},
{'22146742':'1046,71'},
{'53927467':'1383,15'},
{'53927416':'1065,86'},
{'29409854':'2901,06'},
{'45762912':'1120'},
{'9176462':'3227,34'},
{'8457654':'2047,64'},
{'54227680':'3327,4'},
{'52762731':'4283,48'},
{'46814380':'1601,29'},
{'54511949':'3253,95'},
{'50683796':'858,54'},
{'54062109':'86,98'},
{'45454045':'425,53'},
{'45361888':'688,05'},
{'57493151':'85,9'},
{'57493143':'689,42'},
{'40872876':'1470,82'},
{'40866523':'1081,53'},
{'9366679':'2646,49'},
{'9371524':'2784,13'},
{'53416829':'2457,57'},
{'55143641':'905,46'},
{'26919010':'3107,4'},
{'24934462':'888,16'},
{'46870158':'2772,64'},
{'7665580':'1700,89'},
{'44764989':'598,48'},
{'34719608':'1024,9'},
{'45255891':'3013,67'},
{'23359928':'3649,65'},
{'8558140':'872,24'},
{'46223691':'2276,36'},
{'46910389':'327,1'},
{'31952433':'918'},
{'3460525':'308,39'},
{'19910458':'241,14'},
{'19090019':'406,39'},
{'11333524':'1795,92'},
{'10783933':'1701,95'},
{'30136616':'706,13'},
{'45958167':'1940,75'},
{'31766567':'1983,44'},
{'47067790':'436,08'},
{'2254182':'1962,65'},
{'8512698':'10745,45'},
{'8513228':'4570,08'},
{'41732075':'2550,95'},
{'8531625':'463,57'},
{'52341086':'5006,45'},
{'23588960':'1439,21'},
{'26448670':'1739,65'},
{'26697514':'5314,44'},
{'25894464':'1144,82'},
{'30732812':'912,05'},
{'51012461':'1076,88'},
{'4878507':'4281,69'},
{'42675695':'437,06'},
{'29081000':'3318,94'},
{'4845404':'2158,81'},
{'42750379':'953,31'},
{'4858190':'504,86'},
{'53431100':'4231,03'},
{'57713623':'686,87'},
{'57325470':'992,18'},
{'11433863':'1990,58'},
{'55699615':'1328,97'},
{'57820268':'11,56'},
{'4550919':'363,65'},
{'8460507':'8025,12'},
{'56578471':'14,96'},
{'19433021':'240,07'},
{'19362078':'134,14'}]

# Calcular a diferença percentual entre dois valores
def calcular_diferenca_percentual(valor1, valor2):
    """Calcula a diferença percentual entre dois valores"""
    # Substituir vírgula por ponto e converter para float
    v1 = float(valor1.replace(',', '.'))
    v2 = float(valor2.replace(',', '.'))
    
    # Verificar se ambos os valores são zero
    if v1 == 0 and v2 == 0:
        return 0.0
    
    # Evitar divisão por zero
    if v1 == 0:
        return 100.0  # Diferença de 100% se o primeiro valor é zero
    
    # Calcular a diferença percentual
    return abs((v2 - v1) / v1 * 100)

# Calcular estatísticas de valores
def calcular_estatisticas(dicionario, nome):
    # Converter valores para números
    valores_numericos = []
    zeros = 0
    nao_zeros = 0
    
    for valor in dicionario.values():
        # Substituir vírgula por ponto para converter para float
        valor_limpo = valor.replace(',', '.')
        valor_float = float(valor_limpo)
        
        if valor_float == 0:
            zeros += 1
        else:
            nao_zeros += 1
            valores_numericos.append(valor_float)
    
    # Calcular estatísticas apenas para valores não-zero
    if valores_numericos:
        total = sum(valores_numericos)
        media = total / len(valores_numericos)
        valor_maximo = max(valores_numericos)
        valor_minimo = min(valores_numericos)
        
        escrever(f"\nEstatísticas de valores para {nome}:")
        escrever(f"  Total de registros: {len(dicionario)}")
        escrever(f"  Registros com valor zero: {zeros} ({zeros/len(dicionario)*100:.2f}%)")
        escrever(f"  Registros com valor não-zero: {nao_zeros} ({nao_zeros/len(dicionario)*100:.2f}%)")
        escrever(f"  Soma total (excluindo zeros): {total:.2f}")
        escrever(f"  Média (excluindo zeros): {media:.2f}")
        escrever(f"  Valor mínimo (excluindo zeros): {valor_minimo:.2f}")
        escrever(f"  Valor máximo: {valor_maximo:.2f}")

# Verificar chaves duplicadas nas listas originais
def verificar_duplicatas(lista, nome_lista):
    # Usar um dicionário para contar ocorrências de cada chave
    contagem = {}
    for item in lista:
        for chave in item.keys():
            if chave in contagem:
                contagem[chave] += 1
            else:
                contagem[chave] = 1
    
    # Filtrar apenas as chaves que aparecem mais de uma vez
    duplicatas = {chave: qtd for chave, qtd in contagem.items() if qtd > 1}
    
    if duplicatas:
        escrever(f"\nChaves duplicadas na {nome_lista}:")
        for chave, qtd in duplicatas.items():
            escrever(f"  Chave '{chave}' aparece {qtd} vezes")
    else:
        escrever(f"\nNão foram encontradas chaves duplicadas na {nome_lista}")
    
    return duplicatas

# Converter as listas para dicionários para facilitar a comparação
dic_clamed = {}
for item in lista_clamed:
    for chave, valor in item.items():
        dic_clamed[chave] = valor

dic_sistema = {}
for item in lista_sistema:
    for chave, valor in item.items():
        dic_sistema[chave] = valor

# Verificar duplicatas nas listas originais
duplicatas_clamed = verificar_duplicatas(lista_clamed, "lista_clamed")
duplicatas_sistema = verificar_duplicatas(lista_sistema, "lista_sistema")

# Calcular estatísticas para cada conjunto
calcular_estatisticas(dic_clamed, "lista_clamed")
calcular_estatisticas(dic_sistema, "lista_sistema")

# Encontrar chaves comuns
chaves_comuns = set(dic_clamed.keys()) & set(dic_sistema.keys())
escrever(f"\nTotal de chaves comuns: {len(chaves_comuns)}")

# Comparar valores para as chaves comuns
diferencas = {}
for chave in chaves_comuns:
    if dic_clamed[chave] != dic_sistema[chave]:
        diferencas[chave] = {
            'clamed': dic_clamed[chave],
            'sistema': dic_sistema[chave],
            'diferenca_percentual': calcular_diferenca_percentual(dic_clamed[chave], dic_sistema[chave])
        }

# Ordenar as diferenças pela diferença percentual (da maior para a menor)
diferencas_ordenadas = sorted(diferencas.items(), key=lambda x: x[1]['diferenca_percentual'], reverse=True)

# Mostrar as diferenças
escrever(f"\nTotal de chaves com valores diferentes: {len(diferencas)} ({len(diferencas)/len(chaves_comuns)*100:.2f}% das chaves comuns)")
escrever("\nChaves com valores diferentes (ordenadas por diferença percentual):")
for chave, valores in diferencas_ordenadas:
    escrever(f"Chave: {chave}")
    escrever(f"  Valor clamed: {valores['clamed']}")
    escrever(f"  Valor sistema: {valores['sistema']}")
    escrever(f"  Diferença percentual: {valores['diferenca_percentual']:.2f}%")
    escrever("")

# Análise detalhada das diferenças
if diferencas:
    # Calcular estatísticas sobre as diferenças percentuais
    diferencas_percentuais = [valores['diferenca_percentual'] for _, valores in diferencas.items()]
    media_diferenca = sum(diferencas_percentuais) / len(diferencas_percentuais)
    max_diferenca = max(diferencas_percentuais)
    min_diferenca = min(diferencas_percentuais)
    
    escrever("\nEstatísticas das diferenças percentuais:")
    escrever(f"  Média das diferenças: {media_diferenca:.2f}%")
    escrever(f"  Maior diferença: {max_diferenca:.2f}%")
    escrever(f"  Menor diferença: {min_diferenca:.2f}%")
    
    # Classificar as diferenças
    pequenas_diferencas = sum(1 for d in diferencas_percentuais if d < 5)
    medias_diferencas = sum(1 for d in diferencas_percentuais if 5 <= d < 10)
    grandes_diferencas = sum(1 for d in diferencas_percentuais if d >= 10)
    
    escrever("\nClassificação das diferenças:")
    escrever(f"  Pequenas (< 5%): {pequenas_diferencas} ({pequenas_diferencas/len(diferencas_percentuais)*100:.2f}%)")
    escrever(f"  Médias (5% - 10%): {medias_diferencas} ({medias_diferencas/len(diferencas_percentuais)*100:.2f}%)")
    escrever(f"  Grandes (>= 10%): {grandes_diferencas} ({grandes_diferencas/len(diferencas_percentuais)*100:.2f}%)")

# Chaves exclusivas
chaves_somente_clamed = set(dic_clamed.keys()) - set(dic_sistema.keys())
chaves_somente_sistema = set(dic_sistema.keys()) - set(dic_clamed.keys())

escrever(f"\nTotal de chaves apenas em clamed: {len(chaves_somente_clamed)} ({len(chaves_somente_clamed)/len(dic_clamed)*100:.2f}% da lista_clamed)")
escrever(f"Total de chaves apenas em sistema: {len(chaves_somente_sistema)} ({len(chaves_somente_sistema)/len(dic_sistema)*100:.2f}% da lista_sistema)")

# Contar quantas chaves exclusivas têm valor 0
zeros_somente_clamed = sum(1 for chave in chaves_somente_clamed if dic_clamed[chave] == '0')
escrever(f"Das chaves apenas em clamed, {zeros_somente_clamed} ({zeros_somente_clamed/len(chaves_somente_clamed)*100:.2f}%) têm valor 0")

zeros_somente_sistema = sum(1 for chave in chaves_somente_sistema if dic_sistema[chave] == '0')
escrever(f"Das chaves apenas em sistema, {zeros_somente_sistema} ({zeros_somente_sistema/len(chaves_somente_sistema)*100:.2f}%) têm valor 0")

escrever("\nChaves que estão apenas em clamed:")
for chave in sorted(chaves_somente_clamed):
    escrever(f"  {chave}: {dic_clamed[chave]}")

escrever("\nChaves que estão apenas em sistema:")
for chave in sorted(chaves_somente_sistema):
    escrever(f"  {chave}: {dic_sistema[chave]}")

# Análise dos valores de chaves exclusivas
soma_valores_exclusivos_sistema = 0
if chaves_somente_clamed:
    valores_nao_zero_clamed = [float(dic_clamed[chave].replace(',', '.')) for chave in chaves_somente_clamed 
                              if dic_clamed[chave] != '0']
    if valores_nao_zero_clamed:
        soma_valores_exclusivos_clamed = sum(valores_nao_zero_clamed)
        escrever(f"\nSoma dos valores não-zero exclusivos em clamed: {soma_valores_exclusivos_clamed:.2f}")
    else:
        escrever(f"\nNão há valores não-zero exclusivos em clamed")

if chaves_somente_sistema:
    valores_nao_zero_sistema = [float(dic_sistema[chave].replace(',', '.')) for chave in chaves_somente_sistema 
                               if dic_sistema[chave] != '0']
    if valores_nao_zero_sistema:
        soma_valores_exclusivos_sistema = sum(valores_nao_zero_sistema)
        escrever(f"Soma dos valores não-zero exclusivos em sistema: {soma_valores_exclusivos_sistema:.2f}")
    else:
        escrever(f"Não há valores não-zero exclusivos em sistema")

# Resumo final
escrever("\nRESUMO DA COMPARAÇÃO:")
escrever(f"Total de chaves em clamed: {len(dic_clamed)}")
escrever(f"Total de chaves em sistema: {len(dic_sistema)}")
escrever(f"Chaves comuns: {len(chaves_comuns)} ({len(chaves_comuns)/max(len(dic_clamed), len(dic_sistema))*100:.2f}% do maior conjunto)")
escrever(f"Chaves com valores diferentes: {len(diferencas)}")
escrever(f"Chaves apenas em clamed: {len(chaves_somente_clamed)}")
escrever(f"Chaves apenas em sistema: {len(chaves_somente_sistema)}")

# Gerar conclusões e recomendações
gerar_conclusoes(dic_clamed, dic_sistema, chaves_comuns, diferencas, 
                 chaves_somente_clamed, chaves_somente_sistema, 
                 zeros_somente_clamed, soma_valores_exclusivos_sistema)

# Fechar o arquivo de resultados
arquivo_resultado.close()
print("\nResultados salvos no arquivo 'resultado_comparacao.txt'.") 