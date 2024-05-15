import vk_api
import config
import requests
from vk_api.longpoll import VkLongPoll, VkEventType

vk = vk_api.VkApi(token=config.token)
longpoll = VkLongPoll(vk)



def get_keyboard(name):
    keyb = open(f"keyboards/{name}.json", "r", encoding = "UTF-8").read()
    return keyb

user_states = {}

def send_msg(user_id, message, keyboard=None, state=None):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': 0, 'keyboard': keyboard})
    user_states[user_id] = state

def user_prev_state(user_id):
    if user_id in user_states:
        return user_states[user_id]
    else:
        return None

def get_user_name(user_id):
    user_name = vk.method('users.get', {'user_ids': user_id, 'fields': 'first_name'})
    user_name = user_name[0]['first_name']
    return user_name


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        msg = event.text.lower()
        user_id = event.user_id
        if msg in ["начать", "start", "привет", "старт"]:
            message = "Я чат-бот, который поможет Вам узнать актуальную информацию о микрофинансовых организациях. Здесь Вы сможете найти ответы на все вопросы об условиях займов и сбережений, процентных ставках, сроках и прочих услугах. Начнём?"
            send_msg(user_id, message, get_keyboard("da"))
        elif msg == 'да!':
            message = "Какая услуга Вас интересует?"
            send_msg(user_id, message, get_keyboard("empty"), state="start")

            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    msg = event.text.lower()
                    user_id = event.user_id

                    if msg == 'сбережения':
                        message = "Вы хотели бы обратиться онлайн или офлайн?"
                        send_msg(user_id, message, get_keyboard("on_off"), state="service_selection_sber")

                        for event in longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                msg = event.text.lower()
                                user_id = event.user_id 

                                if msg == 'онлайн' and user_states[user_id] == 'service_selection_sber':
                                    message = 'Обратите внимание, что онлайн Вы можете получить услугу только у МФК и МКК.'
                                    send_msg(user_id, message, get_keyboard("rethink_sber"), state="on_off_sber")

                                    for event in longpoll.listen():
                                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                            msg = event.text.lower()
                                            user_id = event.user_id 

                                            if msg == 'хорошо, продолжить' and user_states[user_id] == 'on_off_sber':
                                                message = 'Обратите внимание, что минимальные инвестиции в МФК составляют 1,5 млн'
                                                send_msg(user_id, message, get_keyboard("rethink_sber"), state="agreement_sber")

                                                for event in longpoll.listen():
                                                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                                        msg = event.text.lower()
                                                        user_id = event.user_id
                                                    if msg == 'хорошо, продолжить' and user_states[user_id] == 'agreement_sber':
                                                        send_msg(user_id, 'Введите желаемую сумму', get_keyboard('skip'))
                                                        for event in longpoll.listen():
                                                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                                                msg = event.text.lower()
                                                                send_msg(user_id, 'Введите желаемый процент',
                                                                        get_keyboard('skip'))
                                                                for event in longpoll.listen():
                                                                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                                                        msg = event.text.lower()
                                                                        send_msg(user_id, 'Введите желаемый срок',
                                                                                get_keyboard('skip'))
                                                                        for event in longpoll.listen():
                                                                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                                                                msg = event.text.lower()
                                                                                send_msg(user_id,
                                                                         'На этом мои полномочия заканчиваются:( Предлагаю Вам перейти на наш сайт, где для Вас подобраны подходящие организации ссылка на сайт')

                                                break

                                elif msg == 'офлайн' and user_states[user_id] == 'service_selection_sber':
                                    message = 'Как часто Вы хотите пользоваться услугами? Если регулярно, то лучше стать членом КПК/СКПК и получать услугу в любой удобный момент!'
                                    send_msg(user_id, message, get_keyboard("once"), state="once_sber")

                                    for event in longpoll.listen():
                                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                            msg = event.text.lower()
                                            user_id = event.user_id

                                            if msg == 'регулярно' and user_states[user_id] == 'once_sber':
                                                message = 'Вы занимаетесь сельскохозяйственной деятельностью?'
                                                send_msg(user_id, message, get_keyboard("selhoz_sber"), state="selhos_sber")

                                                for event in longpoll.listen():
                                                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                                        msg = event.text.lower()
                                                        user_id = event.user_id
                                                    if msg == 'да' and user_states[user_id] == 'selhoz_sber':
                                                        message = "Тогда предлагаю Вам воспользоваться услугами СКПК. Обратите внимание, что СКПК требует постоянного членства"
                                                        r4 = requests.get(
                                                            'http://127.0.0.1:8000/api/v1/company/?search=СКПК')
                                                        send_msg(user_id, message,
                                                                 state="skpk_sber")
                                                        send_msg(user_id, r4.text)

                                                        send_msg(user_id,
                                                                'На этом мои полномочия заканчиваются:( Предлагаю Вам перейти на наш сайт для дальнейших действий ссылка на сайт')

                                                    elif msg == 'нет' and user_states[user_id] == 'selhoz_sber':
                                                        message = "Тогда предлагаю Вам воспользоваться услугами КПК. Обратите внимание, что КПК требует постоянного членства"
                                                        r5 = requests.get(
                                                            'http://127.0.0.1:8000/api/v1/company/?search=КПК')
                                                        send_msg(user_id, message,
                                                                 state="kpk_sber")
                                                        send_msg(user_id, r5.text)
                                                        send_msg(user_id,
                                                                 'На этом мои полномочия заканчиваются:( Предлагаю Вам перейти на наш сайт для дальнейших действий ссылка на сайт')

                                                    break

                                            elif msg == 'пока разово' and user_states[user_id] == 'once_sber':
                                                message = 'Тогда предлагаю Вам воспользоваться услугами МФК, МКК или Ломбарда.'
                                                r1 = requests.get('http://127.0.0.1:8000/api/v1/company/?search=МФК')
                                                r2 = requests.get('http://127.0.0.1:8000/api/v1/company/?search=МКК')
                                                r3 = requests.get('http://127.0.0.1:8000/api/v1/company/?search=Ломбард')
                                                send_msg(user_id, r1.text)
                                                send_msg(user_id, r2.text)
                                                send_msg(user_id, r3.text)

                                            elif msg == 'назад':
                                                prev_state = user_prev_state(user_id)
                                                if prev_state == "service_selection_sber":
                                                    message = "Вы вернулись к выбору услуги. Какая услуга Вас интересует?"
                                                    send_msg(user_id, message, get_keyboard("empty"), state ='start')
                                                elif prev_state == "on_off_sber":
                                                    message = "Вы хотели бы обратиться онлайн или офлайн?"
                                                    send_msg(user_id, message, get_keyboard("on_off"), state='service_selection_sber')
                                                elif prev_state == "once_sber":
                                                    message = "Вы хотели бы обратиться онлайн или офлайн?"
                                                    send_msg(user_id, message, get_keyboard("on_off"), state='service_selection_sber')
                                                elif prev_state == "agreement_sber":
                                                    message = "Вы хотели бы обратиться онлайн или офлайн?"
                                                    send_msg(user_id, message, get_keyboard("on_off"), state = 'service_selection_sber')
                                                elif prev_state == "selhos_sber":
                                                    message = 'Как часто Вы хотите пользоваться услугами? Если регулярно, то лучше стать членом КПК/СКПК и получать услугу в любой удобный момент!'
                                                    send_msg(user_id, message, get_keyboard("once"), state='once_sber')
                                        break
                                    
                                elif msg == 'назад':
                                    prev_state = user_prev_state(user_id)
                                    if prev_state == "service_selection_sber":
                                        message = "Вы вернулись к выбору услуги. Какая услуга Вас интересует?"
                                        send_msg(user_id, message, get_keyboard("empty"), state ='start')
                                    elif prev_state == "on_off_sber":
                                        message = "Вы хотели бы обратиться онлайн или офлайн?"
                                        send_msg(user_id, message, get_keyboard("on_off"), state='service_selection_sber')
                                    elif prev_state == "once_sber":
                                        message = "Вы хотели бы обратиться онлайн или офлайн?"
                                        send_msg(user_id, message, get_keyboard("on_off"), state='service_selection_sber')
                                    elif prev_state == "agreement_sber":
                                        message = "Вы хотели бы обратиться онлайн или офлайн?"
                                        send_msg(user_id, message, get_keyboard("on_off"), state = 'service_selection_sber')
                                    elif prev_state == "selhos_sber":
                                        message = 'Как часто Вы хотите пользоваться услугами? Если регулярно, то лучше стать членом КПК/СКПК и получать услугу в любой удобный момент!'
                                        send_msg(user_id, message, get_keyboard("once"), state='once_sber')

                                break

                                
                    elif msg == 'общая информация':
                        message = "О каком типе организации Вам хочется узнать подробнее?"
                        send_msg(user_id, message, get_keyboard("org"), state="service_selection_org")
            
                        for event in longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                msg = event.text.lower()
                                user_id = event.user_id 
                                if msg == "мфк" or msg == "мкк":
                                    message = "Что Вам было бы интересно узнать? Выберите цифру: \n \
                                    1. Что такое МФО и как они работают? \n \
                                    2. Как выбрать подходящую МФО? \n \
                                    3. Какова процедура получения займа? \n \
                                    4. Какая информация обязательна при заполнении заявки? \n \
                                    5. Как долго занимает процесс рассмотрения заявки? \n \
                                    6. Как осуществляется погашение займа? \n \
                                    7. Что происходит, если я не могу погасить займ вовремя?"
                                    send_msg(user_id, message, get_keyboard("numbers7"), state="service_selection_question")

                                    for event in longpoll.listen():
                                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                            msg = event.text.lower()
                                            user_id = event.user_id 
                                            if msg == "1":
                                                message = "МФО (микрофинансовые организации) предоставляют короткосрочные займы физическим лицам и малому бизнесу. \
                                                Они часто работают онлайн и упрощают процесс получения кредита, поскольку не требуют большого количества \
                                                документов и предлагают быстрое одобрение заявки."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "2":
                                                message = "При выборе МФО важно учитывать такие факторы, как процентная ставка по кредиту, \
                                                сроки погашения, условия для получения займа и надежность компании.\
                                                Также полезно ознакомиться с отзывами других пользователей, чтобы получить \
                                                представление о качестве обслуживания."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "3":
                                                message = "Процедура получения займа в МФО обычно очень проста и удобна. \
                                                Вы должны заполнить онлайн-заявку, указав необходимую сумму и срок кредита,\
                                                а также предоставить несколько документов (обычно паспорт и ИНН). \
                                                Затем заявка рассматривается, и если она одобрена, деньги переводятся на ваш счет."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "4":
                                                message = "Обычно при заполнении заявки в МФО требуется указать личную информацию, \
                                                такую как ФИО, дата рождения, адрес проживания, контактные данные. \
                                                Некоторые МФО могут также запросить информацию о доходах, семейном положении и т.д."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "5":
                                                message = "Время рассмотрения заявки в МФО может варьироваться, обычно это занимает \
                                                от нескольких минут до нескольких часов. Некоторые компании могут предлагать \
                                                быстрое одобрение за несколько минут, но это зависит от политики каждой конкретной МФО.\
                                                В любом случае, МФО обычно стараются обеспечить быструю обработку заявок и перевод денег."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "6":
                                                message = "Погашение займа в МФО обычно осуществляется путем перевода суммы платежа \
                                                на счет МФО в указанный срок. Сумма платежа включает сумму основного долга и проценты, \
                                                которые были оговорены в договоре. В некоторых случаях можно выбрать способ погашения займа, \
                                                оплатив с помощью банковской карты или электронного кошелька."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "7":
                                                message = "В случае, если вы не можете погасить займ вовремя, вам следует связаться с МФО \
                                                и подробно объяснить свою ситуацию. МФО могут предложить вам определенные варианты, \
                                                такие как продление срока кредита или установка рассрочки. Важно не игнорировать \
                                                проблему и своевременно обратиться за помощью."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "назад":
                                                message = "О каком типе организации Вам хочется узнать подробнее?"
                                                send_msg(user_id, message, get_keyboard("org"), state="service_selection_org")
                                                break
                                            break

                                elif msg == "скпк":
                                    message = "Что Вам было бы интересно узнать? Выберите цифру: \n \
                                    1. Что такое сельскохозяйственный кредитный потребительский кооператив (СКПК)? \n \
                                    2. Каков процесс вступления в члены СКПК? \n \
                                    3. Какие виды финансовых услуг предоставляются СКПК своим членам? \n \
                                    4. В чем преимущества участия в СКПК по сравнению с другими финансовыми институтами? \n \
                                    5. Как кооператив поддерживает сельскохозяйственное развитие? \n \
                                    6. Каковы условия возврата кредитов в СКПК? \n \
                                    7. Как члены могут влиять на принятие решений в СКПК?"
                                    send_msg(user_id, message, get_keyboard("numbers7"), state="service_selection_question")

                                    for event in longpoll.listen():
                                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                            msg = event.text.lower()
                                            user_id = event.user_id 
                                            if msg == "1":
                                                message = "СКПК – это кооперативная организация, созданная на основе \
                                                членства фермеров и других участников сельского хозяйства, предоставляющая \
                                                финансовую поддержку, кредиты и другие услуги для развития сельского общества."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "2":
                                                message = "Обычно, для вступления в члены СКПК требуется подача заявления, \
                                                оплата членского взноса и соблюдение установленных критериев членства,\
                                                которые могут включать статус фермера или предпринимателя в сельском хозяйстве."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "3":
                                                message = "СКПК предоставляют кредиты для сельскохозяйственных нужд, сберегательные счета, \
                                                страхование, финансовые консультации и другие услуги, направленные на поддержку \
                                                устойчивости и развития сельского хозяйства."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "4":
                                                message = "Члены СКПК могут получать более доступные кредиты, специализированные \
                                                услуги для сельского хозяйства, участвовать в принятии решений по управлению \
                                                кооперативом и обладать определенными финансовыми привилегиями."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "5":
                                                message = "СКПК предоставляют финансовую поддержку для закупки сельскохозяйственного оборудования, \
                                                улучшения инфраструктуры, обучения фермеров, а также содействуют реализации инновационных \
                                                проектов в сельском хозяйстве."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "6":
                                                message = "Условия возврата кредитов зависят от политики каждого СКПК, но обычно \
                                                включают гибкий график платежей, учитывающий сезонные особенности сельского хозяйства,\
                                                и различные программы поддержки в случае временных трудностей."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "7":
                                                message = "Члены СКПК обычно имеют право голоса на собраниях и выборах, где\
                                                принимаются ключевые решения. Участие членов в управлении кооперативом обеспечивает \
                                                демократичность и прозрачность в принятии важных решений."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "назад":
                                                message = "О каком типе организации Вам хочется узнать подробнее?"
                                                send_msg(user_id, message, get_keyboard("org"), state="service_selection_ans")
                                                break
                                            break

                                elif msg == "кпк":
                                    message = "Что Вам было бы интересно узнать? Выберите цифру: \n \
                                    1. Что такое кредитный потребительский кооператив? \n \
                                    2. Как стать членом КПК? \n \
                                    3. Какие услуги предоставляют КПК? \n \
                                    4. Каковы преимущества членства в КПК по сравнению с обычным банком? \n \
                                    5. Что такое лояльность КПК? \n \
                                    6. Какие гарантии безопасности при хранении средств в КПК? \n \
                                    7. Как часто можно получать кредиты от КПК? \n \
                                    8. Как получить подробную информацию о КПК и их услугах?"
                                    send_msg(user_id, message, get_keyboard("numbers8"), state="service_selection_question")

                                    for event in longpoll.listen():
                                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                            msg = event.text.lower()
                                            user_id = event.user_id 
                                            if msg == "1":
                                                message = "КПК – это финансовая организация, основанная на членстве, \
                                                которая предоставляет кредиты, сбережения и другие финансовые услуги своим членам."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "2":
                                                message = "Обычно для становления членом КПК необходимо заполнить анкету, \
                                                внести определенную сумму доли и уплатить членский взнос. \
                                                Точная процедура может отличаться от КПК к КПК."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "3":
                                                message = "КПК обычно предлагают кредиты под различные потребности \
                                                (автокредиты, ипотека и т.д.), вклады, сберегательные счета, услуги по денежному \
                                                переводу и прочие банковские услуги."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "4":
                                                message = "Членами КПК являются его владельцы, поэтому они могут получать более \
                                                высокую доходность на свои вклады, более низкие процентные ставки на кредиты \
                                                и могут принимать участие в управлении кооперативом."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "5":
                                                message = "Лояльность КПК – это способ оценки преданности и доверия членов кооператива.\
                                                Члены, которые используют и рекомендуют услуги КПК, могут получать дополнительные \
                                                преимущества и вознаграждения."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "6":
                                                message = "КПК обычно защищены гарантией страхования депозитов, которая покрывает \
                                                потерю средств в случае банкротства КПК."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "7":
                                                message = "Частота предоставления кредитов зависит от политики каждого КПК, \
                                                но обычно члены могут получать кредиты по мере необходимости, \
                                                соблюдая установленные правила и условия."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "8":
                                                message = "Лучший способ получить информацию о конкретном КПК – \
                                                это посетить их веб-сайт, побеседовать с сотрудниками и прочитать \
                                                отзывы или рекомендации других членов."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")  
                                            elif msg == "назад":
                                                message = "О каком типе организации Вам хочется узнать подробнее?"
                                                send_msg(user_id, message, get_keyboard("org"), state="service_selection_ans")
                                                break 
                                            break

                                elif msg == "ломбард":
                        
                                    message = "Что Вам было бы интересно узнать? Выберите цифру: \n \
                                    1. Что такое ломбард? \n \
                                    2. Какие услуги предоставляет ломбард? \n \
                                    3. Как получить заем от ломбарда? \n \
                                    4. Каковы преимущества залогового кредитования? \n \
                                    5. Какие сроки и процентные ставки у ломбарда? \n \
                                    6. Что происходит, если я не могу погасить займ в ломбарде? \n \
                                    7. Можно ли получить залоговый кредит, если предмет не принадлежит мне полностью? \n \
                                    8. Как выбрать ломбард с хорошей репутацией?"
                                    send_msg(user_id, message, get_keyboard("numbers8"), state="service_selection_question")

                                    for event in longpoll.listen():
                                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                            msg = event.text.lower()
                                            user_id = event.user_id 
                                            if msg == "1":
                                                message = "Ломбард - это финансовая организация, где вы можете получить заем, \
                                                предоставив в залог ценные вещи, такие как ювелирные изделия, \
                                                электроника, автомобиль и т.д."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "2":
                                                message = "Ломбард предоставляет услуги залогового кредитования, \
                                                где вы можете получить деньги в обмен на залог предметов. Они также могут \
                                                предлагать услуги по выкупу заложенных предметов или продаже залогового имущества."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "3":
                                                message = "Для получения займа от ломбарда, вам необходимо предоставить ценную \
                                                вещь в залог. Ломбард произведет оценку предмета и предложит вам сумму займа в \
                                                зависимости от его стоимости и оценки."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "4":
                                                message = "Залоговое кредитование может быть преимущественным способом получения \
                                                займа, особенно если у вас есть нестабильный кредитный рейтинг или отсутствует \
                                                другая возможность получить кредит. Кроме того, процесс получения займа \
                                                относительно просто и быстро."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "5":
                                                message = "Сроки и процентные ставки в ломбардах могут различаться. Обычно займы \
                                                предоставляются на короткий срок от нескольких недель до нескольких месяцев, \
                                                и ставки могут быть разными в зависимости от правил и политики конкретного ломбарда."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "6":
                                                message = "Если вы не можете погасить займ в ломбарде вовремя, они могут отобрать \
                                                предмет, который был заложен в качестве залога, и продать его, чтобы покрыть \
                                                задолженность по займу. Остаток суммы после продажи предмета возвращается вам."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "7":
                                                message = "Обычно ломбарды требуют, чтобы предмет, выступающий в качестве залога, \
                                                был полностью в вашей собственности без других обременений или прав третьих лиц."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "8":
                                                message = "При выборе ломбарда, рекомендуется обратить внимание на репутацию, \
                                                отзывы и условия, предлагаемые различными ломбардами. Также полезно обратиться \
                                                за советом к знакомым или рекомендациям, чтобы выбрать надежный и ответственный ломбард."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")   
                                            break

                                elif msg == "сро":
                        
                                    message = "Что Вам было бы интересно узнать? Выберите цифру: \n \
                                    1. Что такое СРО? \n \
                                    2. Для чего создаются СРО? \n \
                                    3. Кто может быть членом СРО? \n \
                                    4. Как стать членом СРО? \n \
                                    5. Какие преимущества членства в СРО? \n \
                                    6. Какова роль СРО в надзоре за своими членами? \n \
                                    7. Какие санкции могут быть наложены СРО на своих членов? \n \
                                    8. Как получить информацию о СРО и их деятельности?"
                                    send_msg(user_id, message, get_keyboard("numbers8"), state="service_selection_question")

                                    for event in longpoll.listen():
                                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                            msg = event.text.lower()
                                            user_id = event.user_id 
                                            if msg == "1":
                                                message = "СРО (саморегулируемая организация) – это организация, созданная в рамках \
                                                определенной отрасли для саморегулирования и надзора за деятельностью своих членов. \
                                                СРО устанавливают правила и стандарты, которым должны следовать ее члены."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "2":
                                                message = "СРО создаются для обеспечения надлежащего качества и безопасности услуг \
                                                или работ в определенной отрасли. Они контролируют деятельность своих членов, \
                                                разрабатывают общепринятые стандарты и регулируют сферу деятельности."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "3":
                                                message = "Членами СРО могут быть юридические и физические лица, включая компании \
                                                и специалистов, работающих в соответствующей отрасли. Членство в СРО обычно является \
                                                добровольным, однако в некоторых случаях оно может быть обязательным."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "4":
                                                message = "Процесс вступления в СРО может различаться в зависимости от конкретной организации \
                                                и ее правил. Обычно требуется подать заявку, предоставить необходимые документы, \
                                                выполнить определенные условия, такие как обучение или стажировка, и уплатить членские взносы."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "5":
                                                message = "Членство в СРО может предоставлять ряд преимуществ. Это может включать доступ \
                                                к информации и ресурсам, повышение доверия и репутации в отрасли, защиту прав и интересов членов, \
                                                а также возможность повышения профессионального уровня."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "6":
                                                message = "СРО осуществляет надзор и контроль за деятельностью своих членов. Они могут \
                                                проводить проверки, аудиты, разрабатывать правила и нормативы, а также рассматривать \
                                                жалобы и принимать меры в отношении нарушителей."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "7":
                                                message = "СРО могут применять различные санкции к своим членам в случае нарушения правил \
                                                и стандартов. Это может включать штрафы, ограничения в деятельности, аннулирование \
                                                членства или другие меры в соответствии с уставом организации."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")
                                            elif msg == "8":
                                                message = "Для получения подробной информации о конкретном СРО можно обратиться на их\
                                                официальные веб-сайты, изучить их устав и правила, а также проконсультироваться у представителей \
                                                организации или других профессионалов в отрасли."
                                                send_msg(user_id, message, get_keyboard("back"), state="service_selection_ans")   
                                            break
                                elif msg == "назад":
                                    prev_state = user_prev_state(user_id)
                                    if prev_state == "service_selection_question" or prev_state == "service_selection_ans":
                                        message = "О каком типе организации Вам хочется узнать подробнее?"
                                        send_msg(user_id, message, get_keyboard("org"), state="service_selection_org")
                                    elif prev_state == "service_selection_org":
                                        message = "Вы вернулись к выбору услуги. Какая услуга Вас интересует?"


                    elif msg == 'хочу взять займ':
                        send_msg(user_id, 'Вы хотели бы обратиться онлайн или офлайн?', get_keyboard('main'), state="service_selection_zaim")
                        for event in longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                msg = event.text.lower()
                                user_id = event.user_id

                                if msg == 'онлайн' and user_states[user_id] == 'service_selection_zaim':
                                    send_msg(user_id,
                                             'Обратите внимание, что онлайн Вы можете получить услугу только у МФК и МКК.',
                                             get_keyboard('online'), state = 'on_off_zaim')
                                    for event in longpoll.listen():
                                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                            msg = event.text.lower()
                                            if msg == 'я передумал(а), хочу офлайн':
                                                send_msg(user_id,
                                                         'Как часто Вы хотите пользоваться услугами? Если регулярно, то лучше стать членом КПК/СКПК и получать услугу в любой удобный момент!',
                                                         get_keyboard('ofline'))
                                                for event in longpoll.listen():
                                                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                                        msg = event.text.lower()
                                                        if msg == 'регулярно':
                                                            send_msg(user_id,
                                                                     'Вы занимаетесь сельскохозяйственной деятельностью?',
                                                                     get_keyboard('yesno'))
                                                            for event in longpoll.listen():
                                                                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                                                    msg = event.text.lower()
                                                                    if msg == 'да':
                                                                        send_msg(user_id,
                                                                                 'Информация о филиалах и режимах работы СКПК')
                                                                        send_msg(user_id,
                                                                                 'На этом мои полномочия заканчиваются:( Предлагаю Вам перейти на наш сайт для дальнейших действий ссылка на сайт')
                                                                    elif msg == 'нет':
                                                                        send_msg(user_id,
                                                                                 'Информация о филиалах и режимах работы КПК')
                                                                        send_msg(user_id,
                                                                                 'На этом мои полномочия заканчиваются:( Предлагаю Вам перейти на наш сайт для дальнейших действий ссылка на сайт')

                                                        elif msg == 'пока разово':
                                                            send_msg(user_id,
                                                                     'Тогда предлагаю Вам воспользоваться услугами МФК, МКК или Ломбарда.\n\n Информация о филиалах и режимах работы')
                                                            send_msg(user_id, 'Не хотели бы вы вступить в КПК/СКПК?',
                                                                     get_keyboard('regulary'))
                                                            for event in longpoll.listen():
                                                                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                                                    msg = event.text.lower()
                                                                    if msg == 'хотел(-а) бы':
                                                                        send_msg(user_id,
                                                                                 'Вы занимаетесь сельскохозяйственной деятельностью?',
                                                                                 get_keyboard('yesno'))
                                                                        for event in longpoll.listen():
                                                                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                                                                msg = event.text.lower()
                                                                                if msg == 'да':
                                                                                    send_msg(user_id,
                                                                                             'Информация о филиалах и режимах работы СКПК')
                                                                                    send_msg(user_id,
                                                                                             'На этом мои полномочия заканчиваются:( Предлагаю Вам перейти на наш сайт для дальнейших действий ссылка на сайт')
                                                                                elif msg == 'нет':
                                                                                    send_msg(user_id,
                                                                                             'Информация о филиалах и режимах работы КПК')
                                                                                    send_msg(user_id,
                                                                                             'На этом мои полномочия заканчиваются:( Предлагаю Вам перейти на наш сайт для дальнейших действий ссылка на сайт')

                                                                    elif msg == 'не хотел(-а) бы':
                                                                        send_msg(user_id,
                                                                                 'На этом мои полномочия заканчиваются:( Предлагаю Вам перейти на наш сайт для дальнейших действий ссылка на сайт')

                                            elif msg == 'хорошо, продолжить':
                                                send_msg(user_id, 'Введите желаемую сумму', get_keyboard('skip'))
                                                for event in longpoll.listen():
                                                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                                        msg = event.text.lower()
                                                        send_msg(user_id, 'Введите желаемый процент',
                                                                 get_keyboard('skip'))
                                                        for event in longpoll.listen():
                                                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                                                msg = event.text.lower()
                                                                send_msg(user_id, 'Введите желаемый срок',
                                                                         get_keyboard('skip'))
                                                                for event in longpoll.listen():
                                                                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                                                        msg = event.text.lower()
                                                                        send_msg(user_id,
                                                                                 'На этом мои полномочия заканчиваются:( Предлагаю Вам перейти на наш сайт, где для Вас подобраны подходящие организации ссылка на сайт')


                                elif msg == 'офлайн':
                                    send_msg(user_id,
                                             'Как часто Вы хотите пользоваться услугами? Если регулярно, то лучше стать членом КПК/СКПК и получать услугу в любой удобный момент!',
                                             get_keyboard('ofline'))
                                    for event in longpoll.listen():
                                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                            msg = event.text.lower()
                                            if msg == 'регулярно':
                                                send_msg(user_id, 'Вы занимаетесь сельскохозяйственной деятельностью?',
                                                         get_keyboard('yesno'))
                                                for event in longpoll.listen():
                                                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                                        msg = event.text.lower()
                                                        if msg == 'да':
                                                            send_msg(user_id,
                                                                     'Информация о филиалах и режимах работы СКПК')
                                                            send_msg(user_id,
                                                                     'На этом мои полномочия заканчиваются:( Предлагаю Вам перейти на наш сайт для дальнейших действий ссылка на сайт')
                                                        elif msg == 'нет':
                                                            send_msg(user_id,
                                                                     'Информация о филиалах и режимах работы КПК')
                                                            send_msg(user_id,
                                                                     'На этом мои полномочия заканчиваются:( Предлагаю Вам перейти на наш сайт для дальнейших действий ссылка на сайт')

                                            elif msg == 'пока разово':
                                                send_msg(user_id,
                                                         'Тогда предлагаю Вам воспользоваться услугами МФК, МКК или Ломбарда.\n\n Информация о филиалах и режимах работы')
                                                send_msg(user_id, 'Не хотели бы вы вступить в КПК/СКПК?',
                                                         get_keyboard('regulary'))
                                                for event in longpoll.listen():
                                                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                                        msg = event.text.lower()
                                                        if msg == 'хотел(-а) бы':
                                                            send_msg(user_id,
                                                                     'Вы занимаетесь сельскохозяйственной деятельностью?',
                                                                     get_keyboard('yesno'))
                                                            for event in longpoll.listen():
                                                                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                                                    msg = event.text.lower()
                                                                    if msg == 'да':
                                                                        send_msg(user_id,
                                                                                 'Информация о филиалах и режимах работы СКПК')
                                                                        send_msg(user_id,
                                                                                 'На этом мои полномочия заканчиваются:( Предлагаю Вам перейти на наш сайт для дальнейших действий ссылка на сайт')
                                                                    elif msg == 'нет':
                                                                        send_msg(user_id,
                                                                                 'Информация о филиалах и режимах работы КПК')
                                                                        send_msg(user_id,
                                                                                 'На этом мои полномочия заканчиваются:( Предлагаю Вам перейти на наш сайт для дальнейших действий ссылка на сайт')

                                                        elif msg == 'не хотел(-а) бы':
                                                            send_msg(user_id,
                                                                     'На этом мои полномочия заканчиваются:( Предлагаю Вам перейти на наш сайт для дальнейших действий ссылка на сайт')

                    elif msg == 'хочу проверить организацию':
                        send_msg(user_id, f"Хорошо, {get_user_name(user_id)}, введите информацию об организации",
                                 get_keyboard("rrr"))
                        for event in longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                msg = event.text.lower()
                                user_id = event.user_id
                                print(msg, '-', user_id)
                                if msg == 'ввод инн/огрн организации':
                                    send_msg(user_id, f"Хорошо, {get_user_name(user_id)}, введите данные (ИНН/ОГРН)")
                                    for event in longpoll.listen():
                                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                            msg = event.text.lower()
                                            user_id = event.user_id
                                            print(msg, '-', user_id)
                                            url = f"http://127.0.0.1:8000/api/v1/company/?search={msg}"
                                            response = requests.get(url)
                                            if response.status_code == 200:
                                                data = response.json()
                                                if len(data) == 0:
                                                    send_msg(user_id,
                                                             f"Такой организации у меня в базе не оказалось :(")
                                                    send_msg(user_id,
                                                             f"Вы можете перейти в начало, если хотите получить еще какую-то услугу или перейти на наш сайт (ссылка на сайт)")
                                                else:
                                                    send_msg(user_id, response.text)
                                                    send_msg(user_id,
                                                             f"Вы можете перейти в начало, если хотите получить еще какую-то услугу или перейти на наш сайт (ссылка на сайт)")
                                                    send_msg(user_id,
                                                             "Вы можете оставить свою жалобу здесь (ссылка на сайт)")
                                                    send_msg(user_id,
                                                             "Вы можете воспользоваться услугами организации (ссылка на сайт)")
                                elif msg == 'ввод наименования организации':
                                    send_msg(user_id,
                                             f"Хорошо, {get_user_name(user_id)}, введите данные (Наименование)")
                                    for event in longpoll.listen():
                                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                            msg = event.text.lower()
                                            user_id = event.user_id
                                            print(msg, '-', user_id)
                                            url = f"http://127.0.0.1:8000/api/v1/company/?search={msg}"
                                            response = requests.get(url)
                                            if response.status_code == 200:
                                                data = response.json()
                                                if len(data) >= 2:
                                                    send_msg(user_id,
                                                             "С таким названием найдено несколько организаций, уточните ИНН/ОГРН",
                                                             get_keyboard("rr"))
                                                    for event in longpoll.listen():
                                                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                                            msg = event.text.lower()
                                                            user_id = event.user_id
                                                            print(msg, '-', user_id)
                                                            if msg == 'ввод инн/огрн организации':
                                                                send_msg(user_id,
                                                                         f"Хорошо, {get_user_name(user_id)}, введите данные (ИНН/ОГРН)")
                                                                for event in longpoll.listen():
                                                                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                                                        msg = event.text.lower()
                                                                        user_id = event.user_id
                                                                        print(msg, '-', user_id)
                                                                        url = f"http://127.0.0.1:8000/api/v1/company/?search={msg}"
                                                                        response = requests.get(url)
                                                                        if response.status_code == 200:
                                                                            data = response.json()
                                                                            if len(data) == 0:
                                                                                send_msg(user_id,
                                                                                         f"Такой организации у меня в базе не оказалось :(")
                                                                                send_msg(user_id,
                                                                                         f"Вы можете перейти в начало, если хотите получить еще какую-то услугу или перейти на наш сайт (ссылка на сайт)")
                                                                            else:
                                                                                send_msg(user_id, response.text)
                                                                                send_msg(user_id,
                                                                                         f"Вы можете перейти в начало, если хотите получить еще какую-то услугу или перейти на наш сайт (ссылка на сайт)")
                                                                                send_msg(user_id,
                                                                                         "Вы можете оставить свою жалобу здесь (ссылка на сайт)")
                                                                                send_msg(user_id,
                                                                                         "Вы можете воспользоваться услугами организации (ссылка на сайт)")
                                                            else:
                                                                send_msg(user_id,
                                                                         f"Извините, {get_user_name(user_id)}, я вас не понимаю",
                                                                         get_keyboard("rr"))
                                                elif len(data) == 0:
                                                    send_msg(user_id,
                                                             f"Такой организации у меня в базе не оказалось :(")
                                                    send_msg(user_id,
                                                             f"Вы можете перейти в начало, если хотите получить еще какую-то услугу или перейти на наш сайт (ссылка на сайт)")
                                                else:
                                                    send_msg(user_id, response.text)
                                                    send_msg(user_id,
                                                             f"Вы можете перейти в начало, если хотите получить еще какую-то услугу или перейти на наш сайт (ссылка на сайт)")
                                                    send_msg(user_id,
                                                             "Вы можете оставить свою жалобу здесь (ссылка на сайт)")
                                                    send_msg(user_id,
                                                             "Вы можете воспользоваться услугами организации (ссылка на сайт)")

                                else:
                                    send_msg(user_id, f"Извините, {get_user_name(user_id)}, я вас не понимаю",
                                             get_keyboard("rrr"))
                    else:
                        send_msg(user_id, f"Извините, {get_user_name(user_id)}, я вас не понимаю", get_keyboard("1st"))
