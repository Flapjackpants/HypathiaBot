launch_code = '/oppenheimer 7839cvtnn9t87234'

def handle_response(message) -> str:
    p_message = message.lower()

    if p_message == '/test':
        return 'test successful'

    if p_message == '/help':
        return "Coming soon..."

    if p_message == '/ojal':
        return '42.479388, -83.500751'

    if p_message == launch_code:
        return 'https://tenor.com/view/explosion-mushroom-cloud-atomic-bomb-bomb-boom-gif-4464831'

    if 'im gay' in p_message:
        return 'https://tenor.com/view/dioramoseggloshara-gif-25426460'


