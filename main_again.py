import vk_api
import config
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


        elif msg == 'сбережения':
            message = "Вы хотели бы обратиться онлайн или офлайн?"
            send_msg(user_id, message, get_keyboard("on_off"), state="service_selection_sber")


        elif msg == 'онлайн' and user_states[user_id] == 'service_selection_sber':
            message = 'Обратите внимание, что онлайн Вы можете получить услугу только у МФК и МКК.'
            send_msg(user_id, message, get_keyboard("rethink_sber"), state="on_off_sber")
        elif msg == 'офлайн' and user_states[user_id] == 'service_selection_sber':
            message = 'Как часто Вы хотите пользоваться услугами? Если регулярно, то лучше стать членом КПК/СКПК и получать услугу в любой удобный момент!'
            send_msg(user_id, message, get_keyboard("once"), state="once_sber")

        elif msg == 'хорошо, продолжить' and user_states[user_id] == 'on_off_sber':
            message = 'Обратите внимание, что минимальные инвестиции в МФК составляют 1,5 млн'
            send_msg(user_id, message, get_keyboard("rethink_sber"), state="agreement_sber")
        #### ввод сумм и тд дальше в этой ветке


        elif msg == 'регулярно' and user_states[user_id] == 'once_sber':
            message = 'Вы занимаетесь сельскохозяйственной деятельностью?'
            send_msg(user_id, message, get_keyboard("selhoz_sber"), state="selhos_sber")
        #if msg == 'да' and user_states[user_id] == 'selhoz_sber':
            #message = "Тогда предлагаю Вам воспользоваться услугами СКПК. Обратите внимание, что СКПК требует постоянного членства"
        #if msg == 'нет' and user_states[user_id] == 'selhoz_sber':
            #message = "Тогда предлагаю Вам воспользоваться услугами КПК. Обратите внимание, что КПК требует постоянного членства"
        #if msg == 'пока разово' and user_states[user_id] == 'once_sber':
            #message = 'Тогда предлагаю Вам воспользоваться услугами МФК, МКК или Ломбарда.'
            #доделать, когда с sql разберусь