from .bot import Bot
from .id_bot import IdMixin

from config import CENSOR_GUILDS
from discord.commands import DeleteCommand, IdCommand, MessageCommand, ReplyCommand


class CensorBot(IdMixin, Bot):
    def __init__(self):
        super().__init__()

    @property
    def receive_all_messages(self):
        return 'raw'

    async def handle_message(self, gid, cid, author_info, data):
        text = data['content']
        if gid not in CENSOR_GUILDS or author_info['id'] == self._bot_id:
            return

        # censored_words is a list of words ex: censored_words = ["aaa", "bbb"]
        censored = censor(censored_words, text) 
        # if the message contains a censored word, delete it and capture the message
        if censored:
            message_out = f'Censored - {author_info["username"]}: {censored}'
            reply_info = data.get('message_reference')
            ret = [DeleteCommand()]

            # check if the message is a reply
            if reply_info is None:
                ret.append(MessageCommand(cid, message_out))
            else:
                # readd any user mentions that may have been in the original message
                allow_mentions = False
                if 'mentions' in data:
                    allow_mentions = {'user': [user['id'] for user in data['mentions']]}
                ret.append(ReplyCommand(gid, cid, reply_info['message_id'], message_out, allow_mentions=allow_mentions))
            return ret

def censor(words, message_text):
    msg = message_text
    count = 0
    
    # censors out all censored words
    for word in words:
        while word in msg.lower():
            word_index = msg.lower().index(word);
            word_length = len(word)
            replacement_str = word[0] + "*" + word[:1]
                
            msg = msg[:word_index] + replacement_str + msg[word_index + len(word):]
            count = count + 1

    if count >= 1:
        return msg
    else:
        return None
